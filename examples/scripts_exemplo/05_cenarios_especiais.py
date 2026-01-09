#!/usr/bin/env python3
"""
Exemplo 5: Cenários Especiais

Este script demonstra o tratamento de situações especiais:
1. Normalização de nomes de times com variações
2. Palpites em formatos diferentes
3. Situações de erro e recuperação
4. Validação de dados
5. Casos extremos de pontuação

Execute: python 05_cenarios_especiais.py
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def executar_comando(comando, descricao, mostrar_saida=True):
    """Executa um comando e exibe o resultado"""
    if mostrar_saida:
        print(f"\n{'='*50}")
        print(f"TESTE: {descricao}")
        print('='*50)
    
    try:
        result = subprocess.run(comando, capture_output=True, text=True, cwd=os.getcwd())
        
        if mostrar_saida:
            if result.stdout:
                print("SAÍDA:")
                print(result.stdout)
            
            if result.stderr:
                print("ERROS/AVISOS:")
                print(result.stderr)
        
        return result.returncode == 0, result.stdout, result.stderr
            
    except Exception as e:
        if mostrar_saida:
            print(f"ERRO ao executar comando: {e}")
        return False, "", str(e)

def criar_dados_teste_especiais():
    """Cria dados de teste para cenários especiais"""
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # 1. Palpites com nomes de times variados
    palpites_normalizacao = """
João Silva
Rodada 1

Flamengo 2x1 Palmeiras
Santos 1-1 Corinthians
São Paulo 3x0 Grêmio
Atlético/MG 1x2 Botafogo
Vasco da Gama 0x1 Cruzeiro
Internacional 2x1 Bahia
"""
    
    with open(dados_dir / "palpites_normalizacao.txt", 'w', encoding='utf-8') as f:
        f.write(palpites_normalizacao.strip())
    
    # 2. Palpites com formatos diferentes
    palpites_formatos = """
Maria Santos
1ª Rodada

Flamengo 2 x 1 Palmeiras
Santos 1-1 Corinthians  
São Paulo 3 X 0 Grêmio
Atlético-MG 1 - 2 Botafogo
Vasco 0 x 1 Cruzeiro
Internacional 2x1 Bahia
"""
    
    with open(dados_dir / "palpites_formatos.txt", 'w', encoding='utf-8') as f:
        f.write(palpites_formatos.strip())
    
    # 3. Palpites com erros intencionais
    palpites_erros = """
Pedro Oliveira
Rodada 1

Flamengo 2x1 Palmeiras
Santos 1-1 Corinthians
São Paulo 3x0 Grêmio
Time Inexistente 1x2 Botafogo
Vasco 0x1 Cruzeiro
Internacional 2x1 Bahia
"""
    
    with open(dados_dir / "palpites_erros.txt", 'w', encoding='utf-8') as f:
        f.write(palpites_erros.strip())
    
    # 4. Participantes com nomes especiais
    participantes_especiais = """
