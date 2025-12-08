# Design Document

## Overview

O sistema de prototipagem consiste em um conjunto de scripts Python independentes que automatizam tarefas administrativas para gerenciamento de bolões esportivos. Cada script é executado localmente pelo administrador e opera sobre arquivos JSON estruturados seguindo uma hierarquia de diretórios padronizada. O design prioriza simplicidade, validação robusta de dados e operações seguras com backups automáticos.

Os scripts cobrem o ciclo completo de gerenciamento: desde a criação inicial da estrutura de um campeonato, passando pela importação de dados (tabelas e palpites), até o processamento de resultados e geração de relatórios de classificação.

## Architecture

### Arquitetura Geral

O sistema segue uma arquitetura modular baseada em scripts independentes, onde cada script é responsável por uma tarefa específica. Não há servidor ou banco de dados - todo o estado é mantido em arquivos JSON no sistema de arquivos local.

```
┌─────────────────────────────────────────────────────────────┐
│                    Administrador                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Scripts Python CLI                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Criação    │  │  Importação  │  │ Processamento│      │
│  │ Campeonato   │  │    Dados     │  │  Resultados  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Camada de Utilitários                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Normalização │  │  Validação   │  │   Parser     │      │
│  │    Times     │  │    Dados     │  │    Texto     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Sistema de Arquivos                             │
│                                                               │
│  Campeonatos/{Nome}/                                         │
│    ├── Regras/regras.json                                    │
│    ├── Tabela/tabela.json                                    │
│    ├── Resultados/rodadaXX.txt                               │
│    └── Participantes/{Nome}/palpites.json                    │
└─────────────────────────────────────────────────────────────┘
```

### Princípios de Design

1. **Operações Atômicas**: Cada script realiza uma tarefa completa e independente
2. **Validação Primeiro**: Todos os dados são validados antes de qualquer modificação
3. **Segurança com Backups**: Operações destrutivas sempre criam backups com timestamp
4. **Confirmação Explícita**: Operações críticas requerem confirmação do administrador
5. **Normalização Consistente**: Nomes de times são normalizados em todas as operações

## Components and Interfaces

### 1. Script de Criação de Campeonato (`criar_campeonato.py`)

**Responsabilidade**: Criar estrutura de diretórios e arquivos iniciais para um novo campeonato.

**Interface CLI**:
```python
python criar_campeonato.py --nome "Brasileirao-2025" --temporada "2025"
```

**Parâmetros**:
- `--nome`: Nome do campeonato (obrigatório)
- `--temporada`: Ano da temporada (obrigatório)
- `--codigo`: Código único do campeonato (opcional, gerado automaticamente se omitido)

**Saída**:
- Diretório `Campeonatos/{nome}/` com subdiretórios
- Arquivo `regras.json` vazio com estrutura básica
- Arquivo `tabela.json` vazio com estrutura básica

### 2. Script de Geração de Regras (`gerar_regras.py`)

**Responsabilidade**: Criar arquivo de regras com template padrão de pontuação.

**Interface CLI**:
```python
python gerar_regras.py --campeonato "Brasileirao-2025"
```

**Parâmetros**:
- `--campeonato`: Nome do campeonato (obrigatório)
- `--sobrescrever`: Flag para sobrescrever arquivo existente (opcional)

**Saída**:
- Arquivo `regras.json` populado com 10 regras padrão

### 3. Script de Criação de Participantes (`criar_participantes.py`)

**Responsabilidade**: Criar estrutura de diretórios e arquivos para participantes.

**Interface CLI**:
```python
python criar_participantes.py --campeonato "Brasileirao-2025" --arquivo "participantes.txt"
python criar_participantes.py --campeonato "Brasileirao-2025" --excel "participantes.xlsx"
```

**Parâmetros**:
- `--campeonato`: Nome do campeonato (obrigatório)
- `--arquivo`: Arquivo texto com lista de nomes (um por linha)
- `--excel`: Planilha Excel com coluna de nomes
- `--coluna`: Nome da coluna no Excel (padrão: "Nome")

**Saída**:
- Diretório para cada participante em `Participantes/{nome}/`
- Arquivo `palpites.json` vazio para cada participante

