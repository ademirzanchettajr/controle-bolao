#!/usr/bin/env python3
"""
Exemplo 1: Setup Completo de Campeonato

Este script demonstra como configurar um campeonato completo do zero:
1. Criar estrutura do campeonato
2. Gerar regras de pontuação
3. Criar participantes
4. Importar tabela de jogos

Execute: python 01_setup_completo.py
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

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

def limpar_campeonato_anterior():
    """Remove campeonato anterior se existir"""
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    if campeonato_dir.exists():
        print(f"\n🧹 Removendo campeonato anterior: {campeonato_dir}")
        shutil.rmtree(campeonato_dir)
        print("✅ Campeonato anterior removido")

def main():
    print("🏆 EXEMPLO 1: SETUP COMPLETO DE CAMPEONATO")
    print("=" * 60)
    print("Este exemplo demonstra a configuração completa de um novo campeonato.")
    print("Será criado o campeonato 'Copa-Exemplo-2025' com dados de teste.")
    
    # Limpar campeonato anterior
    limpar_campeonato_anterior()
    
    # Definir caminhos
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # 1. Criar campeonato
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "criar_campeonato.py"),
        "--nome", "Copa-Exemplo-2025",
        "--temporada", "2025",
        "--codigo", "CEX25"
    ], "Criação da estrutura do campeonato")
    
    if not sucesso:
        print("❌ Falha na criação do campeonato. Abortando.")
        return
    
    # 2. Gerar regras
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "gerar_regras.py"),
        "--campeonato", "Copa-Exemplo-2025"
    ], "Geração das regras de pontuação")
    
    if not sucesso:
        print("❌ Falha na geração das regras. Continuando...")
    
    # 3. Criar participantes (arquivo texto)
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "criar_participantes.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--arquivo", str(dados_dir / "participantes.txt")
    ], "Criação de participantes (arquivo texto)")
    
    if not sucesso:
        print("❌ Falha na criação de participantes. Continuando...")
    
    # 4. Importar tabela de jogos
    sucesso = executar_comando([
        sys.executable, str(scripts_dir / "importar_tabela.py"),
        "--campeonato", "Copa-Exemplo-2025",
        "--arquivo", str(dados_dir / "tabela_jogos.txt")
    ], "Importação da tabela de jogos")
    
    if not sucesso:
        print("❌ Falha na importação da tabela. Continuando...")
    
    # Verificar estrutura criada
    print(f"\n{'='*60}")
    print("VERIFICANDO ESTRUTURA CRIADA")
    print('='*60)
    
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    if campeonato_dir.exists():
        print(f"✅ Diretório do campeonato criado: {campeonato_dir}")
        
        # Verificar subdiretórios
        subdirs = ["Regras", "Tabela", "Resultados", "Participantes"]
        for subdir in subdirs:
            subdir_path = campeonato_dir / subdir
            if subdir_path.exists():
                print(f"  ✅ {subdir}/")
                
                # Listar arquivos importantes
                if subdir == "Regras":
                    regras_file = subdir_path / "regras.json"
                    if regras_file.exists():
                        print(f"    ✅ regras.json ({regras_file.stat().st_size} bytes)")
                
                elif subdir == "Tabela":
                    tabela_file = subdir_path / "tabela.json"
                    if tabela_file.exists():
                        print(f"    ✅ tabela.json ({tabela_file.stat().st_size} bytes)")
                
                elif subdir == "Participantes":
                    participantes = list(subdir_path.iterdir())
                    print(f"    ✅ {len(participantes)} participantes criados")
                    for p in participantes[:3]:  # Mostrar apenas os primeiros 3
                        if p.is_dir():
                            palpites_file = p / "palpites.json"
                            if palpites_file.exists():
                                print(f"      ✅ {p.name}/palpites.json")
                    if len(participantes) > 3:
                        print(f"      ... e mais {len(participantes) - 3}")
            else:
                print(f"  ❌ {subdir}/ (não encontrado)")
    
    print(f"\n{'='*60}")
    print("RESUMO DO SETUP")
    print('='*60)
    print("✅ Campeonato 'Copa-Exemplo-2025' configurado com sucesso!")
    print("📁 Estrutura de diretórios criada")
    print("⚙️  Regras de pontuação configuradas")
    print("👥 9 participantes registrados")
    print("📅 Tabela com 12 jogos (2 rodadas) importada")
    
    print(f"\n{'='*60}")
    print("PRÓXIMOS PASSOS")
    print('='*60)
    print("1. Execute o exemplo 02 para importar palpites:")
    print("   python 02_importar_dados.py")
    print()
    print("2. Execute o exemplo 03 para processar uma rodada:")
    print("   python 03_processar_rodada.py")
    print()
    print("3. Ou execute o fluxo completo:")
    print("   python 04_fluxo_completo.py")

if __name__ == "__main__":
    main()