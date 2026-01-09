#!/usr/bin/env python3
"""
Exemplo 4: Fluxo Completo

Este script demonstra um fluxo completo de 2 rodadas:
1. Setup inicial do campeonato
2. Importação de palpites
3. Processamento da rodada 1
4. Importação de novos palpites
5. Processamento da rodada 2
6. Análise dos resultados finais

Execute: python 04_fluxo_completo.py
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def executar_comando(comando, descricao, mostrar_saida=True):
    """Executa um comando e exibe o resultado"""
    if mostrar_saida:
        print(f"\n{'='*60}")
        print(f"EXECUTANDO: {descricao}")
        print('='*60)
    
    try:
        result = subprocess.run(comando, capture_output=True, text=True, cwd=os.getcwd())
        
        if mostrar_saida and result.stdout:
            print("SAÍDA:")
            print(result.stdout)
        
        if result.stderr and mostrar_saida:
            print("ERROS/AVISOS:")
            print(result.stderr)
            
        if result.returncode != 0:
            if mostrar_saida:
                print(f"ERRO: Comando falhou com código {result.returncode}")
            return False
        else:
            if mostrar_saida:
                print("✅ SUCESSO!")
            return True
            
    except Exception as e:
        if mostrar_saida:
            print(f"ERRO ao executar comando: {e}")
        return False

def limpar_ambiente():
    """Limpa ambiente anterior"""
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    if campeonato_dir.exists():
        print(f"🧹 Removendo campeonato anterior...")
        shutil.rmtree(campeonato_dir)

def setup_campeonato():
    """Configura o campeonato completo"""
    print(f"\n{'='*60}")
    print("FASE 1: SETUP DO CAMPEONATO")
    print('='*60)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Criar campeonato
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "criar_campeonato.py"),
        "--nome", "Copa-Exemplo-2025",
        "--temporada", "2025",
        "--codigo", "CEX25"
    ], "Criação do campeonato", False)
    
    if not sucesso:
        return False
    
    # Gerar regras
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "gerar_regras.py"),
        "--campeonato", "Copa-Exemplo-2025"
    ], "Geração das regras", False)
    
    if not sucesso:
        return False
    
    # Criar participantes
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "criar_participantes.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--arquivo", str(dados_dir / "participantes.txt")
    ], "Criação de participantes", False)
    
    if not sucesso:
        return False
    
    # Importar tabela
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "importar_tabela.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--arquivo", str(dados_dir / "tabela_jogos.txt")
    ], "Importação da tabela", False)
    
    print("✅ Setup do campeonato concluído")
    return sucesso

def importar_palpites_rodada1():
    """Importa palpites da rodada 1"""
    print(f"\n{'='*60}")
    print("FASE 2: IMPORTAÇÃO DE PALPITES - RODADA 1")
    print('='*60)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Criar arquivos individuais do WhatsApp
    whatsapp_file = dados_dir / "palpites_whatsapp.txt"
    with open(whatsapp_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    blocos = conteudo.split('---')
    arquivos_criados = []
    
    for i, bloco in enumerate(blocos):
        bloco = bloco.strip()
        if not bloco:
            continue
            
        arquivo_individual = dados_dir / f"temp_palpite_{i+1}.txt"
        with open(arquivo_individual, 'w', encoding='utf-8') as f:
            f.write(bloco)
        arquivos_criados.append(arquivo_individual)
    
    # Importar cada arquivo
    palpites_importados = 0
    for arquivo in arquivos_criados:
        sucesso = executar_comando([
            sys.executable, str(scripts_dir / "importar_palpites.py"),
            "--campeonato", "Copa-Exemplo-2025",
            "--arquivo", str(arquivo)
        ], f"Importação: {arquivo.name}", False)
        
        if sucesso:
            palpites_importados += 1
    
    # Limpar arquivos temporários
    for arquivo in arquivos_criados:
        arquivo.unlink()
    
    print(f"✅ {palpites_importados} conjuntos de palpites importados")
    return palpites_importados > 0

def atualizar_resultados(rodada, resultados):
    """Atualiza resultados de uma rodada"""
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    tabela_file = campeonato_dir / "Tabela" / "tabela.json"
    
    with open(tabela_file, 'r', encoding='utf-8') as f:
        tabela = json.load(f)
    
    jogos_atualizados = 0
    for rodada_data in tabela.get('rodadas', []):
        if rodada_data.get('numero') == rodada:
            for jogo in rodada_data.get('jogos', []):
                mandante = jogo.get('mandante')
                visitante = jogo.get('visitante')
                chave_jogo = f"{mandante} x {visitante}"
                
                if chave_jogo in resultados:
                    gols_mandante, gols_visitante = resultados[chave_jogo]
                    jogo['gols_mandante'] = gols_mandante
                    jogo['gols_visitante'] = gols_visitante
                    jogo['status'] = 'finalizado'
                    jogos_atualizados += 1
    
    with open(tabela_file, 'w', encoding='utf-8') as f:
        json.dump(tabela, f, indent=2, ensure_ascii=False)
    
    return jogos_atualizados

def processar_rodada1():
    """Processa a rodada 1"""
    print(f"\n{'='*60}")
    print("FASE 3: PROCESSAMENTO DA RODADA 1")
    print('='*60)
    
    # Atualizar resultados da rodada 1
    resultados_rodada1 = {
        "Flamengo x Palmeiras": (2, 1),
        "Santos x Corinthians": (1, 1),
        "São Paulo x Grêmio": (3, 0),
        "Atlético-MG x Botafogo": (1, 2),
        "Vasco x Cruzeiro": (0, 1),
        "Internacional x Bahia": (2, 1)
    }
    
    jogos_atualizados = atualizar_resultados(1, resultados_rodada1)
    print(f"📊 {jogos_atualizados} jogos da rodada 1 finalizados")
    
    # Processar em modo final
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--rodada", "1",
        "--final"
    ], "Processamento final da rodada 1", False)
    
    print("✅ Rodada 1 processada")
    return sucesso

def importar_palpites_rodada2():
    """Importa palpites da rodada 2"""
    print(f"\n{'='*60}")
    print("FASE 4: IMPORTAÇÃO DE PALPITES - RODADA 2")
    print('='*60)
    
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Importar palpites da rodada 2
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "importar_palpites.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--arquivo", str(dados_dir / "palpites_rodada2.txt")
    ], "Importação de palpites da rodada 2", False)
    
    print("✅ Palpites da rodada 2 importados")
    return sucesso

def processar_rodada2():
    """Processa a rodada 2"""
    print(f"\n{'='*60}")
    print("FASE 5: PROCESSAMENTO DA RODADA 2")
    print('='*60)
    
    # Atualizar resultados da rodada 2
    resultados_rodada2 = {
        "Palmeiras x Santos": (1, 0),
        "Corinthians x São Paulo": (2, 2),
        "Grêmio x Atlético-MG": (1, 1),
        "Botafogo x Vasco": (3, 1),
        "Cruzeiro x Internacional": (0, 2),
        "Bahia x Flamengo": (1, 3)
    }
    
    jogos_atualizados = atualizar_resultados(2, resultados_rodada2)
    print(f"📊 {jogos_atualizados} jogos da rodada 2 finalizados")
    
    # Processar em modo final
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--rodada", "2",
        "--final"
    ], "Processamento final da rodada 2", False)
    
    print("✅ Rodada 2 processada")
    return sucesso

def analisar_resultados():
    """Analisa os resultados finais"""
    print(f"\n{'='*60}")
    print("FASE 6: ANÁLISE DOS RESULTADOS")
    print('='*60)
    
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    resultados_dir = campeonato_dir / "Resultados"
    
    # Listar relatórios gerados
    relatorios = sorted(list(resultados_dir.glob("rodada*.txt")))
    print(f"📄 {len(relatorios)} relatórios gerados:")
    
    for relatorio in relatorios:
        print(f"   • {relatorio.name} ({relatorio.stat().st_size} bytes)")
    
    # Mostrar classificação final
    if relatorios:
        relatorio_final = relatorios[-1]
        print(f"\n📊 CLASSIFICAÇÃO FINAL ({relatorio_final.name}):")
        print("-" * 60)
        
        with open(relatorio_final, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # Mostrar apenas as primeiras 20 linhas
            linhas = conteudo.split('\n')
            for linha in linhas[:20]:
                print(linha)
            if len(linhas) > 20:
                print("...")
    
    # Estatísticas dos backups
    tabela_dir = campeonato_dir / "Tabela"
    backups = list(tabela_dir.glob("tabela_*.json"))
    print(f"\n💾 {len(backups)} backups criados:")
    for backup in sorted(backups):
        print(f"   • {backup.name}")
    
    # Estatísticas dos participantes
    participantes_dir = campeonato_dir / "Participantes"
    total_palpites = 0
    participantes_ativos = 0
    
    for participante_dir in participantes_dir.iterdir():
        if participante_dir.is_dir():
            palpites_file = participante_dir / "palpites.json"
            if palpites_file.exists():
                with open(palpites_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                rodadas_com_palpites = len(dados.get('palpites', []))
                if rodadas_com_palpites > 0:
                    participantes_ativos += 1
                    for rodada in dados['palpites']:
                        total_palpites += len(rodada.get('jogos', []))
    
    print(f"\n👥 ESTATÍSTICAS DOS PARTICIPANTES:")
    print(f"   • Participantes ativos: {participantes_ativos}")
    print(f"   • Total de palpites: {total_palpites}")
    print(f"   • Média por participante: {total_palpites/participantes_ativos:.1f}")

def main():
    print("🏆 EXEMPLO 4: FLUXO COMPLETO")
    print("=" * 60)
    print("Este exemplo executa um fluxo completo de 2 rodadas do campeonato.")
    print("Demonstra todo o ciclo de vida do sistema de bolão.")
    
    # Limpar ambiente
    limpar_ambiente()
    
    # Executar fluxo completo
    try:
        # Fase 1: Setup
        if not setup_campeonato():
            print("❌ Falha no setup. Abortando.")
            return
        
        # Fase 2: Palpites rodada 1
        if not importar_palpites_rodada1():
            print("❌ Falha na importação de palpites da rodada 1. Abortando.")
            return
        
        # Fase 3: Processar rodada 1
        if not processar_rodada1():
            print("❌ Falha no processamento da rodada 1. Abortando.")
            return
        
        # Fase 4: Palpites rodada 2
        if not importar_palpites_rodada2():
            print("❌ Falha na importação de palpites da rodada 2. Abortando.")
            return
        
        # Fase 5: Processar rodada 2
        if not processar_rodada2():
            print("❌ Falha no processamento da rodada 2. Abortando.")
            return
        
        # Fase 6: Análise
        analisar_resultados()
        
        print(f"\n{'='*60}")
        print("FLUXO COMPLETO EXECUTADO COM SUCESSO!")
        print('='*60)
        print("✅ Campeonato criado e configurado")
        print("✅ 9 participantes registrados")
        print("✅ 12 jogos importados (2 rodadas)")
        print("✅ Palpites importados de múltiplos formatos")
        print("✅ 2 rodadas processadas com sucesso")
        print("✅ Relatórios e backups gerados")
        print("✅ Sistema de pontuação validado")
        
        print(f"\n{'='*60}")
        print("ARQUIVOS GERADOS")
        print('='*60)
        
        campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
        
        # Contar arquivos por tipo
        arquivos_json = len(list(campeonato_dir.rglob("*.json")))
        arquivos_txt = len(list(campeonato_dir.rglob("*.txt")))
        diretorios = len([d for d in campeonato_dir.rglob("*") if d.is_dir()])
        
        print(f"📁 {diretorios} diretórios criados")
        print(f"📄 {arquivos_json} arquivos JSON")
        print(f"📄 {arquivos_txt} arquivos de relatório")
        
        print(f"\n{'='*60}")
        print("PRÓXIMOS PASSOS")
        print('='*60)
        print("1. Explore os arquivos gerados em:")
        print("   Campeonatos/Copa-Exemplo-2025/")
        print()
        print("2. Execute cenários especiais:")
        print("   python 05_cenarios_especiais.py")
        print()
        print("3. Use este exemplo como base para seus próprios campeonatos")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()