### 4. Script de Importação de Tabela (`importar_tabela.py`)

**Responsabilidade**: Importar jogos de arquivo externo para tabela.json.

**Interface CLI**:
```python
python importar_tabela.py --campeonato "Brasileirao-2025" --arquivo "jogos.txt"
python importar_tabela.py --campeonato "Brasileirao-2025" --excel "jogos.xlsx"
```

**Parâmetros**:
- `--campeonato`: Nome do campeonato (obrigatório)
- `--arquivo`: Arquivo texto com jogos
- `--excel`: Planilha Excel com jogos
- `--mesclar`: Flag para mesclar com dados existentes (padrão: sobrescrever)

**Formato Texto Esperado**:
```
Rodada 1
2024-04-13 16:00 | Flamengo x Palmeiras | Maracanã
2024-04-13 18:30 | Corinthians x São Paulo | Neo Química Arena
```

**Formato Excel Esperado**:
Colunas: Rodada, Data, Hora, Mandante, Visitante, Local

**Saída**:
- Arquivo `tabela.json` atualizado com jogos organizados por rodadas

### 5. Script de Importação de Palpites (`importar_palpites.py`)

**Responsabilidade**: Processar texto de palpites e atualizar arquivo do participante.

**Interface CLI**:
```python
python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpite.txt"
python importar_palpites.py --campeonato "Brasileirao-2025" --texto "Mario Silva\n1ª Rodada\nFlamengo 2x1 Palmeiras"
```

**Parâmetros**:
- `--campeonato`: Nome do campeonato (obrigatório)
- `--arquivo`: Arquivo texto com palpite
- `--texto`: Texto direto do palpite
- `--rodada`: Forçar número da rodada (opcional)

**Formato Texto Esperado**:
```
Apostador: Mario Silva
1ª Rodada:
Flamengo 2 x 1 Palmeiras
Corinthians 1 x 2 São Paulo

Aposta Extra:
Jogo 5: Botafogo 2 x 2 Vasco
```

**Saída**:
- Arquivo `palpites.json` do participante atualizado
- Mensagem de confirmação ou sugestão de rodada (se inferida)

### 6. Script de Processamento de Resultados (`processar_resultados.py`)

**Responsabilidade**: Calcular pontuações e gerar classificação da rodada.

**Interface CLI**:
```python
python processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --teste
python processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --final
```

**Parâmetros**:
- `--campeonato`: Nome do campeonato (obrigatório)
- `--rodada`: Número da rodada (obrigatório)
- `--teste`: Modo teste (apenas exibe resultados)
- `--final`: Modo final (atualiza arquivos e gera relatório)

**Saída (Modo Teste)**:
- Classificação exibida no terminal

**Saída (Modo Final)**:
- Backup de `tabela.json` com timestamp
- Campo `rodada_atual` atualizado em `tabela.json`
- Arquivo de relatório em `Resultados/rodada{XX}.txt`

### 7. Módulo de Utilitários (`utils/`)

#### 7.1. Normalização de Times (`normalizacao.py`)

**Funções**:
```python
def normalizar_nome_time(nome: str) -> str:
    """Normaliza nome de time para formato padrão"""
    
def encontrar_time_similar(nome: str, times_validos: List[str]) -> Optional[str]:
    """Encontra time similar usando distância de Levenshtein"""
```

#### 7.2. Validação de Dados (`validacao.py`)

**Funções**:
```python
def validar_estrutura_tabela(dados: dict) -> Tuple[bool, List[str]]:
    """Valida estrutura do arquivo tabela.json"""
    
def validar_estrutura_palpites(dados: dict) -> Tuple[bool, List[str]]:
    """Valida estrutura do arquivo palpites.json"""
    
def validar_placar(mandante: Any, visitante: Any) -> Tuple[bool, str]:
    """Valida que placar contém inteiros não-negativos"""
```

#### 7.3. Parser de Texto (`parser.py`)

