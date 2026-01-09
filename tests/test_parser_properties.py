"""
Testes de propriedade para o módulo de parsing de texto.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de parsing definidas no design document.
"""

import pytest
import re
from hypothesis import given, settings, strategies as st, assume
from src.utils.parser import (
    extrair_apostador,
    extrair_rodada,
    extrair_palpites,
    inferir_rodada,
    identificar_apostas_extras,
    processar_texto_palpite
)


# Generators para property-based testing
@st.composite
def participant_names(draw):
    """
    Gera nomes de participantes realistas para testar identificação.
    
    Inclui variações com:
    - Nomes compostos
    - Acentos
    - Diferentes formatos de marcação
    """
    first_names = [
        "Mario", "João", "Ana", "Carlos", "Maria", "José", "Paula", "Pedro",
        "Antônio", "Francisco", "Luiz", "Marcos", "André", "Rafael", "Bruno"
    ]
    
    last_names = [
        "Silva", "Santos", "Oliveira", "Souza", "Costa", "Ferreira", "Almeida",
        "Pereira", "Lima", "Gomes", "Martins", "Araújo", "Melo", "Barbosa"
    ]
    
    first_name = draw(st.sampled_from(first_names))
    last_name = draw(st.sampled_from(last_names))
    
    # Adiciona sufixos opcionais
    suffixes = ["", " Jr.", " Neto", " Filho", " II"]
    suffix = draw(st.sampled_from(suffixes))
    
    full_name = first_name + " " + last_name + suffix
    
    return full_name


@st.composite
def participant_text_with_marker(draw):
    """
    Gera texto com nome de participante usando diferentes marcadores.
    """
    participant_name = draw(participant_names())
    
    # Diferentes formatos de marcação
    markers = [
        f"Apostador: {participant_name}",
        f"Nome: {participant_name}",
        f"apostador: {participant_name}",
        f"APOSTADOR: {participant_name}",
        f"Apostador:{participant_name}",  # Sem espaço após dois pontos
        f"Nome:{participant_name}",
    ]
    
    marker = draw(st.sampled_from(markers))
    
    # Adiciona conteúdo adicional após o marcador
    additional_content = draw(st.text(min_size=0, max_size=100))
    
    return marker + "\n" + additional_content, participant_name


@st.composite
def participant_text_first_line(draw):
    """
    Gera texto com nome de participante na primeira linha (sem marcador).
    """
    participant_name = draw(participant_names())
    
    # Adiciona espaços opcionais
    leading_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    trailing_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    
    first_line = leading_spaces + participant_name + trailing_spaces
    
    # Adiciona conteúdo que não seja indicador de rodada ou jogo
    safe_content = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=0, max_size=50))
    
    return first_line + "\n" + safe_content, participant_name


@st.composite
def round_text_variations(draw):
    """
    Gera texto com indicações de rodada em diferentes formatos.
    """
    round_number = draw(st.integers(min_value=1, max_value=50))
    
    # Diferentes formatos de indicação de rodada
    formats = [
        f"{round_number}ª Rodada",
        f"{round_number}º Rodada", 
        f"{round_number} Rodada",
        f"Rodada {round_number}",
        f"R{round_number}",
        f"R {round_number}",
        f"Round {round_number}",
        f"{round_number}ª rodada",  # lowercase
        f"rodada {round_number}",   # lowercase
        f"{round_number}ª Jornada", # português europeu
        f"Jornada {round_number}",
    ]
    
    format_choice = draw(st.sampled_from(formats))
    
    # Adiciona conteúdo adicional
    additional_content = draw(st.text(min_size=0, max_size=100))
    
    return format_choice + "\n" + additional_content, round_number


@st.composite
def team_names(draw):
    """
    Gera nomes de times realistas para testar parsing de palpites.
    """
    teams = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético-MG",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional", "Cruzeiro",
        "Fluminense", "Bahia", "Sport", "Ceará", "Fortaleza", "Goiás",
        "Atlético/MG", "Atlético-PR", "Coritiba", "Paraná", "Chapecoense"
    ]
    
    return draw(st.sampled_from(teams))


