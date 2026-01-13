import re

class MIPSPipelineSimulator:
    def __init__(self):
        # Dicionário para rastrear quando (em qual ciclo) um registrador estará PRONTO
        self.reg_ready_cycle = {} 
        
    def parse_instr(self, instr):
        """
        Lê uma linha de instrução e separa em:
        - OP: Operação (ADD, L.D, etc)
        - DEST: Registrador de destino (quem é escrito)
        - SRCS: Lista de registradores fonte (quem é lido)
        """
        # Limpeza básica
        instr = instr.split('#')[0].strip() # Remove comentários
        parts = re.split(r'[,\s]+', instr)
        parts = [p for p in parts if p] # Remove strings vazias
        
        if not parts: return None, None, []
        
        op = parts[0].upper()
        
        # Se for Label (ex: "Loop:")
        if op.endswith(':'): return 'LABEL', None, []
        
        dest = None
        srcs = []
        
        # --- Lógica de Parsing MIPS ---
        
        # Categoria 1: Stores e Branches (Não escrevem em registrador, só lêem)
        # Ex: S.D F4, 0(R1) -> Lê F4 e R1. Destino é memória (None).
        # Ex: BEQ R1, R2, Label -> Lê R1 e R2.
        if op in ['S.D', 'SW', 'SB', 'BEQ', 'BNE', 'JR']:
            dest = None
            # Varre os argumentos procurando registradores
            for p in parts[1:]:
                # Se for formato 0(R1), extrai o R1
                if '(' in p:
                    srcs.append(p.split('(')[1].replace(')', ''))
                # Se for label de desvio, ignora
                elif not re.match(r'^[A-Za-z_]+$', p): # Ignora labels simples
                     srcs.append(p)
                # Adiciona registradores normais (ex: F4, R1)
                elif '$' in p or p.upper().startswith('R') or p.upper().startswith('F'):
                     srcs.append(p)

        # Categoria 2: Instruções Aritméticas e Loads (Escrevem em 1 registrador)
        # Ex: ADD R1, R2, R3 -> Dest: R1, Srcs: R2, R3
        # Ex: L.D F0, 0(R1)  -> Dest: F0, Srcs: R1
        else:
            if len(parts) > 1:
                dest = parts[1] # O primeiro argumento geralmente é o destino
                # O resto são fontes
                for p in parts[2:]:
                    if '(' in p:
                        srcs.append(p.split('(')[1].replace(')', ''))
                    else:
                        srcs.append(p)
        
        return op, dest, srcs

    def get_latency(self, op):
        """Define quantos ciclos leva para o dado ficar pronto (Forwarding assumido)"""
        if op in ['DIV.D', 'DIV']: return 10  # Divisão é lenta
        if op in ['MUL.D', 'MUL']: return 4   # Multiplicação média
        if op in ['L.D', 'LW']:    return 2   # Load tem atraso de 1 ciclo (Latencia 2)
        return 1 # ADD, SUB, etc (Resultado pronto no ciclo seguinte via Forwarding)

    def analyze(self, code_str, title=""):
        print(f"\n{'='*60}")
        print(f" ANÁLISE: {title}")
        print(f"{'='*60}")
        
        lines = code_str.strip().split('\n')
        
        self.reg_ready_cycle = {} # Reseta estado
        current_cycle = 1
        output_log = []
        total_stalls = 0
        
        print(f"{'CICLO':<8} | {'INSTRUÇÃO':<30} | {'AÇÃO'}")
        print("-" * 60)

        for line in lines:
            line = line.strip()
            if not line: continue
            
            op, dest, srcs = self.parse_instr(line)
            
            if op == 'LABEL':
                print(f"{current_cycle:<8} | {line:<30} | Label")
                continue
            
            # 1. VERIFICA CONFLITOS (HAZARDS)
            max_stall = 0
            wait_reg = ""
            
            for src in srcs:
                if src in self.reg_ready_cycle:
                    ready_at = self.reg_ready_cycle[src]
                    # Se o dado só fica pronto no futuro (ready_at > current_cycle)
                    if ready_at > current_cycle:
                        wait = ready_at - current_cycle
                        if wait > max_stall:
                            max_stall = wait
                            wait_reg = src
            
            # 2. INSERE BOLHAS (NOPs) SE NECESSÁRIO
            if max_stall > 0:
                for _ in range(max_stall):
                    print(f"{current_cycle:<8} | {'NOP':<30} | Bolha (Esperando {wait_reg})")
                    current_cycle += 1
                    total_stalls += 1
            
            # 3. EXECUTA INSTRUÇÃO ATUAL
            print(f"{current_cycle:<8} | {line:<30} | Executa {op}")
            
            # 4. CALCULA QUANDO O DESTINO ESTARÁ PRONTO
            if dest:
                latency = self.get_latency(op)
                # Dado disponível no início do ciclo: Atual + Latência
                self.reg_ready_cycle[dest] = current_cycle + latency
            
            current_cycle += 1 # Avança pipeline

        # RESULTADO FINAL DO BLOCO
        exec_cycles = current_cycle - 1
        print("-" * 60)
        print(f"RESULTADO FINAL:")
        print(f"Instruções Úteis: {len(lines)}")
        print(f"Bolhas (NOPs):    {total_stalls}")
        print(f"Total de Ciclos:  {exec_cycles}")
        return exec_cycles

# ==========================================
#  ENTRADAS (CÓDIGOS DA TAREFA)
# ==========================================

code_A = """
ADD $t0, $t1, $t2
SUB $t3, $t0, $t4
AND $t5, $t3, $t6
OR $t7, $t5, $t8
"""

code_B = """
ADD R1, R2, R3
SUB R4, R1, R5
AND R6, R1, R7
OR R8, R1, R9
XOR R10, R1, R11
"""

# Caso C (Com Loop) - Análise de uma iteração
code_C = """
L.D F0, 0(R1)
ADD.D F4, F0, F2
S.D F4, 0(R1)
DADDUI R1, R1, #-8
BNE R1, R2, Loop
"""

# Caso C OTIMIZADO (Exemplo de Reordenação Manual)
code_C_opt = """
L.D F0, 0(R1)
DADDUI R1, R1, #-8
ADD.D F4, F0, F2
BNE R1, R2, Loop
S.D F4, 8(R1)
"""

code_D = """
DIV.D F0, F2, F4
ADD.D F10, F0, F8
SUB.D F12, F8, F14
"""

code_E = """
DIV.D F0, F2, F4
ADD.D F6, F0, F8
S.D F6, 0(R1)
SUB.D F8, F10, F14
MUL.D F6, F10, F8
"""

code_F = """
ADD R4, R5, R6
BEQ R1, R2, EXIT
OR R7, R8, R9
"""

# ==========================================
#  EXECUÇÃO PRINCIPAL
# ==========================================
sim = MIPSPipelineSimulator()

# Executa e avalia cada caso
sim.analyze(code_A, "Caso A - Dependência em Cadeia")
sim.analyze(code_B, "Caso B - Dependência Múltipla de R1")
sim.analyze(code_C, "Caso C - Loop Original (Load-Use)")
sim.analyze(code_C_opt, "Caso C - OTIMIZADO (Reordenado)")
sim.analyze(code_D, "Caso D - Dependência de Divisão")
sim.analyze(code_E, "Caso E - Divisão e Store")
sim.analyze(code_F, "Caso F - Branch")