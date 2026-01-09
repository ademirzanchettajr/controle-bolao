"""
Testes de propriedade para o módulo de pontuação.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de pontuação definidas no design document.
"""

import pytest
from hypothesis import given, settings, strategies as st
from src.utils.pontuacao import (
    calcular_pontuacao,
    calcular_bonus_resultado_exato,
    verificar_resultado_exato,
    verificar_resultado_inverso,
    verificar_vitoria_gols_um_time,
    verificar_vitoria_diferenca_gols,
    verificar_vitoria_soma_gols,
    verificar_apenas_vitoria,
    verificar_apenas_empate,
    verificar_gols_um_time,
    verificar_soma_gols
)


# Generators para property-based testing
@st.composite
def score_pair(draw):
    """
    Gera um par de placares (palpite, resultado) para testes.
    
    Returns:
        Tuple com (palpite_dict, resultado_dict)
    """
    # Gera placares realistas (0-10 gols)
    palp_mandante = draw(st.integers(min_value=0, max_value=10))
    palp_visitante = draw(st.integers(min_value=0, max_value=10))
    res_mandante = draw(st.integers(min_value=0, max_value=10))
    res_visitante = draw(st.integers(min_value=0, max_value=10))
    
    palpite = {
        'palpite_mandante': palp_mandante,
        'palpite_visitante': palp_visitante
    }
    
    resultado = {
        'gols_mandante': res_mandante,
        'gols_visitante': res_visitante
    }
    
    return palpite, resultado


@st.composite
def exact_score_scenario(draw):
    """
    Gera cenário onde o palpite tem resultado exato.
    
    Returns:
        Tuple com (palpite_dict, resultado_dict) onde palpite == resultado
    """
    # Gera placar
    mandante = draw(st.integers(min_value=0, max_value=10))
    visitante = draw(st.integers(min_value=0, max_value=10))
    
    palpite = {
        'palpite_mandante': mandante,
        'palpite_visitante': visitante
    }
    
    resultado = {
        'gols_mandante': mandante,
        'gols_visitante': visitante
    }
    
    return palpite, resultado


@st.composite
def rules_config(draw):
    """
    Gera configuração de regras válida para testes.
    
    Returns:
        Dict com configuração das regras
    """
    return {
        'resultado_exato': {
            'pontos_base': 12,
            'bonus_divisor': True,
            'codigo': 'AR'
        },
        'vitoria_gols_um_time': {
            'pontos': 7,
            'codigo': 'VG'
        },
        'vitoria_diferenca_gols': {
            'pontos': 6,
            'codigo': 'VD'
        },
        'vitoria_soma_gols': {
            'pontos': 6,
            'codigo': 'VS'
        },
        'apenas_vitoria': {
            'pontos': 5,
            'codigo': 'AV'
        },
        'apenas_empate': {
            'pontos': 5,
            'codigo': 'AE'
        },
        'gols_um_time': {
            'pontos': 2,
            'codigo': 'AG'
        },
        'soma_gols': {
            'pontos': 1,
            'codigo': 'AS'
        },
        'resultado_inverso': {
            'pontos': -3,
            'codigo': 'RI'
        }
    }


