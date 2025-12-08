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