**Funções**:
```python
def extrair_apostador(texto: str) -> Optional[str]:
    """Extrai nome do apostador do texto"""
    
def extrair_rodada(texto: str) -> Optional[int]:
    """Extrai número da rodada do texto"""
    
def extrair_palpites(texto: str) -> List[Dict]:
    """Extrai lista de palpites (mandante, visitante, gols)"""
    
def inferir_rodada(palpites: List[Dict], tabela: dict) -> Optional[int]:
    """Infere rodada baseado nos times mencionados"""
```

#### 7.4. Motor de Pontuação (`pontuacao.py`)

**Funções**:
```python
def calcular_pontuacao(palpite: Dict, resultado: Dict, regras: Dict, 
                       total_acertos_exatos: int) -> Tuple[float, str]:
    """Calcula pontuação e retorna (pontos, codigo_regra)"""
    
def verificar_resultado_exato(palpite: Dict, resultado: Dict) -> bool:
    """Verifica se palpite tem placar exato"""
    
def verificar_vitoria_gols_um_time(palpite: Dict, resultado: Dict) -> bool:
    """Verifica se acertou vencedor e gols de uma equipe"""
    
# ... outras funções de verificação para cada regra
```

#### 7.5. Gerador de Relatórios (`relatorio.py`)

**Funções**:
```python
def gerar_tabela_classificacao(resultados: List[Dict], rodada: int) -> str:
    """Gera tabela formatada de classificação"""
    
def calcular_variacao_posicao(participante: str, rodada_atual: int, 
                               historico: Dict) -> int:
    """Calcula variação de posição em relação à rodada anterior"""
```

## Data Models

### Modelo: Campeonato (tabela.json)

```python
{
    "campeonato": str,              # Nome do campeonato
    "temporada": str,               # Ano da temporada
    "rodada_atual": int,            # Última rodada processada
    "data_atualizacao": str,        # ISO 8601 timestamp
    "codigo_campeonato": str,       # Código único (5 dígitos)
    "rodadas": [
        {
            "numero": int,          # Número da rodada
            "data_inicial": str,    # ISO 8601 timestamp
            "data_final": str,      # ISO 8601 timestamp
            "jogos": [
                {
                    "id": str,              # ID único (jogo-XXX)
                    "mandante": str,        # Nome do time mandante
                    "visitante": str,       # Nome do time visitante
                    "data": str,            # ISO 8601 timestamp
                    "local": str,           # Nome do estádio
                    "gols_mandante": int,   # Gols do mandante (≥0)
                    "gols_visitante": int,  # Gols do visitante (≥0)
                    "status": str,          # "agendado" | "finalizado"
                    "obrigatorio": bool     # Se palpite é obrigatório
                }
            ]
        }
    ]
}
```

### Modelo: Palpites (palpites.json)

```python
{
    "apostador": str,               # Nome do participante
    "codigo_apostador": str,        # Código único (4 dígitos)
    "campeonato": str,              # Nome do campeonato
    "temporada": str,               # Ano da temporada
    "palpites": [
        {
            "rodada": int,          # Número da rodada
            "data_palpite": str,    # ISO 8601 timestamp
            "jogos": [
                {
                    "id": str,                  # ID do jogo (referência)
                    "mandante": str,            # Nome do time mandante
                    "visitante": str,           # Nome do time visitante
                    "palpite_mandante": int,    # Palpite gols mandante
                    "palpite_visitante": int    # Palpite gols visitante
                }
            ]
        }
    ]
}
```

### Modelo: Regras (regras.json)

```python
{
    "campeonato": str,              # Nome do campeonato
    "temporada": str,               # Ano da temporada
    "versao": str,                  # Versão das regras (ex: "1.0")
    "data_criacao": str,            # ISO 8601 timestamp
    "regras": {
        "resultado_exato": {
            "pontos_base": int,         # Pontos base (12)
            "bonus_divisor": bool,      # Se aplica bônus divisor
            "descricao": str,           # Descrição da regra
            "codigo": str               # Código da regra (AR)
        },
        "vitoria_gols_um_time": {
            "pontos": int,              # Pontos fixos (7)
            "descricao": str,
            "codigo": str               # VG
        },
        # ... outras regras seguem mesmo padrão
    },
    "observacoes": [str]            # Lista de observações
}
```

### Modelo: Resultado de Rodada (estrutura interna)

