"""
Testes de propriedade para o script de importação de palpites.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de importação de palpites definidas no design document.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, settings, strategies as st, assume
from datetime import datetime

from src.scripts.importar_palpites import (
    atualizar_palpites_participante,
    validar_palpites_contra_tabela,
    normalizar_palpites_times,
    salvar_palpites_participante,
    carregar_palpites_participante
)


# Generators para property-based testing
@st.composite
def valid_participant_data(draw):
    """
    Gera dados válidos de participante para testar atualizações.
    """
    participant_names = [
        "Mario Silva", "João Santos", "Ana Paula", "Carlos Alberto", 
        "Maria José", "José Santos", "Paula Lima", "Pedro Oliveira"
    ]
    
    participant_name = draw(st.sampled_from(participant_names))
    participant_code = draw(st.text(alphabet="0123456789", min_size=4, max_size=4))
    championship_name = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=5, max_size=20))
    season = str(draw(st.integers(min_value=2020, max_value=2030)))
    
    return {
        "apostador": participant_name,
        "codigo_apostador": participant_code,
        "campeonato": championship_name,
        "temporada": season,
        "palpites": []
    }


@st.composite
def valid_prediction_data(draw):
    """
    Gera dados válidos de palpite para testar validação e atualização.
    """
    teams = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético-MG",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional"
    ]
    
    home_team = draw(st.sampled_from(teams))
    away_team = draw(st.sampled_from(teams))
    assume(home_team != away_team)  # Times diferentes
    
    home_goals = draw(st.integers(min_value=0, max_value=10))
    away_goals = draw(st.integers(min_value=0, max_value=10))
    
    return {
        "id": f"jogo-{draw(st.integers(min_value=1, max_value=999)):03d}",
        "mandante": home_team,
        "visitante": away_team,
        "palpite_mandante": home_goals,
        "palpite_visitante": away_goals
    }


@st.composite
def valid_table_data(draw):
    """
    Gera dados válidos de tabela para testar validação de palpites.
    """
    teams = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético-MG",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional"
    ]
    
    championship_name = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz-", min_size=5, max_size=20))
    season = str(draw(st.integers(min_value=2020, max_value=2030)))
    round_number = draw(st.integers(min_value=1, max_value=10))
    
    # Gera jogos para a rodada
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
            "id": f"jogo-{round_number:02d}-{game_num+1:02d}",
            "mandante": home_team,
            "visitante": away_team,
            "data": "2024-01-01T10:00:00Z",
            "local": f"Estádio {game_num+1}",
            "gols_mandante": 0,
            "gols_visitante": 0,
            "status": "agendado",
            "obrigatorio": True
        })
    
    return {
        "campeonato": championship_name,
        "temporada": season,
        "rodada_atual": 0,
        "data_atualizacao": "2024-01-01T10:00:00Z",
        "codigo_campeonato": "12345",
        "rodadas": [
            {
                "numero": round_number,
                "jogos": games
            }
        ]
    }, round_number


@st.composite
def prediction_matching_table(draw):
    """
    Gera palpite que corresponde a um jogo na tabela.
    """
    table_data, round_number = draw(valid_table_data())
    
    # Seleciona um jogo da tabela
    games = table_data["rodadas"][0]["jogos"]
    assume(len(games) > 0)
    
    selected_game = draw(st.sampled_from(games))
    
    # Cria palpite baseado no jogo selecionado
    prediction = {
        "mandante": selected_game["mandante"],
        "visitante": selected_game["visitante"],
        "gols_mandante": draw(st.integers(min_value=0, max_value=10)),
        "gols_visitante": draw(st.integers(min_value=0, max_value=10))
    }
    
    return prediction, table_data, round_number, selected_game


@st.composite
def multiple_predictions_for_round(draw):
    """
    Gera múltiplos palpites para uma rodada.
    """
    table_data, round_number = draw(valid_table_data())
    games = table_data["rodadas"][0]["jogos"]
    assume(len(games) >= 2)
    
    # Seleciona alguns jogos para fazer palpites
    num_predictions = draw(st.integers(min_value=1, max_value=min(len(games), 3)))
    
    # Seleciona jogos únicos manualmente para evitar problema com unhashable dict
    selected_games = []
    available_games = games.copy()
    
    for _ in range(num_predictions):
        if not available_games:
            break
        game = draw(st.sampled_from(available_games))
        selected_games.append(game)
        available_games.remove(game)
    
    predictions = []
    for game in selected_games:
        prediction = {
            "mandante": game["mandante"],
            "visitante": game["visitante"],
            "gols_mandante": draw(st.integers(min_value=0, max_value=10)),
            "gols_visitante": draw(st.integers(min_value=0, max_value=10))
        }
        predictions.append(prediction)
    
    return predictions, table_data, round_number


@st.composite
def extra_bets_data(draw):
    """
    Gera dados de apostas extras.
    """
    num_extras = draw(st.integers(min_value=0, max_value=3))
    extras = []
    
    teams = ["Flamengo", "Palmeiras", "São Paulo", "Corinthians"]
    
    for i in range(num_extras):
        home_team = draw(st.sampled_from(teams))
        away_team = draw(st.sampled_from(teams))
        assume(home_team != away_team)
        
        extra = {
            "id": f"jogo-extra-{i+1:02d}",
            "mandante": home_team,
            "visitante": away_team,
            "palpite_mandante": draw(st.integers(min_value=0, max_value=10)),
            "palpite_visitante": draw(st.integers(min_value=0, max_value=10)),
            "tipo": "extra",
            "identificador": f"Jogo {i+1}"
        }
        extras.append(extra)
    
    return extras


class TestImportarPalpitesProperties:
    """Testes de propriedade para importação de palpites."""
    
    @given(valid_participant_data(), prediction_matching_table())
    @settings(max_examples=100)
    def test_property_18_prediction_file_update_single(self, participant_data, prediction_data):
        """
        Property 18: Prediction file update (parte 1 - palpite único)
        
        For any validated prediction, after processing, the participant's "palpites.json" 
        file should contain an entry for that prediction with correct game ID and score values.
        
        **Feature: bolao-prototype-scripts, Property 18: Prediction file update**
        **Validates: Requirements 5.7**
        """
        prediction, table_data, round_number, selected_game = prediction_data
        
        # Valida o palpite contra a tabela
        validated_predictions, errors = validar_palpites_contra_tabela([prediction], round_number, table_data)
        
        # Deve validar com sucesso
        assert len(errors) == 0, f"Palpite válido não deveria ter erros: {errors}"
        assert len(validated_predictions) == 1, f"Deveria validar exatamente 1 palpite, mas validou {len(validated_predictions)}"
        
        validated_prediction = validated_predictions[0]
        
        # Atualiza dados do participante
        updated_data = atualizar_palpites_participante(
            participant_data.copy(), round_number, validated_predictions, []
        )
        
        # Verifica que os dados foram atualizados corretamente
        assert "palpites" in updated_data, "Dados atualizados devem ter campo 'palpites'"
        assert len(updated_data["palpites"]) == 1, f"Deveria ter exatamente 1 entrada de rodada, mas tem {len(updated_data['palpites'])}"
        
        round_entry = updated_data["palpites"][0]
        
        # Verifica estrutura da entrada da rodada
        assert round_entry["rodada"] == round_number, f"Número da rodada não confere: {round_entry['rodada']} vs {round_number}"
        assert "data_palpite" in round_entry, "Entrada da rodada deve ter campo 'data_palpite'"
        assert "jogos" in round_entry, "Entrada da rodada deve ter campo 'jogos'"
        assert len(round_entry["jogos"]) == 1, f"Deveria ter exatamente 1 jogo, mas tem {len(round_entry['jogos'])}"
        
        game_entry = round_entry["jogos"][0]
        
        # Verifica que o palpite foi salvo corretamente
        assert game_entry["id"] == selected_game["id"], f"ID do jogo não confere: {game_entry['id']} vs {selected_game['id']}"
        assert game_entry["mandante"] == selected_game["mandante"], f"Time mandante não confere: {game_entry['mandante']} vs {selected_game['mandante']}"
        assert game_entry["visitante"] == selected_game["visitante"], f"Time visitante não confere: {game_entry['visitante']} vs {selected_game['visitante']}"
        assert game_entry["palpite_mandante"] == prediction["gols_mandante"], f"Palpite mandante não confere: {game_entry['palpite_mandante']} vs {prediction['gols_mandante']}"
        assert game_entry["palpite_visitante"] == prediction["gols_visitante"], f"Palpite visitante não confere: {game_entry['palpite_visitante']} vs {prediction['gols_visitante']}"
        
        # Verifica que timestamp foi adicionado e é válido
        try:
            datetime.fromisoformat(round_entry["data_palpite"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail(f"Timestamp inválido: {round_entry['data_palpite']}")
    
    @given(valid_participant_data(), multiple_predictions_for_round())
    @settings(max_examples=50)  # Reduzido porque é mais complexo
    def test_property_18_prediction_file_update_multiple(self, participant_data, predictions_data):
        """
        Property 18: Prediction file update (parte 2 - múltiplos palpites)
        
        For any set of validated predictions for the same round, after processing, 
        the participant's "palpites.json" file should contain entries for all 
        predictions with correct game IDs and score values.
        
        **Feature: bolao-prototype-scripts, Property 18: Prediction file update**
        **Validates: Requirements 5.7**
        """
        predictions, table_data, round_number = predictions_data
        
        # Valida os palpites contra a tabela
        validated_predictions, errors = validar_palpites_contra_tabela(predictions, round_number, table_data)
        
        # Deve validar com sucesso
        assert len(errors) == 0, f"Palpites válidos não deveriam ter erros: {errors}"
        assert len(validated_predictions) == len(predictions), f"Deveria validar {len(predictions)} palpites, mas validou {len(validated_predictions)}"
        
        # Atualiza dados do participante
        updated_data = atualizar_palpites_participante(
            participant_data.copy(), round_number, validated_predictions, []
        )
        
        # Verifica que os dados foram atualizados corretamente
        assert "palpites" in updated_data, "Dados atualizados devem ter campo 'palpites'"
        assert len(updated_data["palpites"]) == 1, f"Deveria ter exatamente 1 entrada de rodada, mas tem {len(updated_data['palpites'])}"
        
        round_entry = updated_data["palpites"][0]
        
        # Verifica estrutura da entrada da rodada
        assert round_entry["rodada"] == round_number, f"Número da rodada não confere: {round_entry['rodada']} vs {round_number}"
        assert "data_palpite" in round_entry, "Entrada da rodada deve ter campo 'data_palpite'"
        assert "jogos" in round_entry, "Entrada da rodada deve ter campo 'jogos'"
        assert len(round_entry["jogos"]) == len(predictions), f"Deveria ter {len(predictions)} jogos, mas tem {len(round_entry['jogos'])}"
        
        # Verifica que todos os palpites foram salvos corretamente
        for original_prediction in predictions:
            # Procura o palpite correspondente nos dados salvos
            found = False
            for game_entry in round_entry["jogos"]:
                if (game_entry["mandante"] == original_prediction["mandante"] and
                    game_entry["visitante"] == original_prediction["visitante"]):
                    
                    # Verifica que os dados estão corretos
                    assert game_entry["palpite_mandante"] == original_prediction["gols_mandante"], f"Palpite mandante não confere para {original_prediction['mandante']} vs {original_prediction['visitante']}"
                    assert game_entry["palpite_visitante"] == original_prediction["gols_visitante"], f"Palpite visitante não confere para {original_prediction['mandante']} vs {original_prediction['visitante']}"
                    assert "id" in game_entry, f"Entrada do jogo deve ter campo 'id': {game_entry}"
                    
                    found = True
                    break
            
            assert found, f"Palpite não encontrado nos dados salvos: {original_prediction['mandante']} vs {original_prediction['visitante']}"
    
    @given(valid_participant_data(), prediction_matching_table(), extra_bets_data())
    @settings(max_examples=50)  # Reduzido porque é mais complexo
    def test_property_18_prediction_file_update_with_extras(self, participant_data, prediction_data, extra_bets):
        """
        Property 18: Prediction file update (parte 3 - com apostas extras)
        
        For any validated predictions including extra bets, after processing, 
        the participant's "palpites.json" file should contain entries for both 
        regular predictions and extra bets with appropriate identification.
        
        **Feature: bolao-prototype-scripts, Property 18: Prediction file update**
        **Validates: Requirements 5.7**
        """
        prediction, table_data, round_number, selected_game = prediction_data
        
        # Valida o palpite regular contra a tabela
        validated_predictions, errors = validar_palpites_contra_tabela([prediction], round_number, table_data)
        
        # Deve validar com sucesso
        assert len(errors) == 0, f"Palpite válido não deveria ter erros: {errors}"
        assert len(validated_predictions) == 1, f"Deveria validar exatamente 1 palpite, mas validou {len(validated_predictions)}"
        
        # Atualiza dados do participante com palpites regulares e extras
        updated_data = atualizar_palpites_participante(
            participant_data.copy(), round_number, validated_predictions, extra_bets
        )
        
        # Verifica que os dados foram atualizados corretamente
        assert "palpites" in updated_data, "Dados atualizados devem ter campo 'palpites'"
        assert len(updated_data["palpites"]) == 1, f"Deveria ter exatamente 1 entrada de rodada, mas tem {len(updated_data['palpites'])}"
        
        round_entry = updated_data["palpites"][0]
        
        # Verifica estrutura da entrada da rodada
        assert round_entry["rodada"] == round_number, f"Número da rodada não confere: {round_entry['rodada']} vs {round_number}"
        assert "data_palpite" in round_entry, "Entrada da rodada deve ter campo 'data_palpite'"
        assert "jogos" in round_entry, "Entrada da rodada deve ter campo 'jogos'"
        assert len(round_entry["jogos"]) == 1, f"Deveria ter exatamente 1 jogo regular, mas tem {len(round_entry['jogos'])}"
        
        # Verifica palpite regular
        game_entry = round_entry["jogos"][0]
        assert game_entry["id"] == selected_game["id"], f"ID do jogo não confere: {game_entry['id']} vs {selected_game['id']}"
        assert game_entry["palpite_mandante"] == prediction["gols_mandante"], f"Palpite mandante não confere: {game_entry['palpite_mandante']} vs {prediction['gols_mandante']}"
        assert game_entry["palpite_visitante"] == prediction["gols_visitante"], f"Palpite visitante não confere: {game_entry['palpite_visitante']} vs {prediction['gols_visitante']}"
        
        # Verifica apostas extras se houver
        if extra_bets:
            assert "apostas_extras" in round_entry, "Entrada da rodada deve ter campo 'apostas_extras' quando há apostas extras"
            assert len(round_entry["apostas_extras"]) == len(extra_bets), f"Deveria ter {len(extra_bets)} apostas extras, mas tem {len(round_entry['apostas_extras'])}"
            
            # Verifica cada aposta extra
            for original_extra in extra_bets:
                found = False
                for saved_extra in round_entry["apostas_extras"]:
                    if (saved_extra.get("identificador") == original_extra.get("identificador") and
                        saved_extra.get("mandante") == original_extra.get("mandante") and
                        saved_extra.get("visitante") == original_extra.get("visitante")):
                        
                        # Verifica que os dados estão corretos
                        assert saved_extra["palpite_mandante"] == original_extra["palpite_mandante"], f"Palpite mandante da aposta extra não confere"
                        assert saved_extra["palpite_visitante"] == original_extra["palpite_visitante"], f"Palpite visitante da aposta extra não confere"
                        assert saved_extra.get("tipo") == "extra", f"Tipo da aposta extra deve ser 'extra'"
                        
                        found = True
                        break
                
                assert found, f"Aposta extra não encontrada nos dados salvos: {original_extra}"
        else:
            # Se não há apostas extras, o campo não deve existir ou deve estar vazio
            if "apostas_extras" in round_entry:
                assert len(round_entry["apostas_extras"]) == 0, "Campo 'apostas_extras' deve estar vazio quando não há apostas extras"
    
    @given(valid_participant_data(), prediction_matching_table())
    @settings(max_examples=50)
    def test_property_18_prediction_file_update_persistence(self, participant_data, prediction_data):
        """
        Property 18: Prediction file update (parte 4 - persistência em arquivo)
        
        For any validated prediction, after saving to file and reloading, 
        the data should be identical to what was saved.
        
        **Feature: bolao-prototype-scripts, Property 18: Prediction file update**
        **Validates: Requirements 5.7**
        """
        prediction, table_data, round_number, selected_game = prediction_data
        
        # Valida o palpite contra a tabela
        validated_predictions, errors = validar_palpites_contra_tabela([prediction], round_number, table_data)
        
        # Deve validar com sucesso
        assert len(errors) == 0, f"Palpite válido não deveria ter erros: {errors}"
        assert len(validated_predictions) == 1, f"Deveria validar exatamente 1 palpite, mas validou {len(validated_predictions)}"
        
        # Atualiza dados do participante
        updated_data = atualizar_palpites_participante(
            participant_data.copy(), round_number, validated_predictions, []
        )
        
        # Cria diretório temporário para teste
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Salva os dados
            save_success = salvar_palpites_participante(temp_path, updated_data)
            assert save_success, "Falha ao salvar dados do participante"
            
            # Verifica que o arquivo foi criado
            palpites_file = temp_path / "palpites.json"
            assert palpites_file.exists(), "Arquivo palpites.json não foi criado"
            
            # Carrega os dados salvos
            loaded_data = carregar_palpites_participante(temp_path)
            assert loaded_data is not None, "Falha ao carregar dados salvos"
            
            # Verifica que os dados carregados são idênticos aos salvos
            assert loaded_data["apostador"] == updated_data["apostador"], "Nome do apostador não confere após reload"
            assert loaded_data["codigo_apostador"] == updated_data["codigo_apostador"], "Código do apostador não confere após reload"
            assert loaded_data["campeonato"] == updated_data["campeonato"], "Nome do campeonato não confere após reload"
            assert loaded_data["temporada"] == updated_data["temporada"], "Temporada não confere após reload"
            
            # Verifica estrutura dos palpites
            assert len(loaded_data["palpites"]) == len(updated_data["palpites"]), "Número de entradas de palpites não confere após reload"
            
            if len(loaded_data["palpites"]) > 0:
                loaded_round = loaded_data["palpites"][0]
                original_round = updated_data["palpites"][0]
                
                assert loaded_round["rodada"] == original_round["rodada"], "Número da rodada não confere após reload"
                assert loaded_round["data_palpite"] == original_round["data_palpite"], "Data do palpite não confere após reload"
                assert len(loaded_round["jogos"]) == len(original_round["jogos"]), "Número de jogos não confere após reload"
                
                # Verifica cada jogo
                for i, loaded_game in enumerate(loaded_round["jogos"]):
                    original_game = original_round["jogos"][i]
                    
                    assert loaded_game["id"] == original_game["id"], f"ID do jogo {i} não confere após reload"
                    assert loaded_game["mandante"] == original_game["mandante"], f"Time mandante do jogo {i} não confere após reload"
                    assert loaded_game["visitante"] == original_game["visitante"], f"Time visitante do jogo {i} não confere após reload"
                    assert loaded_game["palpite_mandante"] == original_game["palpite_mandante"], f"Palpite mandante do jogo {i} não confere após reload"
                    assert loaded_game["palpite_visitante"] == original_game["palpite_visitante"], f"Palpite visitante do jogo {i} não confere após reload"
    
    @given(valid_participant_data(), st.integers(min_value=1, max_value=5))
    @settings(max_examples=50)
    def test_property_18_prediction_file_update_round_isolation(self, participant_data, num_rounds):
        """
        Property 18: Prediction file update (parte 5 - isolamento entre rodadas)
        
        For any participant with predictions in multiple rounds, updating one round 
        should not affect predictions from other rounds.
        
        **Feature: bolao-prototype-scripts, Property 18: Prediction file update**
        **Validates: Requirements 5.7**
        """
        # Cria dados iniciais com múltiplas rodadas
        initial_data = participant_data.copy()
        
        # Adiciona palpites para várias rodadas
        for round_num in range(1, num_rounds + 1):
            round_entry = {
                "rodada": round_num,
                "data_palpite": f"2024-01-{round_num:02d}T10:00:00Z",
                "jogos": [
                    {
                        "id": f"jogo-{round_num:02d}-01",
                        "mandante": "Flamengo",
                        "visitante": "Palmeiras",
                        "palpite_mandante": round_num,  # Usa número da rodada como placar para diferenciação
                        "palpite_visitante": round_num + 1
                    }
                ]
            }
            initial_data["palpites"].append(round_entry)
        
        # Seleciona uma rodada para atualizar (não a primeira nem a última)
        target_round = min(2, num_rounds)
        
        # Cria novos palpites para a rodada alvo
        new_predictions = [
            {
                "id": f"jogo-{target_round:02d}-02",
                "mandante": "São Paulo",
                "visitante": "Corinthians",
                "palpite_mandante": 99,  # Valor único para identificar
                "palpite_visitante": 88
            }
        ]
        
        # Atualiza apenas a rodada alvo
        updated_data = atualizar_palpites_participante(
            initial_data.copy(), target_round, new_predictions, []
        )
        
        # Verifica que o número total de rodadas não mudou
        assert len(updated_data["palpites"]) == num_rounds, f"Número de rodadas mudou: {len(updated_data['palpites'])} vs {num_rounds}"
        
        # Verifica que outras rodadas não foram afetadas
        for round_entry in updated_data["palpites"]:
            round_num = round_entry["rodada"]
            
            if round_num != target_round:
                # Esta rodada não deveria ter mudado
                original_entry = None
                for orig_entry in initial_data["palpites"]:
                    if orig_entry["rodada"] == round_num:
                        original_entry = orig_entry
                        break
                
                assert original_entry is not None, f"Rodada original {round_num} não encontrada"
                
                # Verifica que os dados são idênticos
                assert round_entry["data_palpite"] == original_entry["data_palpite"], f"Data da rodada {round_num} foi alterada"
                assert len(round_entry["jogos"]) == len(original_entry["jogos"]), f"Número de jogos da rodada {round_num} foi alterado"
                
                for i, game in enumerate(round_entry["jogos"]):
                    original_game = original_entry["jogos"][i]
                    assert game["id"] == original_game["id"], f"ID do jogo na rodada {round_num} foi alterado"
                    assert game["palpite_mandante"] == original_game["palpite_mandante"], f"Palpite mandante na rodada {round_num} foi alterado"
                    assert game["palpite_visitante"] == original_game["palpite_visitante"], f"Palpite visitante na rodada {round_num} foi alterado"
            
            else:
                # Esta é a rodada alvo - deve ter os novos palpites
                found_new_prediction = False
                for game in round_entry["jogos"]:
                    if (game["mandante"] == "São Paulo" and 
                        game["visitante"] == "Corinthians" and
                        game["palpite_mandante"] == 99 and
                        game["palpite_visitante"] == 88):
                        found_new_prediction = True
                        break
                
                assert found_new_prediction, f"Novo palpite não encontrado na rodada alvo {target_round}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])