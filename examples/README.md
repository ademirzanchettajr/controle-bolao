# Exemplos de Uso - Sistema de Controle de Bolão

Este diretório contém exemplos práticos de uso do Sistema de Controle de Bolão, incluindo scripts de demonstração e dados de teste.

## Estrutura dos Exemplos

```
examples/
├── README.md                           # Este arquivo
├── dados_teste/                        # Dados de exemplo para demonstração
│   ├── participantes.txt              # Lista de participantes
│   ├── participantes.xlsx             # Planilha com participantes
│   ├── tabela_jogos.txt               # Tabela de jogos em texto
│   ├── tabela_jogos.xlsx              # Tabela de jogos em Excel
│   ├── palpites_rodada1.txt           # Palpites da rodada 1
│   ├── palpites_rodada2.txt           # Palpites da rodada 2
│   └── palpites_whatsapp.txt          # Exemplos de mensagens do WhatsApp
├── scripts_exemplo/                    # Scripts de demonstração
│   ├── 01_setup_completo.py           # Configuração completa de campeonato
│   ├── 02_importar_dados.py           # Importação de dados
│   ├── 03_processar_rodada.py         # Processamento de rodada
│   ├── 04_fluxo_completo.py           # Fluxo completo de uma rodada
│   └── 05_cenarios_especiais.py       # Cenários especiais e edge cases
└── resultados_esperados/               # Resultados esperados dos exemplos
    ├── classificacao_rodada1.txt      # Classificação esperada rodada 1
    ├── classificacao_rodada2.txt      # Classificação esperada rodada 2
    └── relatorio_final.txt            # Relatório final esperado
```

## Como Usar os Exemplos

### 1. Executar Setup Completo

```bash
cd examples/scripts_exemplo
python 01_setup_completo.py
```

Este script demonstra:
- Criação de campeonato
- Geração de regras
- Criação de participantes
- Importação de tabela

### 2. Importar Dados

```bash
python 02_importar_dados.py
```

Demonstra diferentes formatos de importação:
- Participantes de arquivo texto e Excel
- Tabela de jogos de arquivo texto e Excel
- Palpites de mensagens do WhatsApp

### 3. Processar Rodada

```bash
python 03_processar_rodada.py
```

Mostra o processamento completo de uma rodada:
- Modo teste para verificação
- Modo final com backup e relatório

### 4. Fluxo Completo

```bash
python 04_fluxo_completo.py
```

Executa um fluxo completo de 2 rodadas:
- Setup inicial
- Importação de palpites
- Processamento de resultados
- Geração de relatórios

### 5. Cenários Especiais

```bash
python 05_cenarios_especiais.py
```

Demonstra tratamento de:
- Nomes de times com variações
- Palpites em formatos diferentes
- Situações de erro e recuperação

## Dados de Teste Incluídos

### Campeonato: Copa-Exemplo-2025

**Participantes (9 pessoas)**:
- João Silva
- Maria Santos
- Pedro Oliveira
- Ana Costa
- Carlos Alberto
- Fernanda Lima
- Roberto Carlos
- José Santos
- Mario Silva

**Times**:
- Flamengo, Palmeiras, São Paulo, Corinthians
- Santos, Grêmio, Atlético-MG, Botafogo
- Vasco, Cruzeiro, Internacional, Bahia

**Rodadas**:
- Rodada 1: 6 jogos (13/04/2025)
- Rodada 2: 6 jogos (20/04/2025)

### Formatos de Palpites Demonstrados

1. **Formato Básico**:
```
João Silva
Rodada 1
Flamengo 2x1 Palmeiras
Santos 0-0 Corinthians
```

2. **Formato com Marcadores**:
```
Apostador: Maria Santos
1ª Rodada:
Flamengo 2-1 Palmeiras
Santos 0x0 Corinthians
```

3. **Formato WhatsApp Real**:
```
Oi pessoal, meus palpites da rodada 1:

Flamengo 3 x 1 Palmeiras
Santos 1-1 Corinthians
São Paulo 2x0 Grêmio
Atlético-MG 1 x 2 Botafogo
Vasco 0-1 Cruzeiro
Internacional 2x1 Bahia

Valeu!
Pedro
```

## Resultados Esperados

Os exemplos incluem os resultados esperados para validação:

### Classificação Rodada 1
```
Pos | Participante    | Pts Rodada | Pts Total | Variação
----|-----------------|------------|-----------|----------
1º  | João Silva      | 15.33      | 15.33     | --
2º  | Maria Santos    | 14.00      | 14.00     | --
3º  | Pedro Oliveira  | 13.00      | 13.00     | --
```

### Códigos de Acerto Demonstrados
- **AR**: Resultado exato (12 + bônus)
- **VG**: Vencedor + gols de uma equipe (7 pts)
- **VD**: Vencedor + diferença de gols (6 pts)
- **V**: Apenas vencedor (5 pts)
- **E**: Apenas empate (5 pts)
- **G**: Gols de um time (2 pts)
- **S**: Soma total de gols (1 pt)
- **RI**: Resultado invertido (-3 pts)
- **PA**: Palpite ausente (-1 pt)

## Validação dos Exemplos

Para validar que os exemplos funcionam corretamente:

```bash
# Executar todos os exemplos
cd examples/scripts_exemplo
python 01_setup_completo.py
python 02_importar_dados.py
python 03_processar_rodada.py

# Verificar resultados gerados
diff ../resultados_esperados/classificacao_rodada1.txt ../../Campeonatos/Copa-Exemplo-2025/Resultados/rodada01.txt
```

## Troubleshooting

### Problemas Comuns

1. **"Campeonato já existe"**
   - Remover diretório `Campeonatos/Copa-Exemplo-2025/` antes de executar

2. **"Arquivo não encontrado"**
   - Executar scripts a partir do diretório `examples/scripts_exemplo/`

3. **"Jogos não finalizados"**
   - Os scripts de exemplo atualizam automaticamente os resultados

### Limpeza

Para limpar os dados de exemplo:

```bash
rm -rf ../../Campeonatos/Copa-Exemplo-2025/
```

## Personalização

Para criar seus próprios exemplos:

1. Copie um dos scripts de exemplo
2. Modifique os dados em `dados_teste/`
3. Ajuste os nomes de campeonato e participantes
4. Execute e valide os resultados

---

**Nota**: Estes exemplos são para fins educacionais e demonstração. Use-os como base para entender o funcionamento do sistema antes de processar dados reais.