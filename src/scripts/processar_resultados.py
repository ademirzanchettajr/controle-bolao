#!/usr/bin/env python3
"""
Script de processamento de resultados para o Sistema de Controle de Bolão.

Este script calcula pontuações de uma rodada específica baseado nos palpites
dos participantes e nos resultados dos jogos. Suporta modo teste (apenas exibe)
e modo final (atualiza arquivos e gera relatório).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Adicionar src ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from config import CAMPEONATOS_DIR, ARQUIVO_TABELA, ARQUIVO_REGRAS, ARQUIVO_PALPITES
from utils.validacao import validar_estrutura_tabela, validar_estrutura_regras, validar_estrutura_palpites
from utils.pontuacao import calcular_pontuacao, calcular_pontuacao_palpite_ausente
from utils.relatorio import gerar_tabela_classificacao, gerar_resumo_rodada


def carregar_dados_campeonato(nome_campeonato: str) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    """
    Carrega tabela, regras e palpites de todos os participantes do campeonato.
    
    Args:
        nome_campeonato: Nome do campeonato
        
    Returns:
        Tupla (tabela, regras, lista_palpites_participantes)
        
    Raises:
        FileNotFoundError: Se arquivos obrigatórios não existirem
        ValueError: Se dados estiverem inválidos
    """
    caminho_campeonato = CAMPEONATOS_DIR / nome_campeonato
    
    if not caminho_campeonato.exists():
        raise FileNotFoundError(f"Campeonato '{nome_campeonato}' não encontrado")
    
    # Carregar tabela
    caminho_tabela = caminho_campeonato / "Tabela" / ARQUIVO_TABELA
    if not caminho_tabela.exists():
        raise FileNotFoundError(f"Arquivo de tabela não encontrado: {caminho_tabela}")
    
    with open(caminho_tabela, 'r', encoding='utf-8') as f:
        tabela = json.load(f)
    
    # Validar estrutura da tabela
    valido, erros = validar_estrutura_tabela(tabela)
    if not valido:
        raise ValueError(f"Estrutura da tabela inválida: {'; '.join(erros)}")
    
    # Carregar regras
    caminho_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
    if not caminho_regras.exists():
        raise FileNotFoundError(f"Arquivo de regras não encontrado: {caminho_regras}")
    
    with open(caminho_regras, 'r', encoding='utf-8') as f:
        regras = json.load(f)
    
    # Validar estrutura das regras
    valido, erros = validar_estrutura_regras(regras)
    if not valido:
        raise ValueError(f"Estrutura das regras inválida: {'; '.join(erros)}")
    
    # Carregar palpites de todos os participantes
    caminho_participantes = caminho_campeonato / "Participantes"
    if not caminho_participantes.exists():
        raise FileNotFoundError(f"Diretório de participantes não encontrado: {caminho_participantes}")
    
    palpites_participantes = []
    
    for dir_participante in caminho_participantes.iterdir():
        if not dir_participante.is_dir():
            continue
        
        caminho_palpites = dir_participante / ARQUIVO_PALPITES
        if not caminho_palpites.exists():
            print(f"Aviso: Arquivo de palpites não encontrado para {dir_participante.name}")
            continue
        
        try:
            with open(caminho_palpites, 'r', encoding='utf-8') as f:
                palpites = json.load(f)
            
            # Validar estrutura dos palpites
            valido, erros = validar_estrutura_palpites(palpites)
            if not valido:
                print(f"Aviso: Estrutura de palpites inválida para {dir_participante.name}: {'; '.join(erros)}")
                continue
            
            palpites_participantes.append(palpites)
            
        except Exception as e:
            print(f"Erro ao carregar palpites de {dir_participante.name}: {e}")
            continue
    
    if not palpites_participantes:
        raise ValueError("Nenhum arquivo de palpites válido encontrado")
    
    return tabela, regras, palpites_participantes


def obter_jogos_rodada(tabela: Dict[str, Any], numero_rodada: int) -> List[Dict[str, Any]]:
    """
    Obtém lista de jogos de uma rodada específica.
    
    Args:
        tabela: Dados da tabela do campeonato
        numero_rodada: Número da rodada
        
    Returns:
        Lista de jogos da rodada
        
    Raises:
        ValueError: Se rodada não for encontrada
    """
    for rodada in tabela.get("rodadas", []):
        if rodada.get("numero") == numero_rodada:
            return rodada.get("jogos", [])
    
    raise ValueError(f"Rodada {numero_rodada} não encontrada na tabela")


def validar_jogos_obrigatorios_finalizados(jogos: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Valida que todos os jogos obrigatórios da rodada estão finalizados.
    
    Args:
        jogos: Lista de jogos da rodada
        
    Returns:
        Tupla (todos_finalizados, lista_jogos_pendentes)
    """
    jogos_pendentes = []
    
    for jogo in jogos:
        if jogo.get("obrigatorio", False) and jogo.get("status") != "finalizado":
            info_jogo = f"{jogo.get('mandante', 'N/A')} x {jogo.get('visitante', 'N/A')} (ID: {jogo.get('id', 'N/A')})"
            jogos_pendentes.append(info_jogo)
    
    return len(jogos_pendentes) == 0, jogos_pendentes


