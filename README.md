# Sistema de Controle de Bolão

Sistema de gerenciamento de apostas esportivas para grupos fechados de participantes pré-registrados.

## Visão Geral

O Sistema de Controle de Bolão é uma ferramenta para administradores que gerenciam grupos de apostas de futebol. O sistema processa palpites de mensagens do WhatsApp, calcula pontuações baseadas em regras configuráveis e gera classificações em tempo real.

### Características Principais

- **Suporte a múltiplos campeonatos** com pontuação e participantes independentes
- **Conversão automática** de mensagens de texto do WhatsApp para dados estruturados JSON
- **Sistema de pontuação flexível** com 10 níveis diferentes de precisão (do resultado exato às penalidades)
- **Geração automatizada de classificações** com relatórios detalhados por rodada
- **Organização hierárquica de dados** por campeonato/participante

## Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Dependências

Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

As principais dependências incluem:
- `hypothesis` - Para testes baseados em propriedades
- `pytest` - Framework de testes
- `openpyxl` - Leitura de planilhas Excel
- `python-dateutil` - Manipulação de datas
- `python-Levenshtein` - Cálculo de similaridade de strings

## Estrutura do Projeto

```
ControleBolao/
├── Campeonatos/                    # Diretório raiz dos campeonatos
│   └── {NomeDoCampeonato}/
│       ├── Regras/
│       │   └── regras.json         # Configuração das regras de pontuação
│       ├── Tabela/
│       │   └── tabela.json         # Cronograma e resultados dos jogos
│       ├── Resultados/
│       │   └── rodada01.txt        # Relatórios das rodadas
│       └── Participantes/
│           ├── {NomeParticipante}/
│           │   └── palpites.json   # Palpites do participante
│           └── formulario_palpites.md
├── src/
│   ├── scripts/                    # Scripts principais
│   └── utils/                      # Módulos utilitários
├── tests/                          # Testes automatizados
└── requirements.txt
```

## Guia de Uso

### 1. Criar um Novo Campeonato

```bash
python src/scripts/criar_campeonato.py --nome "Brasileirao-2025" --temporada 2025 --codigo "BR25"
```

**Parâmetros:**
- `--nome`: Nome do campeonato (será normalizado para nome de diretório)
- `--temporada`: Ano da temporada
- `--codigo`: Código único do campeonato (3-10 caracteres)

### 2. Gerar Regras de Pontuação

```bash
python src/scripts/gerar_regras.py --campeonato "Brasileirao-2025"
```

**Parâmetros:**
- `--campeonato`: Nome do campeonato
- `--sobrescrever`: (Opcional) Sobrescrever regras existentes sem confirmação

### 3. Criar Participantes

#### A partir de arquivo de texto:
```bash
python src/scripts/criar_participantes.py --campeonato "Brasileirao-2025" --arquivo participantes.txt
```

#### A partir de planilha Excel:
```bash
python src/scripts/criar_participantes.py --campeonato "Brasileirao-2025" --excel participantes.xlsx --coluna A
```

**Parâmetros:**
- `--campeonato`: Nome do campeonato
- `--arquivo`: Arquivo de texto com nomes (um por linha)
- `--excel`: Planilha Excel com nomes
- `--coluna`: Coluna da planilha (padrão: A)

### 4. Importar Tabela de Jogos

#### A partir de arquivo de texto:
```bash
python src/scripts/importar_tabela.py --campeonato "Brasileirao-2025" --arquivo tabela_jogos.txt
```

#### A partir de planilha Excel:
```bash
python src/scripts/importar_tabela.py --campeonato "Brasileirao-2025" --excel tabela_jogos.xlsx
```

**Parâmetros:**
- `--campeonato`: Nome do campeonato
- `--arquivo`: Arquivo de texto com jogos
- `--excel`: Planilha Excel com jogos
- `--mesclar`: (Opcional) Mesclar com tabela existente

### 5. Importar Palpites

#### Palpites de uma rodada:
```bash
python src/scripts/importar_palpites.py --campeonato "Brasileirao-2025" --arquivo palpites_rodada1.txt
```

#### Palpites de múltiplas rodadas:
```bash
python src/scripts/importar_palpites.py --campeonato "Brasileirao-2025" --arquivo palpites_completos.txt
```

#### Importar apenas uma rodada específica de um arquivo com múltiplas rodadas:
```bash
python src/scripts/importar_palpites.py --campeonato "Brasileirao-2025" --arquivo palpites_completos.txt --rodada 3
```

**Parâmetros:**
- `--campeonato`: Nome do campeonato
- `--arquivo`: Arquivo com texto dos palpites
- `--texto`: (Opcional) Texto direto dos palpites
- `--rodada`: (Opcional) Forçar número da rodada ou filtrar rodada específica
- `--forcar`: (Opcional) Não solicitar confirmações