```python
{
    "participante": str,            # Nome do participante
    "codigo": str,                  # Código do participante
    "jogos": [
        {
            "id": str,              # ID do jogo
            "pontos": float,        # Pontos obtidos
            "codigo_regra": str     # Código da regra aplicada
        }
    ],
    "total_rodada": float,          # Total de pontos na rodada
    "total_acumulado": float,       # Total acumulado até a rodada
    "posicao": int,                 # Posição na classificação
    "variacao": int,                # Variação de posição (+2, -1, 0)
    "jogos_participados": int       # Total de jogos com palpite
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Championship directory structure completeness

*For any* valid championship name and season, after executing the creation script, the championship directory should contain exactly 4 subdirectories: "Regras", "Tabela", "Resultados", and "Participantes".

**Validates: Requirements 1.1, 1.2**

### Property 2: Initial JSON files validity

*For any* created championship, the initial "regras.json" and "tabela.json" files should be valid JSON with the required top-level fields present.

**Validates: Requirements 1.3**

### Property 3: Championship name normalization consistency

*For any* championship name containing special characters, the normalization function should produce a valid directory name that is consistent across multiple invocations with the same input.

**Validates: Requirements 1.5**

### Property 4: Rules file completeness

*For any* championship, the generated rules file should contain exactly 10 scoring rules, each with the required fields "pontos" (or "pontos_base"), "descricao", and "codigo".

**Validates: Requirements 2.1, 2.3**

### Property 5: Rules file metadata inclusion

*For any* championship name and season provided, the generated rules file should include those exact values in the "campeonato" and "temporada" fields.

**Validates: Requirements 2.2, 2.5**

### Property 6: Participant structure creation

*For any* list of participant names, the number of subdirectories created in "Participantes" should equal the number of unique normalized names in the input list.

**Validates: Requirements 3.1, 3.2**

### Property 7: Participant palpites file structure

*For any* created participant, the "palpites.json" file should be valid JSON containing the required fields "apostador", "codigo_apostador", "campeonato", and an empty "palpites" array.

**Validates: Requirements 3.3, 3.5**

### Property 8: Participant name normalization

*For any* participant name with spaces or special characters, the normalized directory name should contain only alphanumeric characters and be consistent across multiple invocations.

**Validates: Requirements 3.4**

### Property 9: Game data extraction completeness

*For any* valid input file (text or Excel) containing game information, all games should be extracted with the required fields: mandante, visitante, data, and local.

**Validates: Requirements 4.1, 4.2**

### Property 10: Game organization by rounds

*For any* set of games imported, each game should be assigned to exactly one round in the "tabela.json" file, and games should be grouped correctly by their round number.

**Validates: Requirements 4.3**

### Property 11: Game initialization state

*For any* game added to the table, it should have a unique ID, status set to "agendado", and both gols_mandante and gols_visitante initialized to 0.

**Validates: Requirements 4.4**

### Property 12: Team name normalization equivalence

*For any* two team name variations that differ only in slashes vs hyphens, accents, case, or surrounding whitespace, the normalization function should produce identical output.

**Validates: Requirements 4.5, 9.1, 9.2, 9.3, 9.4**

### Property 13: Date format conversion

*For any* valid date in a recognized format, the conversion function should produce a valid ISO 8601 timestamp string.

**Validates: Requirements 4.6**

### Property 14: Participant identification from text

*For any* prediction text containing a registered participant's name, the system should correctly identify and match the participant to their directory.

**Validates: Requirements 5.1**

### Property 15: Round extraction from text

*For any* prediction text containing a round indication (e.g., "1ª Rodada", "Rodada 2"), the system should correctly extract the round number.

**Validates: Requirements 5.2**

### Property 16: Round inference from team names

*For any* prediction text without round indication but containing team names that appear in exactly one round, the system should correctly infer that round number.

**Validates: Requirements 5.3**

### Property 17: Score format recognition

*For any* score written in valid formats ("2x1", "2 x 1", "2-1"), the parser should extract the same numeric values for home and away goals.

**Validates: Requirements 5.5**

### Property 18: Prediction file update

*For any* validated prediction, after processing, the participant's "palpites.json" file should contain an entry for that prediction with correct game ID and score values.

**Validates: Requirements 5.7**

### Property 19: Extra bet identification

*For any* prediction text containing extra bet markers (e.g., "Aposta Extra:", "Jogo X:"), those predictions should be stored with appropriate identification in the palpites file.

**Validates: Requirements 5.9**

### Property 20: Test mode file immutability

*For any* championship and round, after executing result processing in test mode, no JSON files should be modified (file modification timestamps should remain unchanged).

**Validates: Requirements 6.1**

### Property 21: Ranking completeness

*For any* round processed, the generated ranking should include an entry for every registered participant in the championship.

**Validates: Requirements 6.2**

### Property 22: Ranking entry completeness

*For any* participant in a generated ranking, the entry should include match codes, points per game, round total, and accumulated total.

**Validates: Requirements 6.3, 6.4**

### Property 23: Ranking sort order

*For any* generated ranking, participants should be ordered by accumulated total score in descending order (highest score first).

**Validates: Requirements 6.6**

### Property 24: Mandatory games validation

*For any* round, the system should reject processing if any game marked as "obrigatorio: true" has status other than "finalizado".

**Validates: Requirements 6.7**

### Property 25: Backup creation with timestamp

*For any* final mode processing, a backup file should be created with the original filename plus a timestamp in the format "tabela_YYYYMMDD_HHMMSS.json".

**Validates: Requirements 7.1, 7.2**

### Property 26: Current round update

*For any* round processed in final mode, the "rodada_atual" field in "tabela.json" should be updated to that round number.

**Validates: Requirements 7.3**

### Property 27: Report file generation

*For any* round processed in final mode, a report file should be created in the "Resultados" directory with a name containing the round number.

**Validates: Requirements 7.4, 7.6**

### Property 28: Report content completeness

*For any* generated report, it should contain a formatted table with all participants showing their position, variation, match codes, and scores.

**Validates: Requirements 7.5**

### Property 29: Exact score bonus calculation

*For any* game where N participants predicted the exact score, each should receive 12 + (1/N) points for that game.

**Validates: Requirements 8.1, 8.2**

### Property 30: Scoring rule hierarchy

*For any* prediction and result pair, the system should award points according to the highest-value rule that applies, and only that rule.

**Validates: Requirements 8.12**

### Property 31: Winner and one team goals scoring

*For any* prediction that matches the winner and the exact goal count of exactly one team (but not both), the system should award exactly 7 points.

**Validates: Requirements 8.3**

### Property 32: Winner and goal difference scoring

*For any* prediction that matches the winner and the goal difference (but not the exact score), the system should award exactly 6 points.

**Validates: Requirements 8.4**

### Property 33: Winner and total goals scoring

*For any* prediction that matches the winner and the total goals (but not the exact score or goal difference), the system should award exactly 6 points.

**Validates: Requirements 8.5**

### Property 34: Winner only scoring

*For any* prediction that matches only the winner (no other criteria), the system should award exactly 5 points.

**Validates: Requirements 8.6**

### Property 35: Draw only scoring

*For any* prediction that correctly predicts a draw (but not the exact score), the system should award exactly 5 points.

**Validates: Requirements 8.7**

### Property 36: One team goals scoring

*For any* prediction that matches exactly one team's goal count (without matching the result), the system should award exactly 2 points.

**Validates: Requirements 8.8**

### Property 37: Total goals only scoring

*For any* prediction that matches only the total goals (without matching the result or one team's goals), the system should award exactly 1 point.

**Validates: Requirements 8.9**

### Property 38: Inverted score penalty

*For any* prediction where the home and away scores are exactly swapped compared to the result (e.g., prediction "2x1", result "1x2"), the system should award exactly -3 points.

**Validates: Requirements 8.10**

### Property 39: Missing prediction penalty

*For any* mandatory game where a participant has no prediction, the system should award exactly -1 point to that participant for that game.

**Validates: Requirements 8.11**

### Property 40: Required fields validation

*For any* input data structure, the validation function should return false if any required field is missing, and true only if all required fields are present.

**Validates: Requirements 10.1**

### Property 41: Date format validation

*For any* date string input, the validation function should return true only if the string represents a valid date in a recognized format.

**Validates: Requirements 10.2**

### Property 42: Score validation

*For any* score input, the validation function should return true only if both home and away values are non-negative integers.

**Validates: Requirements 10.3**

### Property 43: Game ID reference validation

*For any* game ID referenced in a prediction, the validation function should return true only if that ID exists in the championship's table.

**Validates: Requirements 10.4**

### Property 44: Participant registration validation

*For any* participant name referenced, the validation function should return true only if that participant has a directory in the championship's "Participantes" folder.

**Validates: Requirements 10.5**

### Property 45: Error message clarity

*For any* validation failure, the error message should contain specific information about which field or value caused the failure.

**Validates: Requirements 10.6**

## Error Handling

### Validation Errors

Todas as funções de validação devem retornar tuplas `(bool, List[str])` onde o booleano indica sucesso/falha e a lista contém mensagens de erro específicas.

**Estratégia**:
- Validar todos os dados antes de qualquer modificação de arquivo
- Acumular todas as mensagens de erro antes de exibir ao usuário
- Fornecer mensagens em português com contexto específico
- Incluir sugestões de correção quando possível

**Exemplos de Mensagens**:
```python
"Campo obrigatório 'mandante' ausente no jogo ID 'jogo-001'"
"Data inválida: '2024-13-45' não é uma data válida"
"Time 'Atletico MG' não encontrado. Você quis dizer 'Atlético-MG'?"
"Participante 'João Silva' não está registrado neste campeonato"
```

### File Operation Errors

**Estratégia**:
- Usar blocos try-except para operações de I/O
- Verificar permissões antes de operações de escrita
- Criar diretórios pais automaticamente quando necessário
- Fornecer mensagens claras sobre problemas de acesso

**Tratamento**:
```python
try:
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
except PermissionError:
    print(f"Erro: Sem permissão para escrever em {filepath}")
