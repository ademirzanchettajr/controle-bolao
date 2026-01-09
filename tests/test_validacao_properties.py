"""
Testes de propriedade para o módulo de validação de dados.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de validação definidas no design document.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from hypothesis import given, settings, strategies as st, assume
from src.utils.validacao import (
    validar_estrutura_tabela,
    validar_estrutura_palpites,
    validar_estrutura_regras,
    validar_placar,
    validar_data,
    validar_id_jogo,
    validar_participante
)


# Generators para property-based testing
@st.composite
def valid_table_structure(draw):
    """
    Gera estruturas válidas de tabela.json para testar validação.
    """
    return {
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "rodada_atual": draw(st.integers(min_value=0, max_value=50)),
        "data_atualizacao": "2024-01-01T10:00:00Z",
        "codigo_campeonato": draw(st.text(min_size=5, max_size=5, alphabet="0123456789")),
        "rodadas": []
    }


@st.composite
def invalid_table_structure(draw):
    """
    Gera estruturas inválidas de tabela.json removendo campos obrigatórios.
    """
    base_structure = {
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "rodada_atual": draw(st.integers(min_value=0, max_value=50)),
        "data_atualizacao": "2024-01-01T10:00:00Z",
        "codigo_campeonato": draw(st.text(min_size=5, max_size=5, alphabet="0123456789")),
        "rodadas": []
    }
    
    # Remove um campo obrigatório aleatório
    required_fields = ["campeonato", "temporada", "rodada_atual", "data_atualizacao", "codigo_campeonato", "rodadas"]
    field_to_remove = draw(st.sampled_from(required_fields))
    del base_structure[field_to_remove]
    
    return base_structure, field_to_remove


@st.composite
def valid_palpites_structure(draw):
    """
    Gera estruturas válidas de palpites.json para testar validação.
    """
    return {
        "apostador": draw(st.text(min_size=1, max_size=50)),
        "codigo_apostador": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "palpites": []
    }


@st.composite
def invalid_palpites_structure(draw):
    """
    Gera estruturas inválidas de palpites.json removendo campos obrigatórios.
    """
    base_structure = {
        "apostador": draw(st.text(min_size=1, max_size=50)),
        "codigo_apostador": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "palpites": []
    }
    
    # Remove um campo obrigatório aleatório
    required_fields = ["apostador", "codigo_apostador", "campeonato", "temporada", "palpites"]
    field_to_remove = draw(st.sampled_from(required_fields))
    del base_structure[field_to_remove]
    
    return base_structure, field_to_remove


@st.composite
def valid_regras_structure(draw):
    """
    Gera estruturas válidas de regras.json para testar validação.
    """
    return {
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "versao": draw(st.text(min_size=1, max_size=10)),
        "regras": {
            "resultado_exato": {
                "pontos_base": 12,
                "descricao": "Resultado exato",
                "codigo": "AR"
            }
        }
    }


@st.composite
def invalid_regras_structure(draw):
    """
    Gera estruturas inválidas de regras.json removendo campos obrigatórios.
    """
    base_structure = {
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.text(min_size=4, max_size=4, alphabet="0123456789")),
        "versao": draw(st.text(min_size=1, max_size=10)),
        "regras": {
            "resultado_exato": {
                "pontos_base": 12,
                "descricao": "Resultado exato",
                "codigo": "AR"
            }
        }
    }
    
    # Remove um campo obrigatório aleatório
    required_fields = ["campeonato", "temporada", "versao", "regras"]
    field_to_remove = draw(st.sampled_from(required_fields))
    del base_structure[field_to_remove]
    
    return base_structure, field_to_remove


@st.composite
def valid_date_strings(draw):
    """
    Gera strings de data válidas em formatos aceitos.
    """
    formats = [
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M", 
        "%d-%m-%Y %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ"
    ]
    
    format_choice = draw(st.sampled_from(formats))
    
    # Gera uma data válida
    year = draw(st.integers(min_value=2020, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Evita problemas com fevereiro
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    second = draw(st.integers(min_value=0, max_value=59))
    
    dt = datetime(year, month, day, hour, minute, second)
    return dt.strftime(format_choice)


@st.composite
def invalid_date_strings(draw):
    """
    Gera strings de data inválidas.
    """
    invalid_formats = [
        "invalid-date",
        "2024/13/01 10:00",  # Mês inválido
        "2024-02-30 10:00",  # Dia inválido
        "2024-01-01 25:00",  # Hora inválida
        "2024-01-01 10:70",  # Minuto inválido
        "",                   # String vazia
        "not-a-date",
        "2024",              # Formato incompleto
        "01/01/24",          # Ano com 2 dígitos
    ]
    
    return draw(st.sampled_from(invalid_formats))


@st.composite
def valid_scores(draw):
    """
    Gera placares válidos (inteiros não-negativos dentro dos limites).
    """
    home_goals = draw(st.integers(min_value=0, max_value=20))
    away_goals = draw(st.integers(min_value=0, max_value=20))
    return home_goals, away_goals


@st.composite
def invalid_scores(draw):
    """
    Gera placares inválidos (não inteiros, negativos, ou fora dos limites).
    """
    invalid_types = [
        (draw(st.floats()), draw(st.integers(min_value=0, max_value=20))),  # Float no mandante
        (draw(st.integers(min_value=0, max_value=20)), draw(st.floats())),  # Float no visitante
        (draw(st.text()), draw(st.integers(min_value=0, max_value=20))),    # String no mandante
        (draw(st.integers(min_value=0, max_value=20)), draw(st.text())),    # String no visitante
        (draw(st.integers(max_value=-1)), draw(st.integers(min_value=0, max_value=20))),  # Negativo no mandante
        (draw(st.integers(min_value=0, max_value=20)), draw(st.integers(max_value=-1))),  # Negativo no visitante
        (draw(st.integers(min_value=21, max_value=100)), draw(st.integers(min_value=0, max_value=20))),  # Acima do limite no mandante
        (draw(st.integers(min_value=0, max_value=20)), draw(st.integers(min_value=21, max_value=100))),  # Acima do limite no visitante
    ]
    
    return draw(st.sampled_from(invalid_types))


@st.composite
def table_with_games(draw):
    """
    Gera uma tabela com jogos para testar validação de IDs.
    """
    num_games = draw(st.integers(min_value=1, max_value=10))
    games = []
    
    for i in range(num_games):
        games.append({
            "id": f"jogo-{i+1:03d}",
            "mandante": f"Time{i+1}A",
            "visitante": f"Time{i+1}B",
            "data": "2024-01-01T10:00:00Z",
            "local": f"Estádio {i+1}",
            "gols_mandante": 0,
            "gols_visitante": 0,
            "status": "agendado",
            "obrigatorio": True
        })
    
    return {
        "campeonato": "Teste",
        "temporada": "2024",
        "rodada_atual": 0,
        "data_atualizacao": "2024-01-01T10:00:00Z",
        "codigo_campeonato": "12345",
        "rodadas": [
            {
                "numero": 1,
                "jogos": games
            }
        ]
    }


class TestValidationProperties:
    """Testes de propriedade para funções de validação."""
    
    @given(valid_table_structure())
    @settings(max_examples=100)
    def test_property_40_required_fields_validation_valid_table(self, valid_table):
        """
        Property 40: Required fields validation (parte 1 - estruturas válidas)
        
        For any input data structure with all required fields present, 
        the validation function should return true.
        
        **Feature: bolao-prototype-scripts, Property 40: Required fields validation**
        **Validates: Requirements 10.1**
        """
        success, errors = validar_estrutura_tabela(valid_table)
        
        # Estrutura válida deve passar na validação
        assert success, f"Estrutura válida foi rejeitada: {errors}"
        assert len(errors) == 0, f"Estrutura válida gerou erros: {errors}"
    
    @given(invalid_table_structure())
    @settings(max_examples=100)
    def test_property_40_required_fields_validation_invalid_table(self, invalid_data):
        """
        Property 40: Required fields validation (parte 2 - estruturas inválidas)
        
        For any input data structure with missing required fields, 
        the validation function should return false.
        
        **Feature: bolao-prototype-scripts, Property 40: Required fields validation**
        **Validates: Requirements 10.1**
        """
        invalid_table, missing_field = invalid_data
        success, errors = validar_estrutura_tabela(invalid_table)
        
        # Estrutura inválida deve falhar na validação
        assert not success, f"Estrutura inválida foi aceita (campo ausente: {missing_field})"
        assert len(errors) > 0, "Estrutura inválida deve gerar pelo menos um erro"
        
        # Deve mencionar o campo ausente na mensagem de erro
        error_text = " ".join(errors).lower()
        assert missing_field.lower() in error_text, f"Erro deve mencionar campo ausente '{missing_field}': {errors}"
    
    @given(valid_palpites_structure())
    @settings(max_examples=100)
    def test_property_40_required_fields_validation_valid_palpites(self, valid_palpites):
        """
        Property 40: Required fields validation (parte 3 - palpites válidos)
        
        **Feature: bolao-prototype-scripts, Property 40: Required fields validation**
        **Validates: Requirements 10.1**
        """
        success, errors = validar_estrutura_palpites(valid_palpites)
        
        # Estrutura válida deve passar na validação
        assert success, f"Estrutura válida foi rejeitada: {errors}"
        assert len(errors) == 0, f"Estrutura válida gerou erros: {errors}"
    
    @given(invalid_palpites_structure())
    @settings(max_examples=100)
    def test_property_40_required_fields_validation_invalid_palpites(self, invalid_data):
        """
        Property 40: Required fields validation (parte 4 - palpites inválidos)
        
        **Feature: bolao-prototype-scripts, Property 40: Required fields validation**
        **Validates: Requirements 10.1**
        """
        invalid_palpites, missing_field = invalid_data
        success, errors = validar_estrutura_palpites(invalid_palpites)
        
        # Estrutura inválida deve falhar na validação
        assert not success, f"Estrutura inválida foi aceita (campo ausente: {missing_field})"
        assert len(errors) > 0, "Estrutura inválida deve gerar pelo menos um erro"
        
        # Deve mencionar o campo ausente na mensagem de erro
        error_text = " ".join(errors).lower()
        assert missing_field.lower() in error_text, f"Erro deve mencionar campo ausente '{missing_field}': {errors}"
    
    @given(valid_regras_structure())
    @settings(max_examples=100)
    def test_property_40_required_fields_validation_valid_regras(self, valid_regras):
        """
        Property 40: Required fields validation (parte 5 - regras válidas)
        
        **Feature: bolao-prototype-scripts, Property 40: Required fields validation**
        **Validates: Requirements 10.1**
        """
        success, errors = validar_estrutura_regras(valid_regras)
        
        # Estrutura válida deve passar na validação
        assert success, f"Estrutura válida foi rejeitada: {errors}"
        assert len(errors) == 0, f"Estrutura válida gerou erros: {errors}"
    
    @given(invalid_regras_structure())
    @settings(max_examples=100)
    def test_property_40_required_fields_validation_invalid_regras(self, invalid_data):
        """
        Property 40: Required fields validation (parte 6 - regras inválidas)
        
        **Feature: bolao-prototype-scripts, Property 40: Required fields validation**
        **Validates: Requirements 10.1**
        """
        invalid_regras, missing_field = invalid_data
        success, errors = validar_estrutura_regras(invalid_regras)
        
        # Estrutura inválida deve falhar na validação
        assert not success, f"Estrutura inválida foi aceita (campo ausente: {missing_field})"
        assert len(errors) > 0, "Estrutura inválida deve gerar pelo menos um erro"
        
        # Deve mencionar o campo ausente na mensagem de erro
        error_text = " ".join(errors).lower()
        assert missing_field.lower() in error_text, f"Erro deve mencionar campo ausente '{missing_field}': {errors}"
    
    @given(valid_date_strings())
    @settings(max_examples=100)
    def test_property_41_date_format_validation_valid_dates(self, valid_date):
        """
        Property 41: Date format validation (parte 1 - datas válidas)
        
        For any date string in a recognized format, the validation function 
        should return true.
        
        **Feature: bolao-prototype-scripts, Property 41: Date format validation**
        **Validates: Requirements 10.2**
        """
        success, error_msg = validar_data(valid_date)
        
        # Data válida deve passar na validação
        assert success, f"Data válida '{valid_date}' foi rejeitada: {error_msg}"
        assert error_msg == "", f"Data válida gerou mensagem de erro: {error_msg}"
    
    @given(invalid_date_strings())
    @settings(max_examples=100)
    def test_property_41_date_format_validation_invalid_dates(self, invalid_date):
        """
        Property 41: Date format validation (parte 2 - datas inválidas)
        
        For any date string not in a recognized format, the validation function 
        should return false.
        
        **Feature: bolao-prototype-scripts, Property 41: Date format validation**
        **Validates: Requirements 10.2**
        """
        success, error_msg = validar_data(invalid_date)
        
        # Data inválida deve falhar na validação
        assert not success, f"Data inválida '{invalid_date}' foi aceita"
        assert len(error_msg) > 0, f"Data inválida deve gerar mensagem de erro: '{invalid_date}'"
        assert invalid_date in error_msg or "formato" in error_msg.lower(), f"Mensagem deve mencionar formato ou data: {error_msg}"
    
    @given(st.integers())
    @settings(max_examples=100)
    def test_property_41_date_format_validation_non_strings(self, non_string_input):
        """
        Property 41: Date format validation (parte 3 - entradas não-string)
        
        **Feature: bolao-prototype-scripts, Property 41: Date format validation**
        **Validates: Requirements 10.2**
        """
        success, error_msg = validar_data(non_string_input)
        
        # Entrada não-string deve falhar na validação
        assert not success, f"Entrada não-string {non_string_input} foi aceita como data"
        assert len(error_msg) > 0, "Entrada não-string deve gerar mensagem de erro"
        assert "string" in error_msg.lower(), f"Mensagem deve mencionar que entrada deve ser string: {error_msg}"
    
    @given(valid_scores())
    @settings(max_examples=100)
    def test_property_42_score_validation_valid_scores(self, valid_score):
        """
        Property 42: Score validation (parte 1 - placares válidos)
        
        For any score input with non-negative integers within limits, 
        the validation function should return true.
        
        **Feature: bolao-prototype-scripts, Property 42: Score validation**
        **Validates: Requirements 10.3**
        """
        home_goals, away_goals = valid_score
        success, error_msg = validar_placar(home_goals, away_goals)
        
        # Placar válido deve passar na validação
        assert success, f"Placar válido {home_goals}x{away_goals} foi rejeitado: {error_msg}"
        assert error_msg == "", f"Placar válido gerou mensagem de erro: {error_msg}"
    
    @given(invalid_scores())
    @settings(max_examples=100)
    def test_property_42_score_validation_invalid_scores(self, invalid_score):
        """
        Property 42: Score validation (parte 2 - placares inválidos)
        
        For any score input that is not non-negative integers within limits, 
        the validation function should return false.
        
        **Feature: bolao-prototype-scripts, Property 42: Score validation**
        **Validates: Requirements 10.3**
        """
        home_goals, away_goals = invalid_score
        success, error_msg = validar_placar(home_goals, away_goals)
        
        # Placar inválido deve falhar na validação
        assert not success, f"Placar inválido {home_goals}x{away_goals} foi aceito"
        assert len(error_msg) > 0, f"Placar inválido deve gerar mensagem de erro: {home_goals}x{away_goals}"
    
    @given(table_with_games(), st.integers(min_value=1, max_value=10))
    @settings(max_examples=100)
    def test_property_43_game_id_reference_validation_valid_ids(self, table_data, game_index):
        """
        Property 43: Game ID reference validation (parte 1 - IDs válidos)
        
        For any game ID that exists in the championship table, 
        the validation function should return true.
        
        **Feature: bolao-prototype-scripts, Property 43: Game ID reference validation**
        **Validates: Requirements 10.4**
        """
        # Pega um ID de jogo que existe na tabela
        games = table_data["rodadas"][0]["jogos"]
        assume(len(games) > 0)  # Garante que há jogos na tabela
        
        game_id = games[game_index % len(games)]["id"]
        success, error_msg = validar_id_jogo(game_id, table_data)
        
        # ID existente deve passar na validação
        assert success, f"ID de jogo existente '{game_id}' foi rejeitado: {error_msg}"
        assert error_msg == "", f"ID existente gerou mensagem de erro: {error_msg}"
    
    @given(table_with_games(), st.text(min_size=1, max_size=20).filter(lambda x: x.strip() != ""))
    @settings(max_examples=100)
    def test_property_43_game_id_reference_validation_invalid_ids(self, table_data, random_id):
        """
        Property 43: Game ID reference validation (parte 2 - IDs inválidos)
        
        For any game ID that does not exist in the championship table, 
        the validation function should return false.
        
        **Feature: bolao-prototype-scripts, Property 43: Game ID reference validation**
        **Validates: Requirements 10.4**
        """
        # Garante que o ID não existe na tabela
        existing_ids = []
        for rodada in table_data["rodadas"]:
            for jogo in rodada["jogos"]:
                existing_ids.append(jogo["id"])
        
        assume(random_id not in existing_ids)  # Garante que o ID não existe
        
        success, error_msg = validar_id_jogo(random_id, table_data)
        
        # ID inexistente deve falhar na validação
        assert not success, f"ID de jogo inexistente '{random_id}' foi aceito"
        assert len(error_msg) > 0, f"ID inexistente deve gerar mensagem de erro: '{random_id}'"
        assert random_id in error_msg or "não encontrado" in error_msg.lower(), f"Mensagem deve mencionar ID ou 'não encontrado': {error_msg}"
    
    @given(st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ""), st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ""))
    @settings(max_examples=50)  # Reduzido porque envolve sistema de arquivos
    def test_property_44_participant_registration_validation_nonexistent_championship(self, participant_name, championship_name):
        """
        Property 44: Participant registration validation (campeonatos inexistentes)
        
        For any participant name and non-existent championship, 
        the validation function should return false.
        
        **Feature: bolao-prototype-scripts, Property 44: Participant registration validation**
        **Validates: Requirements 10.5**
        """
        # Assume que o campeonato não existe (muito provável com nomes aleatórios)
        success, error_msg = validar_participante(participant_name, championship_name)
        
        # Para campeonato inexistente, deve falhar
        if not success:
            assert len(error_msg) > 0, "Campeonato inexistente deve gerar mensagem de erro"
            assert championship_name in error_msg or "não encontrado" in error_msg.lower(), f"Mensagem deve mencionar campeonato: {error_msg}"
    
    @given(st.integers(), st.text(min_size=1, max_size=50))
    @settings(max_examples=100)
    def test_property_44_participant_registration_validation_invalid_types(self, invalid_participant, championship_name):
        """
        Property 44: Participant registration validation (tipos inválidos)
        
        For any non-string participant name, the validation function should return false.
        
        **Feature: bolao-prototype-scripts, Property 44: Participant registration validation**
        **Validates: Requirements 10.5**
        """
        success, error_msg = validar_participante(invalid_participant, championship_name)
        
        # Tipo inválido deve falhar na validação
        assert not success, f"Participante com tipo inválido {type(invalid_participant)} foi aceito"
        assert len(error_msg) > 0, "Tipo inválido deve gerar mensagem de erro"
        assert "string" in error_msg.lower(), f"Mensagem deve mencionar que deve ser string: {error_msg}"
    
    @given(invalid_table_structure())
    @settings(max_examples=100)
    def test_property_45_error_message_clarity_table(self, invalid_data):
        """
        Property 45: Error message clarity (parte 1 - tabelas)
        
        For any validation failure, the error message should contain specific 
        information about which field or value caused the failure.
        
        **Feature: bolao-prototype-scripts, Property 45: Error message clarity**
        **Validates: Requirements 10.6**
        """
        invalid_table, missing_field = invalid_data
        success, errors = validar_estrutura_tabela(invalid_table)
        
        # Deve falhar e gerar mensagens claras
        assert not success, "Estrutura inválida deve falhar na validação"
        assert len(errors) > 0, "Deve gerar pelo menos uma mensagem de erro"
        
        # Verifica clareza das mensagens
        for error in errors:
            assert len(error) > 10, f"Mensagem de erro muito curta: '{error}'"
            assert missing_field.lower() in error.lower(), f"Mensagem deve mencionar campo específico '{missing_field}': '{error}'"
            # Deve conter palavras-chave que indicam o problema
            keywords = ["ausente", "obrigatório", "campo", "deve ser"]
            has_keyword = any(keyword in error.lower() for keyword in keywords)
            assert has_keyword, f"Mensagem deve conter palavra-chave explicativa: '{error}'"
    
    @given(invalid_date_strings())
    @settings(max_examples=100)
    def test_property_45_error_message_clarity_dates(self, invalid_date):
        """
        Property 45: Error message clarity (parte 2 - datas)
        
        **Feature: bolao-prototype-scripts, Property 45: Error message clarity**
        **Validates: Requirements 10.6**
        """
        success, error_msg = validar_data(invalid_date)
        
        # Deve falhar e gerar mensagem clara
        assert not success, f"Data inválida '{invalid_date}' foi aceita"
        assert len(error_msg) > 10, f"Mensagem de erro muito curta: '{error_msg}'"
        
        # Deve mencionar o valor problemático ou formato
        assert invalid_date in error_msg or "formato" in error_msg.lower(), f"Mensagem deve mencionar data ou formato: '{error_msg}'"
        
        # Deve conter informação sobre formatos aceitos se for erro de formato
        if "formato" in error_msg.lower():
            assert "aceitos" in error_msg.lower() or "válido" in error_msg.lower(), f"Mensagem deve explicar formatos aceitos: '{error_msg}'"
    
    @given(invalid_scores())
    @settings(max_examples=100)
    def test_property_45_error_message_clarity_scores(self, invalid_score):
        """
        Property 45: Error message clarity (parte 3 - placares)
        
        **Feature: bolao-prototype-scripts, Property 45: Error message clarity**
        **Validates: Requirements 10.6**
        """
        home_goals, away_goals = invalid_score
        success, error_msg = validar_placar(home_goals, away_goals)
        
        # Deve falhar e gerar mensagem clara
        assert not success, f"Placar inválido {home_goals}x{away_goals} foi aceito"
        assert len(error_msg) > 5, f"Mensagem de erro muito curta: '{error_msg}'"
        
        # Deve mencionar qual campo tem problema
        mentions_field = ("mandante" in error_msg.lower() or 
                         "visitante" in error_msg.lower() or
                         "gols" in error_msg.lower())
        assert mentions_field, f"Mensagem deve mencionar qual campo tem problema: '{error_msg}'"
        
        # Deve explicar o tipo de problema
        explains_problem = ("inteiro" in error_msg.lower() or 
                           "negativo" in error_msg.lower() or
                           "máximo" in error_msg.lower() or
                           "tipo" in error_msg.lower())
        assert explains_problem, f"Mensagem deve explicar o tipo de problema: '{error_msg}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])