### 6. Processar Resultados

#### Modo teste (apenas visualizar):
```bash
python src/scripts/processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --teste
```

#### Modo final (atualizar arquivos):
```bash
python src/scripts/processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --final
```

**Parâmetros:**
- `--campeonato`: Nome do campeonato
- `--rodada`: Número da rodada a processar
- `--teste`: Modo teste (não modifica arquivos)
- `--final`: Modo final (cria backup e atualiza arquivos)

## Formatos de Entrada Aceitos

### Formato de Palpites (WhatsApp)

O sistema aceita múltiplos formatos de texto para palpites, incluindo **palpites de múltiplas rodadas em um único arquivo**.

#### Formato Básico (Rodada Única):
```
João Silva
Rodada 1

Flamengo 2x1 Palmeiras
Santos 0-0 Corinthians
São Paulo 3 x 2 Grêmio
```

#### Formato com Múltiplas Rodadas:
```
Batman
Palpites Completos - Campeonato Paulista 2026

🦇 RODADA 1 🦇
São Paulo 2x1 Palmeiras
Corinthians 1-0 Santos
Ponte Preta 1x1 Guarani

🦇 RODADA 2 🦇
Palmeiras 2-1 Corinthians
Santos 3x0 Ponte Preta
Guarani 0x2 São Paulo

🦇 RODADA 3 🦇
São Paulo 1x0 Corinthians
Palmeiras 2-2 Santos
Ponte Preta 1x2 Mirassol
```

#### Marcadores de Rodada Suportados:
- `🦇 RODADA 1 🦇` (formato Batman)
- `⚡ RODADA 2 ⚡` (formato Robin)
- `RODADA 3` (formato simples)
- `1ª RODADA` (formato ordinal)
- `R4` (formato abreviado)
- `ROUND 5` (formato inglês)

#### Com Marcadores:
```
Apostador: Maria Santos
Rodada: 5

Flamengo 2-1 Palmeiras
Santos 0x0 Corinthians
São Paulo 3 - 2 Grêmio
```

#### Formatos de Placar Aceitos:
- `2x1`, `2-1`, `2 x 1`, `2 - 1`
- `0x0`, `0-0`, `0 x 0`, `0 - 0`
- `2:1` (formato com dois pontos)

### Formato de Tabela de Jogos

#### Arquivo de Texto:
```
Rodada 1
13/04/2025 16:00 - Flamengo x Palmeiras - Maracanã
13/04/2025 18:30 - Santos x Corinthians - Vila Belmiro

Rodada 2
20/04/2025 16:00 - Palmeiras x São Paulo - Allianz Parque
```

#### Planilha Excel:
| Rodada | Data | Hora | Mandante | Visitante | Local | Obrigatório |
|--------|------|------|----------|-----------|-------|-------------|
| 1 | 13/04/2025 | 16:00 | Flamengo | Palmeiras | Maracanã | Sim |
| 1 | 13/04/2025 | 18:30 | Santos | Corinthians | Vila Belmiro | Sim |

### Lista de Participantes

#### Arquivo de Texto:
```
João Silva
Maria Santos
Pedro Oliveira
Ana Costa
```

#### Planilha Excel:
| Nome |
|------|
| João Silva |
| Maria Santos |
| Pedro Oliveira |
| Ana Costa |

## Sistema de Pontuação

O sistema utiliza uma hierarquia de regras de pontuação:

1. **Resultado Exato (AR)**: 12 pontos + bônus (12/N, onde N = número de acertos exatos)
2. **Vencedor + Gols de Uma Equipe (VG)**: 7 pontos
3. **Vencedor + Diferença de Gols (VD)**: 6 pontos
4. **Vencedor + Soma Total de Gols (VS)**: 6 pontos
5. **Apenas Vencedor (V)**: 5 pontos
6. **Apenas Empate (E)**: 5 pontos
7. **Gols de Um Time (G)**: 2 pontos
8. **Apenas Soma Total de Gols (S)**: 1 ponto
9. **Resultado Invertido (RI)**: -3 pontos (penalidade)
10. **Palpite Ausente (PA)**: -1 ponto (jogo obrigatório)

### Exemplo de Cálculo:

**Resultado Real**: Flamengo 2x1 Palmeiras  
**Palpite**: Flamengo 2x1 Palmeiras  
**Pontuação**: 12 pontos (resultado exato) + bônus

**Resultado Real**: Flamengo 2x1 Palmeiras  
**Palpite**: Flamengo 3x1 Palmeiras  
**Pontuação**: 7 pontos (vencedor + gols do Flamengo)

## Estrutura dos Arquivos JSON