except IOError as e:
    print(f"Erro ao escrever arquivo: {e}")
```

### Parsing Errors

**Estratégia**:
- Tentar múltiplos formatos antes de falhar
- Fornecer feedback sobre qual parte do texto causou problema
- Sugerir correções quando padrões são quase reconhecidos
- Permitir que administrador force valores quando inferência falha

**Exemplo**:
```python
"Não foi possível extrair placar de 'Flamengo dois x um Palmeiras'"
"Sugestão: Use formato numérico como 'Flamengo 2 x 1 Palmeiras'"
```

### Data Consistency Errors

**Estratégia**:
- Verificar consistência entre arquivos relacionados
- Detectar IDs duplicados
- Validar referências entre arquivos (ex: ID de jogo em palpite existe na tabela)
- Oferecer opção de corrigir automaticamente quando possível

### Confirmation Prompts

Para operações críticas, usar prompts claros:

```python
def confirmar_operacao(mensagem: str) -> bool:
    """Solicita confirmação do usuário"""
    resposta = input(f"{mensagem} (s/n): ").strip().lower()
    return resposta in ['s', 'sim', 'y', 'yes']
```

**Operações que requerem confirmação**:
- Sobrescrever arquivos existentes
- Processar rodada em modo final
- Atualizar palpites já registrados
- Mesclar dados com tabela existente

## Testing Strategy

### Unit Testing

Utilizaremos `pytest` como framework de testes unitários para Python.

**Áreas de Cobertura**:

1. **Funções de Normalização**:
   - Testar casos específicos de normalização de nomes
   - Verificar remoção de acentos, conversão de caracteres especiais
   - Testar casos extremos (strings vazias, apenas espaços, caracteres unicode)

2. **Funções de Validação**:
   - Testar validação de estruturas JSON com dados válidos e inválidos
   - Verificar detecção de campos faltantes
   - Testar validação de tipos de dados

3. **Funções de Parsing**:
   - Testar extração de apostador, rodada e palpites
   - Verificar reconhecimento de diferentes formatos de placar
   - Testar casos com formatação irregular

4. **Funções de Pontuação**:
   - Testar cada regra de pontuação individualmente
   - Verificar cálculo de bônus para resultado exato
   - Testar casos onde múltiplas regras poderiam aplicar

5. **Funções de Geração de Relatórios**:
   - Testar formatação de tabelas
   - Verificar cálculo de variação de posição
   - Testar ordenação de classificação

**Exemplo de Teste Unitário**:
```python
def test_normalizar_nome_time():
    assert normalizar_nome_time("Atlético/MG") == "atletico-mg"
    assert normalizar_nome_time("São Paulo") == "sao-paulo"
    assert normalizar_nome_time("  Flamengo  ") == "flamengo"
    assert normalizar_nome_time("Atlético-MG") == "atletico-mg"