@st.composite
def score_formats(draw):
    """
    Gera diferentes formatos de placar para testar reconhecimento.
    """
    home_goals = draw(st.integers(min_value=0, max_value=10))
    away_goals = draw(st.integers(min_value=0, max_value=10))
    
    # Diferentes formatos de placar
    formats = [
        f"{home_goals}x{away_goals}",           # "2x1"
        f"{home_goals} x {away_goals}",         # "2 x 1"
        f"{home_goals}  x  {away_goals}",       # "2  x  1" (espaços extras)
        f"{home_goals}-{away_goals}",           # "2-1"
        f"{home_goals} - {away_goals}",         # "2 - 1"
        f"{home_goals}:{away_goals}",           # "2:1"
        f"{home_goals} : {away_goals}",         # "2 : 1"
        f"({home_goals}) x ({away_goals})",     # "(2) x (1)"
        f"( {home_goals} ) x ( {away_goals} )", # "( 2 ) x ( 1 )"
    ]
    
    format_choice = draw(st.sampled_from(formats))
    
    return format_choice, home_goals, away_goals


@st.composite
def prediction_text(draw):
    """
    Gera texto de palpite com time e placar em formato válido.
    """
    home_team = draw(team_names())
    away_team = draw(team_names())
    assume(home_team != away_team)  # Times diferentes
    
    score_text, home_goals, away_goals = draw(score_formats())
    
    prediction_line = f"{home_team} {score_text} {away_team}"
    
    return prediction_line, {
        'mandante': home_team,
        'visitante': away_team,
        'gols_mandante': home_goals,
        'gols_visitante': away_goals
    }


@st.composite
def multiple_predictions_text(draw):
    """
    Gera texto com múltiplos palpites.
    """
    num_predictions = draw(st.integers(min_value=1, max_value=5))
    predictions = []
    lines = []
    
    for _ in range(num_predictions):
        pred_line, pred_data = draw(prediction_text())
        predictions.append(pred_data)
        lines.append(pred_line)
    
    # Adiciona linhas extras que não são palpites
    extra_lines = [
        "1ª Rodada:",
        "Apostador: João Silva",
        "",  # linha vazia
        "Observações:",
    ]
    
    # Intercala palpites com linhas extras
    all_lines = []
    for i, line in enumerate(lines):
        if i < len(extra_lines):
            all_lines.append(extra_lines[i])
        all_lines.append(line)
    
    text = "\n".join(all_lines)
    
    return text, predictions


@st.composite
def table_with_teams(draw):
    """
    Gera uma tabela com times para testar inferência de rodada.
    """
    teams = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético-MG",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional"
    ]
    
    num_rounds = draw(st.integers(min_value=1, max_value=3))
    rounds = []
    
    for round_num in range(1, num_rounds + 1):
        num_games = draw(st.integers(min_value=2, max_value=5))
        games = []
        
        used_teams = set()
        for game_num in range(num_games):
            # Seleciona times que ainda não jogaram nesta rodada
            available_teams = [t for t in teams if t not in used_teams]
            if len(available_teams) < 2:
                break  # Não há times suficientes
            
            home_team = draw(st.sampled_from(available_teams))
            available_teams.remove(home_team)
            away_team = draw(st.sampled_from(available_teams))
            
            used_teams.add(home_team)
            used_teams.add(away_team)
            
            games.append({
                "id": f"jogo-{round_num:02d}-{game_num+1:02d}",
                "mandante": home_team,
                "visitante": away_team,
                "data": "2024-01-01T10:00:00Z",
                "local": f"Estádio {game_num+1}",
                "gols_mandante": 0,
                "gols_visitante": 0,
                "status": "agendado",
                "obrigatorio": True
            })
        
        if games:  # Só adiciona rodada se tem jogos
            rounds.append({
                "numero": round_num,
                "jogos": games
            })
    
    return {
        "campeonato": "Teste",
        "temporada": "2024", 
        "rodada_atual": 0,
        "data_atualizacao": "2024-01-01T10:00:00Z",
        "codigo_campeonato": "12345",
        "rodadas": rounds
    }