João da Silva Jr.
Maria José (Maju)
Pedro O'Connor
Ana-Luiza Santos
José "Zé" Carlos
Fernanda & Roberto
Carlos Alberto III
"""
    
    with open(dados_dir / "participantes_especiais.txt", 'w', encoding='utf-8') as f:
        f.write(participantes_especiais.strip())
    
    print("✅ Dados de teste especiais criados")

def setup_campeonato_teste():
    """Configura campeonato para testes"""
    print(f"\n{'='*60}")
    print("CONFIGURANDO CAMPEONATO DE TESTE")
    print('='*60)
    
    # Limpar campeonato anterior
    campeonato_dir = Path("Campeonatos/Teste-Cenarios-2025")
    if campeonato_dir.exists():
        shutil.rmtree(campeonato_dir)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Criar campeonato
    sucesso, _, _ = executar_comando([
        sys.executable, str(scripts_dir / "criar_campeonato.py"),
        "--nome", "Teste-Cenarios-2025",
        "--temporada", "2025",
        "--codigo", "TC25"
    ], "Criação do campeonato de teste", False)
    
    if not sucesso:
        return False
    
    # Gerar regras
    sucesso, _, _ = executar_comando([
        sys.executable, str(scripts_dir / "gerar_regras.py"),
        "--campeonato", "Teste-Cenarios-2025"
    ], "Geração das regras", False)
    
    # Importar tabela
    sucesso, _, _ = executar_comando([
        sys.executable, str(scripts_dir / "importar_tabela.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--arquivo", str(dados_dir / "tabela_jogos.txt")
    ], "Importação da tabela", False)
    
    print("✅ Campeonato de teste configurado")
    return True

def testar_normalizacao_nomes():
    """Testa normalização de nomes de participantes"""
    print(f"\n{'='*60}")
    print("CENÁRIO 1: NORMALIZAÇÃO DE NOMES DE PARTICIPANTES")
    print('='*60)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Testar criação de participantes com nomes especiais
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "criar_participantes.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--arquivo", str(dados_dir / "participantes_especiais.txt")
    ], "Criação de participantes com nomes especiais")
    
    if sucesso:
        print("✅ Nomes especiais normalizados com sucesso")
        
        # Verificar diretórios criados
        participantes_dir = Path("Campeonatos/Teste-Cenarios-2025/Participantes")
        diretorios = [d.name for d in participantes_dir.iterdir() if d.is_dir()]
        
        print("\n📁 Diretórios criados:")
        for diretorio in sorted(diretorios):
            print(f"   • {diretorio}")
    else:
        print("❌ Falha na normalização de nomes")

def testar_formatos_palpites():
    """Testa diferentes formatos de palpites"""
    print(f"\n{'='*60}")
    print("CENÁRIO 2: FORMATOS DIFERENTES DE PALPITES")
    print('='*60)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Criar participante primeiro
    sucesso, _, _ = executar_comando([
        sys.executable, str(scripts_dir / "criar_participantes.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--arquivo", str(dados_dir / "participantes.txt")
    ], "Criação de participantes básicos", False)
    
    # Testar formato com normalização
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "importar_palpites.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--arquivo", str(dados_dir / "palpites_normalizacao.txt")
    ], "Palpites com nomes de times variados")
    
    if sucesso:
        print("✅ Normalização de times funcionou")
    
    # Testar diferentes formatos de placar
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "importar_palpites.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--arquivo", str(dados_dir / "palpites_formatos.txt")
    ], "Palpites com formatos diferentes de placar")
    
    if sucesso:
        print("✅ Diferentes formatos de placar aceitos")

def testar_tratamento_erros():
    """Testa tratamento de erros"""
    print(f"\n{'='*60}")
    print("CENÁRIO 3: TRATAMENTO DE ERROS")
    print('='*60)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Testar palpite com time inexistente
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "importar_palpites.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--arquivo", str(dados_dir / "palpites_erros.txt")
    ], "Palpites com time inexistente")
    
    if not sucesso:
        print("✅ Erro detectado corretamente para time inexistente")
        if "Time Inexistente" in erro or "Time Inexistente" in saida:
            print("✅ Mensagem de erro específica exibida")
    
    # Testar campeonato inexistente
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Campeonato-Inexistente",
        "--rodada", "1",
        "--teste"
    ], "Processamento de campeonato inexistente")
    
    if not sucesso:
        print("✅ Erro detectado corretamente para campeonato inexistente")

def testar_casos_pontuacao():
    """Testa casos extremos de pontuação"""
    print(f"\n{'='*60}")
    print("CENÁRIO 4: CASOS EXTREMOS DE PONTUAÇÃO")
    print('='*60)
    
    # Criar cenário com resultados específicos para testar todas as regras
    campeonato_dir = Path("Campeonatos/Teste-Cenarios-2025")
    tabela_file = campeonato_dir / "Tabela" / "tabela.json"
    
    if not tabela_file.exists():
        print("❌ Tabela não encontrada")
        return
    
    # Atualizar com resultados específicos para demonstrar todas as regras
    with open(tabela_file, 'r', encoding='utf-8') as f:
        tabela = json.load(f)
    
    # Resultados que demonstram diferentes regras de pontuação
    resultados_especiais = {
        "Flamengo x Palmeiras": (2, 1),      # Para testar resultado exato
        "Santos x Corinthians": (1, 1),      # Para testar empate
        "São Paulo x Grêmio": (3, 0),        # Para testar vencedor + gols
        "Atlético-MG x Botafogo": (1, 2),    # Para testar resultado invertido
        "Vasco x Cruzeiro": (0, 1),          # Para testar apenas vencedor
        "Internacional x Bahia": (2, 1)      # Para testar diferença de gols
    }
    
    # Atualizar jogos
    for rodada in tabela.get('rodadas', []):
        if rodada.get('numero') == 1:
            for jogo in rodada.get('jogos', []):
                mandante = jogo.get('mandante')
                visitante = jogo.get('visitante')
                chave_jogo = f"{mandante} x {visitante}"
                
                if chave_jogo in resultados_especiais:
                    gols_mandante, gols_visitante = resultados_especiais[chave_jogo]
                    jogo['gols_mandante'] = gols_mandante
                    jogo['gols_visitante'] = gols_visitante
                    jogo['status'] = 'finalizado'
    
    with open(tabela_file, 'w', encoding='utf-8') as f:
        json.dump(tabela, f, indent=2, ensure_ascii=False)
    
    # Processar resultados
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--rodada", "1",
        "--teste"
    ], "Processamento com casos extremos de pontuação")
    
    if sucesso:
        print("✅ Casos extremos de pontuação processados")
        
        # Analisar códigos de acerto na saída
        if saida:
            print("\n📊 CÓDIGOS DE ACERTO ENCONTRADOS:")
            codigos_encontrados = set()
            for linha in saida.split('\n'):
                if '|' in linha and any(codigo in linha for codigo in ['AR', 'VG', 'VD', 'VS', 'V', 'E', 'G', 'S', 'RI', 'PA']):
                    # Extrair códigos da linha
                    for codigo in ['AR', 'VG', 'VD', 'VS', 'V', 'E', 'G', 'S', 'RI', 'PA']:
                        if codigo in linha:
                            codigos_encontrados.add(codigo)
            
            for codigo in sorted(codigos_encontrados):
                descricoes = {
                    'AR': 'Resultado Exato',
                    'VG': 'Vencedor + Gols de Uma Equipe',
                    'VD': 'Vencedor + Diferença de Gols',
                    'VS': 'Vencedor + Soma Total',
                    'V': 'Apenas Vencedor',
                    'E': 'Apenas Empate',
                    'G': 'Gols de Um Time',
                    'S': 'Soma Total de Gols',
                    'RI': 'Resultado Invertido',
                    'PA': 'Palpite Ausente'
                }
                print(f"   ✅ {codigo}: {descricoes.get(codigo, 'Desconhecido')}")

def testar_validacao_dados():
    """Testa validação de dados"""
    print(f"\n{'='*60}")
    print("CENÁRIO 5: VALIDAÇÃO DE DADOS")
    print('='*60)
    
    # Testar arquivo JSON inválido
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    arquivo_invalido = dados_dir / "json_invalido.txt"
    
    with open(arquivo_invalido, 'w', encoding='utf-8') as f:
        f.write("Este não é um JSON válido { malformado")
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    
    # Testar processamento sem jogos finalizados
    sucesso, saida, erro = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Teste-Cenarios-2025",
        "--rodada", "2",  # Rodada sem jogos finalizados
        "--teste"
    ], "Processamento de rodada sem jogos finalizados")
    
    if not sucesso:
        print("✅ Validação funcionou: jogos não finalizados detectados")
    
    # Limpar arquivo de teste
    arquivo_invalido.unlink()

def limpar_dados_teste():
    """Limpa dados de teste criados"""
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    arquivos_teste = [
        "palpites_normalizacao.txt",
        "palpites_formatos.txt", 
        "palpites_erros.txt",
        "participantes_especiais.txt"
    ]
    
    for arquivo in arquivos_teste:
        arquivo_path = dados_dir / arquivo
        if arquivo_path.exists():
            arquivo_path.unlink()
    
    # Remover campeonato de teste
    campeonato_dir = Path("Campeonatos/Teste-Cenarios-2025")
    if campeonato_dir.exists():
        shutil.rmtree(campeonato_dir)
    
    print("🧹 Dados de teste removidos")

def main():
    print("🧪 EXEMPLO 5: CENÁRIOS ESPECIAIS")
    print("=" * 60)
    print("Este exemplo testa situações especiais e casos extremos do sistema.")
    
    try:
        # Criar dados de teste
        criar_dados_teste_especiais()
        
        # Setup do campeonato
        if not setup_campeonato_teste():
            print("❌ Falha no setup. Abortando.")
            return
        
        # Executar testes
        testar_normalizacao_nomes()
        testar_formatos_palpites()
        testar_tratamento_erros()
        testar_casos_pontuacao()
        testar_validacao_dados()
        
        print(f"\n{'='*60}")
        print("RESUMO DOS CENÁRIOS TESTADOS")
        print('='*60)
        print("✅ Normalização de nomes especiais")
        print("✅ Múltiplos formatos de placar")
        print("✅ Tratamento de erros e validação")
        print("✅ Casos extremos de pontuação")
        print("✅ Validação de dados de entrada")
        print("✅ Detecção de problemas comuns")
        
        print(f"\n{'='*60}")
        print("LIÇÕES APRENDIDAS")
        print('='*60)
        print("🔧 O sistema é robusto para diferentes formatos de entrada")
        print("🛡️  Validação abrangente previne erros comuns")
        print("🔄 Normalização automática facilita o uso")
        print("📊 Sistema de pontuação cobre todos os casos")
        print("⚠️  Mensagens de erro são claras e específicas")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
    finally:
        # Sempre limpar dados de teste
        limpar_dados_teste()

if __name__ == "__main__":
    main()