def obter_palpites_participante_rodada(palpites_participante: Dict[str, Any], numero_rodada: int) -> Dict[str, Dict[str, Any]]:
    """
    Obtém palpites de um participante para uma rodada específica.
    
    Args:
        palpites_participante: Dados de palpites do participante
        numero_rodada: Número da rodada
        
    Returns:
        Dicionário {id_jogo: palpite} para a rodada
    """
    palpites_rodada = {}
    
    for rodada_palpites in palpites_participante.get("palpites", []):
        if rodada_palpites.get("rodada") == numero_rodada:
            for jogo_palpite in rodada_palpites.get("jogos", []):
                id_jogo = jogo_palpite.get("id")
                if id_jogo:
                    palpites_rodada[id_jogo] = jogo_palpite
            break
    
    return palpites_rodada


def contar_acertos_exatos_por_jogo(jogos: List[Dict[str, Any]], 
                                  todos_palpites: List[Dict[str, Any]],
                                  numero_rodada: int) -> Dict[str, int]:
    """
    Conta quantos participantes acertaram o resultado exato de cada jogo.
    
    Args:
        jogos: Lista de jogos da rodada
        todos_palpites: Lista de palpites de todos os participantes
        numero_rodada: Número da rodada
        
    Returns:
        Dicionário {id_jogo: numero_acertos_exatos}
    """
    acertos_por_jogo = {}
    
    for jogo in jogos:
        id_jogo = jogo.get("id")
        if not id_jogo or jogo.get("status") != "finalizado":
            continue
        
        acertos_exatos = 0
        
        for palpites_participante in todos_palpites:
            palpites_rodada = obter_palpites_participante_rodada(palpites_participante, numero_rodada)
            
            if id_jogo in palpites_rodada:
                palpite = palpites_rodada[id_jogo]
                
                # Verificar se é resultado exato
                if (palpite.get("palpite_mandante") == jogo.get("gols_mandante") and
                    palpite.get("palpite_visitante") == jogo.get("gols_visitante")):
                    acertos_exatos += 1
        
        acertos_por_jogo[id_jogo] = acertos_exatos
    
    return acertos_por_jogo


def calcular_pontuacao_participante(participante: Dict[str, Any], 
                                   jogos: List[Dict[str, Any]],
                                   regras: Dict[str, Any],
                                   numero_rodada: int,
                                   acertos_exatos_por_jogo: Dict[str, int]) -> Dict[str, Any]:
    """
    Calcula pontuação de um participante para uma rodada.
    
    Args:
        participante: Dados de palpites do participante
        jogos: Lista de jogos da rodada
        regras: Regras de pontuação
        numero_rodada: Número da rodada
        acertos_exatos_por_jogo: Contagem de acertos exatos por jogo
        
    Returns:
        Dicionário com resultado do participante
    """
    nome_participante = participante.get("apostador", "Desconhecido")
    codigo_participante = participante.get("codigo_apostador", "")
    
    palpites_rodada = obter_palpites_participante_rodada(participante, numero_rodada)
    
    jogos_resultado = []
    total_pontos_rodada = 0.0
    jogos_participados = 0
    
    for jogo in jogos:
        id_jogo = jogo.get("id")
        if not id_jogo:
            continue
        
        # Verificar se jogo está finalizado
        if jogo.get("status") != "finalizado":
            continue
        
        # Verificar se participante tem palpite para este jogo
        if id_jogo in palpites_rodada:
            palpite = palpites_rodada[id_jogo]
            total_acertos_exatos = acertos_exatos_por_jogo.get(id_jogo, 1)
            
            pontos, codigo_regra = calcular_pontuacao(
                palpite, jogo, regras.get("regras", {}), total_acertos_exatos
            )
            
            jogos_resultado.append({
                "id": id_jogo,
                "mandante": jogo.get("mandante"),
                "visitante": jogo.get("visitante"),
                "pontos": pontos,
                "codigo_regra": codigo_regra
            })
            
            total_pontos_rodada += pontos
            jogos_participados += 1
            
        elif jogo.get("obrigatorio", False):
            # Palpite ausente em jogo obrigatório
            pontos, codigo_regra = calcular_pontuacao_palpite_ausente()
            
            jogos_resultado.append({
                "id": id_jogo,
                "mandante": jogo.get("mandante"),
                "visitante": jogo.get("visitante"),
                "pontos": pontos,
                "codigo_regra": codigo_regra
            })
            
            total_pontos_rodada += pontos
            # Não incrementa jogos_participados para palpites ausentes
    
    return {
        "participante": nome_participante,
        "codigo": codigo_participante,
        "jogos": jogos_resultado,
        "total_rodada": total_pontos_rodada,
        "jogos_participados": jogos_participados,
        "codigos_regra": [j["codigo_regra"] for j in jogos_resultado]
    }


