"""
Módulo de pontuação para o sistema de bolão.

Este módulo implementa o motor de pontuação que calcula os pontos
de cada palpite baseado nas regras hierárquicas do sistema.
"""

from typing import Dict, Tuple, Optional, Any


def verificar_resultado_exato(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se o palpite tem placar exato igual ao resultado.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se o placar for exatamente igual
    """
    return (palpite.get('palpite_mandante') == resultado.get('gols_mandante') and
            palpite.get('palpite_visitante') == resultado.get('gols_visitante'))


def verificar_vitoria_gols_um_time(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou vencedor e gols de exatamente uma equipe.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou vencedor e gols de uma equipe (mas não ambas)
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Verifica se acertou o vencedor
    if palp_mandante > palp_visitante and res_mandante > res_visitante:
        # Mandante venceu - verifica se acertou gols de exatamente um time
        acertou_mandante = palp_mandante == res_mandante
        acertou_visitante = palp_visitante == res_visitante
        return acertou_mandante != acertou_visitante  # XOR - apenas um dos dois
    elif palp_visitante > palp_mandante and res_visitante > res_mandante:
        # Visitante venceu - verifica se acertou gols de exatamente um time
        acertou_mandante = palp_mandante == res_mandante
        acertou_visitante = palp_visitante == res_visitante
        return acertou_mandante != acertou_visitante  # XOR - apenas um dos dois
    
    return False


def verificar_vitoria_diferenca_gols(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou vencedor e diferença de gols.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou vencedor e diferença de gols
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Calcula diferenças
    diff_palpite = palp_mandante - palp_visitante
    diff_resultado = res_mandante - res_visitante
    
    # Verifica se acertou o vencedor e a diferença
    if palp_mandante > palp_visitante and res_mandante > res_visitante:
        # Mandante venceu em ambos
        return diff_palpite == diff_resultado
    elif palp_visitante > palp_mandante and res_visitante > res_mandante:
        # Visitante venceu em ambos
        return diff_palpite == diff_resultado
    
    return False


def verificar_vitoria_soma_gols(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou vencedor e soma total de gols.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou vencedor e soma total de gols
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Calcula somas
    soma_palpite = palp_mandante + palp_visitante
    soma_resultado = res_mandante + res_visitante
    
    # Verifica se acertou o vencedor e a soma
    if palp_mandante > palp_visitante and res_mandante > res_visitante:
        # Mandante venceu em ambos
        return soma_palpite == soma_resultado
    elif palp_visitante > palp_mandante and res_visitante > res_mandante:
        # Visitante venceu em ambos
        return soma_palpite == soma_resultado
    
    return False


def verificar_apenas_vitoria(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou apenas o vencedor (sem outras condições).
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou apenas o vencedor
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Verifica se acertou o vencedor
    vencedor_correto = False
    if palp_mandante > palp_visitante and res_mandante > res_visitante:
        vencedor_correto = True  # Mandante venceu em ambos
    elif palp_visitante > palp_mandante and res_visitante > res_mandante:
        vencedor_correto = True  # Visitante venceu em ambos
    
    return vencedor_correto


def verificar_apenas_empate(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou apenas que houve empate.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou que houve empate
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Verifica se ambos são empates
    return palp_mandante == palp_visitante and res_mandante == res_visitante


def verificar_gols_um_time(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou gols de exatamente um time (sem acertar o resultado).
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou gols de exatamente um time
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Verifica se acertou gols de exatamente um time
    acertou_mandante = palp_mandante == res_mandante
    acertou_visitante = palp_visitante == res_visitante
    
    # Deve acertar exatamente um (XOR) e não pode ter acertado o resultado
    acertou_um_time = acertou_mandante != acertou_visitante
    
    # Verifica se NÃO acertou o resultado (vencedor)
    nao_acertou_resultado = True
    if palp_mandante > palp_visitante and res_mandante > res_visitante:
        nao_acertou_resultado = False  # Acertou mandante vencedor
    elif palp_visitante > palp_mandante and res_visitante > res_mandante:
        nao_acertou_resultado = False  # Acertou visitante vencedor
    elif palp_mandante == palp_visitante and res_mandante == res_visitante:
        nao_acertou_resultado = False  # Acertou empate
    
    return acertou_um_time and nao_acertou_resultado


def verificar_soma_gols(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se acertou apenas a soma total de gols.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se acertou apenas a soma total
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Calcula somas
    soma_palpite = palp_mandante + palp_visitante
    soma_resultado = res_mandante + res_visitante
    
    # Verifica se acertou a soma
    acertou_soma = soma_palpite == soma_resultado
    
    # Verifica se NÃO acertou o resultado nem gols individuais
    nao_acertou_resultado = True
    nao_acertou_gols_individuais = True
    
    # Não acertou resultado se não acertou vencedor/empate
    if palp_mandante > palp_visitante and res_mandante > res_visitante:
        nao_acertou_resultado = False
    elif palp_visitante > palp_mandante and res_visitante > res_mandante:
        nao_acertou_resultado = False
    elif palp_mandante == palp_visitante and res_mandante == res_visitante:
        nao_acertou_resultado = False
    
    # Não acertou gols individuais se acertou pelo menos um
    if palp_mandante == res_mandante or palp_visitante == res_visitante:
        nao_acertou_gols_individuais = False
    
    return acertou_soma and nao_acertou_resultado and nao_acertou_gols_individuais


def verificar_resultado_inverso(palpite: Dict[str, Any], resultado: Dict[str, Any]) -> bool:
    """
    Verifica se o palpite tem placar exatamente invertido ao resultado.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
    
    Returns:
        bool: True se o placar for exatamente invertido
    """
    palp_mandante = palpite.get('palpite_mandante', 0)
    palp_visitante = palpite.get('palpite_visitante', 0)
    res_mandante = resultado.get('gols_mandante', 0)
    res_visitante = resultado.get('gols_visitante', 0)
    
    # Verifica se os placares são exatamente invertidos
    # E que não é um empate (pois empate invertido seria o mesmo placar)
    return (palp_mandante == res_visitante and 
            palp_visitante == res_mandante and
            not (palp_mandante == palp_visitante and res_mandante == res_visitante))


def calcular_bonus_resultado_exato(total_acertos_exatos: int) -> float:
    """
    Calcula o bônus proporcional para resultado exato (1/N).
    
    Args:
        total_acertos_exatos: Número total de participantes que acertaram o resultado exato
    
    Returns:
        float: Valor do bônus (1/N)
    """
    if total_acertos_exatos <= 0:
        return 0.0
    return 1.0 / total_acertos_exatos


def calcular_pontuacao(palpite: Dict[str, Any], resultado: Dict[str, Any], 
                      regras: Dict[str, Any], total_acertos_exatos: int = 1) -> Tuple[float, str]:
    """
    Calcula a pontuação de um palpite aplicando a hierarquia de regras.
    
    Retorna apenas a pontuação da regra de maior valor que se aplica.
    Resultado inverso é uma penalidade especial que tem precedência.
    
    Args:
        palpite: Dict com 'palpite_mandante' e 'palpite_visitante'
        resultado: Dict com 'gols_mandante' e 'gols_visitante'
        regras: Dict com configuração das regras de pontuação
        total_acertos_exatos: Número de participantes que acertaram resultado exato
    
    Returns:
        Tuple[float, str]: (pontos, codigo_regra)
    """
    # PRIMEIRO: Verificar resultado inverso (penalidade especial)
    if verificar_resultado_inverso(palpite, resultado):
        pontos = regras.get('resultado_inverso', {}).get('pontos', -3)
        codigo = regras.get('resultado_inverso', {}).get('codigo', 'RI')
        return pontos, codigo
    
    # Hierarquia de regras positivas (da maior para menor pontuação)
    
    # 1. Resultado exato (12 + bônus)
    if verificar_resultado_exato(palpite, resultado):
        pontos_base = regras.get('resultado_exato', {}).get('pontos_base', 12)
        bonus = calcular_bonus_resultado_exato(total_acertos_exatos)
        codigo = regras.get('resultado_exato', {}).get('codigo', 'AR')
        return pontos_base + bonus, codigo
    
    # 2. Vencedor + gols de uma equipe (7 pontos)
    if verificar_vitoria_gols_um_time(palpite, resultado):
        pontos = regras.get('vitoria_gols_um_time', {}).get('pontos', 7)
        codigo = regras.get('vitoria_gols_um_time', {}).get('codigo', 'VG')
        return pontos, codigo
    
    # 3. Vencedor + diferença de gols (6 pontos)
    if verificar_vitoria_diferenca_gols(palpite, resultado):
        pontos = regras.get('vitoria_diferenca_gols', {}).get('pontos', 6)
        codigo = regras.get('vitoria_diferenca_gols', {}).get('codigo', 'VD')
        return pontos, codigo
    
    # 4. Vencedor + soma total de gols (6 pontos)
    if verificar_vitoria_soma_gols(palpite, resultado):
        pontos = regras.get('vitoria_soma_gols', {}).get('pontos', 6)
        codigo = regras.get('vitoria_soma_gols', {}).get('codigo', 'VS')
        return pontos, codigo
    
    # 5. Apenas vencedor (5 pontos)
    if verificar_apenas_vitoria(palpite, resultado):
        pontos = regras.get('apenas_vitoria', {}).get('pontos', 5)
        codigo = regras.get('apenas_vitoria', {}).get('codigo', 'AV')
        return pontos, codigo
    
    # 6. Apenas empate (5 pontos)
    if verificar_apenas_empate(palpite, resultado):
        pontos = regras.get('apenas_empate', {}).get('pontos', 5)
        codigo = regras.get('apenas_empate', {}).get('codigo', 'AE')
        return pontos, codigo
    
    # 7. Gols de um time (2 pontos)
    if verificar_gols_um_time(palpite, resultado):
        pontos = regras.get('gols_um_time', {}).get('pontos', 2)
        codigo = regras.get('gols_um_time', {}).get('codigo', 'AG')
        return pontos, codigo
    
    # 8. Soma total de gols (1 ponto)
    if verificar_soma_gols(palpite, resultado):
        pontos = regras.get('soma_gols', {}).get('pontos', 1)
        codigo = regras.get('soma_gols', {}).get('codigo', 'AS')
        return pontos, codigo
    
    # 9. Nenhuma regra aplicável (0 pontos)
    return 0.0, 'NP'  # Nenhum Ponto


def calcular_pontuacao_palpite_ausente() -> Tuple[float, str]:
    """
    Calcula a pontuação para palpite ausente em jogo obrigatório.
    
    Returns:
        Tuple[float, str]: (-1.0, 'PA') - Palpite Ausente
    """
    return -1.0, 'PA'