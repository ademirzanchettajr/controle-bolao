"""
Utilitários para normalização, validação e processamento de dados
"""

from .normalizacao import (
    normalizar_nome_time,
    normalizar_nome_participante,
    normalizar_nome_campeonato,
    encontrar_time_similar
)

from .validacao import (
    validar_estrutura_tabela,
    validar_estrutura_palpites,
    validar_estrutura_regras,
    validar_placar,
    validar_data,
    validar_id_jogo,
    validar_participante
)

from .pontuacao import (
    verificar_resultado_exato,
    verificar_vitoria_gols_um_time,
    verificar_vitoria_diferenca_gols,
    verificar_vitoria_soma_gols,
    verificar_apenas_vitoria,
    verificar_apenas_empate,
    verificar_gols_um_time,
    verificar_soma_gols,
    verificar_resultado_inverso,
    calcular_pontuacao,
    calcular_bonus_resultado_exato,
    calcular_pontuacao_palpite_ausente
)

from .relatorio import (
    gerar_tabela_classificacao,
    calcular_variacao_posicao,
    formatar_linha_participante,
    gerar_cabecalho_relatorio,
    gerar_resumo_rodada
)

__all__ = [
    'normalizar_nome_time',
    'normalizar_nome_participante', 
    'normalizar_nome_campeonato',
    'encontrar_time_similar',
    'validar_estrutura_tabela',
    'validar_estrutura_palpites',
    'validar_estrutura_regras',
    'validar_placar',
    'validar_data',
    'validar_id_jogo',
    'validar_participante',
    'verificar_resultado_exato',
    'verificar_vitoria_gols_um_time',
    'verificar_vitoria_diferenca_gols',
    'verificar_vitoria_soma_gols',
    'verificar_apenas_vitoria',
    'verificar_apenas_empate',
    'verificar_gols_um_time',
    'verificar_soma_gols',
    'verificar_resultado_inverso',
    'calcular_pontuacao',
    'calcular_bonus_resultado_exato',
    'calcular_pontuacao_palpite_ausente',
    'gerar_tabela_classificacao',
    'calcular_variacao_posicao',
    'formatar_linha_participante',
    'gerar_cabecalho_relatorio',
    'gerar_resumo_rodada'
]