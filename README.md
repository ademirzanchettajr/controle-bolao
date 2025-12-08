# Sistema de Controle de Bolão

## Visão Geral

Sistema para gerenciar apostas esportivas de um grupo fechado de participantes pré-cadastrados. O sistema processa palpites de resultados de jogos de futebol, calcula pontuações baseadas em regras definidas e mantém classificações por campeonato.

## Índice

1. [Funcionalidades Principais](#funcionalidades-principais)
2. [Estrutura de Diretórios](#estrutura-de-diretórios)
3. [Gestão de Campeonatos](#gestão-de-campeonatos)
4. [Processamento de Palpites](#processamento-de-palpites)
5. [Sistema de Pontuação](#sistema-de-pontuação)
6. [Classificação e Rankings](#classificação-e-rankings)
7. [Formatos de Dados](#formatos-de-dados)

---

## Funcionalidades Principais

- **Gestão Multi-Campeonato**: Suporte para múltiplos campeonatos simultâneos
- **Processamento Automático**: Conversão de mensagens de texto (WhatsApp) em dados estruturados JSON
- **Sistema de Pontuação Flexível**: Regras configuráveis por campeonato
- **Classificação em Tempo Real**: Atualização automática de rankings após cada rodada
- **Armazenamento Estruturado**: Organização hierárquica de dados por campeonato

---

## Estrutura de Diretórios

O sistema organiza os dados seguindo uma estrutura hierárquica padronizada:

```
Campeonatos/
├── {NomeDoCampeonato}/
│   ├── Regras/
│   │   └── regras.json
│   ├── Tabela/
│   │   └── tabela.json
│   ├── Resultados/
│   │   ├── rodada01.json
│   │   ├── rodada02.json
│   │   └── ...
│   └── Participantes/
│       ├── {NomeParticipante1}/
│       │   └── palpites.json
│       ├── {NomeParticipante2}/
│       │   └── palpites.json
│       └── ...
```

### Exemplo Prático

```
Campeonatos/
├── Brasileirao-2025/
│   ├── Regras/
│   │   └── regras.json
│   ├── Tabela/
│   │   └── tabela.json
│   ├── Resultados/
│   │   ├── rodada01.json
│   │   └── rodada02.json
│   └── Participantes/
│       ├── MarioSilva/
│       │   └── palpites.json
│       └── JoaoSantos/
│           └── palpites.json
└── CampeonatoPaulista-2025/
    ├── Regras/
    │   └── regras.json
    ├── Tabela/
    │   └── tabela.json
    ├── Resultados/
    │   └── rodada01.json
    └── Participantes/
        └── MarioSilva/
            └── palpites.json
```

---

## Gestão de Campeonatos

### Características

- Cada campeonato é independente com suas próprias regras e participantes
- Pontuações e palpites são isolados por campeonato
- Tabela de jogos mantida em formato JSON agrupada por rodadas

### Componentes por Campeonato

1. **Regras** (`regras.json`): Define o sistema de pontuação específico
2. **Tabela** (`tabela.json`): Lista completa de jogos organizados por rodada
3. **Resultados**: Resultados oficiais de cada rodada
4. **Participantes**: Palpites individuais de cada apostador

---

## Processamento de Palpites

### Fluxo de Entrada

1. Participante envia mensagem de texto via WhatsApp
2. Sistema extrai e processa o texto não estruturado
3. Dados são convertidos para formato JSON
4. Arquivo `palpites.json` é criado/atualizado no diretório do participante

### Formato de Entrada (Texto WhatsApp)

Exemplo de mensagem recebida:

```
Apostador: Mario Silva
1ª Rodada:
Atlético/MG 1 x 2 Flamengo 
Grêmio 1 x 2 Palmeiras
Vitória 1 x 2 Mirassol 

Aposta Extra:
Jogo 5: Santos 2 x 1 Sport
```

Em algumas instancias, os apostadores mandam os palpites sem a informacao sobre o numero da rodada. Nesses casos o sistema deve tentar encontrar a rodada correta atraves de checagem dos nomes dos times e rodadas registrados no sistema, e sugerir para qual rodada o palpite esta relacionado.

### Características do Parser

- Suporta formato livre de texto
- Identifica apostador, rodada e palpites
- Reconhece diferentes formatos de escrita (ex: "2x1", "2 x 1")
- Processa apostas extras quando aplicável
- Normaliza nomes de times

---

## Sistema de Pontuação

### Hierarquia de Pontuação

O sistema avalia palpites em ordem de precisão, atribuindo pontos conforme o nível de acerto:

#### 1. Resultado Exato (12 pontos + bônus)
- **Condição**: Placar do palpite idêntico ao resultado oficial
- **Pontuação**: 12 pontos fixos + bônus
- **Bônus**: 1 ponto ÷ número de apostadores que acertaram o mesmo jogo
- **Exemplo**: Palpite "2x1" e resultado oficial "2x1"
- **Código**: AR

#### 2. Vitória + Gols de Uma Equipe (7 pontos)
- **Condição**: Acerta o vencedor E o número de gols de um dos times
- **Pontuação**: 7 pontos
- **Exemplo**: Palpite "3x1", resultado "3x2" (acertou os 3 gols do vencedor)
- **Código**: VG

#### 3. Vitória + Diferença de Gols (6 pontos)
- **Condição**: Acerta o vencedor E a diferença entre gols do vencedor e perdedor
- **Pontuação**: 6 pontos
- **Exemplo**: Palpite "2x0", resultado "3x1" (diferença de 2 gols em ambos)
- **Código**: VD

#### 4. Vitória + Soma de Gols (6 pontos)
- **Condição**: Acerta o vencedor E o total de gols da partida
- **Pontuação**: 6 pontos
- **Exemplo**: Palpite "2x1", resultado "3x0" (soma = 3 gols em ambos)
- **Código**: VS

#### 5. Apenas Vitória (5 pontos)
- **Condição**: Acerta apenas qual time venceu
- **Pontuação**: 5 pontos
- **Exemplo**: Palpite "1x0", resultado "3x1" (ambos vitória do mandante)
- **Código**: AV


#### 6. Apenas Empate (5 pontos)
- **Condição**: Acerta que houve empate, mas não o placar
- **Pontuação**: 5 pontos
- **Exemplo**: Palpite "1x1", resultado "2x2"
- **Código**: AE

#### 7. Gols de Um Time (2 pontos)
- **Condição**: Acerta o número de gols de apenas um time, sem acertar resultado
- **Pontuação**: 2 pontos
- **Exemplo**: Palpite "2x1", resultado "2x3" (acertou 2 gols, mas so de um dos times e o sem acertar o time vitorioso)
- **Código**: AG

#### 8. Soma de Gols (1 ponto)
- **Condição**: Acerta apenas o total de gols, sem acertar resultado
- **Pontuação**: 1 ponto
- **Exemplo**: Palpite "2x1", resultado "0x3" (soma = 3 em ambos)
- **Código**: AS

#### 9. Resultado Inverso (-3 pontos)
- **Condição**: Placar exatamente oposto ao resultado oficial
- **Pontuação**: -3 pontos (penalidade)
- **Exemplo**: Palpite "2x1", resultado "1x2"
- **Código**: RI

#### 9. Sem Palpite (-1 ponto)
- **Condição**: Apostador nao enviou palpite para o jogo
- **Pontuação**: -1 ponto (penalidade)
- **Código**: SP


### Regras de Aplicação

- As condições são avaliadas em ordem de prioridade
- Apenas uma pontuação é atribuída por palpite (a de maior valor aplicável)
- O bônus do resultado exato é proporcional ao número de acertos

---

## Classificação e Rankings

### Cálculo de Classificação

- Calcular inicialmente o resultado da rodada atual com detalhes
- Soma total determina a posição no ranking
- Depois calcular pontuação acumulada de todas as rodadas, ate a rodada atual
- Atualização automática após processamento de cada rodada, incluindo geração do relatorio para apostadores

### Formato de Apresentação

A classificação é exibida em formato tabular.
O relatorio inicial da rodada atual tem o seguinte formato:

| COLOCACAO | VARIACAO | PARTICIPANTE | GRE X FLU | FOR X COR | SP X INT | Extra | Rodada | TOTAL | PG |
| ----------|----------|--------------|-----------|-----------|----------|-------|--------|------|----|
| 1 | 0 | Murilo Zanchetta | AG	2.00 |	AE	5.00 |	AS	1.00 |	0.00 | 8.00 | 585.20 | 80.00 |
| 2 | 0 | Vitinho |	AG	2.00 |	VD	6.00 |	VG	7.00 |	0.00 | 15.00 | 	554.95 | 80.00 |
| 3 | 0 | Gú Stival |	AG	2.00 |	VD	6.00 |	VG	7.00 |	0.00 | 15.00 | 526.01 |	80.00 |
| 4 | 0 | Renan Dias | AR	12.05 |	AG	2.00 |	0.00 |	0.00 | 14.05 | 521.63 |	80.00 |
| 5 | +1 | David Guidotti | AR	12.05 |	VD	6.00 |	VG	7.00 |	0.00 | 25.05 |	518.95 | 80.00 |
| 6 | -1 | Pedro Ivo | AS	1.00 |	AG	2.00 |	RI	-3.00 |	0.00 |	0.00 | 497.20 |	80.00 |
| 7 | -2 | Pedrox |	AV	5.00 |	0.00 | AS	1.00 |	0.00 | 6.00 | 493.82 | 80.00 |
| 8 | +2 | Waguinho Siqueira |	SP	-1.00 |	SP	-1.00 |	AS	1.00 | 0.00 |  -1.00 | 490.59 | 80.00 |
| 9 | 0 | Tatico |	AS	1.00 |	VD	6.00 | AV	5.00 |	0.00 |12.00 | 482.89 | 80.00 |
| 10 | +1 | Lucas Ribeiro |	AG	2.00 |	AG	2.00 |	AS	1.00 |	0.00 |	5.00 |	477.95 | 80.00 |


### Critérios de Ordenação

1. **Primário**: Maior pontuação total
2. **Desempate**: (a ser definido - sugestões: número de resultados exatos, rodada mais recente, etc.)

---

## Formatos de Dados

### 1. Tabela de Jogos (`tabela.json`)

Estrutura sugerida:

```json
{
  "campeonato": "Brasileirão 2025",
  "rodada_atual": 0,
  "data_atualizacao": "2025-04-01T05:00:00Z",
  "rodadas": [
    {
      "numero": 1,
      "data_inicial": "2025-04-10T16:00:00Z",
      "data_final": "2025-04-16T16:00:00Z",
      "jogos": [
        {
          "id": "jogo-001",
          "mandante": "Atlético/MG",
          "visitante": "Flamengo",
          "data": "2025-04-15T16:00:00Z",
          "local": "Mineirão",
          "gols_mandante": 0,
          "gols_visitante": 0,
          "status": "agendado",
          "obrigatorio": true 
        }
      ]
    }
  ]
}
```

### 2. Palpites (`palpites.json`)

Estrutura sugerida:

```json
{
  "apostador": "Mario Silva",
  "codigo_apostador": "0230",
  "campeonato": "Brasileirão 2025",
  "palpites": [
    {
      "rodada": 1,
      "data_palpite": "2025-02-15T10:00:00Z",
      "jogos": [
        {
          "id": "jogo-001",
          "mandante": "Atlético/MG",
          "visitante": "Flamengo",
          "palpite_mandante": 1,
          "palpite_visitante": 2
        }
      ]
    }
  ]
}
```

### 3. Resultados

Os resultados sao atualizados diretamente na Tabela de Jogos (`tabela.json`), onde o "status" de cada jogo é registrado.

```json
{
  "campeonato": "Brasileirão 2025",
  "rodada": 1,
  "jogos": [
    {
        "id": "jogo-001",
        "mandante": "Atlético/MG",
        "visitante": "Flamengo",
        "data": "2025-04-15T16:00:00Z",
        "local": "Mineirão",
        "gols_mandante": 1,
        "gols_visitante": 2,
        "status": "finalizado",
        "obrigatorio": true 
    }
  ]
}
```

### 4. Regras de Pontuação (`regras.json`)

Estrutura sugerida:

```json
{
  "campeonato": "Brasileirão 2025",
  "versao": "1.0",
  "regras": {
    "resultado_exato": {
      "pontos_base": 12,
      "bonus_divisor": true,
      "descricao": "Placar exato + bônus proporcional",
      "codigo": "AR"
    },
    "vitoria_gols_um_time": {
      "pontos": 7,
      "descricao": "Acerta vencedor e gols de uma equipe",
      "codigo": "VG"

    },
    "vitoria_diferenca_gols": {
      "pontos": 6,
      "descricao": "Acerta vencedor e diferença de gols",
      "codigo": "VD"
    },
    "vitoria_soma_gols": {
      "pontos": 6,
      "descricao": "Acerta vencedor e total de gols",
      "codigo": "VS"
    },
    "apenas_vitoria": {
      "pontos": 5,
      "descricao": "Acerta apenas o vencedor",
      "codigo": "AV"
    },
    "apenas_empate": {
      "pontos": 5,
      "descricao": "Acerta que houve empate",
      "codigo": "AE"
    },
    "gols_um_time": {
      "pontos": 2,
      "descricao": "Acerta gols de apenas um time",
      "codigo": "AG"
    },
    "soma_gols": {
      "pontos": 1,
      "descricao": "Acerta apenas o total de gols",
      "codigo": "AS"
    },
    "resultado_inverso": {
      "pontos": -3,
      "descricao": "Placar exatamente invertido",
      "codigo": "RI"
    },
    "sem_palpite": {
      "pontos": -1,
      "descricao": "Palpite nao enviado pelo apostador",
      "codigo": "SP"
    }
  }
}
```

---

## Requisitos Técnicos

### Funcionalidades a Implementar

1. **Parser de Mensagens**: Extração de palpites de texto não estruturado
2. **Motor de Pontuação**: Implementação das regras de cálculo
3. **Gerenciador de Campeonatos**: CRUD de campeonatos e configurações
4. **Processador de Resultados**: Comparação de palpites vs resultados oficiais
5. **Gerador de Rankings**: Cálculo e apresentação de classificações
6. **API de Integração**: Interface para recebimento de mensagens WhatsApp

### Considerações de Implementação

- Inicialmente, na fase de prototipo, criaremos arquivos Python a serem rodados localmente no computador do administrador. Nesse prototipo, criaremos codigo para automacao das seguintes tarefas:
  - Criacao inicial da estrutura de um campeonato novo. Exemplo: criar um subdirectorio especifico para o campeonato dentro de "Campeonatos" com a estrutura inicial pre-criada em com a criacao de arquivos de dados vazios a serem preenchidos.
  - Criar o arquivo de regras baseado nas regras padrao descritas no arquivo README.md
  - Criar a estrutura de dados de cada participante a partir de uma lista com o nome de cada um, em formato texto ou planilha excel.
  - Atualizar a tabela de jogos do campeonato automaticamente a partir de um arquivo texto ou planilha excel
  - Importar palpite de participante em formato text e registrar os dados no arquivo de palpites correspondente ao apostador.
  - Processar resultados da rodada, em modo teste (exibir resultados no output sem alterar arquivo tabela.json) ou em modo final (atualiza tabela.json apos criar uma copia backup do arquivo original)

Em todas essa tarefas o codigo gerado devera fazer:
- Validação de dados de entrada
- Tratamento de erros e casos especiais
- Suporte a múltiplos formatos de entrada de texto
- Normalização de nomes de times (ex: "Atlético/MG" = "Atlético-MG" = "Atletico MG")
- Histórico de alterações em palpites (se permitido)
- Backup e recuperação de dados

---

## Próximos Passos

1. Definir tecnologias e linguagens de programação
2. Criar especificações detalhadas de APIs
3. Desenvolver protótipo do parser de mensagens
4. Implementar motor de pontuação com testes unitários
5. Criar interface de visualização de classificações
6. Integrar com API do WhatsApp
7. Implementar testes end-to-end

---

## Notas de Versão

- **Versão 1.0**: Sistema básico para campeonatos de futebol
- **Futuras Expansões**: Outros esportes, apostas especiais, estatísticas avançadas
