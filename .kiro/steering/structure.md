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

## Configuration Directory

`.kiro/` - IDE configuration and steering rules (this directory).