class TestScoringProperties:
    """Testes de propriedade para funções de pontuação."""
    
    @given(exact_score_scenario(), st.integers(min_value=1, max_value=50), rules_config())
    @settings(max_examples=100)
    def test_property_29_exact_score_bonus_calculation(self, score_data, total_exact_hits, regras):
        """
        Property 29: Exact score bonus calculation
        
        For any game where N participants predicted the exact score, each should 
        receive 12 + (1/N) points for that game.
        
        **Feature: bolao-prototype-scripts, Property 29: Exact score bonus calculation**
        **Validates: Requirements 8.1, 8.2**
        """
        palpite, resultado = score_data
        
        # Verifica que é realmente um resultado exato
        assert verificar_resultado_exato(palpite, resultado), "Deve ser resultado exato"
        
        # Calcula a pontuação
        pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_exact_hits)
        
        # Verifica que o código é correto para resultado exato
        assert codigo == 'AR', f"Código deve ser 'AR' para resultado exato, mas foi '{codigo}'"
        
        # Calcula a pontuação esperada
        pontos_base = 12
        bonus_esperado = 1.0 / total_exact_hits
        pontos_esperados = pontos_base + bonus_esperado
        
        # Verifica que a pontuação está correta (com tolerância para float)
        assert abs(pontos - pontos_esperados) < 0.0001, \
            f"Pontuação deve ser {pontos_esperados} (12 + 1/{total_exact_hits}), mas foi {pontos}"
        
        # Verifica que o bônus é calculado corretamente
        bonus_calculado = calcular_bonus_resultado_exato(total_exact_hits)
        assert abs(bonus_calculado - bonus_esperado) < 0.0001, \
            f"Bônus deve ser {bonus_esperado}, mas foi {bonus_calculado}"
        
        # Verifica que o bônus é sempre positivo para valores válidos
        assert bonus_calculado > 0, "Bônus deve ser sempre positivo"
        
        # Verifica que o bônus diminui conforme aumenta o número de acertos
        if total_exact_hits > 1:
            bonus_menor = calcular_bonus_resultado_exato(total_exact_hits + 1)
            assert bonus_calculado > bonus_menor, \
                "Bônus deve diminuir conforme aumenta o número de participantes que acertaram"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_30_scoring_rule_hierarchy(self, score_data, regras):
        """
        Property 30: Scoring rule hierarchy
        
        For any prediction and result pair, the system should award points according 
        to the highest-value rule that applies, and only that rule.
        
        **Feature: bolao-prototype-scripts, Property 30: Scoring rule hierarchy**
        **Validates: Requirements 8.12**
        """
        palpite, resultado = score_data
        
        # Calcula a pontuação usando o sistema
        pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
        
        # Verifica manualmente quais regras se aplicam e suas pontuações
        regras_aplicaveis = []
        
        # Verifica resultado inverso (penalidade especial - tem precedência)
        if verificar_resultado_inverso(palpite, resultado):
            regras_aplicaveis.append(('RI', -3))
        
        # Se não é resultado inverso, verifica regras positivas
        if not regras_aplicaveis:
            # Resultado exato
            if verificar_resultado_exato(palpite, resultado):
                regras_aplicaveis.append(('AR', 12 + 1.0))  # 12 + bônus mínimo
            
            # Vencedor + gols de uma equipe
            if verificar_vitoria_gols_um_time(palpite, resultado):
                regras_aplicaveis.append(('VG', 7))
            
            # Vencedor + diferença de gols
            if verificar_vitoria_diferenca_gols(palpite, resultado):
                regras_aplicaveis.append(('VD', 6))
            
            # Vencedor + soma total de gols
            if verificar_vitoria_soma_gols(palpite, resultado):
                regras_aplicaveis.append(('VS', 6))
            
            # Apenas vencedor
            if verificar_apenas_vitoria(palpite, resultado):
                regras_aplicaveis.append(('AV', 5))
            
            # Apenas empate
            if verificar_apenas_empate(palpite, resultado):
                regras_aplicaveis.append(('AE', 5))
            
            # Gols de um time
            if verificar_gols_um_time(palpite, resultado):
                regras_aplicaveis.append(('AG', 2))
            
            # Soma total de gols
            if verificar_soma_gols(palpite, resultado):
                regras_aplicaveis.append(('AS', 1))
        
        # Se nenhuma regra se aplica
        if not regras_aplicaveis:
            regras_aplicaveis.append(('NP', 0))
        
        # Encontra a regra de maior valor
        regra_maior_valor = max(regras_aplicaveis, key=lambda x: x[1])
        codigo_esperado, pontos_minimos = regra_maior_valor
        
        # Verifica que o sistema aplicou a regra de maior valor
        assert codigo == codigo_esperado, \
            f"Sistema deveria aplicar regra '{codigo_esperado}' (maior valor), mas aplicou '{codigo}'. " \
            f"Regras aplicáveis: {regras_aplicaveis}"
        
        # Para resultado exato, verifica que os pontos são pelo menos o valor base + bônus mínimo
        if codigo == 'AR':
            assert pontos >= 12 + 1.0, \
                f"Resultado exato deve ter pelo menos 13 pontos (12 + 1), mas teve {pontos}"
        else:
            # Para outras regras, verifica que os pontos correspondem ao valor esperado
            assert pontos == pontos_minimos, \
                f"Pontuação deve ser {pontos_minimos} para regra '{codigo}', mas foi {pontos}"
        
        # Verifica que apenas uma regra foi aplicada (não há soma de pontos)
        # Isso é implícito no design - o sistema retorna apenas um código e uma pontuação
        assert isinstance(pontos, (int, float)), "Pontuação deve ser um número único"
        assert isinstance(codigo, str), "Código deve ser uma string única"
        assert len(codigo) <= 3, "Código deve ser conciso (máximo 3 caracteres)"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_31_winner_and_one_team_goals_scoring(self, score_data, regras):
        """
        Property 31: Winner and one team goals scoring
        
        For any prediction that matches the winner and the exact goal count of exactly 
        one team (but not both), the system should award exactly 7 points.
        
        **Feature: bolao-prototype-scripts, Property 31: Winner and one team goals scoring**
        **Validates: Requirements 8.3**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica
        if verificar_vitoria_gols_um_time(palpite, resultado):
            # Calcula pontuação
            pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
            
            # Verifica que recebeu exatamente 7 pontos e código VG
            assert pontos == 7, f"Deve receber 7 pontos para vencedor + gols de um time, mas recebeu {pontos}"
            assert codigo == 'VG', f"Código deve ser 'VG', mas foi '{codigo}'"
            
            # Verifica que realmente acertou o vencedor
            palp_mandante = palpite.get('palpite_mandante', 0)
            palp_visitante = palpite.get('palpite_visitante', 0)
            res_mandante = resultado.get('gols_mandante', 0)
            res_visitante = resultado.get('gols_visitante', 0)
            
            # Deve ter acertado o vencedor
            if palp_mandante > palp_visitante:
                assert res_mandante > res_visitante, "Deve ter acertado que mandante venceu"
            elif palp_visitante > palp_mandante:
                assert res_visitante > res_mandante, "Deve ter acertado que visitante venceu"
            
            # Deve ter acertado gols de exatamente um time
            acertou_mandante = palp_mandante == res_mandante
            acertou_visitante = palp_visitante == res_visitante
            assert acertou_mandante != acertou_visitante, "Deve ter acertado gols de exatamente um time"
            
            # Não deve ser resultado exato
            assert not verificar_resultado_exato(palpite, resultado), "Não deve ser resultado exato"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_32_winner_and_goal_difference_scoring(self, score_data, regras):
        """
        Property 32: Winner and goal difference scoring
        
        For any prediction that matches the winner and the goal difference 
        (but not the exact score), the system should award exactly 6 points.
        
        **Feature: bolao-prototype-scripts, Property 32: Winner and goal difference scoring**
        **Validates: Requirements 8.4**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica E não há regras de maior prioridade
        if (verificar_vitoria_diferenca_gols(palpite, resultado) and
            not verificar_resultado_exato(palpite, resultado) and
            not verificar_vitoria_gols_um_time(palpite, resultado) and
            not verificar_resultado_inverso(palpite, resultado)):
            
            # Calcula pontuação
            pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
            
            # Verifica que recebeu exatamente 6 pontos e código VD
            assert pontos == 6, f"Deve receber 6 pontos para vencedor + diferença de gols, mas recebeu {pontos}"
            assert codigo == 'VD', f"Código deve ser 'VD', mas foi '{codigo}'"
            
            # Verifica que realmente acertou vencedor e diferença
            palp_mandante = palpite.get('palpite_mandante', 0)
            palp_visitante = palpite.get('palpite_visitante', 0)
            res_mandante = resultado.get('gols_mandante', 0)
            res_visitante = resultado.get('gols_visitante', 0)
            
            diff_palpite = palp_mandante - palp_visitante
            diff_resultado = res_mandante - res_visitante
            
            # Deve ter acertado a diferença
            assert diff_palpite == diff_resultado, "Deve ter acertado a diferença de gols"
            
            # Deve ter acertado o vencedor
            if palp_mandante > palp_visitante:
                assert res_mandante > res_visitante, "Deve ter acertado que mandante venceu"
            elif palp_visitante > palp_mandante:
                assert res_visitante > res_mandante, "Deve ter acertado que visitante venceu"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_33_winner_and_total_goals_scoring(self, score_data, regras):
        """
        Property 33: Winner and total goals scoring
        
        For any prediction that matches the winner and the total goals 
        (but not the exact score or goal difference), the system should award exactly 6 points.
        
        **Feature: bolao-prototype-scripts, Property 33: Winner and total goals scoring**
        **Validates: Requirements 8.5**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica E não há regras de maior prioridade
        if (verificar_vitoria_soma_gols(palpite, resultado) and
            not verificar_resultado_exato(palpite, resultado) and
            not verificar_vitoria_gols_um_time(palpite, resultado) and
            not verificar_vitoria_diferenca_gols(palpite, resultado) and
            not verificar_resultado_inverso(palpite, resultado)):
            
            # Calcula pontuação
            pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
            
            # Verifica que recebeu exatamente 6 pontos e código VS
            assert pontos == 6, f"Deve receber 6 pontos para vencedor + soma de gols, mas recebeu {pontos}"
            assert codigo == 'VS', f"Código deve ser 'VS', mas foi '{codigo}'"
            
            # Verifica que realmente acertou vencedor e soma
            palp_mandante = palpite.get('palpite_mandante', 0)
            palp_visitante = palpite.get('palpite_visitante', 0)
            res_mandante = resultado.get('gols_mandante', 0)
            res_visitante = resultado.get('gols_visitante', 0)
            
            soma_palpite = palp_mandante + palp_visitante
            soma_resultado = res_mandante + res_visitante
            
            # Deve ter acertado a soma
            assert soma_palpite == soma_resultado, "Deve ter acertado a soma de gols"
            
            # Deve ter acertado o vencedor
            if palp_mandante > palp_visitante:
                assert res_mandante > res_visitante, "Deve ter acertado que mandante venceu"
            elif palp_visitante > palp_mandante:
                assert res_visitante > res_mandante, "Deve ter acertado que visitante venceu"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_34_winner_only_scoring(self, score_data, regras):
        """
        Property 34: Winner only scoring
        
        For any prediction that matches only the winner (no other criteria), 
        the system should award exactly 5 points.
        
        **Feature: bolao-prototype-scripts, Property 34: Winner only scoring**
        **Validates: Requirements 8.6**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica
        if verificar_apenas_vitoria(palpite, resultado):
            # Verifica que não se aplica nenhuma regra de maior valor
            if (not verificar_resultado_exato(palpite, resultado) and
                not verificar_vitoria_gols_um_time(palpite, resultado) and
                not verificar_vitoria_diferenca_gols(palpite, resultado) and
                not verificar_vitoria_soma_gols(palpite, resultado)):
                
                # Calcula pontuação
                pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
                
                # Verifica que recebeu exatamente 5 pontos e código AV
                assert pontos == 5, f"Deve receber 5 pontos para apenas vencedor, mas recebeu {pontos}"
                assert codigo == 'AV', f"Código deve ser 'AV', mas foi '{codigo}'"
                
                # Verifica que realmente acertou apenas o vencedor
                palp_mandante = palpite.get('palpite_mandante', 0)
                palp_visitante = palpite.get('palpite_visitante', 0)
                res_mandante = resultado.get('gols_mandante', 0)
                res_visitante = resultado.get('gols_visitante', 0)
                
                # Deve ter acertado o vencedor
                if palp_mandante > palp_visitante:
                    assert res_mandante > res_visitante, "Deve ter acertado que mandante venceu"
                elif palp_visitante > palp_mandante:
                    assert res_visitante > res_mandante, "Deve ter acertado que visitante venceu"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_35_draw_only_scoring(self, score_data, regras):
        """
        Property 35: Draw only scoring
        
        For any prediction that correctly predicts a draw (but not the exact score), 
        the system should award exactly 5 points.
        
        **Feature: bolao-prototype-scripts, Property 35: Draw only scoring**
        **Validates: Requirements 8.7**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica
        if verificar_apenas_empate(palpite, resultado):
            # Verifica que não é resultado exato
            if not verificar_resultado_exato(palpite, resultado):
                # Calcula pontuação
                pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
                
                # Verifica que recebeu exatamente 5 pontos e código AE
                assert pontos == 5, f"Deve receber 5 pontos para apenas empate, mas recebeu {pontos}"
                assert codigo == 'AE', f"Código deve ser 'AE', mas foi '{codigo}'"
                
                # Verifica que realmente foi empate em ambos
                palp_mandante = palpite.get('palpite_mandante', 0)
                palp_visitante = palpite.get('palpite_visitante', 0)
                res_mandante = resultado.get('gols_mandante', 0)
                res_visitante = resultado.get('gols_visitante', 0)
                
                assert palp_mandante == palp_visitante, "Palpite deve ser empate"
                assert res_mandante == res_visitante, "Resultado deve ser empate"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_36_one_team_goals_scoring(self, score_data, regras):
        """
        Property 36: One team goals scoring
        
        For any prediction that matches exactly one team's goal count 
        (without matching the result), the system should award exactly 2 points.
        
        **Feature: bolao-prototype-scripts, Property 36: One team goals scoring**
        **Validates: Requirements 8.8**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica
        if verificar_gols_um_time(palpite, resultado):
            # Verifica que não se aplica nenhuma regra de maior valor
            if (not verificar_resultado_exato(palpite, resultado) and
                not verificar_vitoria_gols_um_time(palpite, resultado) and
                not verificar_vitoria_diferenca_gols(palpite, resultado) and
                not verificar_vitoria_soma_gols(palpite, resultado) and
                not verificar_apenas_vitoria(palpite, resultado) and
                not verificar_apenas_empate(palpite, resultado)):
                
                # Calcula pontuação
                pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
                
                # Verifica que recebeu exatamente 2 pontos e código AG
                assert pontos == 2, f"Deve receber 2 pontos para gols de um time, mas recebeu {pontos}"
                assert codigo == 'AG', f"Código deve ser 'AG', mas foi '{codigo}'"
                
                # Verifica que realmente acertou gols de exatamente um time
                palp_mandante = palpite.get('palpite_mandante', 0)
                palp_visitante = palpite.get('palpite_visitante', 0)
                res_mandante = resultado.get('gols_mandante', 0)
                res_visitante = resultado.get('gols_visitante', 0)
                
                acertou_mandante = palp_mandante == res_mandante
                acertou_visitante = palp_visitante == res_visitante
                
                # Deve ter acertado exatamente um time (XOR)
                assert acertou_mandante != acertou_visitante, "Deve ter acertado gols de exatamente um time"
                
                # Não deve ter acertado o resultado
                assert not (palp_mandante > palp_visitante and res_mandante > res_visitante), "Não deve ter acertado mandante vencedor"
                assert not (palp_visitante > palp_mandante and res_visitante > res_mandante), "Não deve ter acertado visitante vencedor"
                assert not (palp_mandante == palp_visitante and res_mandante == res_visitante), "Não deve ter acertado empate"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_37_total_goals_only_scoring(self, score_data, regras):
        """
        Property 37: Total goals only scoring
        
        For any prediction that matches only the total goals 
        (without matching the result or one team's goals), the system should award exactly 1 point.
        
        **Feature: bolao-prototype-scripts, Property 37: Total goals only scoring**
        **Validates: Requirements 8.9**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica E não há regras de maior prioridade
        if (verificar_soma_gols(palpite, resultado) and
            not verificar_resultado_exato(palpite, resultado) and
            not verificar_vitoria_gols_um_time(palpite, resultado) and
            not verificar_vitoria_diferenca_gols(palpite, resultado) and
            not verificar_vitoria_soma_gols(palpite, resultado) and
            not verificar_apenas_vitoria(palpite, resultado) and
            not verificar_apenas_empate(palpite, resultado) and
            not verificar_gols_um_time(palpite, resultado) and
            not verificar_resultado_inverso(palpite, resultado)):
            
            # Calcula pontuação
            pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
            
            # Verifica que recebeu exatamente 1 ponto e código AS
            assert pontos == 1, f"Deve receber 1 ponto para soma de gols, mas recebeu {pontos}"
            assert codigo == 'AS', f"Código deve ser 'AS', mas foi '{codigo}'"
            
            # Verifica que realmente acertou apenas a soma
            palp_mandante = palpite.get('palpite_mandante', 0)
            palp_visitante = palpite.get('palpite_visitante', 0)
            res_mandante = resultado.get('gols_mandante', 0)
            res_visitante = resultado.get('gols_visitante', 0)
            
            soma_palpite = palp_mandante + palp_visitante
            soma_resultado = res_mandante + res_visitante
            
            # Deve ter acertado a soma
            assert soma_palpite == soma_resultado, "Deve ter acertado a soma de gols"
            
            # Não deve ter acertado o resultado
            assert not (palp_mandante > palp_visitante and res_mandante > res_visitante), "Não deve ter acertado mandante vencedor"
            assert not (palp_visitante > palp_mandante and res_visitante > res_mandante), "Não deve ter acertado visitante vencedor"
            assert not (palp_mandante == palp_visitante and res_mandante == res_visitante), "Não deve ter acertado empate"
            
            # Não deve ter acertado gols individuais
            assert palp_mandante != res_mandante, "Não deve ter acertado gols do mandante"
            assert palp_visitante != res_visitante, "Não deve ter acertado gols do visitante"

    @given(score_pair(), rules_config())
    @settings(max_examples=100)
    def test_property_38_inverted_score_penalty(self, score_data, regras):
        """
        Property 38: Inverted score penalty
        
        For any prediction where the home and away scores are exactly swapped compared 
        to the result (e.g., prediction "2x1", result "1x2"), the system should award exactly -3 points.
        
        **Feature: bolao-prototype-scripts, Property 38: Inverted score penalty**
        **Validates: Requirements 8.10**
        """
        palpite, resultado = score_data
        
        # Verifica se esta condição se aplica
        if verificar_resultado_inverso(palpite, resultado):
            # Calcula pontuação
            pontos, codigo = calcular_pontuacao(palpite, resultado, regras, total_acertos_exatos=1)
            
            # Verifica que recebeu exatamente -3 pontos e código RI
            assert pontos == -3, f"Deve receber -3 pontos para resultado inverso, mas recebeu {pontos}"
            assert codigo == 'RI', f"Código deve ser 'RI', mas foi '{codigo}'"
            
            # Verifica que realmente é resultado inverso
            palp_mandante = palpite.get('palpite_mandante', 0)
            palp_visitante = palpite.get('palpite_visitante', 0)
            res_mandante = resultado.get('gols_mandante', 0)
            res_visitante = resultado.get('gols_visitante', 0)
            
            # Placares devem estar invertidos
            assert palp_mandante == res_visitante, "Gols do mandante no palpite devem igual gols do visitante no resultado"
            assert palp_visitante == res_mandante, "Gols do visitante no palpite devem igual gols do mandante no resultado"
            
            # Não deve ser empate (empate invertido seria o mesmo placar)
            assert not (palp_mandante == palp_visitante and res_mandante == res_visitante), "Não deve ser empate"

    @given(rules_config())
    @settings(max_examples=100)
    def test_property_39_missing_prediction_penalty(self, regras):
        """
        Property 39: Missing prediction penalty
        
        For any mandatory game where a participant has no prediction, 
        the system should award exactly -1 point to that participant for that game.
        
        **Feature: bolao-prototype-scripts, Property 39: Missing prediction penalty**
        **Validates: Requirements 8.11**
        """
        # Testa a função específica para palpite ausente
        from src.utils.pontuacao import calcular_pontuacao_palpite_ausente
        
        pontos, codigo = calcular_pontuacao_palpite_ausente()
        
        # Verifica que recebeu exatamente -1 ponto e código PA
        assert pontos == -1.0, f"Deve receber -1 ponto para palpite ausente, mas recebeu {pontos}"
        assert codigo == 'PA', f"Código deve ser 'PA', mas foi '{codigo}'"
        
        # Verifica que a penalidade é consistente
        pontos2, codigo2 = calcular_pontuacao_palpite_ausente()
        assert pontos == pontos2, "Penalidade deve ser consistente"
        assert codigo == codigo2, "Código deve ser consistente"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])