```

### Property-Based Testing

Utilizaremos `hypothesis` como biblioteca de property-based testing para Python.

**Configuração**:
- Mínimo de 100 iterações por propriedade
- Cada teste deve referenciar explicitamente a propriedade do design document

**Estratégia de Generators**:

1. **Generator de Nomes de Times**:
```python
from hypothesis import strategies as st

@st.composite
def team_name(draw):
    """Gera nomes de times com variações realistas"""
    base_names = ["Flamengo", "Palmeiras", "São Paulo", "Atlético"]
    suffixes = ["", "/MG", "-MG", " MG", "/SP"]
    name = draw(st.sampled_from(base_names))
    suffix = draw(st.sampled_from(suffixes))
    return name + suffix
```

2. **Generator de Placares**:
```python
@st.composite
def score(draw):
    """Gera placares válidos (0-10 gols)"""
    home = draw(st.integers(min_value=0, max_value=10))
    away = draw(st.integers(min_value=0, max_value=10))
    return (home, away)
```

3. **Generator de Palpites e Resultados**:
```python
@st.composite
def prediction_and_result(draw):
    """Gera par de palpite e resultado para testar pontuação"""
    pred_home = draw(st.integers(min_value=0, max_value=5))
    pred_away = draw(st.integers(min_value=0, max_value=5))
    res_home = draw(st.integers(min_value=0, max_value=5))
    res_away = draw(st.integers(min_value=0, max_value=5))
    return {
        "palpite": {"mandante": pred_home, "visitante": pred_away},
        "resultado": {"mandante": res_home, "visitante": res_away}
    }
