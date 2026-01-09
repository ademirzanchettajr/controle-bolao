#!/usr/bin/env python3
"""
Exemplo 3: Processamento de Rodada

Este script demonstra o processamento completo de uma rodada:
1. Atualizar resultados dos jogos
2. Processar em modo teste
3. Processar em modo final
4. Verificar relatório gerado

Execute: python 03_processar_rodada.py
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def executar_comando(comando, descricao):
    """Executa um comando e exibe o resultado"""
    print(f"\n{'='*60}")
    print(f"EXECUTANDO: {descricao}")
    print(f"COMANDO: {' '.join(comando)}")
    print('='*60)
    
    try:
        result = subprocess.run(comando, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.stdout:
            print("SAÍDA:")
            print(result.stdout)
        
        if result.stderr:
            print("ERROS/AVISOS:")
            print(result.stderr)
            
        if result.returncode != 0:
            print(f"ERRO: Comando falhou com código {result.returncode}")
            return False
        else:
            print("✅ SUCESSO!")
            return True
            
    except Exception as e:
        print(f"ERRO ao executar comando: {e}")
        return False

def verificar_campeonato():
    """Verifica se o campeonato existe"""
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    if not campeonato_dir.exists():
        print("❌ Campeonato 'Copa-Exemplo-2025' não encontrado!")
        print("Execute primeiro: python 01_setup_completo.py")
        return False
    return True

def atualizar_resultados_rodada1():
    """Atualiza os resultados da rodada 1 na tabela"""
    print(f"\n{'='*60}")
    print("ATUALIZANDO RESULTADOS DA RODADA 1")
    print('='*60)
    
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    tabela_file = campeonato_dir / "Tabela" / "tabela.json"
    
    if not tabela_file.exists():
        print(f"❌ Arquivo tabela.json não encontrado: {tabela_file}")
        return False
    
    # Ler tabela atual
    with open(tabela_file, 'r', encoding='utf-8') as f:
        tabela = json.load(f)
    
    # Resultados da rodada 1 (simulados)
    resultados_rodada1 = {
        "Flamengo x Palmeiras": (2, 1),      # Flamengo 2x1 Palmeiras
        "Santos x Corinthians": (1, 1),      # Santos 1x1 Corinthians  
        "São Paulo x Grêmio": (3, 0),        # São Paulo 3x0 Grêmio
        "Atlético-MG x Botafogo": (1, 2),    # Atlético-MG 1x2 Botafogo
        "Vasco x Cruzeiro": (0, 1),          # Vasco 0x1 Cruzeiro
        "Internacional x Bahia": (2, 1)      # Internacional 2x1 Bahia
    }
    
    # Atualizar jogos da rodada 1
    jogos_atualizados = 0
    for rodada in tabela.get('rodadas', []):
        if rodada.get('numero') == 1:
            for jogo in rodada.get('jogos', []):
                mandante = jogo.get('mandante')
                visitante = jogo.get('visitante')
                chave_jogo = f"{mandante} x {visitante}"
                
                if chave_jogo in resultados_rodada1:
                    gols_mandante, gols_visitante = resultados_rodada1[chave_jogo]
                    jogo['gols_mandante'] = gols_mandante
                    jogo['gols_visitante'] = gols_visitante
                    jogo['status'] = 'finalizado'
                    jogos_atualizados += 1
                    print(f"✅ {chave_jogo}: {gols_mandante}x{gols_visitante}")
    
    # Salvar tabela atualizada
    with open(tabela_file, 'w', encoding='utf-8') as f:
        json.dump(tabela, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 {jogos_atualizados} jogos atualizados na tabela")
    return True

def processar_modo_teste():
    """Processa a rodada em modo teste"""
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--rodada", "1",
        "--teste"
    ], "Processamento da rodada 1 em MODO TESTE")
    
    return sucesso

def processar_modo_final():
    """Processa a rodada em modo final"""
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "processar_resultados.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--rodada", "1",
        "--final"
    ], "Processamento da rodada 1 em MODO FINAL")
    
    return sucesso

def verificar_arquivos_gerados():
    """Verifica os arquivos gerados pelo processamento"""
    print(f"\n{'='*60}")
    print("VERIFICANDO ARQUIVOS GERADOS")
    print('='*60)
    
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    
    # Verificar backup da tabela
    tabela_dir = campeonato_dir / "Tabela"
    backups = list(tabela_dir.glob("tabela_*.json"))
    if backups:
        backup_mais_recente = max(backups, key=lambda x: x.stat().st_mtime)
        print(f"✅ Backup criado: {backup_mais_recente.name}")
        print(f"   Tamanho: {backup_mais_recente.stat().st_size} bytes")
    else:
        print("⚠️  Nenhum backup encontrado")
    
    # Verificar relatório da rodada
    resultados_dir = campeonato_dir / "Resultados"
    relatorios = list(resultados_dir.glob("rodada*.txt"))
    if relatorios:
        for relatorio in relatorios:
            print(f"✅ Relatório: {relatorio.name}")
            print(f"   Tamanho: {relatorio.stat().st_size} bytes")
            
            # Mostrar início do relatório
            with open(relatorio, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                print(f"   Linhas: {len(linhas)}")
                if linhas:
                    print("   Início do relatório:")
                    for linha in linhas[:5]:
                        print(f"     {linha.rstrip()}")
                    if len(linhas) > 5:
                        print("     ...")
    else:
        print("⚠️  Nenhum relatório encontrado")
    
    # Verificar atualização da rodada atual
    tabela_file = campeonato_dir / "Tabela" / "tabela.json"
    if tabela_file.exists():
        with open(tabela_file, 'r', encoding='utf-8') as f:
            tabela = json.load(f)
        
        rodada_atual = tabela.get('rodada_atual', 0)
        print(f"✅ Rodada atual atualizada: {rodada_atual}")
    else:
        print("❌ Arquivo tabela.json não encontrado")

def mostrar_classificacao():
    """Mostra a classificação atual"""
    print(f"\n{'='*60}")
    print("CLASSIFICAÇÃO ATUAL")
    print('='*60)
    
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    resultados_dir = campeonato_dir / "Resultados"
    
    # Procurar relatório mais recente
    relatorios = list(resultados_dir.glob("rodada*.txt"))
    if not relatorios:
        print("❌ Nenhum relatório encontrado")
        return
    
    relatorio_mais_recente = max(relatorios, key=lambda x: x.stat().st_mtime)
    
    print(f"📊 Relatório: {relatorio_mais_recente.name}")
    print("-" * 60)
    
    with open(relatorio_mais_recente, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        print(conteudo)

def main():
    print("⚽ EXEMPLO 3: PROCESSAMENTO DE RODADA")
    print("=" * 60)
    print("Este exemplo demonstra o processamento completo de uma rodada.")
    
    # Verificar se campeonato existe
    if not verificar_campeonato():
        return
    
    # Verificar se há palpites
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    participantes_dir = campeonato_dir / "Participantes"
    
    tem_palpites = False
    if participantes_dir.exists():
        for participante_dir in participantes_dir.iterdir():
            if participante_dir.is_dir():
                palpites_file = participante_dir / "palpites.json"
                if palpites_file.exists():
                    with open(palpites_file, 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                    if dados.get('palpites'):
                        tem_palpites = True
                        break
    
    if not tem_palpites:
        print("⚠️  Nenhum palpite encontrado!")
        print("Execute primeiro: python 02_importar_dados.py")
        return
    
    # 1. Atualizar resultados
    if not atualizar_resultados_rodada1():
        print("❌ Falha ao atualizar resultados. Abortando.")
        return
    
    # 2. Processar em modo teste
    print(f"\n{'='*60}")
    print("PROCESSAMENTO EM MODO TESTE")
    print('='*60)
    print("O modo teste permite verificar os cálculos sem modificar arquivos.")
    
    if not processar_modo_teste():
        print("❌ Falha no processamento em modo teste")
        return
    
    # 3. Processar em modo final
    print(f"\n{'='*60}")
    print("PROCESSAMENTO EM MODO FINAL")
    print('='*60)
    print("O modo final cria backup e atualiza os arquivos oficialmente.")
    
    if not processar_modo_final():
        print("❌ Falha no processamento em modo final")
        return
    
    # 4. Verificar arquivos gerados
    verificar_arquivos_gerados()
    
    # 5. Mostrar classificação
    mostrar_classificacao()
    
    print(f"\n{'='*60}")
    print("RESUMO DO PROCESSAMENTO")
    print('='*60)
    print("✅ Resultados da rodada 1 atualizados")
    print("🧪 Processamento testado em modo seguro")
    print("💾 Backup automático criado")
    print("📊 Classificação calculada e salva")
    print("📄 Relatório da rodada gerado")
    print("🔄 Rodada atual atualizada no sistema")
    
    print(f"\n{'='*60}")
    print("PRÓXIMOS PASSOS")
    print('='*60)
    print("1. Execute o fluxo completo com múltiplas rodadas:")
    print("   python 04_fluxo_completo.py")
    print()
    print("2. Explore cenários especiais:")
    print("   python 05_cenarios_especiais.py")

if __name__ == "__main__":
    main()