"""
Módulo de validação de dados para o Sistema de Controle de Bolão

Este módulo contém funções para validar estruturas de dados JSON,
campos obrigatórios, formatos de data, placares e referências entre arquivos.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

# Import config with fallback for testing
try:
    from ..config import (
        FORMATOS_DATA, 
        MAX_GOLS_POR_TIME, 
        MIN_GOLS_POR_TIME,
        CAMPEONATOS_DIR
    )
except ImportError:
    # Fallback for direct testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config import (
        FORMATOS_DATA, 
        MAX_GOLS_POR_TIME, 
        MIN_GOLS_POR_TIME,
        CAMPEONATOS_DIR
    )


def validar_estrutura_tabela(dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida estrutura do arquivo tabela.json
    
    Args:
        dados: Dicionário com dados da tabela
        
    Returns:
        Tupla (sucesso, lista_de_erros)
    """
    erros = []
    
    # Campos obrigatórios no nível raiz
    campos_obrigatorios = [
        "campeonato", "temporada", "rodada_atual", 
        "data_atualizacao", "codigo_campeonato", "rodadas"
    ]
    
    for campo in campos_obrigatorios:
        if campo not in dados:
            erros.append(f"Campo obrigatório '{campo}' ausente na estrutura da tabela")
    
    # Validar tipos dos campos
    if "campeonato" in dados and not isinstance(dados["campeonato"], str):
        erros.append("Campo 'campeonato' deve ser uma string")
    
    if "temporada" in dados and not isinstance(dados["temporada"], str):
        erros.append("Campo 'temporada' deve ser uma string")
    
    if "rodada_atual" in dados and not isinstance(dados["rodada_atual"], int):
        erros.append("Campo 'rodada_atual' deve ser um número inteiro")
    
    if "codigo_campeonato" in dados and not isinstance(dados["codigo_campeonato"], str):
        erros.append("Campo 'codigo_campeonato' deve ser uma string")
    
    # Validar data de atualização
    if "data_atualizacao" in dados:
        valido, erro_data = validar_data(dados["data_atualizacao"])
        if not valido:
            erros.append(f"Campo 'data_atualizacao' inválido: {erro_data}")
    
    # Validar estrutura das rodadas
    if "rodadas" in dados:
        if not isinstance(dados["rodadas"], list):
            erros.append("Campo 'rodadas' deve ser uma lista")
        else:
            for i, rodada in enumerate(dados["rodadas"]):
                erros_rodada = _validar_estrutura_rodada(rodada, i + 1)
                erros.extend(erros_rodada)
    
    return len(erros) == 0, erros