def calcular_pontuacao_acumulada(resultados_rodada: List[Dict[str, Any]], 
                                tabela: Dict[str, Any],
                                todos_palpites: List[Dict[str, Any]],
                                regras: Dict[str, Any],
                                rodada_atual: int) -> List[Dict[str, Any]]:
    """
    Calcula pontuação acumulada até a rodada atual para todos os participantes.
    
    Args:
        resultados_rodada: Resultados da rodada atual
        tabela: Dados da tabela do campeonato
        todos_palpites: Lista de palpites de todos os participantes
        regras: Regras de pontuação
        rodada_atual: Número da rodada atual
        
    Returns:
        Lista de resultados com pontuação acumulada
    """
    # Criar mapa de participantes por nome
    participantes_map = {}
    for palpites in todos_palpites:
        nome = palpites.get("apostador")
        if nome:
            participantes_map[nome] = palpites
    
    # Calcular pontuação acumulada para cada participante
    for resultado in resultados_rodada:
        nome_participante = resultado["participante"]
        total_acumulado = resultado["total_rodada"]
        
        if nome_participante in participantes_map:
            participante = participantes_map[nome_participante]
            
            # Somar pontos de rodadas anteriores
            for rodada_num in range(1, rodada_atual):
                try:
                    jogos_rodada = obter_jogos_rodada(tabela, rodada_num)
                    acertos_exatos = contar_acertos_exatos_por_jogo(jogos_rodada, todos_palpites, rodada_num)
                    
                    resultado_rodada_anterior = calcular_pontuacao_participante(
                        participante, jogos_rodada, regras, rodada_num, acertos_exatos
                    )
                    
                    total_acumulado += resultado_rodada_anterior["total_rodada"]
                    
                except ValueError:
                    # Rodada não encontrada ou sem jogos finalizados
                    continue
        
        resultado["total_acumulado"] = total_acumulado
    
    return resultados_rodada


