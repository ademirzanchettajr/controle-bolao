"""
Módulo de normalização de nomes para o Sistema de Controle de Bolão.

Este módulo fornece funções para normalizar nomes de times, participantes e campeonatos,
garantindo consistência nos dados e facilitando a correspondência entre variações
de escrita do mesmo nome.
"""

import re
import unicodedata
from typing import Optional, List
from Levenshtein import distance


def normalizar_nome_time(nome: str) -> str:
    """
    Normaliza nome de time para formato padrão.
    
    Remove acentos, converte barras/hífens para formato consistente,
    normaliza case e remove espaços extras.
    
    Args:
        nome: Nome do time a ser normalizado
        
    Returns:
        Nome normalizado em lowercase, sem acentos, com hífens ao invés de barras
        
    Examples:
        >>> normalizar_nome_time("Atlético/MG")
        'atletico-mg'
        >>> normalizar_nome_time("São Paulo")
        'sao-paulo'
        >>> normalizar_nome_time("  Flamengo  ")
        'flamengo'
    """
    if not nome or not isinstance(nome, str):
        return ""
    
    # Remove espaços extras no início e fim
    nome = nome.strip()
    
    # Remove acentos
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(char for char in nome if unicodedata.category(char) != 'Mn')
    
    # Converte para lowercase
    nome = nome.lower()
    
    # Converte barras para hífens
    nome = nome.replace('/', '-')
    
    # Normaliza espaços múltiplos para um único espaço
    nome = re.sub(r'\s+', ' ', nome)
    
    # Substitui espaços por hífens
    nome = nome.replace(' ', '-')
    
    # Remove caracteres especiais exceto hífens
    nome = re.sub(r'[^a-z0-9\-]', '', nome)
    
    # Remove hífens múltiplos
    nome = re.sub(r'-+', '-', nome)
    
    # Remove hífens no início e fim
    nome = nome.strip('-')
    
    return nome


def normalizar_nome_participante(nome: str) -> str:
    """
    Normaliza nome de participante para formato de diretório.
    
    Remove espaços e caracteres especiais, mantendo apenas letras e números.
    
    Args:
        nome: Nome do participante a ser normalizado
        
    Returns:
        Nome normalizado para uso como nome de diretório
        
    Examples:
        >>> normalizar_nome_participante("Mario Silva")
        'MarioSilva'
        >>> normalizar_nome_participante("João da Silva Jr.")
        'JoaodaSilvaJr'
        >>> normalizar_nome_participante("Ana-Paula")
        'AnaPaula'
    """
    if not nome or not isinstance(nome, str):
        return ""
    
    # Remove espaços extras no início e fim
    nome = nome.strip()
    
    # Remove acentos
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(char for char in nome if unicodedata.category(char) != 'Mn')
    
    # Remove espaços e caracteres especiais, mantendo apenas letras e números
    nome = re.sub(r'[^a-zA-Z0-9]', '', nome)
    
    # Capitaliza primeira letra de cada palavra original (aproximação)
    # Como removemos espaços, vamos tentar manter o padrão CamelCase
    return nome


def normalizar_nome_campeonato(nome: str) -> str:
    """
    Normaliza nome de campeonato para formato de diretório.
    
    Remove ou substitui caracteres problemáticos, mantendo legibilidade.
    
    Args:
        nome: Nome do campeonato a ser normalizado
        
    Returns:
        Nome normalizado para uso como nome de diretório
        
    Examples:
        >>> normalizar_nome_campeonato("Brasileirão 2025")
        'Brasileirao-2025'
        >>> normalizar_nome_campeonato("Copa do Brasil/2025")
        'Copa-do-Brasil-2025'
        >>> normalizar_nome_campeonato("Campeonato Paulista: Série A1")
        'Campeonato-Paulista-Serie-A1'
    """
    if not nome or not isinstance(nome, str):
        return ""
    
    # Remove espaços extras no início e fim
    nome = nome.strip()
    
    # Remove acentos
    nome = unicodedata.normalize('NFD', nome)
    nome = ''.join(char for char in nome if unicodedata.category(char) != 'Mn')
    
    # Substitui caracteres problemáticos por hífens
    nome = re.sub(r'[/\\:*?"<>|]', '-', nome)
    
    # Normaliza espaços múltiplos para um único espaço
    nome = re.sub(r'\s+', ' ', nome)
    
    # Substitui espaços por hífens
    nome = nome.replace(' ', '-')
    
    # Remove caracteres especiais exceto hífens e números
    nome = re.sub(r'[^a-zA-Z0-9\-]', '', nome)
    
    # Remove hífens múltiplos
    nome = re.sub(r'-+', '-', nome)
    
    # Remove hífens no início e fim
    nome = nome.strip('-')
    
    return nome


def encontrar_time_similar(nome: str, times_validos: List[str], limite_distancia: int = 3) -> Optional[str]:
    """
    Encontra time similar usando distância de Levenshtein.
    
    Procura por times com nomes similares na lista de times válidos,
    usando distância de edição para encontrar correspondências aproximadas.
    
    Args:
        nome: Nome do time a ser procurado
        times_validos: Lista de nomes de times válidos
        limite_distancia: Distância máxima permitida (padrão: 3)
        
    Returns:
        Nome do time mais similar encontrado, ou None se nenhum for suficientemente similar
        
    Examples:
        >>> times = ["Flamengo", "Palmeiras", "São Paulo"]
        >>> encontrar_time_similar("Flamego", times)
        'Flamengo'
        >>> encontrar_time_similar("Palmerias", times)
        'Palmeiras'
        >>> encontrar_time_similar("XYZ", times)
        None
    """
    if not nome or not isinstance(nome, str) or not times_validos:
        return None
    
    # Normaliza o nome de entrada
    nome_normalizado = normalizar_nome_time(nome)
    
    melhor_match = None
    menor_distancia = float('inf')
    
    for time_valido in times_validos:
        # Normaliza o time válido para comparação
        time_normalizado = normalizar_nome_time(time_valido)
        
        # Calcula distância de Levenshtein
        dist = distance(nome_normalizado, time_normalizado)
        
        # Se encontrou correspondência exata, retorna imediatamente
        if dist == 0:
            return time_valido
        
        # Se está dentro do limite e é melhor que o anterior
        if dist <= limite_distancia and dist < menor_distancia:
            menor_distancia = dist
            melhor_match = time_valido
    
    return melhor_match


def _preservar_case_original(nome_original: str, nome_normalizado: str) -> str:
    """
    Função auxiliar para preservar o case original quando possível.
    
    Args:
        nome_original: Nome original com case preservado
        nome_normalizado: Nome já normalizado
        
    Returns:
        Nome com case preservado quando possível
    """
    # Esta é uma implementação simplificada
    # Em casos mais complexos, poderia tentar mapear caracteres individuais
    return nome_original if nome_original.lower().replace(' ', '-') == nome_normalizado else nome_normalizado