def _validar_estrutura_rodada(rodada: Dict[str, Any], numero_rodada: int) -> List[str]:
    """
    Valida estrutura de uma rodada específica
    
    Args:
        rodada: Dicionário com dados da rodada
        numero_rodada: Número da rodada para mensagens de erro
        
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Campos obrigatórios da rodada
    campos_obrigatorios = ["numero", "jogos"]
    
    for campo in campos_obrigatorios:
        if campo not in rodada:
            erros.append(f"Campo obrigatório '{campo}' ausente na rodada {numero_rodada}")
    
    # Validar número da rodada
    if "numero" in rodada and not isinstance(rodada["numero"], int):
        erros.append(f"Campo 'numero' da rodada {numero_rodada} deve ser um inteiro")
    
    # Validar datas opcionais
    for campo_data in ["data_inicial", "data_final"]:
        if campo_data in rodada:
            valido, erro_data = validar_data(rodada[campo_data])
            if not valido:
                erros.append(f"Campo '{campo_data}' da rodada {numero_rodada} inválido: {erro_data}")
    
    # Validar jogos
    if "jogos" in rodada:
        if not isinstance(rodada["jogos"], list):
            erros.append(f"Campo 'jogos' da rodada {numero_rodada} deve ser uma lista")
        else:
            for j, jogo in enumerate(rodada["jogos"]):
                erros_jogo = _validar_estrutura_jogo(jogo, numero_rodada, j + 1)
                erros.extend(erros_jogo)
    
    return erros


def _validar_estrutura_jogo(jogo: Dict[str, Any], numero_rodada: int, numero_jogo: int) -> List[str]:
    """
    Valida estrutura de um jogo específico
    
    Args:
        jogo: Dicionário com dados do jogo
        numero_rodada: Número da rodada
        numero_jogo: Número do jogo na rodada
        
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Campos obrigatórios do jogo
    campos_obrigatorios = [
        "id", "mandante", "visitante", "data", "local",
        "gols_mandante", "gols_visitante", "status", "obrigatorio"
    ]
    
    for campo in campos_obrigatorios:
        if campo not in jogo:
            erros.append(f"Campo obrigatório '{campo}' ausente no jogo {numero_jogo} da rodada {numero_rodada}")
    
    # Validar ID do jogo
    if "id" in jogo:
        if not isinstance(jogo["id"], str):
            erros.append(f"Campo 'id' do jogo {numero_jogo} da rodada {numero_rodada} deve ser uma string")
        elif not jogo["id"].startswith("jogo-"):
            erros.append(f"ID do jogo {numero_jogo} da rodada {numero_rodada} deve começar com 'jogo-'")
    
    # Validar nomes dos times
    for campo_time in ["mandante", "visitante"]:
        if campo_time in jogo and not isinstance(jogo[campo_time], str):
            erros.append(f"Campo '{campo_time}' do jogo {numero_jogo} da rodada {numero_rodada} deve ser uma string")
    
    # Validar data do jogo
    if "data" in jogo:
        valido, erro_data = validar_data(jogo["data"])
        if not valido:
            erros.append(f"Data do jogo {numero_jogo} da rodada {numero_rodada} inválida: {erro_data}")
    
    # Validar local
    if "local" in jogo and not isinstance(jogo["local"], str):
        erros.append(f"Campo 'local' do jogo {numero_jogo} da rodada {numero_rodada} deve ser uma string")
    
    # Validar placares
    if "gols_mandante" in jogo and "gols_visitante" in jogo:
        valido, erro_placar = validar_placar(jogo["gols_mandante"], jogo["gols_visitante"])
        if not valido:
            erros.append(f"Placar do jogo {numero_jogo} da rodada {numero_rodada} inválido: {erro_placar}")
    
    # Validar status
    if "status" in jogo:
        if not isinstance(jogo["status"], str):
            erros.append(f"Campo 'status' do jogo {numero_jogo} da rodada {numero_rodada} deve ser uma string")
        elif jogo["status"] not in ["agendado", "finalizado"]:
            erros.append(f"Status do jogo {numero_jogo} da rodada {numero_rodada} deve ser 'agendado' ou 'finalizado'")
    
    # Validar campo obrigatório
    if "obrigatorio" in jogo and not isinstance(jogo["obrigatorio"], bool):
        erros.append(f"Campo 'obrigatorio' do jogo {numero_jogo} da rodada {numero_rodada} deve ser um booleano")
    
    return erros


