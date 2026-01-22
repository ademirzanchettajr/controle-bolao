"""
Módulo de geração de relatórios para o sistema de bolão.

Este módulo contém funções para formatar tabelas de classificação,
calcular variações de posição e gerar relatórios de rodadas.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime


def gerar_cabecalho_relatorio(campeonato: str, rodada: int, temporada: str = None) -> str:
    """
    Gera cabeçalho formatado para relatório de rodada.
    
    Args:
        campeonato: Nome do campeonato
        rodada: Número da rodada
        temporada: Ano da temporada (opcional)
    
    Returns:
        String formatada com cabeçalho do relatório
    """
    data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    linhas = []
    linhas.append("=" * 80)
    linhas.append(f"RELATÓRIO DE CLASSIFICAÇÃO - RODADA {rodada:02d}")
    linhas.append("=" * 80)
    linhas.append(f"Campeonato: {campeonato}")
    
    if temporada:
        linhas.append(f"Temporada: {temporada}")
    
    linhas.append(f"Gerado em: {data_atual}")
    linhas.append("=" * 80)
    linhas.append("")
    
    return "\n".join(linhas)


def calcular_variacao_posicao(participante: str, posicao_atual: int, 
                             historico_posicoes: Dict[str, Dict[int, int]]) -> int:
    """
    Calcula variação de posição de um participante em relação à rodada anterior.
    
    Args:
        participante: Nome do participante
        posicao_atual: Posição atual do participante
        historico_posicoes: Dicionário com histórico de posições por rodada
                           Formato: {participante: {rodada: posicao}}
    
    Returns:
        Variação de posição (positivo = subiu, negativo = desceu, 0 = manteve)
    """
    if participante not in historico_posicoes:
        return 0
    
    posicoes_participante = historico_posicoes[participante]
    
    if not posicoes_participante:
        return 0
    
    # Encontra a rodada anterior mais recente
    rodadas_anteriores = [r for r in posicoes_participante.keys() if r < max(posicoes_participante.keys())]
    
    if not rodadas_anteriores:
        return 0
    
    rodada_anterior = max(rodadas_anteriores)
    posicao_anterior = posicoes_participante[rodada_anterior]
    
    # Variação é negativa quando sobe (posição menor é melhor)
    return posicao_anterior - posicao_atual


def formatar_linha_participante(posicao: int, participante: str, pontos_rodada: float,
                               pontos_acumulados: float, variacao: int,
                               codigos_acerto: List[str] = None,
                               jogos_participados: int = None) -> str:
    """
    Formata linha individual de um participante na tabela de classificação.
    
    Args:
        posicao: Posição na classificação
        participante: Nome do participante
        pontos_rodada: Pontos obtidos na rodada
        pontos_acumulados: Pontos acumulados total
        variacao: Variação de posição (+2, -1, 0, etc.)
        codigos_acerto: Lista de códigos de acerto por jogo (opcional)
        jogos_participados: Número de jogos com palpite (opcional)
    
    Returns:
        String formatada com linha do participante
    """
    # Formatar variação de posição
    if variacao > 0:
        var_str = f"↑{variacao}"
    elif variacao < 0:
        var_str = f"↓{abs(variacao)}"
    else:
        var_str = "="
    
    # Formatar códigos de acerto
    codigos_str = ""
    if codigos_acerto:
        codigos_str = " ".join(codigos_acerto)
    
    # Linha básica com posição, nome, pontos e variação
    linha = f"{posicao:2d}º {participante:<20} {pontos_rodada:5.1f} {pontos_acumulados:6.1f} {var_str:>4}"
    
    # Adicionar códigos de acerto se fornecidos
    if codigos_str:
        linha += f" | {codigos_str}"
    
    # Adicionar número de jogos se fornecido
    if jogos_participados is not None:
        linha += f" ({jogos_participados} jogos)"
    
    return linha


def gerar_tabela_classificacao(resultados: List[Dict[str, Any]], rodada: int,
                              campeonato: str = None, temporada: str = None,
                              incluir_codigos: bool = True,
                              historico_posicoes: Dict[str, Dict[int, int]] = None) -> str:
    """
    Gera tabela completa de classificação formatada.
    
    Args:
        resultados: Lista de dicionários com dados dos participantes
                   Cada item deve conter: participante, total_rodada, total_acumulado
                   Opcionalmente: codigos_regra, jogos_participados, variacao
        rodada: Número da rodada
        campeonato: Nome do campeonato (opcional)
        temporada: Ano da temporada (opcional)
        incluir_codigos: Se deve incluir códigos de acerto na tabela
        historico_posicoes: Histórico de posições para calcular variação (opcional)
    
    Returns:
        String com tabela completa formatada
    """
    if not resultados:
        return "Nenhum resultado encontrado para esta rodada."
    
    # Ordenar resultados por pontuação acumulada (decrescente)
    resultados_ordenados = sorted(resultados, 
                                 key=lambda x: x.get('total_acumulado', 0), 
                                 reverse=True)
    
    linhas = []
    
    # Adicionar cabeçalho se informações fornecidas
    if campeonato:
        linhas.append(gerar_cabecalho_relatorio(campeonato, rodada, temporada))
    
    # Cabeçalho da tabela
    cabecalho = "Pos Nome                 Rodada  Total Var"
    if incluir_codigos:
        cabecalho += " | Códigos de Acerto"
    
    linhas.append(cabecalho)
    linhas.append("-" * len(cabecalho))
    
    # Processar cada participante
    for i, resultado in enumerate(resultados_ordenados, 1):
        participante = resultado.get('participante', 'Desconhecido')
        pontos_rodada = resultado.get('total_rodada', 0.0)
        pontos_acumulados = resultado.get('total_acumulado', 0.0)
        
        # Usar variação já calculada ou calcular se necessário
        variacao = resultado.get('variacao', 0)
        if variacao == 0 and historico_posicoes:
            variacao = calcular_variacao_posicao(participante, i, historico_posicoes)
        
        # Obter códigos de acerto
        codigos = None
        if incluir_codigos and 'codigos_regra' in resultado:
            codigos = resultado['codigos_regra']
        
        # Obter jogos participados
        jogos = resultado.get('jogos_participados')
        
        # Formatar linha
        linha = formatar_linha_participante(
            posicao=i,
            participante=participante,
            pontos_rodada=pontos_rodada,
            pontos_acumulados=pontos_acumulados,
            variacao=variacao,
            codigos_acerto=codigos,
            jogos_participados=jogos
        )
        
        linhas.append(linha)
    
    # Adicionar rodapé
    linhas.append("-" * len(cabecalho))
    linhas.append(f"Total de participantes: {len(resultados_ordenados)}")
    linhas.append("")
    
    # Adicionar legenda de códigos se incluídos
    if incluir_codigos:
        linhas.extend([
            "LEGENDA DOS CÓDIGOS:",
            "AR = Resultado Exato (12 + bônus)",
            "VG = Vencedor + Gols de Um Time (7)",
            "VD = Vencedor + Diferença de Gols (6)",
            "VS = Vencedor + Soma de Gols (6)",
            "V  = Apenas Vencedor (5)",
            "E  = Apenas Empate (5)",
            "G  = Gols de Um Time (2)",
            "S  = Soma de Gols (1)",
            "I  = Placar Invertido (-3)",
            "N  = Não Enviou Palpite (-1)",
            ""
        ])
    
    return "\n".join(linhas)


def gerar_resumo_rodada(resultados: List[Dict[str, Any]], rodada: int) -> str:
    """
    Gera resumo estatístico da rodada.
    
    Args:
        resultados: Lista de resultados dos participantes
        rodada: Número da rodada
    
    Returns:
        String com resumo da rodada
    """
    if not resultados:
        return "Nenhum dado disponível para resumo."
    
    # Calcular estatísticas
    total_participantes = len(resultados)
    pontos_rodada = [r.get('total_rodada', 0) for r in resultados]
    
    maior_pontuacao = max(pontos_rodada) if pontos_rodada else 0
    menor_pontuacao = min(pontos_rodada) if pontos_rodada else 0
    media_pontuacao = sum(pontos_rodada) / len(pontos_rodada) if pontos_rodada else 0
    
    # Encontrar participantes com maior e menor pontuação
    melhor_participante = None
    pior_participante = None
    
    for resultado in resultados:
        if resultado.get('total_rodada', 0) == maior_pontuacao:
            melhor_participante = resultado.get('participante')
        if resultado.get('total_rodada', 0) == menor_pontuacao:
            pior_participante = resultado.get('participante')
    
    linhas = [
        f"RESUMO DA RODADA {rodada:02d}",
        "=" * 30,
        f"Participantes: {total_participantes}",
        f"Maior pontuação: {maior_pontuacao:.1f} ({melhor_participante})",
        f"Menor pontuação: {menor_pontuacao:.1f} ({pior_participante})",
        f"Média da rodada: {media_pontuacao:.1f}",
        ""
    ]
    
    return "\n".join(linhas)