def gerar_classificacao_ordenada(resultados: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Gera classificação ordenada por pontuação acumulada.
    
    Args:
        resultados: Lista de resultados dos participantes
        
    Returns:
        Lista ordenada por pontuação decrescente
    """
    return sorted(resultados, key=lambda x: x.get("total_acumulado", 0), reverse=True)


def calcular_variacao_posicao_participantes(resultados: List[Dict[str, Any]], 
                                          tabela: Dict[str, Any],
                                          todos_palpites: List[Dict[str, Any]],
                                          regras: Dict[str, Any],
                                          rodada_atual: int) -> List[Dict[str, Any]]:
    """
    Calcula variação de posição de cada participante em relação à rodada anterior.
    
    Args:
        resultados: Resultados da rodada atual (já ordenados)
        tabela: Dados da tabela do campeonato
        todos_palpites: Lista de palpites de todos os participantes
        regras: Regras de pontuação
        rodada_atual: Número da rodada atual
        
    Returns:
        Lista de resultados com variação de posição
    """
    if rodada_atual <= 1:
        # Primeira rodada, não há variação
        for i, resultado in enumerate(resultados):
            resultado["posicao"] = i + 1
            resultado["variacao"] = 0
        return resultados
    
    # Calcular classificação da rodada anterior
    try:
        jogos_rodada_anterior = obter_jogos_rodada(tabela, rodada_atual - 1)
        acertos_exatos_anterior = contar_acertos_exatos_por_jogo(jogos_rodada_anterior, todos_palpites, rodada_atual - 1)
        
        resultados_anterior = []
        participantes_map = {}
        for palpites in todos_palpites:
            nome = palpites.get("apostador")
            if nome:
                participantes_map[nome] = palpites
        
        for nome, participante in participantes_map.items():
            resultado_anterior = calcular_pontuacao_participante(
                participante, jogos_rodada_anterior, regras, rodada_atual - 1, acertos_exatos_anterior
            )
            
            # Calcular acumulado até rodada anterior
            total_acumulado_anterior = resultado_anterior["total_rodada"]
            for rodada_num in range(1, rodada_atual - 1):
                try:
                    jogos_rodada_hist = obter_jogos_rodada(tabela, rodada_num)
                    acertos_exatos_hist = contar_acertos_exatos_por_jogo(jogos_rodada_hist, todos_palpites, rodada_num)
                    
                    resultado_hist = calcular_pontuacao_participante(
                        participante, jogos_rodada_hist, regras, rodada_num, acertos_exatos_hist
                    )
                    
                    total_acumulado_anterior += resultado_hist["total_rodada"]
                except ValueError:
                    continue
            
            resultado_anterior["total_acumulado"] = total_acumulado_anterior
            resultados_anterior.append(resultado_anterior)
        
        # Ordenar resultados da rodada anterior
        resultados_anterior_ordenados = sorted(resultados_anterior, 
                                             key=lambda x: x.get("total_acumulado", 0), 
                                             reverse=True)
        
        # Criar mapa de posições da rodada anterior
        posicoes_anteriores = {}
        for i, resultado in enumerate(resultados_anterior_ordenados):
            posicoes_anteriores[resultado["participante"]] = i + 1
        
        # Calcular variação para cada participante
        for i, resultado in enumerate(resultados):
            posicao_atual = i + 1
            nome_participante = resultado["participante"]
            posicao_anterior = posicoes_anteriores.get(nome_participante, posicao_atual)
            
            resultado["posicao"] = posicao_atual
            resultado["variacao"] = posicao_anterior - posicao_atual  # Positivo = subiu
        
    except ValueError:
        # Erro ao obter rodada anterior, assumir sem variação
        for i, resultado in enumerate(resultados):
            resultado["posicao"] = i + 1
            resultado["variacao"] = 0
    
    return resultados


def criar_backup_tabela(caminho_tabela: Path) -> str:
    """
    Cria backup da tabela com timestamp.
    
    Args:
        caminho_tabela: Caminho para o arquivo tabela.json
        
    Returns:
        Nome do arquivo de backup criado
        
    Raises:
        IOError: Se não conseguir criar o backup
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"tabela_backup_{timestamp}.json"
    caminho_backup = caminho_tabela.parent / nome_backup
    
    try:
        # Copiar arquivo original para backup
        with open(caminho_tabela, 'r', encoding='utf-8') as f_orig:
            conteudo = f_orig.read()
        
        with open(caminho_backup, 'w', encoding='utf-8') as f_backup:
            f_backup.write(conteudo)
        
        return nome_backup
        
    except Exception as e:
        raise IOError(f"Erro ao criar backup: {e}")


def atualizar_rodada_atual(caminho_tabela: Path, nova_rodada: int) -> None:
    """
    Atualiza o campo rodada_atual na tabela.
    
    Args:
        caminho_tabela: Caminho para o arquivo tabela.json
        nova_rodada: Número da nova rodada atual
        
    Raises:
        IOError: Se não conseguir atualizar o arquivo
    """
    try:
        # Carregar tabela atual
        with open(caminho_tabela, 'r', encoding='utf-8') as f:
            tabela = json.load(f)
        
        # Atualizar rodada atual
        tabela["rodada_atual"] = nova_rodada
        
        # Salvar tabela atualizada
        with open(caminho_tabela, 'w', encoding='utf-8') as f:
            json.dump(tabela, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        raise IOError(f"Erro ao atualizar rodada atual: {e}")


def salvar_relatorio_rodada(caminho_resultados: Path, numero_rodada: int, 
                           relatorio: str, resumo: str) -> str:
    """
    Salva relatório da rodada no diretório Resultados.
    
    Args:
        caminho_resultados: Caminho para o diretório Resultados
        numero_rodada: Número da rodada
        relatorio: Conteúdo do relatório de classificação
        resumo: Conteúdo do resumo da rodada
        
    Returns:
        Nome do arquivo de relatório criado
        
    Raises:
        IOError: Se não conseguir salvar o relatório
    """
    # Criar diretório se não existir
    caminho_resultados.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo de relatório
    nome_arquivo = f"rodada{numero_rodada:02d}.txt"
    caminho_arquivo = caminho_resultados / nome_arquivo
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conteudo_completo = f"""RELATÓRIO DA RODADA {numero_rodada}
Gerado em: {timestamp}

{relatorio}

{resumo}
"""
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_completo)
        
        return nome_arquivo
        
    except Exception as e:
        raise IOError(f"Erro ao salvar relatório: {e}")


def processar_resultados_modo_final(nome_campeonato: str, numero_rodada: int) -> bool:
    """
    Processa resultados em modo final (atualiza arquivos e gera relatório).
    
    Args:
        nome_campeonato: Nome do campeonato
        numero_rodada: Número da rodada
        
    Returns:
        True se processamento foi bem-sucedido
    """
    try:
        print(f"Processando resultados da rodada {numero_rodada} do campeonato '{nome_campeonato}' (MODO FINAL)")
        print("=" * 80)
        
        # Carregar dados
        tabela, regras, todos_palpites = carregar_dados_campeonato(nome_campeonato)
        
        # Obter jogos da rodada
        jogos = obter_jogos_rodada(tabela, numero_rodada)
        
        # Validar jogos obrigatórios finalizados
        todos_finalizados, jogos_pendentes = validar_jogos_obrigatorios_finalizados(jogos)
        if not todos_finalizados:
            print("ERRO: Nem todos os jogos obrigatórios estão finalizados:")
            for jogo in jogos_pendentes:
                print(f"  - {jogo}")
            return False
        
        # Confirmar processamento em modo final
        print("\nATENÇÃO: Modo final irá modificar arquivos permanentemente!")
        print("Operações que serão realizadas:")
        print("1. Criar backup da tabela atual")
        print("2. Atualizar rodada atual na tabela")
        print("3. Gerar e salvar relatório da rodada")
        
        resposta = input("\nDeseja continuar? (s/N): ").strip().lower()
        if resposta not in ['s', 'sim', 'y', 'yes']:
            print("Operação cancelada pelo usuário.")
            return False
        
        # Definir caminhos
        caminho_campeonato = CAMPEONATOS_DIR / nome_campeonato
        caminho_tabela = caminho_campeonato / "Tabela" / ARQUIVO_TABELA
        caminho_resultados = caminho_campeonato / "Resultados"
        
        # 1. Criar backup da tabela
        print("\n1. Criando backup da tabela...")
        nome_backup = criar_backup_tabela(caminho_tabela)
        print(f"   Backup criado: {nome_backup}")
        
        # Contar acertos exatos por jogo
        acertos_exatos_por_jogo = contar_acertos_exatos_por_jogo(jogos, todos_palpites, numero_rodada)
        
        # Calcular pontuação de cada participante
        resultados = []
        for participante in todos_palpites:
            resultado = calcular_pontuacao_participante(
                participante, jogos, regras, numero_rodada, acertos_exatos_por_jogo
            )
            resultados.append(resultado)
        
        # Calcular pontuação acumulada
        resultados = calcular_pontuacao_acumulada(resultados, tabela, todos_palpites, regras, numero_rodada)
        
        # Gerar classificação ordenada
        resultados = gerar_classificacao_ordenada(resultados)
        
        # Calcular variação de posição
        resultados = calcular_variacao_posicao_participantes(resultados, tabela, todos_palpites, regras, numero_rodada)
        
        # Gerar relatórios
        relatorio = gerar_tabela_classificacao(
            resultados, numero_rodada, nome_campeonato, 
            tabela.get("temporada"), incluir_codigos=True
        )
        resumo = gerar_resumo_rodada(resultados, numero_rodada)
        
        # 2. Atualizar rodada atual na tabela
        print("2. Atualizando rodada atual na tabela...")
        atualizar_rodada_atual(caminho_tabela, numero_rodada)
        print(f"   Rodada atual atualizada para: {numero_rodada}")
        
        # 3. Salvar relatório
        print("3. Salvando relatório da rodada...")
        nome_relatorio = salvar_relatorio_rodada(caminho_resultados, numero_rodada, relatorio, resumo)
        print(f"   Relatório salvo: {nome_relatorio}")
        
        # Exibir resultados
        print("\nRESULTADOS DA RODADA (MODO FINAL):")
        print("=" * 80)
        print(relatorio)
        print(resumo)
        
        print("MODO FINAL: Arquivos atualizados com sucesso!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"Erro ao processar resultados: {e}")
        return False


def processar_resultados_modo_teste(nome_campeonato: str, numero_rodada: int) -> bool:
    """
    Processa resultados em modo teste (apenas exibe, não modifica arquivos).
    
    Args:
        nome_campeonato: Nome do campeonato
        numero_rodada: Número da rodada
        
    Returns:
        True se processamento foi bem-sucedido
    """
    try:
        print(f"Processando resultados da rodada {numero_rodada} do campeonato '{nome_campeonato}' (MODO TESTE)")
        print("=" * 80)
        
        # Carregar dados
        tabela, regras, todos_palpites = carregar_dados_campeonato(nome_campeonato)
        
        # Obter jogos da rodada
        jogos = obter_jogos_rodada(tabela, numero_rodada)
        
        # Validar jogos obrigatórios finalizados
        todos_finalizados, jogos_pendentes = validar_jogos_obrigatorios_finalizados(jogos)
        if not todos_finalizados:
            print("ERRO: Nem todos os jogos obrigatórios estão finalizados:")
            for jogo in jogos_pendentes:
                print(f"  - {jogo}")
            return False
        
        # Contar acertos exatos por jogo
        acertos_exatos_por_jogo = contar_acertos_exatos_por_jogo(jogos, todos_palpites, numero_rodada)
        
        # Calcular pontuação de cada participante
        resultados = []
        for participante in todos_palpites:
            resultado = calcular_pontuacao_participante(
                participante, jogos, regras, numero_rodada, acertos_exatos_por_jogo
            )
            resultados.append(resultado)
        
        # Calcular pontuação acumulada
        resultados = calcular_pontuacao_acumulada(resultados, tabela, todos_palpites, regras, numero_rodada)
        
        # Gerar classificação ordenada
        resultados = gerar_classificacao_ordenada(resultados)
        
        # Calcular variação de posição
        resultados = calcular_variacao_posicao_participantes(resultados, tabela, todos_palpites, regras, numero_rodada)
        
        # Exibir resultados
        print("\nRESULTADOS DA RODADA (MODO TESTE):")
        print("=" * 80)
        
        relatorio = gerar_tabela_classificacao(
            resultados, numero_rodada, nome_campeonato, 
            tabela.get("temporada"), incluir_codigos=True
        )
        print(relatorio)
        
        # Exibir resumo
        resumo = gerar_resumo_rodada(resultados, numero_rodada)
        print(resumo)
        
        print("MODO TESTE: Nenhum arquivo foi modificado.")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"Erro ao processar resultados: {e}")
        return False


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Processa resultados de uma rodada do campeonato",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Processar rodada 1 em modo teste
  python processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --teste
  
  # Processar rodada 1 em modo final
  python processar_resultados.py --campeonato "Brasileirao-2025" --rodada 1 --final
        """
    )
    
    parser.add_argument(
        "--campeonato",
        required=True,
        help="Nome do campeonato"
    )
    
    parser.add_argument(
        "--rodada",
        type=int,
        required=True,
        help="Número da rodada a processar"
    )
    
    grupo_modo = parser.add_mutually_exclusive_group(required=True)
    grupo_modo.add_argument(
        "--teste",
        action="store_true",
        help="Modo teste (apenas exibe resultados, não modifica arquivos)"
    )
    
    grupo_modo.add_argument(
        "--final",
        action="store_true",
        help="Modo final (atualiza arquivos e gera relatório)"
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if args.rodada < 1:
        print("Erro: Número da rodada deve ser maior que 0")
        sys.exit(1)
    
    # Processar baseado no modo
    if args.teste:
        sucesso = processar_resultados_modo_teste(args.campeonato, args.rodada)
    else:
        # Modo final
        sucesso = processar_resultados_modo_final(args.campeonato, args.rodada)
    
    sys.exit(0 if sucesso else 1)


if __name__ == "__main__":
    main()