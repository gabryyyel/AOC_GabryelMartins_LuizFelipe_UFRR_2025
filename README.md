🧠 MIPS Pipeline Optimization Simulator










Simulador didático de pipeline MIPS com detecção de hazards e inserção de stalls, desenvolvido para a disciplina de Arquitetura e Organização de Computadores II (AOC II).

📘 Sobre o Projeto

Este projeto realiza uma análise teórica e prática do impacto de hazards de dados e controle em um processador MIPS com pipeline clássico de 5 estágios.

Além da análise manual dos códigos MIPS, foi desenvolvido um simulador em Python capaz de:

🔍 Detectar dependências RAW
⚠️ Identificar Load-Use Hazard
🫧 Inserir bolhas (NOPs)
⏱️ Calcular ciclos totais de execução
📊 Comparar código original vs otimizado

O objetivo é demonstrar como técnicas de escalonamento estático de instruções reduzem o CPI efetivo e melhoram o throughput.

🏗️ Arquitetura Considerada

Pipeline MIPS clássico de 5 estágios:

Estágio	Descrição
IF	Instruction Fetch
ID	Instruction Decode
EX	Execute
MEM	Memory Access
WB	Write Back
🔎 Assumptions do Simulador
Forwarding habilitado
Load-Use gera 1 stall
Latências estimadas:
DIV.D → 10 ciclos
MUL.D → 4 ciclos
L.D / LW → 2 ciclos
Aritméticas simples → 1 ciclo
Modelo didático (não simula hardware real completo)
📂 Estrutura do Projeto
📁 mips-pipeline-simulator
 ├── simulator.py
 ├── README.md
 └── relatório.pdf
🧠 Casos Analisados
Caso	Descrição
A	Dependência RAW em cadeia
B	Dependência múltipla de registrador
C	Loop com Load-Use Hazard
C (Otimizado)	Reordenamento manual
D	Divisão com alta latência
E	RAW + possível WAW
F	Hazard de controle (Branch)
🐍 Simulador em Python

Classe principal:

class MIPSPipelineSimulator
🔧 Funcionalidades
Parsing automático de instruções MIPS
Identificação de registradores destino e fonte
Rastreamento de disponibilidade de dados
Inserção automática de bolhas
Relatório ciclo a ciclo
Cálculo total de ciclos e stalls
▶️ Como Executar
📌 Requisitos
Python 3.x
Biblioteca padrão re
📌 Execução
python simulator.py

O programa exibirá:

Tabela ciclo a ciclo
Inserção de NOPs
Total de ciclos
Total de bolhas
Comparação entre versões
📊 Exemplo de Saída
CICLO   | INSTRUÇÃO                    | AÇÃO
------------------------------------------------------------
1       | L.D F0, 0(R1)                | Executa L.D
2       | NOP                          | Bolha (Esperando F0)
3       | ADD.D F4, F0, F2             | Executa ADD.D
...
RESULTADO FINAL:
Instruções Úteis: 5
Bolhas (NOPs): 1
Total de Ciclos: 6
🚀 Resultados Obtidos
Redução de bolhas após reordenamento
Melhor aproveitamento do pipeline
Redução do número total de ciclos
Aproximação do CPI ao ideal teórico

O caso do loop (Caso C) apresentou a maior melhoria após otimização.

📚 Referências
Hennessy & Patterson – Computer Architecture: A Quantitative Approach
Patterson & Hennessy – Computer Organization and Design (MIPS Edition)
Stallings – Arquitetura e Organização de Computadores
Documentação Oficial MIPS32
🎓 Contexto Acadêmico

Disciplina: Arquitetura e Organização de Computadores II
Instituição: Universidade Federal de Roraima (UFRR)

Autores:

Luiz Felipe Faria Rodrigues
Gabryel Martins Assis
📌 Conclusão

Este projeto evidencia que:

O desempenho de arquiteturas com pipeline depende tanto do hardware quanto da organização das instruções.

A combinação entre análise teórica e simulação prática reforça a importância do entendimento de hazards para otimização eficiente.
