#!/usr/bin/env python3
"""
Script de criação de campeonato para o Sistema de Controle de Bolão.

Este script cria a estrutura inicial de diretórios e arquivos JSON
para um novo campeonato, incluindo validação de nomes duplicados
e normalização de nomes.
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
    SUBDIRS_CAMPEONATO, 
    ARQUIVO_REGRAS, 
    ARQUIVO_TABELA,
    REGRAS_PONTUACAO_PADRAO
)
from utils.normalizacao import normalizar_nome_campeonato
from utils.validacao import validar_estrutura_tabela, validar_estrutura_regras


def gerar_codigo_campeonato() -> str:
    """
    Gera código único de 5 dígitos para o campeonato.
    
    Returns:
        String com código único
    """
    import random
    import string
    
    # Gera código alfanumérico de 5 caracteres
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def criar_estrutura_basica_tabela(nome_campeonato: str, temporada: str, codigo: str) -> dict:
    """
    Cria estrutura básica do arquivo tabela.json.
    
    Args:
        nome_campeonato: Nome do campeonato
        temporada: Temporada do campeonato
        codigo: Código único do campeonato
        
    Returns:
        Dicionário com estrutura básica da tabela
    """
    return {
        "campeonato": nome_campeonato,
        "temporada": temporada,
        "rodada_atual": 0,
        "data_atualizacao": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "codigo_campeonato": codigo,
        "rodadas": []
    }


def criar_estrutura_basica_regras(nome_campeonato: str, temporada: str) -> dict:
    """
    Cria estrutura básica do arquivo regras.json.
    
    Args:
        nome_campeonato: Nome do campeonato
        temporada: Temporada do campeonato
        
    Returns:
        Dicionário com estrutura básica das regras
    """
    return {
        "campeonato": nome_campeonato,
        "temporada": temporada,
        "versao": "1.0",
        "data_criacao": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "regras": {
            # Adiciona uma regra básica para passar na validação
            "placeholder": {
                "pontos": 0,
                "descricao": "Regra temporária - use gerar_regras.py para criar regras completas",
                "codigo": "TEMP"
            }
        },
        "observacoes": [
            "Arquivo de regras criado automaticamente",
            "Use o script gerar_regras.py para popular com regras padrão"
        ]
    }


def validar_nome_duplicado(nome_normalizado: str) -> bool:
    """
    Verifica se já existe um campeonato com o mesmo nome.
    
    Args:
        nome_normalizado: Nome normalizado do campeonato
        
    Returns:
        True se o nome já existe, False caso contrário
    """
    caminho_campeonato = CAMPEONATOS_DIR / nome_normalizado
    return caminho_campeonato.exists()


def criar_diretorio_campeonato(nome_normalizado: str, sobrescrever: bool = False) -> Path:
    """
    Cria o diretório principal do campeonato.
    
    Args:
        nome_normalizado: Nome normalizado do campeonato
        sobrescrever: Se True, remove diretório existente antes de criar
        
    Returns:
        Path para o diretório criado
        
    Raises:
        OSError: Se não conseguir criar o diretório
    """
    caminho_campeonato = CAMPEONATOS_DIR / nome_normalizado
    
    try:
        # Criar diretório Campeonatos se não existir
        CAMPEONATOS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Se deve sobrescrever e o diretório existe, remove primeiro
        if sobrescrever and caminho_campeonato.exists():
            import shutil
            shutil.rmtree(caminho_campeonato)
        
        # Criar diretório do campeonato
        caminho_campeonato.mkdir(parents=True, exist_ok=sobrescrever)
        
        return caminho_campeonato
        
    except FileExistsError:
        raise OSError(f"Diretório do campeonato '{nome_normalizado}' já existe")
    except Exception as e:
        raise OSError(f"Erro ao criar diretório do campeonato: {str(e)}")


def criar_subdiretorios(caminho_campeonato: Path) -> None:
    """
    Cria os subdiretórios padrão do campeonato.
    
    Args:
        caminho_campeonato: Path para o diretório do campeonato
        
    Raises:
        OSError: Se não conseguir criar algum subdiretório
    """
    try:
        for subdir in SUBDIRS_CAMPEONATO:
            subdir_path = caminho_campeonato / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            
    except Exception as e:
        raise OSError(f"Erro ao criar subdiretórios: {str(e)}")


def criar_arquivos_json_basicos(caminho_campeonato: Path, nome_campeonato: str, 
                                temporada: str, codigo: str) -> None:
    """
    Cria os arquivos JSON básicos com estrutura válida.
    
    Args:
        caminho_campeonato: Path para o diretório do campeonato
        nome_campeonato: Nome original do campeonato
        temporada: Temporada do campeonato
        codigo: Código único do campeonato
        
    Raises:
        OSError: Se não conseguir criar algum arquivo
        ValueError: Se a estrutura gerada for inválida
    """
    try:
        # Criar arquivo tabela.json
        estrutura_tabela = criar_estrutura_basica_tabela(nome_campeonato, temporada, codigo)
        
        # Validar estrutura antes de salvar
        valido, erros = validar_estrutura_tabela(estrutura_tabela)
        if not valido:
            raise ValueError(f"Estrutura da tabela inválida: {'; '.join(erros)}")
        
        caminho_tabela = caminho_campeonato / "Tabela" / ARQUIVO_TABELA
        with open(caminho_tabela, 'w', encoding='utf-8') as f:
            json.dump(estrutura_tabela, f, indent=2, ensure_ascii=False)
        
        # Criar arquivo regras.json
        estrutura_regras = criar_estrutura_basica_regras(nome_campeonato, temporada)
        
        # Validar estrutura antes de salvar
        valido, erros = validar_estrutura_regras(estrutura_regras)
        if not valido:
            raise ValueError(f"Estrutura das regras inválida: {'; '.join(erros)}")
        
        caminho_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
        with open(caminho_regras, 'w', encoding='utf-8') as f:
            json.dump(estrutura_regras, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        raise OSError(f"Erro ao criar arquivos JSON: {str(e)}")


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


def criar_campeonato(nome: str, temporada: str, codigo: Optional[str] = None, 
                    forcar: bool = False) -> bool:
    """
    Função principal para criar um novo campeonato.
    
    Args:
        nome: Nome do campeonato
        temporada: Temporada do campeonato
        codigo: Código único (opcional, será gerado se não fornecido)
        forcar: Se True, não solicita confirmação para sobrescrever
        
    Returns:
        True se o campeonato foi criado com sucesso, False caso contrário
    """
    try:
        # Normalizar nome do campeonato
        nome_normalizado = normalizar_nome_campeonato(nome)
        
        if not nome_normalizado:
            print("Erro: Nome do campeonato inválido após normalização")
            return False
        
        # Verificar se nome já existe
        sobrescrever = False
        if validar_nome_duplicado(nome_normalizado):
            if not forcar:
                print(f"Aviso: Já existe um campeonato com nome '{nome_normalizado}'")
                if not confirmar_operacao("Deseja continuar mesmo assim?"):
                    print("Operação cancelada pelo usuário")
                    return False
                sobrescrever = True
            else:
                print(f"Aviso: Sobrescrevendo campeonato existente '{nome_normalizado}'")
                sobrescrever = True
        
        # Gerar código se não fornecido
        if not codigo:
            codigo = gerar_codigo_campeonato()
        
        print(f"Criando campeonato '{nome}' (normalizado: '{nome_normalizado}')")
        print(f"Temporada: {temporada}")
        print(f"Código: {codigo}")
        
        # Criar estrutura do campeonato
        caminho_campeonato = criar_diretorio_campeonato(nome_normalizado, sobrescrever)
        print(f"✓ Diretório principal criado: {caminho_campeonato}")
        
        criar_subdiretorios(caminho_campeonato)
        print("✓ Subdiretórios criados:", ", ".join(SUBDIRS_CAMPEONATO))
        
        criar_arquivos_json_basicos(caminho_campeonato, nome, temporada, codigo)
        print("✓ Arquivos JSON básicos criados")
        
        print(f"\n🎉 Campeonato '{nome}' criado com sucesso!")
        print(f"📁 Localização: {caminho_campeonato}")
        print(f"🔑 Código: {codigo}")
        
        # Sugerir próximos passos
        print("\n📋 Próximos passos sugeridos:")
        print(f"1. Execute: python gerar_regras.py --campeonato '{nome_normalizado}' (para criar regras padrão)")
        print(f"2. Execute: python criar_participantes.py --campeonato '{nome_normalizado}' --arquivo lista.txt")
        print(f"3. Execute: python importar_tabela.py --campeonato '{nome_normalizado}' --arquivo jogos.txt")
        
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
        description="Cria estrutura inicial de um novo campeonato",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python criar_campeonato.py --nome "Brasileirão 2025" --temporada "2025"
  python criar_campeonato.py --nome "Copa do Brasil" --temporada "2025" --codigo "CBR25"
  python criar_campeonato.py --nome "Paulistão" --temporada "2025" --forcar
        """
    )
    
    parser.add_argument(
        '--nome',
        required=True,
        help='Nome do campeonato (será normalizado para nome do diretório)'
    )
    
    parser.add_argument(
        '--temporada',
        required=True,
        help='Temporada do campeonato (ex: "2025")'
    )
    
    parser.add_argument(
        '--codigo',
        help='Código único do campeonato (5 caracteres, gerado automaticamente se omitido)'
    )
    
    parser.add_argument(
        '--forcar',
        action='store_true',
        help='Força criação sem confirmação, mesmo se campeonato já existir'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.nome.strip():
        print("Erro: Nome do campeonato não pode estar vazio")
        sys.exit(1)
    
    if not args.temporada.strip():
        print("Erro: Temporada não pode estar vazia")
        sys.exit(1)
    
    if args.codigo and len(args.codigo) != 5:
        print("Erro: Código do campeonato deve ter exatamente 5 caracteres")
        sys.exit(1)
    
    # Executar criação do campeonato
    sucesso = criar_campeonato(
        nome=args.nome.strip(),
        temporada=args.temporada.strip(),
        codigo=args.codigo.strip() if args.codigo else None,
        forcar=args.forcar
    )
    
    if sucesso:
        print("\n✅ Script executado com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Falha na execução do script")
        sys.exit(1)


if __name__ == "__main__":
    main()