# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Product Overview

Sistema de Controle de Bolão - A sports betting management system for closed groups of pre-registered participants.

## Core Purpose

Manages football match predictions (palpites) for multiple championships, processes WhatsApp text messages into structured data, calculates scores based on configurable rules, and maintains real-time rankings.

## Key Features

- Multi-championship support with independent scoring and participants
- Automatic text-to-JSON conversion of WhatsApp predictions
- Flexible scoring system with 10 different accuracy levels (from exact result to penalties)
- Automated ranking generation with detailed round reports
- Hierarchical data organization by championship/participant

## Target Users

Administrators managing closed betting groups who need to:
- Process unstructured prediction messages
- Calculate complex scoring rules automatically
- Generate rankings and reports per round
- Maintain historical data across multiple championships

## Language

All documentation, data structures, and user-facing content are in Portuguese (Brazilian).

# Project Structure

## Directory Organization

The system follows a strict hierarchical structure for data organization:

```
Campeonatos/
├── {NomeDoCampeonato}/
│   ├── Regras/
│   │   └── regras.json
│   ├── Tabela/
│   │   └── tabela.json
│   ├── Resultados/
│   │   ├── rodada01.json (future use)
│   │   └── ...
│   └── Participantes/
│       ├── {NomeParticipante}/
│       │   └── palpites.json
│       └── formulario_palpites.md
```

## Key Directories

### `/Campeonatos`
Root directory for all championships. Each championship is completely independent.

### `/Campeonatos/{NomeDoCampeonato}/Regras`
Contains `regras.json` - scoring rules configuration for the championship.

### `/Campeonatos/{NomeDoCampeonato}/Tabela`
Contains `tabela.json` - complete match schedule organized by rounds (rodadas).
Results are updated directly in this file by changing match status to "finalizado" and updating goal counts.

### `/Campeonatos/{NomeDoCampeonato}/Participantes`
One subdirectory per participant, named after the participant.
Each contains `palpites.json` with all predictions for that participant.

### `/Campeonatos/{NomeDoCampeonato}/Resultados`
Reserved for future use - currently results are stored in `tabela.json`.

## File Naming Conventions

- Championship directories: Use descriptive names like `Brasileirao-2025` or `CampeonatoPaulista-2025`
- Participant directories: Use participant's name without spaces or special characters (e.g., `MarioSilva`)
- All JSON files use lowercase with underscores if needed
- Round files (future): `rodada01.json`, `rodada02.json`, etc.

## Data File Standards

### Required Fields in tabela.json
- `campeonato`, `temporada`, `rodada_atual`, `codigo_campeonato`
- Each match must have: `id`, `mandante`, `visitante`, `data`, `local`, `gols_mandante`, `gols_visitante`, `status`, `obrigatorio`

### Required Fields in palpites.json
- `apostador`, `codigo_apostador`, `campeonato`, `temporada`
- Each prediction must reference match by `id` and include `palpite_mandante`, `palpite_visitante`

### Required Fields in regras.json
- `campeonato`, `temporada`, `versao`
- Each rule must have: `pontos` (or `pontos_base`), `descricao`, `codigo`

## Archive Directory

`/archive` - Contains old documentation versions. Not part of active system.

# Technology Stack

## Current Phase: Prototype

The system is in prototype phase with local Python scripts run by administrators.

## Tech Stack

- **Language**: Python (local scripts)
- **Data Format**: JSON for all structured data
- **Input Sources**: Text files, Excel spreadsheets, WhatsApp messages
- **Deployment**: Local execution on administrator's computer

## Data Formats

All data is stored in JSON format:
- `tabela.json` - Match schedules and results
- `regras.json` - Scoring rules configuration
- `palpites.json` - Individual participant predictions
- No database - file-based storage

## Common Operations

Since this is a prototype phase, there are no build/test commands yet. The system consists of Python scripts for:

- Creating new championship structure
- Generating rules files from standard template
- Creating participant data structures from lists
- Importing match schedules from text/Excel
- Parsing predictions from text format
- Processing round results (test mode and final mode with backup)

## Development Guidelines

### Data Validation
- Always validate input data before processing
- Handle errors and edge cases gracefully
- Support multiple text input formats

### Team Name Normalization
- Normalize team names (e.g., "Atlético/MG" = "Atlético-MG" = "Atletico MG")
- Maintain consistent naming across all data files

### Backup Strategy
- Create backup copies before modifying data files
- Implement test mode for result processing before final updates

### Date/Time Format
- Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
- All timestamps in UTC

## Future Considerations

- API integration with WhatsApp
- Web interface for visualization
- Database migration for scalability
- Support for other sports beyond football


## Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# All tests
python -m pytest tests/ -v

# Single test file
python -m pytest tests/test_normalizacao.py -v

# Property-based tests only
python -m pytest tests/test_*_properties.py -v
```

### Main Scripts
All scripts are run from the project root:

```bash
# Create championship structure
python src/scripts/criar_campeonato.py --nome "Brasileirao-2025" --temporada 2025 --codigo "BR25"

# Generate scoring rules
python src/scripts/gerar_regras.py --campeonato "Brasileirao-2025"

# Create participants
python src/scripts/criar_participantes.py --campeonato "Brasileirao-2025" --arquivo participantes.txt

# Import match schedule
python src/scripts/importar_tabela.py --campeonato "Brasileirao-2025" --arquivo tabela_jogos.txt

# Import predictions (supports single or multiple rounds in one file)
python src/scripts/importar_palpites.py --campeonato "Brasileirao-2025" --arquivo palpites.txt

# Process results (test mode first, then final)
python src/scripts/processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --teste
python src/scripts/processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --final
```

## Architecture

### Data Flow
1. **Input**: WhatsApp text messages, TXT files, or Excel spreadsheets
2. **Parsing** (`src/utils/parser.py`): Extracts bettor name, round number, and predictions from unstructured text
3. **Normalization** (`src/utils/normalizacao.py`): Standardizes team names (handles accents, separators, case)
4. **Scoring** (`src/utils/pontuacao.py`): Applies hierarchical scoring rules
5. **Output**: JSON files and TXT reports

### Directory Structure Convention
```
Campeonatos/
└── {ChampionshipName}/
    ├── Regras/regras.json       # Scoring rules
    ├── Tabela/tabela.json       # Match schedule + results
    ├── Resultados/              # Generated round reports
    └── Participantes/
        └── {ParticipantName}/palpites.json
```

### Key Modules
- `src/config.py`: Default scoring rules, file paths, parsing patterns
- `src/utils/parser.py`: Text parsing with regex patterns for multiple score formats (`2x1`, `2-1`, `2:1`)
- `src/utils/pontuacao.py`: Scoring engine with 10 hierarchical rules (exact result → penalty)
- `src/utils/validacao.py`: JSON structure and data validation
- `src/utils/relatorio.py`: Report generation

### Scoring Hierarchy (highest to lowest)
1. **AR** (12 pts + bonus): Exact result
2. **VG** (7 pts): Winner + goals of one team
3. **VD** (6 pts): Winner + goal difference
4. **VS** (6 pts): Winner + total goals
5. **V/E** (5 pts): Winner only / Draw only
6. **G** (2 pts): Goals of one team (wrong result)
7. **S** (1 pt): Total goals only
8. **RI** (-3 pts): Inverted result (penalty)
9. **PA** (-1 pt): Missing prediction (mandatory match)

## Language

All user-facing content, documentation, and data structures are in Brazilian Portuguese.