### tabela.json
```json
{
  "campeonato": "Brasileirao-2025",
  "temporada": 2025,
  "rodada_atual": 1,
  "codigo_campeonato": "BR25",
  "data_atualizacao": "2025-01-09T12:00:00Z",
  "rodadas": [
    {
      "numero": 1,
      "jogos": [
        {
          "id": "jogo-001",
          "mandante": "Flamengo",
          "visitante": "Palmeiras",
          "data": "2025-04-13T19:00:00Z",
          "local": "Maracanã",
          "gols_mandante": 2,
          "gols_visitante": 1,
          "status": "finalizado",
          "obrigatorio": true
        }
      ]
    }
  ]
}
```

### regras.json
```json
{
  "campeonato": "Brasileirao-2025",
  "temporada": 2025,
  "versao": "1.0",
  "data_criacao": "2025-01-09T12:00:00Z",
  "regras": {
    "resultado_exato": {
      "pontos_base": 12,
      "bonus_divisor": true,
      "descricao": "Resultado exato (placar idêntico)",
      "codigo": "AR"
    }
  }
}
```

### palpites.json
```json
{
  "apostador": "João Silva",
  "codigo_apostador": "JOAO001",
  "campeonato": "Brasileirao-2025",
  "temporada": 2025,
  "palpites": [
    {
      "rodada": 1,
      "data_palpite": "2025-04-13T10:00:00Z",
      "jogos": [
        {
          "id": "jogo-001",
          "mandante": "Flamengo",
          "visitante": "Palmeiras",
          "palpite_mandante": 2,
          "palpite_visitante": 1
        }
      ]
    }
  ]
}
```

## Fluxo de Trabalho Típico

1. **Configuração Inicial**:
   - Criar campeonato
   - Gerar regras padrão
   - Criar participantes
   - Importar tabela de jogos

2. **Por Rodada**:
   - Receber palpites via WhatsApp
   - Importar palpites no sistema
   - Aguardar finalização dos jogos
   - Atualizar resultados na tabela
   - Processar resultados (teste → final)
   - Compartilhar relatório gerado

3. **Manutenção**:
   - Backup automático antes de atualizações
   - Validação de dados em todas as operações
   - Logs de erro para troubleshooting

## Normalização de Nomes

O sistema normaliza automaticamente nomes de:

### Times:
- Remove acentos: "São Paulo" → "Sao Paulo"
- Converte separadores: "Atlético/MG" → "Atletico-MG"
- Normaliza case: "FLAMENGO" → "Flamengo"

### Participantes:
- Remove espaços: "João Silva" → "JoaoSilva"
- Remove caracteres especiais: "José (Zé)" → "JoseZe"
- Remove acentos: "José" → "Jose"

### Campeonatos:
- Substitui caracteres problemáticos: "Copa/2025" → "Copa-2025"
- Remove acentos: "Paulistão" → "Paulistao"
- Normaliza espaços: "Copa  Brasil" → "Copa-Brasil"

## Validação de Dados

O sistema valida automaticamente:

- **Estruturas JSON**: Campos obrigatórios e tipos de dados
- **Formatos de data**: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
- **Placares**: Números inteiros não-negativos
- **IDs de jogos**: Referências válidas na tabela
- **Participantes**: Registro no campeonato

## Tratamento de Erros

### Erros Comuns e Soluções:

**"Campeonato não encontrado"**
- Verificar nome exato do diretório em `Campeonatos/`
- Usar aspas se o nome contém espaços

**"Jogos obrigatórios não finalizados"**
- Atualizar status dos jogos para "finalizado"
- Verificar se todos os placares estão preenchidos

**"Participante não encontrado"**
- Verificar se o diretório do participante existe
- Conferir normalização do nome

**"Formato de data inválido"**
- Usar formato ISO 8601: `2025-04-13T19:00:00Z`
- Verificar timezone (sempre UTC)

## Testes

Execute os testes automatizados:

```bash
# Todos os testes
python -m pytest tests/ -v

# Testes específicos
python -m pytest tests/test_normalizacao.py -v

# Testes de propriedades
python -m pytest tests/test_*_properties.py -v
```

O sistema inclui 131 testes automatizados cobrindo:
- Testes unitários para funções individuais
- Testes de propriedades (Property-Based Testing)
- Testes de integração para fluxos completos

## Suporte e Contribuição

Este é um sistema em fase de protótipo. Para questões ou melhorias:

1. Verificar logs de erro nos scripts
2. Executar testes para identificar problemas
3. Consultar documentação de formatos aceitos
4. Validar estrutura de diretórios e arquivos

## Roadmap Futuro

- Integração com API do WhatsApp
- Interface web para visualização
- Migração para banco de dados
- Suporte a outros esportes além do futebol
- Sistema de notificações automáticas

---

**Versão**: 1.0  
**Última Atualização**: Janeiro 2025  
**Linguagem**: Python 3.8+  
**Licença**: Uso interno