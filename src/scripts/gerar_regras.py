#!/usr/bin/env python3
"""
Script de geração de regras para o Sistema de Controle de Bolão.

Este script gera o arquivo regras.json com o template padrão de pontuação
para um campeonato existente, incluindo validação e confirmação para
sobrescrever arquivos existentes.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Adicionar o diretório pai ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    CAMPEONATOS_DIR, 
    ARQUIVO_REGRAS, 
    REGRAS_PONTUACAO_PADRAO
)
from utils.validacao import validar_estrutura_regras


def carregar_template_regras_padrao() -> dict:
    """
    Carrega o template de regras padrão do sistema.
    
    Returns:
        Dicionário com as regras de pontuação padrão
    """
    return REGRAS_PONTUACAO_PADRAO.copy()


def criar_estrutura_regras_completa(nome_campeonato: str, temporada: str) -> dict:
    """
    Cria estrutura completa do arquivo regras.json com todas as regras padrão.
    
    Args:
        nome_campeonato: Nome do campeonato
        temporada: Temporada do campeonato
        
    Returns:
        Dicionário com estrutura completa das regras
    """
    regras_padrao = carregar_template_regras_padrao()
    
    return {
        "campeonato": nome_campeonato,
        "temporada": temporada,
        "versao": "1.0",
        "data_criacao": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "regras": regras_padrao,
        "observacoes": [
            "Regras de pontuação padrão do Sistema de Controle de Bolão",
            "Hierarquia: maior pontuação aplicável é atribuída",
            "Bônus para resultado exato: 1/N onde N = número de acertos exatos no jogo",
            "Jogos obrigatórios sem palpite recebem penalidade de -1 ponto"
        ]
    }


def obter_dados_campeonato_existente(caminho_campeonato: Path) -> Optional[tuple]:
    """
    Obtém dados do campeonato existente a partir do arquivo tabela.json.
    
    Args:
        caminho_campeonato: Path para o diretório do campeonato
        
    Returns:
        Tupla (nome_campeonato, temporada) ou None se não conseguir obter
    """
    try:
        caminho_tabela = caminho_campeonato / "Tabela" / "tabela.json"
        
        if not caminho_tabela.exists():
            return None
            
        with open(caminho_tabela, 'r', encoding='utf-8') as f:
            dados_tabela = json.load(f)
            
        nome = dados_tabela.get("campeonato")
        temporada = dados_tabela.get("temporada")
        
        if nome and temporada:
            return (nome, temporada)
            
        return None
        
    except Exception:
        return None


def verificar_campeonato_existe(nome_campeonato: str) -> tuple:
    """
    Verifica se o campeonato existe e retorna informações.
    
    Args:
        nome_campeonato: Nome normalizado do campeonato
        
    Returns:
        Tupla (existe: bool, caminho: Path, dados: tuple ou None)
    """
    caminho_campeonato = CAMPEONATOS_DIR / nome_campeonato
    
    if not caminho_campeonato.exists():
        return (False, caminho_campeonato, None)
    
    # Verificar se é um diretório válido de campeonato
    if not caminho_campeonato.is_dir():
        return (False, caminho_campeonato, None)
    
    # Tentar obter dados do campeonato
    dados = obter_dados_campeonato_existente(caminho_campeonato)
    
    return (True, caminho_campeonato, dados)


def verificar_arquivo_regras_existe(caminho_campeonato: Path) -> bool:
    """
    Verifica se o arquivo regras.json já existe.
    
    Args:
        caminho_campeonato: Path para o diretório do campeonato
        
    Returns:
        True se o arquivo existe, False caso contrário
    """
    caminho_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
    return caminho_regras.exists()


def confirmar_operacao(mensagem: str) -> bool:
    """
    Solicita confirmação do usuário para operações críticas.
    
    Args:
        mensagem: Mensagem a ser exibida
        
    Returns:
        True se o usuário confirmar, False caso contrário
    """
    resposta = input(f"{mensagem} (s/n): ").strip().lower()
    return resposta in ['s', 'sim', 'y', 'yes']


def escrever_arquivo_regras(caminho_campeonato: Path, estrutura_regras: dict) -> None:
    """
    Escreve o arquivo regras.json no diretório do campeonato.
    
    Args:
        caminho_campeonato: Path para o diretório do campeonato
        estrutura_regras: Estrutura das regras a ser salva
        
    Raises:
        OSError: Se não conseguir escrever o arquivo
        ValueError: Se a estrutura for inválida
    """
    try:
        # Validar estrutura antes de salvar
        valido, erros = validar_estrutura_regras(estrutura_regras)
        if not valido:
            raise ValueError(f"Estrutura das regras inválida: {'; '.join(erros)}")
        
        # Garantir que o diretório Regras existe
        dir_regras = caminho_campeonato / "Regras"
        dir_regras.mkdir(parents=True, exist_ok=True)
        
        # Escrever arquivo
        caminho_regras = dir_regras / ARQUIVO_REGRAS
        with open(caminho_regras, 'w', encoding='utf-8') as f:
            json.dump(estrutura_regras, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        raise OSError(f"Erro ao escrever arquivo de regras: {str(e)}")


def gerar_regras(nome_campeonato: str, sobrescrever: bool = False) -> bool:
    """
    Função principal para gerar arquivo de regras.
    
    Args:
        nome_campeonato: Nome normalizado do campeonato
        sobrescrever: Se True, não solicita confirmação para sobrescrever
        
    Returns:
        True se as regras foram geradas com sucesso, False caso contrário
    """
    try:
        # Verificar se campeonato existe
        existe, caminho_campeonato, dados_campeonato = verificar_campeonato_existe(nome_campeonato)
        
        if not existe:
            print(f"Erro: Campeonato '{nome_campeonato}' não encontrado")
            print(f"Verifique se o diretório existe em: {caminho_campeonato}")
            return False
        
        # Obter dados do campeonato
        if dados_campeonato:
            nome_original, temporada = dados_campeonato
            print(f"Campeonato encontrado: {nome_original} ({temporada})")
        else:
            print(f"Aviso: Não foi possível obter dados do campeonato de tabela.json")
            print("Será necessário fornecer nome e temporada manualmente")
            
            nome_original = input("Digite o nome do campeonato: ").strip()
            temporada = input("Digite a temporada: ").strip()
            
            if not nome_original or not temporada:
                print("Erro: Nome e temporada são obrigatórios")
                return False
        
        # Verificar se arquivo de regras já existe
        arquivo_existe = verificar_arquivo_regras_existe(caminho_campeonato)
        
        if arquivo_existe and not sobrescrever:
            print(f"Aviso: Arquivo de regras já existe para o campeonato '{nome_campeonato}'")
            if not confirmar_operacao("Deseja sobrescrever o arquivo existente?"):
                print("Operação cancelada pelo usuário")
                return False
        
        print(f"Gerando arquivo de regras para '{nome_original}'...")
        
        # Criar estrutura das regras
        estrutura_regras = criar_estrutura_regras_completa(nome_original, temporada)
        
        # Escrever arquivo
        escrever_arquivo_regras(caminho_campeonato, estrutura_regras)
        
        # Exibir resumo das regras criadas
        total_regras = len(estrutura_regras["regras"])
        print(f"✓ Arquivo de regras criado com {total_regras} regras de pontuação")
        
        # Listar as regras criadas
        print("\n📋 Regras de pontuação configuradas:")
        for codigo_regra, regra in estrutura_regras["regras"].items():
            pontos = regra.get("pontos_base", regra.get("pontos", 0))
            codigo = regra.get("codigo", "")
            descricao = regra.get("descricao", "")
            
            if regra.get("bonus_divisor"):
                print(f"  [{codigo}] {descricao}: {pontos} + bônus (1/N)")
            else:
                print(f"  [{codigo}] {descricao}: {pontos} pontos")
        
        caminho_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
        print(f"\n🎉 Arquivo de regras gerado com sucesso!")
        print(f"📁 Localização: {caminho_regras}")
        
        # Sugerir próximos passos
        print("\n📋 Próximos passos sugeridos:")
        print(f"1. Execute: python criar_participantes.py --campeonato '{nome_campeonato}' --arquivo lista.txt")
        print(f"2. Execute: python importar_tabela.py --campeonato '{nome_campeonato}' --arquivo jogos.txt")
        print(f"3. Execute: python importar_palpites.py --campeonato '{nome_campeonato}' --arquivo palpite.txt")
        
        return True
        
    except OSError as e:
        print(f"Erro de sistema: {str(e)}")
        return False
    except ValueError as e:
        print(f"Erro de validação: {str(e)}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return False


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Gera arquivo de regras com template padrão para um campeonato",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python gerar_regras.py --campeonato "brasileirao-2025"
  python gerar_regras.py --campeonato "copa-do-brasil" --sobrescrever
        """
    )
    
    parser.add_argument(
        '--campeonato',
        required=True,
        help='Nome do campeonato (deve corresponder ao nome do diretório)'
    )
    
    parser.add_argument(
        '--sobrescrever',
        action='store_true',
        help='Sobrescreve arquivo de regras existente sem confirmação'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.campeonato.strip():
        print("Erro: Nome do campeonato não pode estar vazio")
        sys.exit(1)
    
    # Executar geração de regras
    sucesso = gerar_regras(
        nome_campeonato=args.campeonato.strip(),
        sobrescrever=args.sobrescrever
    )
    
    if sucesso:
        print("\n✅ Script executado com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Falha na execução do script")
        sys.exit(1)


if __name__ == "__main__":
    main()