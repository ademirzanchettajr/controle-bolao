#!/bin/bash
# Setup script for Sistema de Controle de Bolão
# Run with: source setup_env.sh

echo "🏆 Configurando ambiente do Sistema de Controle de Bolão..."

# Create aliases for convenience
alias python='python3'
alias pip='pip3'

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Test the environment
echo "✅ Python version: $(python3 --version)"
echo "✅ Pip version: $(pip3 --version | cut -d' ' -f1-2)"

# Test if all dependencies are available
echo "🧪 Testando dependências..."

python3 -c "
import sys
dependencies = ['hypothesis', 'pytest', 'openpyxl', 'dateutil', 'Levenshtein']
missing = []

for dep in dependencies:
    try:
        if dep == 'dateutil':
            import dateutil
        else:
            __import__(dep)
        print(f'✅ {dep}')
    except ImportError:
        print(f'❌ {dep}')
        missing.append(dep)

if missing:
    print(f'\\n⚠️  Dependências faltando: {missing}')
    print('Execute: pip3 install -r requirements.txt')
    sys.exit(1)
else:
    print('\\n🎉 Todas as dependências estão instaladas!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 Ambiente configurado com sucesso!"
    echo ""
    echo "📋 Comandos disponíveis:"
    echo "  python3 src/scripts/criar_campeonato.py --help"
    echo "  python3 src/scripts/gerar_regras.py --help"
    echo "  python3 src/scripts/criar_participantes.py --help"
    echo "  python3 src/scripts/importar_tabela.py --help"
    echo "  python3 src/scripts/importar_palpites.py --help"
    echo "  python3 src/scripts/processar_resultados.py --help"
    echo ""
    echo "📚 Exemplos de uso:"
    echo "  cd examples/scripts_exemplo"
    echo "  python3 01_setup_completo.py"
    echo ""
    echo "🧪 Executar testes:"
    echo "  python3 -m pytest tests/ -v"
else
    echo "❌ Erro na configuração do ambiente"
fi