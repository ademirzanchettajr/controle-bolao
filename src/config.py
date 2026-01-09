"""
Configuração básica do Sistema de Controle de Bolão
"""

import os
from pathlib import Path

# Diretórios base
BASE_DIR = Path(__file__).parent.parent
CAMPEONATOS_DIR = BASE_DIR / "Campeonatos"

# Estrutura de diretórios padrão para campeonatos
SUBDIRS_CAMPEONATO = ["Regras", "Tabela", "Resultados", "Participantes"]

# Arquivos JSON padrão
ARQUIVO_REGRAS = "regras.json"
ARQUIVO_TABELA = "tabela.json"
ARQUIVO_PALPITES = "palpites.json"

# Configurações de validação
MAX_GOLS_POR_TIME = 20  # Limite máximo de gols por time
MIN_GOLS_POR_TIME = 0   # Limite mínimo de gols por time

# Formatos de data aceitos
FORMATOS_DATA = [
    "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%f"  # Suporte para microsegundos
]

# Configurações de pontuação padrão
REGRAS_PONTUACAO_PADRAO = {
    "resultado_exato": {
        "pontos_base": 12,
        "bonus_divisor": True,
        "descricao": "Resultado exato (placar idêntico)",
        "codigo": "AR"
    },
    "vitoria_gols_um_time": {
        "pontos": 7,
        "descricao": "Vencedor + gols de uma equipe",
        "codigo": "VG"
    },
    "vitoria_diferenca_gols": {
        "pontos": 6,
        "descricao": "Vencedor + diferença de gols",
        "codigo": "VD"
    },
    "vitoria_soma_gols": {
        "pontos": 6,
        "descricao": "Vencedor + soma total de gols",
        "codigo": "VS"
    },
    "apenas_vitoria": {
        "pontos": 5,
        "descricao": "Apenas vencedor",
        "codigo": "V"
    },
    "apenas_empate": {
        "pontos": 5,
        "descricao": "Apenas empate",
        "codigo": "E"
    },
    "gols_um_time": {
        "pontos": 2,
        "descricao": "Gols de um time (sem resultado)",
        "codigo": "G"
    },
    "soma_gols": {
        "pontos": 1,
        "descricao": "Apenas soma total de gols",
        "codigo": "S"
    },
    "resultado_inverso": {
        "pontos": -3,
        "descricao": "Resultado invertido (penalidade)",
        "codigo": "RI"
    },
    "palpite_ausente": {
        "pontos": -1,
        "descricao": "Palpite não enviado (jogo obrigatório)",
        "codigo": "PA"
    }
}

# Configurações de normalização de nomes
CARACTERES_ESPECIAIS = {
    'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
    'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
    'ç': 'c', 'ñ': 'n',
    '/': '-', '\\': '-', '_': '-'
}

# Configurações de parsing de texto
MARCADORES_RODADA = [
    r'(\d+)[ªº°]?\s*rodada',
    r'rodada\s*(\d+)',
    r'r(\d+)',
    r'round\s*(\d+)'
]

MARCADORES_APOSTADOR = [
    r'apostador:\s*(.+)',
    r'nome:\s*(.+)',
    r'participante:\s*(.+)'
]

MARCADORES_APOSTA_EXTRA = [
    'aposta extra',
    'extra',
    'jogo extra',
    'adicional'
]

# Formatos de placar aceitos
FORMATOS_PLACAR = [
    r'(.+?)\s+(\d+)\s*x\s*(\d+)\s+(.+)',      # "Time1 2x1 Time2"
    r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)',      # "Time1 2-1 Time2"
    r'(.+?)\s+(\d+)\s*:\s*(\d+)\s+(.+)',      # "Time1 2:1 Time2"
    r'(.+?)\s*\(\s*(\d+)\s*\)\s*x\s*\(\s*(\d+)\s*\)\s*(.+)'  # "Time1 (2) x (1) Time2"
]

# Configurações de relatórios
FORMATO_RELATORIO_RODADA = "rodada{:02d}.txt"
FORMATO_BACKUP_TABELA = "tabela_{timestamp}.json"