```

**Exemplo de Property Test**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@given(team_name(), team_name())
@settings(max_examples=100)
def test_property_12_team_normalization_equivalence(name1, name2):
    """
    Feature: bolao-prototype-scripts, Property 12: Team name normalization equivalence
    
    For any two team name variations that differ only in slashes vs hyphens,
    accents, case, or surrounding whitespace, the normalization function
    should produce identical output.
    """
    # Normalize both names
    norm1 = normalizar_nome_time(name1)
    norm2 = normalizar_nome_time(name2)
    
    # If names are equivalent (same base), normalization should match
    base1 = name1.strip().lower().replace("/", "-").replace("ã", "a").replace("é", "e")
    base2 = name2.strip().lower().replace("/", "-").replace("ã", "a").replace("é", "e")
    
    if base1 == base2:
        assert norm1 == norm2
```

**Propriedades Prioritárias para PBT**:

As seguintes propriedades são críticas e devem ter testes property-based:

- **Property 12**: Normalização de nomes de times (equivalência)
- **Property 29**: Cálculo de bônus de resultado exato
- **Property 30**: Hierarquia de regras de pontuação (apenas maior valor)
- **Property 31-39**: Todas as regras de pontuação individuais
- **Property 40-44**: Validações de dados

**Anotação de Testes**:

Cada teste property-based DEVE incluir um comentário no formato:
```python
"""
Feature: bolao-prototype-scripts, Property {N}: {Nome da Propriedade}

{Descrição da propriedade}
"""
```

### Integration Testing

Testes de integração verificarão fluxos completos:

1. **Fluxo de Criação de Campeonato**:
   - Criar campeonato → Gerar regras → Criar participantes → Verificar estrutura completa

2. **Fluxo de Importação**:
   - Importar tabela → Importar palpites → Verificar consistência de IDs

3. **Fluxo de Processamento**:
   - Processar em modo teste → Verificar sem modificações → Processar em modo final → Verificar backup e relatório