def validar_estrutura_palpites(dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida estrutura do arquivo palpites.json
    
    Args:
        dados: Dicionário com dados dos palpites
        
    Returns:
        Tupla (sucesso, lista_de_erros)
    """
    erros = []
    
    # Campos obrigatórios no nível raiz
    campos_obrigatorios = [
        "apostador", "codigo_apostador", "campeonato", "temporada", "palpites"
    ]
    
    for campo in campos_obrigatorios:
        if campo not in dados:
            erros.append(f"Campo obrigatório '{campo}' ausente na estrutura de palpites")
    
    # Validar tipos dos campos
    if "apostador" in dados and not isinstance(dados["apostador"], str):
        erros.append("Campo 'apostador' deve ser uma string")
    
    if "codigo_apostador" in dados and not isinstance(dados["codigo_apostador"], str):
        erros.append("Campo 'codigo_apostador' deve ser uma string")
    
    if "campeonato" in dados and not isinstance(dados["campeonato"], str):
        erros.append("Campo 'campeonato' deve ser uma string")
    
    if "temporada" in dados and not isinstance(dados["temporada"], str):
        erros.append("Campo 'temporada' deve ser uma string")
    
    # Validar estrutura dos palpites
    if "palpites" in dados:
        if not isinstance(dados["palpites"], list):
            erros.append("Campo 'palpites' deve ser uma lista")
        else:
            for i, palpite_rodada in enumerate(dados["palpites"]):
                erros_palpite = _validar_estrutura_palpite_rodada(palpite_rodada, i + 1)
                erros.extend(erros_palpite)
    
    return len(erros) == 0, erros


def _validar_estrutura_palpite_rodada(palpite_rodada: Dict[str, Any], indice: int) -> List[str]:
    """
    Valida estrutura de palpites de uma rodada específica
    
    Args:
        palpite_rodada: Dicionário com palpites da rodada
        indice: Índice da rodada para mensagens de erro
        
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Campos obrigatórios da rodada de palpites
    campos_obrigatorios = ["rodada", "data_palpite", "jogos"]
    
    for campo in campos_obrigatorios:
        if campo not in palpite_rodada:
            erros.append(f"Campo obrigatório '{campo}' ausente na rodada de palpites {indice}")
    
    # Validar número da rodada
    if "rodada" in palpite_rodada and not isinstance(palpite_rodada["rodada"], int):
        erros.append(f"Campo 'rodada' do palpite {indice} deve ser um inteiro")
    
    # Validar data do palpite
    if "data_palpite" in palpite_rodada:
        valido, erro_data = validar_data(palpite_rodada["data_palpite"])
        if not valido:
            erros.append(f"Data do palpite da rodada {indice} inválida: {erro_data}")
    
    # Validar jogos
    if "jogos" in palpite_rodada:
        if not isinstance(palpite_rodada["jogos"], list):
            erros.append(f"Campo 'jogos' da rodada de palpites {indice} deve ser uma lista")
        else:
            for j, jogo_palpite in enumerate(palpite_rodada["jogos"]):
                erros_jogo = _validar_estrutura_jogo_palpite(jogo_palpite, indice, j + 1)
                erros.extend(erros_jogo)
    
    return erros


def _validar_estrutura_jogo_palpite(jogo_palpite: Dict[str, Any], rodada: int, jogo: int) -> List[str]:
    """
    Valida estrutura de um palpite de jogo específico
    
    Args:
        jogo_palpite: Dicionário com palpite do jogo
        rodada: Número da rodada
        jogo: Número do jogo
        
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Campos obrigatórios do palpite de jogo
    campos_obrigatorios = [
        "id", "mandante", "visitante", "palpite_mandante", "palpite_visitante"
    ]
    
    for campo in campos_obrigatorios:
        if campo not in jogo_palpite:
            erros.append(f"Campo obrigatório '{campo}' ausente no palpite do jogo {jogo} da rodada {rodada}")
    
    # Validar ID do jogo
    if "id" in jogo_palpite:
        if not isinstance(jogo_palpite["id"], str):
            erros.append(f"Campo 'id' do palpite do jogo {jogo} da rodada {rodada} deve ser uma string")
        elif not jogo_palpite["id"].startswith("jogo-"):
            erros.append(f"ID do palpite do jogo {jogo} da rodada {rodada} deve começar com 'jogo-'")
    
    # Validar nomes dos times
    for campo_time in ["mandante", "visitante"]:
        if campo_time in jogo_palpite and not isinstance(jogo_palpite[campo_time], str):
            erros.append(f"Campo '{campo_time}' do palpite do jogo {jogo} da rodada {rodada} deve ser uma string")
    
    # Validar palpites
    if "palpite_mandante" in jogo_palpite and "palpite_visitante" in jogo_palpite:
        valido, erro_placar = validar_placar(jogo_palpite["palpite_mandante"], jogo_palpite["palpite_visitante"])
        if not valido:
            erros.append(f"Palpite do jogo {jogo} da rodada {rodada} inválido: {erro_placar}")
    
    return erros


def validar_estrutura_regras(dados: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida estrutura do arquivo regras.json
    
    Args:
        dados: Dicionário com dados das regras
        
    Returns:
        Tupla (sucesso, lista_de_erros)
    """
    erros = []
    
    # Campos obrigatórios no nível raiz
    campos_obrigatorios = ["campeonato", "temporada", "versao", "regras"]
    
    for campo in campos_obrigatorios:
        if campo not in dados:
            erros.append(f"Campo obrigatório '{campo}' ausente na estrutura de regras")
    
    # Validar tipos dos campos
    if "campeonato" in dados and not isinstance(dados["campeonato"], str):
        erros.append("Campo 'campeonato' deve ser uma string")
    
    if "temporada" in dados and not isinstance(dados["temporada"], str):
        erros.append("Campo 'temporada' deve ser uma string")
    
    if "versao" in dados and not isinstance(dados["versao"], str):
        erros.append("Campo 'versao' deve ser uma string")
    
    # Validar data de criação (opcional)
    if "data_criacao" in dados:
        valido, erro_data = validar_data(dados["data_criacao"])
        if not valido:
            erros.append(f"Campo 'data_criacao' inválido: {erro_data}")
    
    # Validar estrutura das regras
    if "regras" in dados:
        if not isinstance(dados["regras"], dict):
            erros.append("Campo 'regras' deve ser um dicionário")
        else:
            erros_regras = _validar_estrutura_regras_pontuacao(dados["regras"])
            erros.extend(erros_regras)
    
    # Validar observações (opcional)
    if "observacoes" in dados:
        if not isinstance(dados["observacoes"], list):
            erros.append("Campo 'observacoes' deve ser uma lista")
        else:
            for i, obs in enumerate(dados["observacoes"]):
                if not isinstance(obs, str):
                    erros.append(f"Observação {i + 1} deve ser uma string")
    
    return len(erros) == 0, erros


def _validar_estrutura_regras_pontuacao(regras: Dict[str, Any]) -> List[str]:
    """
    Valida estrutura das regras de pontuação
    
    Args:
        regras: Dicionário com regras de pontuação
        
    Returns:
        Lista de erros encontrados
    """
    erros = []
    
    # Regras esperadas (pelo menos algumas devem estar presentes)
    regras_esperadas = [
        "resultado_exato", "vitoria_gols_um_time", "vitoria_diferenca_gols",
        "vitoria_soma_gols", "apenas_vitoria", "apenas_empate",
        "gols_um_time", "soma_gols", "resultado_inverso", "palpite_ausente"
    ]
    
    if len(regras) == 0:
        erros.append("Nenhuma regra de pontuação definida")
        return erros
    
    # Validar cada regra
    for nome_regra, regra in regras.items():
        if not isinstance(regra, dict):
            erros.append(f"Regra '{nome_regra}' deve ser um dicionário")
            continue
        
        # Campos obrigatórios para cada regra
        campos_obrigatorios = ["descricao", "codigo"]
        
        # Verificar se tem pontos ou pontos_base
        if "pontos" not in regra and "pontos_base" not in regra:
            erros.append(f"Regra '{nome_regra}' deve ter campo 'pontos' ou 'pontos_base'")
        
        for campo in campos_obrigatorios:
            if campo not in regra:
                erros.append(f"Campo obrigatório '{campo}' ausente na regra '{nome_regra}'")
        
        # Validar tipos
        if "pontos" in regra and not isinstance(regra["pontos"], (int, float)):
            erros.append(f"Campo 'pontos' da regra '{nome_regra}' deve ser um número")
        
        if "pontos_base" in regra and not isinstance(regra["pontos_base"], (int, float)):
            erros.append(f"Campo 'pontos_base' da regra '{nome_regra}' deve ser um número")
        
        if "descricao" in regra and not isinstance(regra["descricao"], str):
            erros.append(f"Campo 'descricao' da regra '{nome_regra}' deve ser uma string")
        
        if "codigo" in regra and not isinstance(regra["codigo"], str):
            erros.append(f"Campo 'codigo' da regra '{nome_regra}' deve ser uma string")
        
        # Validar campos específicos
        if "bonus_divisor" in regra and not isinstance(regra["bonus_divisor"], bool):
            erros.append(f"Campo 'bonus_divisor' da regra '{nome_regra}' deve ser um booleano")
    
    return erros


def validar_placar(gols_mandante: Any, gols_visitante: Any) -> Tuple[bool, str]:
    """
    Valida que placar contém inteiros não-negativos
    
    Args:
        gols_mandante: Gols do time mandante
        gols_visitante: Gols do time visitante
        
    Returns:
        Tupla (sucesso, mensagem_de_erro)
    """
    # Verificar se são números inteiros
    if not isinstance(gols_mandante, int):
        return False, f"Gols do mandante deve ser um número inteiro, recebido: {type(gols_mandante).__name__}"
    
    if not isinstance(gols_visitante, int):
        return False, f"Gols do visitante deve ser um número inteiro, recebido: {type(gols_visitante).__name__}"
    
    # Verificar se são não-negativos
    if gols_mandante < MIN_GOLS_POR_TIME:
        return False, f"Gols do mandante não pode ser negativo: {gols_mandante}"
    
    if gols_visitante < MIN_GOLS_POR_TIME:
        return False, f"Gols do visitante não pode ser negativo: {gols_visitante}"
    
    # Verificar se não excedem o máximo
    if gols_mandante > MAX_GOLS_POR_TIME:
        return False, f"Gols do mandante excede o máximo permitido ({MAX_GOLS_POR_TIME}): {gols_mandante}"
    
    if gols_visitante > MAX_GOLS_POR_TIME:
        return False, f"Gols do visitante excede o máximo permitido ({MAX_GOLS_POR_TIME}): {gols_visitante}"
    
    return True, ""


def validar_data(data_str: str) -> Tuple[bool, str]:
    """
    Valida que string está em formato de data válido
    
    Args:
        data_str: String com data para validar
        
    Returns:
        Tupla (sucesso, mensagem_de_erro)
    """
    if not isinstance(data_str, str):
        return False, f"Data deve ser uma string, recebido: {type(data_str).__name__}"
    
    if not data_str.strip():
        return False, "Data não pode estar vazia"
    
    # Tentar cada formato de data configurado
    for formato in FORMATOS_DATA:
        try:
            datetime.strptime(data_str, formato)
            return True, ""
        except ValueError:
            continue
    
    # Se chegou aqui, nenhum formato funcionou
    formatos_str = ", ".join(FORMATOS_DATA)
    return False, f"Data '{data_str}' não está em formato válido. Formatos aceitos: {formatos_str}"


def validar_id_jogo(id_jogo: str, tabela: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Valida que ID de jogo existe na tabela do campeonato
    
    Args:
        id_jogo: ID do jogo para validar
        tabela: Dicionário com dados da tabela
        
    Returns:
        Tupla (sucesso, mensagem_de_erro)
    """
    if not isinstance(id_jogo, str):
        return False, f"ID do jogo deve ser uma string, recebido: {type(id_jogo).__name__}"
    
    if not id_jogo.strip():
        return False, "ID do jogo não pode estar vazio"
    
    # Verificar se a tabela tem estrutura válida
    if "rodadas" not in tabela:
        return False, "Tabela não contém campo 'rodadas'"
    
    if not isinstance(tabela["rodadas"], list):
        return False, "Campo 'rodadas' da tabela deve ser uma lista"
    
    # Procurar o ID em todas as rodadas
    for rodada in tabela["rodadas"]:
        if "jogos" not in rodada or not isinstance(rodada["jogos"], list):
            continue
        
        for jogo in rodada["jogos"]:
            if isinstance(jogo, dict) and jogo.get("id") == id_jogo:
                return True, ""
    
    return False, f"ID do jogo '{id_jogo}' não encontrado na tabela do campeonato"


def validar_participante(nome_participante: str, campeonato: str) -> Tuple[bool, str]:
    """
    Valida que participante está registrado no campeonato
    
    Args:
        nome_participante: Nome do participante para validar
        campeonato: Nome do campeonato
        
    Returns:
        Tupla (sucesso, mensagem_de_erro)
    """
    if not isinstance(nome_participante, str):
        return False, f"Nome do participante deve ser uma string, recebido: {type(nome_participante).__name__}"
    
    if not nome_participante.strip():
        return False, "Nome do participante não pode estar vazio"
    
    if not isinstance(campeonato, str):
        return False, f"Nome do campeonato deve ser uma string, recebido: {type(campeonato).__name__}"
    
    if not campeonato.strip():
        return False, "Nome do campeonato não pode estar vazio"
    
    # Construir caminho para o diretório do campeonato
    caminho_campeonato = CAMPEONATOS_DIR / campeonato
    
    if not caminho_campeonato.exists():
        return False, f"Campeonato '{campeonato}' não encontrado"
    
    # Construir caminho para o diretório de participantes
    caminho_participantes = caminho_campeonato / "Participantes"
    
    if not caminho_participantes.exists():
        return False, f"Diretório de participantes não encontrado no campeonato '{campeonato}'"
    
    # Procurar diretório do participante (pode ter nome normalizado)
    try:
        from .normalizacao import normalizar_nome_participante
    except ImportError:
        # Fallback for direct testing
        from normalizacao import normalizar_nome_participante
    
    nome_normalizado = normalizar_nome_participante(nome_participante)
    caminho_participante = caminho_participantes / nome_normalizado
    
    if caminho_participante.exists():
        return True, ""
    
    # Se não encontrou com nome normalizado, listar participantes disponíveis
    try:
        participantes_existentes = [p.name for p in caminho_participantes.iterdir() if p.is_dir()]
        if participantes_existentes:
            participantes_str = ", ".join(participantes_existentes)
            return False, f"Participante '{nome_participante}' (normalizado: '{nome_normalizado}') não encontrado. Participantes registrados: {participantes_str}"
        else:
            return False, f"Nenhum participante registrado no campeonato '{campeonato}'"
    except Exception as e:
        return False, f"Erro ao verificar participantes do campeonato '{campeonato}': {str(e)}"