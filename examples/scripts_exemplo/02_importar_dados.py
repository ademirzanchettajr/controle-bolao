#!/usr/bin/env python3
"""
Exemplo 2: Importação de Dados

Este script demonstra diferentes formas de importar dados:
1. Participantes de arquivo Excel
2. Palpites de mensagens do WhatsApp
3. Validação de dados importados

Execute: python 02_importar_dados.py
"""

import sys
import os
import subprocess
import json
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

def verificar_campeonato():
    """Verifica se o campeonato existe"""
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    if not campeonato_dir.exists():
        print("❌ Campeonato 'Copa-Exemplo-2025' não encontrado!")
        print("Execute primeiro: python 01_setup_completo.py")
        return False
    return True

def criar_palpites_individuais():
    """Cria arquivos de palpites individuais a partir do arquivo WhatsApp"""
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    whatsapp_file = dados_dir / "palpites_whatsapp.txt"
    
    if not whatsapp_file.exists():
        print(f"❌ Arquivo não encontrado: {whatsapp_file}")
        return
    
    # Ler arquivo WhatsApp
    with open(whatsapp_file, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Dividir por participante (separado por ---)
    blocos = conteudo.split('---')
    
    for i, bloco in enumerate(blocos):
        bloco = bloco.strip()
        if not bloco:
            continue
            
        # Criar arquivo individual
        arquivo_individual = dados_dir / f"palpite_individual_{i+1}.txt"
        with open(arquivo_individual, 'w', encoding='utf-8') as f:
            f.write(bloco)
        
        print(f"✅ Criado: {arquivo_individual.name}")

def importar_palpites_whatsapp():
    """Importa palpites do formato WhatsApp"""
    base_dir = Path(__file__).parent.parent.parent
    scripts_dir = base_dir / "src" / "scripts"
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    print(f"\n{'='*60}")
    print("IMPORTANDO PALPITES DO WHATSAPP")
    print('='*60)
    
    # Criar arquivos individuais
    criar_palpites_individuais()
    
    # Importar cada arquivo individual
    arquivos_palpites = list(dados_dir.glob("palpite_individual_*.txt"))
    
    for arquivo in sorted(arquivos_palpites):
        sucesso = executar_comando([
            sys.executable, str(scripts_dir / "importar_palpites.py"),
            "--campeonato", "Copa-Exemplo-2025",
            "--arquivo", str(arquivo)
        ], f"Importação de palpites: {arquivo.name}")
        
        if not sucesso:
            print(f"❌ Falha na importação de {arquivo.name}")

def verificar_dados_importados():
    """Verifica os dados que foram importados"""
    print(f"\n{'='*60}")
    print("VERIFICANDO DADOS IMPORTADOS")
    print('='*60)
    
    campeonato_dir = Path("Campeonatos/Copa-Exemplo-2025")
    participantes_dir = campeonato_dir / "Participantes"
    
    if not participantes_dir.exists():
        print("❌ Diretório de participantes não encontrado")
        return
    
    # Contar participantes com palpites
    participantes_com_palpites = 0
    total_palpites = 0
    
    for participante_dir in participantes_dir.iterdir():
        if not participante_dir.is_dir():
            continue
            
        palpites_file = participante_dir / "palpites.json"
        if palpites_file.exists():
            try:
                with open(palpites_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                if dados.get('palpites'):
                    participantes_com_palpites += 1
                    for rodada in dados['palpites']:
                        total_palpites += len(rodada.get('jogos', []))
                    
                    print(f"✅ {participante_dir.name}: {len(dados['palpites'])} rodada(s)")
                else:
                    print(f"⚠️  {participante_dir.name}: sem palpites")
                    
            except Exception as e:
                print(f"❌ Erro ao ler {participante_dir.name}: {e}")
    
    print(f"\n📊 RESUMO:")
    print(f"   👥 Participantes com palpites: {participantes_com_palpites}")
    print(f"   🎯 Total de palpites: {total_palpites}")

def demonstrar_formatos():
    """Demonstra diferentes formatos de entrada aceitos"""
    print(f"\n{'='*60}")
    print("FORMATOS DE ENTRADA DEMONSTRADOS")
    print('='*60)
    
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    
    # Mostrar formato básico
    print("\n1. FORMATO BÁSICO (palpites_rodada1.txt):")
    print("-" * 40)
    with open(dados_dir / "palpites_rodada1.txt", 'r', encoding='utf-8') as f:
        print(f.read())
    
    # Mostrar formato com marcadores
    print("\n2. FORMATO COM MARCADORES (palpites_rodada2.txt):")
    print("-" * 40)
    with open(dados_dir / "palpites_rodada2.txt", 'r', encoding='utf-8') as f:
        print(f.read())
    
    # Mostrar formato WhatsApp (apenas primeiro bloco)
    print("\n3. FORMATO WHATSAPP (primeiro exemplo):")
    print("-" * 40)
    with open(dados_dir / "palpites_whatsapp.txt", 'r', encoding='utf-8') as f:
        conteudo = f.read()
        primeiro_bloco = conteudo.split('---')[0].strip()
        print(primeiro_bloco)
        print("\n... (mais exemplos no arquivo palpites_whatsapp.txt)")

def main():
    print("📥 EXEMPLO 2: IMPORTAÇÃO DE DADOS")
    print("=" * 60)
    print("Este exemplo demonstra diferentes formas de importar dados no sistema.")
    
    # Verificar se campeonato existe
    if not verificar_campeonato():
        return
    
    # Demonstrar formatos
    demonstrar_formatos()
    
    # Importar palpites do WhatsApp
    importar_palpites_whatsapp()
    
    # Verificar dados importados
    verificar_dados_importados()
    
    print(f"\n{'='*60}")
    print("RESUMO DA IMPORTAÇÃO")
    print('='*60)
    print("✅ Palpites importados de mensagens do WhatsApp")
    print("📝 Diferentes formatos de texto processados:")
    print("   • Formato básico (Nome + Rodada + Palpites)")
    print("   • Formato com marcadores (Apostador: Nome)")
    print("   • Formato WhatsApp real (texto livre)")
    print("🔍 Normalização automática de nomes de times")
    print("✅ Validação de dados durante importação")
    
    print(f"\n{'='*60}")
    print("PRÓXIMOS PASSOS")
    print('='*60)
    print("1. Execute o exemplo 03 para processar resultados:")
    print("   python 03_processar_rodada.py")
    print()
    print("2. Ou execute o fluxo completo:")
    print("   python 04_fluxo_completo.py")
    
    # Limpar arquivos temporários
    dados_dir = Path(__file__).parent.parent / "dados_teste"
    for arquivo in dados_dir.glob("palpite_individual_*.txt"):
        arquivo.unlink()
    print(f"\n🧹 Arquivos temporários removidos")

if __name__ == "__main__":
    main()