**Exemplo**:
```python
def test_integration_championship_creation_flow(tmp_path):
    """Testa fluxo completo de criação de campeonato"""
    # Setup
    base_dir = tmp_path / "Campeonatos"
    
    # Criar campeonato
    criar_campeonato("Teste-2025", "2025", base_dir)
    
    # Verificar estrutura
    assert (base_dir / "Teste-2025" / "Regras").exists()
    assert (base_dir / "Teste-2025" / "Tabela").exists()
    assert (base_dir / "Teste-2025" / "Resultados").exists()
    assert (base_dir / "Teste-2025" / "Participantes").exists()
    
    # Gerar regras
    gerar_regras("Teste-2025", base_dir)
    
    # Verificar arquivo de regras
    regras_path = base_dir / "Teste-2025" / "Regras" / "regras.json"
    assert regras_path.exists()
    
    with open(regras_path) as f:
        regras = json.load(f)
    
    assert len(regras["regras"]) == 10
    assert regras["campeonato"] == "Teste-2025"
```

### Test Data

Utilizaremos os dados em `Campeonatos/Exemplo01/` como fixtures para testes:

- Copiar estrutura para diretório temporário em cada teste
- Usar dados reais para validar parsing e cálculos
- Criar variações dos dados para testar casos extremos

### Continuous Validation

Durante desenvolvimento, executar:

```bash
# Testes unitários
pytest tests/unit/ -v

# Testes property-based (pode demorar mais)
pytest tests/properties/ -v --hypothesis-show-statistics

# Testes de integração
pytest tests/integration/ -v

# Cobertura
pytest --cov=src --cov-report=html
```

## Implementation Notes

### Python Version

- **Versão Mínima**: Python 3.8
- **Versão Recomendada**: Python 3.10+

### Dependencies

```
# requirements.txt
hypothesis>=6.0.0      # Property-based testing
pytest>=7.0.0          # Unit testing framework
openpyxl>=3.0.0        # Excel file handling
python-dateutil>=2.8.0 # Date parsing
python-Levenshtein>=0.12.0  # String similarity
```

### Code Organization

```
bolao-prototype/
├── src/
│   ├── scripts/
│   │   ├── criar_campeonato.py
│   │   ├── gerar_regras.py
│   │   ├── criar_participantes.py
│   │   ├── importar_tabela.py
│   │   ├── importar_palpites.py
│   │   └── processar_resultados.py
│   └── utils/
│       ├── normalizacao.py
│       ├── validacao.py
│       ├── parser.py
│       ├── pontuacao.py
│       └── relatorio.py
├── tests/
│   ├── unit/
│   ├── properties/
│   └── integration/
├── Campeonatos/
│   └── Exemplo01/
├── requirements.txt
└── README.md
```

### CLI Design Principles

1. **Argumentos Nomeados**: Usar sempre `--argumento valor` para clareza
2. **Help Text**: Cada script deve ter `--help` com descrição completa
3. **Feedback Visual**: Usar mensagens claras de progresso e sucesso
4. **Cores (Opcional)**: Considerar usar `colorama` para output colorido
5. **Dry-Run**: Scripts destrutivos devem suportar modo `--dry-run`

### Performance Considerations

Para a fase de protótipo, performance não é crítica, mas algumas considerações:

- **Caching**: Carregar arquivos JSON uma vez e reutilizar em memória
- **Lazy Loading**: Carregar apenas dados necessários para operação
- **Batch Operations**: Processar múltiplos palpites de uma vez quando possível

### Future Extensibility

O design deve facilitar futuras expansões:

1. **API REST**: Funções de utils podem ser reutilizadas em API
2. **Web Interface**: Lógica de negócio separada de CLI
3. **Database Migration**: Modelos de dados já estruturados para ORM
4. **Multi-Sport**: Normalização e pontuação podem ser generalizadas

### Logging

Implementar logging básico para debugging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bolao.log'),
        logging.StreamHandler()
    ]
)
```

### Configuration

Considerar arquivo de configuração para valores padrão:

```json
{
  "base_directory": "Campeonatos",
  "date_formats": [
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%dT%H:%M:%SZ"
  ],
  "score_formats": ["x", " x ", "-", " - "],
  "backup_format": "_%Y%m%d_%H%M%S"
}
```