@st.composite
def extra_bet_text(draw):
    """
    Gera texto com apostas extras em diferentes formatos.
    """
    game_number = draw(st.integers(min_value=1, max_value=20))
    pred_line, pred_data = draw(prediction_text())
    
    # Diferentes formatos de aposta extra
    formats = [
        f"Aposta Extra:\nJogo {game_number}: {pred_line}",
        f"Apostas Extras:\nJogo {game_number}: {pred_line}",
        f"Extra:\nJogo {game_number}: {pred_line}",
        f"APOSTA EXTRA:\nJOGO {game_number}: {pred_line}",
        f"Jogo {game_number}: {pred_line}",  # Sem marcador de seção
        f"Aposta Extra\nJogo {game_number}: {pred_line}",  # Sem dois pontos
    ]
    
    format_choice = draw(st.sampled_from(formats))
    
    expected_extra = pred_data.copy()
    expected_extra['tipo'] = 'extra'
    expected_extra['identificador'] = f'Jogo {game_number}'
    
    return format_choice, expected_extra


class TestParserProperties:
    """Testes de propriedade para funções de parsing."""
    
    @given(participant_text_with_marker())
    @settings(max_examples=100)
    def test_property_14_participant_identification_with_marker(self, text_data):
        """
        Property 14: Participant identification from text (parte 1 - com marcador)
        
        For any prediction text containing a registered participant's name with 
        explicit marker, the system should correctly identify and match the participant.
        
        **Feature: bolao-prototype-scripts, Property 14: Participant identification from text**
        **Validates: Requirements 5.1**
        """
        text, expected_name = text_data
        
        result = extrair_apostador(text)
        
        # Deve extrair o nome corretamente
        assert result is not None, f"Falhou ao extrair apostador do texto: '{text[:100]}...'"
        assert result == expected_name, f"Nome extraído '{result}' não confere com esperado '{expected_name}'"
    
    @given(participant_text_first_line())
    @settings(max_examples=100)
    def test_property_14_participant_identification_first_line(self, text_data):
        """
        Property 14: Participant identification from text (parte 2 - primeira linha)
        
        For any prediction text with participant name in first line (no marker),
        the system should correctly identify the participant.
        
        **Feature: bolao-prototype-scripts, Property 14: Participant identification from text**
        **Validates: Requirements 5.1**
        """
        text, expected_name = text_data
        
        result = extrair_apostador(text)
        
        # Deve extrair o nome corretamente ou retornar None se ambíguo
        if result is not None:
            # Se extraiu algo, deve ser o nome esperado (possivelmente com espaços normalizados)
            assert result.strip() == expected_name.strip(), f"Nome extraído '{result}' não confere com esperado '{expected_name}'"
    
    @given(round_text_variations())
    @settings(max_examples=100)
    def test_property_15_round_extraction_from_text(self, text_data):
        """
        Property 15: Round extraction from text
        
        For any prediction text containing a round indication (e.g., "1ª Rodada", "Rodada 2"), 
        the system should correctly extract the round number.
        
        **Feature: bolao-prototype-scripts, Property 15: Round extraction from text**
        **Validates: Requirements 5.2**
        """
        text, expected_round = text_data
        
        result = extrair_rodada(text)
        
        # Deve extrair o número da rodada corretamente
        assert result is not None, f"Falhou ao extrair rodada do texto: '{text[:100]}...'"
        assert result == expected_round, f"Rodada extraída {result} não confere com esperada {expected_round}"
        
        # Verifica que o resultado está dentro do range válido
        assert 1 <= result <= 50, f"Rodada extraída {result} fora do range válido (1-50)"
    
    @given(table_with_teams(), st.integers(min_value=1, max_value=3))
    @settings(max_examples=50)  # Reduzido porque é mais complexo
    def test_property_16_round_inference_from_team_names(self, table_data, target_round):
        """
        Property 16: Round inference from team names
        
        For any prediction text without round indication but containing team names 
        that appear in exactly one round, the system should correctly infer that round number.
        
        **Feature: bolao-prototype-scripts, Property 16: Round inference from team names**
        **Validates: Requirements 5.3**
        """
        # Filtra para rodadas que existem na tabela
        available_rounds = [r['numero'] for r in table_data['rodadas']]
        assume(target_round in available_rounds)
        
        # Pega jogos da rodada alvo
        target_round_data = None
        for rodada in table_data['rodadas']:
            if rodada['numero'] == target_round:
                target_round_data = rodada
                break
        
        assume(target_round_data is not None)
        assume(len(target_round_data['jogos']) > 0)
        
        # Verifica se os times da rodada alvo aparecem em outras rodadas
        target_teams = set()
        for jogo in target_round_data['jogos']:
            target_teams.add(jogo['mandante'])
            target_teams.add(jogo['visitante'])
        
        # Verifica se há conflito com outras rodadas
        has_conflict = False
        for rodada in table_data['rodadas']:
            if rodada['numero'] != target_round:
                for jogo in rodada['jogos']:
                    if jogo['mandante'] in target_teams or jogo['visitante'] in target_teams:
                        has_conflict = True
                        break
        
        # Se há conflito, a função pode retornar qualquer rodada válida
        # Se não há conflito, deve retornar a rodada correta
        
        # Cria palpites baseados nos jogos da rodada alvo
        palpites = []
        for jogo in target_round_data['jogos'][:2]:  # Pega até 2 jogos
            palpites.append({
                'mandante': jogo['mandante'],
                'visitante': jogo['visitante'],
                'gols_mandante': 2,
                'gols_visitante': 1
            })
        
        result = inferir_rodada(palpites, table_data)
        
        # Deve inferir uma rodada válida
        if result is not None:
            assert result in available_rounds, f"Rodada inferida {result} não está nas rodadas disponíveis {available_rounds}"
            
            # Se não há conflito, deve ser a rodada correta
            if not has_conflict:
                assert result == target_round, f"Rodada inferida {result} não confere com esperada {target_round} (sem conflito)"
    
    @given(prediction_text())
    @settings(max_examples=100)
    def test_property_17_score_format_recognition_single(self, pred_data):
        """
        Property 17: Score format recognition (parte 1 - formato único)
        
        For any score written in valid formats ("2x1", "2 x 1", "2-1"), 
        the parser should extract the same numeric values for home and away goals.
        
        **Feature: bolao-prototype-scripts, Property 17: Score format recognition**
        **Validates: Requirements 5.5**
        """
        pred_line, expected_data = pred_data
        
        result = extrair_palpites(pred_line)
        
        # Deve extrair exatamente um palpite
        assert len(result) == 1, f"Deveria extrair 1 palpite, mas extraiu {len(result)} de: '{pred_line}'"
        
        extracted = result[0]
        
        # Verifica que os dados extraídos conferem
        assert extracted['mandante'].strip() == expected_data['mandante'], f"Time mandante não confere: '{extracted['mandante']}' vs '{expected_data['mandante']}'"
        assert extracted['visitante'].strip() == expected_data['visitante'], f"Time visitante não confere: '{extracted['visitante']}' vs '{expected_data['visitante']}'"
        assert extracted['gols_mandante'] == expected_data['gols_mandante'], f"Gols mandante não conferem: {extracted['gols_mandante']} vs {expected_data['gols_mandante']}"
        assert extracted['gols_visitante'] == expected_data['gols_visitante'], f"Gols visitante não conferem: {extracted['gols_visitante']} vs {expected_data['gols_visitante']}"
    
    @given(multiple_predictions_text())
    @settings(max_examples=50)  # Reduzido porque é mais complexo
    def test_property_17_score_format_recognition_multiple(self, text_data):
        """
        Property 17: Score format recognition (parte 2 - múltiplos formatos)
        
        For any text with multiple predictions in different valid formats,
        the parser should extract all predictions with correct numeric values.
        
        **Feature: bolao-prototype-scripts, Property 17: Score format recognition**
        **Validates: Requirements 5.5**
        """
        text, expected_predictions = text_data
        
        result = extrair_palpites(text)
        
        # Deve extrair pelo menos o número esperado de palpites
        # (pode extrair mais se houver linhas que parecem palpites)
        assert len(result) >= len(expected_predictions), f"Deveria extrair pelo menos {len(expected_predictions)} palpites, mas extraiu {len(result)}"
        
        # Verifica que todos os palpites esperados estão presentes
        for expected in expected_predictions:
            # Procura por um palpite correspondente nos resultados
            found = False
            for extracted in result:
                if (extracted['mandante'].strip() == expected['mandante'] and
                    extracted['visitante'].strip() == expected['visitante'] and
                    extracted['gols_mandante'] == expected['gols_mandante'] and
                    extracted['gols_visitante'] == expected['gols_visitante']):
                    found = True
                    break
            
            assert found, f"Palpite esperado não encontrado: {expected['mandante']} {expected['gols_mandante']}x{expected['gols_visitante']} {expected['visitante']}"
    
    @given(extra_bet_text())
    @settings(max_examples=100)
    def test_property_19_extra_bet_identification(self, bet_data):
        """
        Property 19: Extra bet identification
        
        For any prediction text containing extra bet markers (e.g., "Aposta Extra:", "Jogo X:"), 
        those predictions should be stored with appropriate identification in the palpites file.
        
        **Feature: bolao-prototype-scripts, Property 19: Extra bet identification**
        **Validates: Requirements 5.9**
        """
        text, expected_extra = bet_data
        
        result = identificar_apostas_extras(text)
        
        # Deve identificar pelo menos uma aposta extra
        assert len(result) >= 1, f"Deveria identificar pelo menos 1 aposta extra, mas identificou {len(result)} em: '{text}'"
        
        # Verifica que a aposta extra esperada está presente
        found = False
        for extra in result:
            # Comparação case-insensitive para identificador
            extra_id_lower = extra.get('identificador', '').lower()
            expected_id_lower = expected_extra['identificador'].lower()
            
            if (extra.get('tipo') == expected_extra['tipo'] and
                extra_id_lower == expected_id_lower and
                extra.get('mandante') == expected_extra['mandante'] and
                extra.get('visitante') == expected_extra['visitante'] and
                extra.get('gols_mandante') == expected_extra['gols_mandante'] and
                extra.get('gols_visitante') == expected_extra['gols_visitante']):
                found = True
                break
        
        assert found, f"Aposta extra esperada não encontrada: {expected_extra}"
        
        # Verifica que todas as apostas extras têm os campos obrigatórios
        for extra in result:
            assert 'tipo' in extra, f"Aposta extra deve ter campo 'tipo': {extra}"
            assert extra['tipo'] == 'extra', f"Campo 'tipo' deve ser 'extra': {extra}"
            assert 'identificador' in extra, f"Aposta extra deve ter campo 'identificador': {extra}"
            assert 'mandante' in extra, f"Aposta extra deve ter campo 'mandante': {extra}"
            assert 'visitante' in extra, f"Aposta extra deve ter campo 'visitante': {extra}"
            assert 'gols_mandante' in extra, f"Aposta extra deve ter campo 'gols_mandante': {extra}"
            assert 'gols_visitante' in extra, f"Aposta extra deve ter campo 'gols_visitante': {extra}"
    
    @given(st.text(min_size=0, max_size=10))
    @settings(max_examples=100)
    def test_property_14_participant_identification_edge_cases(self, random_text):
        """
        Property 14: Participant identification from text (parte 3 - casos extremos)
        
        For any random or malformed text, the participant identification should 
        handle gracefully without crashing.
        
        **Feature: bolao-prototype-scripts, Property 14: Participant identification from text**
        **Validates: Requirements 5.1**
        """
        # Testa que a função não quebra com entrada aleatória
        result = extrair_apostador(random_text)
        
        # Resultado deve ser None ou string válida
        assert result is None or isinstance(result, str), f"Resultado deve ser None ou string, mas foi {type(result)}: {result}"
        
        # Se retornou string, deve ser não vazia
        if result is not None:
            assert len(result.strip()) > 0, f"Se retornou string, deve ser não vazia: '{result}'"
    
    @given(st.text(min_size=0, max_size=20))
    @settings(max_examples=100)
    def test_property_15_round_extraction_edge_cases(self, random_text):
        """
        Property 15: Round extraction from text (parte 2 - casos extremos)
        
        For any random or malformed text, the round extraction should 
        handle gracefully without crashing.
        
        **Feature: bolao-prototype-scripts, Property 15: Round extraction from text**
        **Validates: Requirements 5.2**
        """
        # Testa que a função não quebra com entrada aleatória
        result = extrair_rodada(random_text)
        
        # Resultado deve ser None ou inteiro válido
        assert result is None or isinstance(result, int), f"Resultado deve ser None ou int, mas foi {type(result)}: {result}"
        
        # Se retornou inteiro, deve estar no range válido
        if result is not None:
            assert 1 <= result <= 50, f"Se retornou inteiro, deve estar no range 1-50: {result}"
    
    @given(st.text(min_size=0, max_size=50))
    @settings(max_examples=100)
    def test_property_17_score_format_recognition_edge_cases(self, random_text):
        """
        Property 17: Score format recognition (parte 3 - casos extremos)
        
        For any random or malformed text, the score parsing should 
        handle gracefully without crashing.
        
        **Feature: bolao-prototype-scripts, Property 17: Score format recognition**
        **Validates: Requirements 5.5**
        """
        # Testa que a função não quebra com entrada aleatória
        result = extrair_palpites(random_text)
        
        # Resultado deve ser lista
        assert isinstance(result, list), f"Resultado deve ser lista, mas foi {type(result)}: {result}"
        
        # Todos os itens da lista devem ser dicionários válidos
        for item in result:
            assert isinstance(item, dict), f"Item da lista deve ser dict, mas foi {type(item)}: {item}"
            
            # Verifica campos obrigatórios
            required_fields = ['mandante', 'visitante', 'gols_mandante', 'gols_visitante']
            for field in required_fields:
                assert field in item, f"Item deve ter campo '{field}': {item}"
            
            # Verifica tipos dos campos
            assert isinstance(item['mandante'], str), f"Campo 'mandante' deve ser string: {item}"
            assert isinstance(item['visitante'], str), f"Campo 'visitante' deve ser string: {item}"
            
            # Gols podem ser None (placar não especificado) ou inteiros válidos
            if item['gols_mandante'] is not None:
                assert isinstance(item['gols_mandante'], int), f"Campo 'gols_mandante' deve ser int ou None: {item}"
                assert 0 <= item['gols_mandante'] <= 20, f"Gols mandante fora do range válido: {item}"
            
            if item['gols_visitante'] is not None:
                assert isinstance(item['gols_visitante'], int), f"Campo 'gols_visitante' deve ser int ou None: {item}"
                assert 0 <= item['gols_visitante'] <= 20, f"Gols visitante fora do range válido: {item}"
    
    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=100)
    def test_property_19_extra_bet_identification_edge_cases(self, random_text):
        """
        Property 19: Extra bet identification (parte 2 - casos extremos)
        
        For any random or malformed text, the extra bet identification should 
        handle gracefully without crashing.
        
        **Feature: bolao-prototype-scripts, Property 19: Extra bet identification**
        **Validates: Requirements 5.9**
        """
        # Testa que a função não quebra com entrada aleatória
        result = identificar_apostas_extras(random_text)
        
        # Resultado deve ser lista
        assert isinstance(result, list), f"Resultado deve ser lista, mas foi {type(result)}: {result}"
        
        # Todos os itens da lista devem ser dicionários válidos de apostas extras
        for item in result:
            assert isinstance(item, dict), f"Item da lista deve ser dict, mas foi {type(item)}: {item}"
            
            # Verifica campos obrigatórios de aposta extra
            required_fields = ['tipo', 'identificador', 'mandante', 'visitante', 'gols_mandante', 'gols_visitante']
            for field in required_fields:
                assert field in item, f"Aposta extra deve ter campo '{field}': {item}"
            
            # Verifica valores específicos
            assert item['tipo'] == 'extra', f"Campo 'tipo' deve ser 'extra': {item}"
            assert isinstance(item['identificador'], str), f"Campo 'identificador' deve ser string: {item}"
            assert len(item['identificador'].strip()) > 0, f"Campo 'identificador' não deve ser vazio: {item}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])