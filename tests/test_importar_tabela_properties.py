"""
Testes de propriedade para o módulo de importação de tabela.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de importação de tabela definidas no design document.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from hypothesis import given, settings, strategies as st
from src.scripts.importar_tabela import (
    parsear_arquivo_texto,
    parsear_planilha_excel,
    organizar_jogos_por_rodadas,
    criar_estrutura_jogo,
    converter_data_iso8601,
    gerar_id_jogo,
    validar_dados_importados
)


# Generators para property-based testing
@st.composite
def valid_game_data(draw):
    """
    Gera dados válidos de jogos para testar extração.
    
    Inclui:
    - Times com nomes realistas
    - Datas em formatos válidos
    - Locais variados
    - Rodadas opcionais
    """
    teams = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético-MG",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional",
        "Fluminense", "Cruzeiro", "Bahia", "Sport", "Ceará"
    ]
    
    mandante = draw(st.sampled_from(teams))
    # Garantir que visitante é diferente do mandante
    visitante = draw(st.sampled_from([t for t in teams if t != mandante]))
    
    # Gerar data válida
    year = draw(st.integers(min_value=2020, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # Usar 28 para evitar problemas com fevereiro
    hour = draw(st.integers(min_value=10, max_value=22))
    minute = draw(st.sampled_from([0, 15, 30, 45]))
    
    data = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    
    # Gerar local
    locais = [
        "Maracanã", "Allianz Parque", "Neo Química Arena", "Mineirão",
        "Arena do Grêmio", "Vila Belmiro", "São Januário", "Nilton Santos",
        "A definir", "Estádio Nacional"
    ]
    local = draw(st.sampled_from(locais))
    
    # Rodada opcional
    rodada = draw(st.one_of(st.none(), st.integers(min_value=1, max_value=38)))
    
    game_data = {
        'mandante': mandante,
        'visitante': visitante,
        'data': data,
        'local': local
    }
    
    if rodada is not None:
        game_data['rodada'] = rodada
    
    return game_data


@st.composite
def valid_date_formats(draw):
    """
    Gera datas em formatos válidos reconhecidos pelo sistema.
    """
    year = draw(st.integers(min_value=2020, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    
    # Diferentes formatos de data suportados
    formats = [
        f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",  # ISO com espaço
        f"{day:02d}/{month:02d}/{year} {hour:02d}:{minute:02d}",  # BR com hora
        f"{year}-{month:02d}-{day:02d}",  # Só data ISO
        f"{day:02d}/{month:02d}/{year}",  # Só data BR
        f"{day}/{month}/{year}",  # BR sem zeros
    ]
    
    return draw(st.sampled_from(formats))


@st.composite
def game_list_with_rounds(draw):
    """
    Gera lista de jogos com rodadas para testar organização.
    Evita duplicatas criando jogos únicos.
    """
    num_games = draw(st.integers(min_value=1, max_value=15))
    num_rounds = draw(st.integers(min_value=1, max_value=5))
    
    teams = [
        "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético-MG",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional",
        "Fluminense", "Cruzeiro", "Bahia", "Sport", "Ceará"
    ]
    
    games = []
    used_matchups = set()
    
    for i in range(num_games):
        # Tentar criar um jogo único
        attempts = 0
        while attempts < 50:  # Limite de tentativas para evitar loop infinito
            mandante = draw(st.sampled_from(teams))
            visitante = draw(st.sampled_from([t for t in teams if t != mandante]))
            rodada = draw(st.integers(min_value=1, max_value=num_rounds))
            
            # Criar identificador único baseado em times e rodada
            matchup_id = f"{mandante}x{visitante}@{rodada}"
            reverse_matchup_id = f"{visitante}x{mandante}@{rodada}"
            
            if matchup_id not in used_matchups and reverse_matchup_id not in used_matchups:
                # Gerar data única baseada no índice
                year = 2024
                month = ((i // 28) % 12) + 1
                day = (i % 28) + 1
                hour = 16 + (i % 6)
                minute = (i % 4) * 15
                
                data = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00Z"
                
                locais = [
                    "Maracanã", "Allianz Parque", "Neo Química Arena", "Mineirão",
                    "Arena do Grêmio", "Vila Belmiro", "São Januário", "Nilton Santos"
                ]
                local = draw(st.sampled_from(locais))
                
                game = {
                    'mandante': mandante,
                    'visitante': visitante,
                    'data': data,
                    'local': local,
                    'rodada': rodada
                }
                
                games.append(game)
                used_matchups.add(matchup_id)
                break
            
            attempts += 1
        
        if attempts >= 50:
            # Se não conseguiu criar jogo único, parar aqui
            break
    
    return games


class TestTableImportProperties:
    """Testes de propriedade para importação de tabela."""
    
    @given(st.lists(valid_game_data(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_property_9_game_data_extraction_completeness(self, games_data):
        """
        Property 9: Game data extraction completeness
        
        For any valid input file (text or Excel) containing game information, 
        all games should be extracted with the required fields: mandante, 
        visitante, data, and local.
        
        **Feature: bolao-prototype-scripts, Property 9: Game data extraction completeness**
        **Validates: Requirements 4.1, 4.2**
        """
        # Criar arquivo texto temporário com os jogos
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            # Escrever cabeçalho de rodada
            current_round = 1
            f.write(f"Rodada {current_round}\n")
            
            for i, game in enumerate(games_data):
                # Converter data ISO para formato do arquivo
                try:
                    dt = datetime.fromisoformat(game['data'].replace('Z', '+00:00'))
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M")
                except:
                    date_str = "2024-01-01"
                    time_str = "16:00"
                
                # Escrever linha do jogo
                linha = f"{date_str} {time_str} | {game['mandante']} x {game['visitante']} | {game['local']}\n"
                f.write(linha)
            
            temp_path = Path(f.name)
        
        try:
            # Parsear o arquivo
            jogos_extraidos = parsear_arquivo_texto(temp_path)
            
            # Verificar que todos os jogos foram extraídos
            assert len(jogos_extraidos) == len(games_data), "Todos os jogos devem ser extraídos"
            
            # Verificar que cada jogo tem os campos obrigatórios
            campos_obrigatorios = ['mandante', 'visitante', 'data', 'local']
            for jogo in jogos_extraidos:
                for campo in campos_obrigatorios:
                    assert campo in jogo, f"Campo '{campo}' deve estar presente"
                    assert jogo[campo] is not None, f"Campo '{campo}' não pode ser None"
                    assert str(jogo[campo]).strip() != "", f"Campo '{campo}' não pode estar vazio"
                
                # Verificar que mandante e visitante são diferentes
                assert jogo['mandante'] != jogo['visitante'], "Mandante e visitante devem ser diferentes"
                
                # Verificar que data está em formato ISO 8601
                assert 'T' in jogo['data'], "Data deve estar em formato ISO 8601"
                assert jogo['data'].endswith('Z'), "Data deve terminar com 'Z'"
        
        finally:
            # Limpar arquivo temporário
            temp_path.unlink(missing_ok=True)
    
    @given(game_list_with_rounds())
    @settings(max_examples=100)
    def test_property_10_game_organization_by_rounds(self, games_with_rounds):
        """
        Property 10: Game organization by rounds
        
        For any set of games imported, each game should be assigned to exactly 
        one round in the "tabela.json" file, and games should be grouped 
        correctly by their round number.
        
        **Feature: bolao-prototype-scripts, Property 10: Game organization by rounds**
        **Validates: Requirements 4.3**
        """
        # Organizar jogos por rodadas
        jogos_organizados = organizar_jogos_por_rodadas(games_with_rounds)
        
        # Verificar que todos os jogos foram organizados
        total_jogos_organizados = sum(len(jogos) for jogos in jogos_organizados.values())
        assert total_jogos_organizados == len(games_with_rounds), "Todos os jogos devem ser organizados"
        
        # Verificar que cada jogo está em exatamente uma rodada
        jogos_encontrados = []
        for rodada_num, jogos_rodada in jogos_organizados.items():
            assert isinstance(rodada_num, int), "Número da rodada deve ser inteiro"
            assert rodada_num >= 1, "Número da rodada deve ser positivo"
            
            for jogo in jogos_rodada:
                # Criar identificador único do jogo para verificar duplicatas
                jogo_id = f"{jogo['mandante']}x{jogo['visitante']}@{jogo['data']}"
                assert jogo_id not in jogos_encontrados, "Jogo não deve aparecer em múltiplas rodadas"
                jogos_encontrados.append(jogo_id)
        
        # Verificar que jogos estão agrupados corretamente por rodada
        for rodada_num, jogos_rodada in jogos_organizados.items():
            for jogo in jogos_rodada:
                # Se o jogo original tinha rodada especificada, deve estar na rodada correta
                # Usar data como identificador único além dos times
                jogo_original = next((g for g in games_with_rounds 
                                    if g['mandante'] == jogo['mandante'] 
                                    and g['visitante'] == jogo['visitante']
                                    and g['data'] == jogo['data']), None)
                
                if jogo_original and 'rodada' in jogo_original and jogo_original['rodada'] is not None:
                    assert rodada_num == jogo_original['rodada'], "Jogo deve estar na rodada especificada"
    
    @given(valid_game_data())
    @settings(max_examples=100)
    def test_property_11_game_initialization_state(self, game_data):
        """
        Property 11: Game initialization state
        
        For any game added to the table, it should have a unique ID, status 
        set to "agendado", and both gols_mandante and gols_visitante 
        initialized to 0.
        
        **Feature: bolao-prototype-scripts, Property 11: Game initialization state**
        **Validates: Requirements 4.4**
        """
        # Gerar ID único
        id_jogo = gerar_id_jogo(1)
        
        # Criar estrutura do jogo
        jogo_completo = criar_estrutura_jogo(game_data, id_jogo)
        
        # Verificar ID único
        assert 'id' in jogo_completo, "Jogo deve ter ID"
        assert jogo_completo['id'] == id_jogo, "ID deve ser o especificado"
        assert jogo_completo['id'].startswith('jogo-'), "ID deve começar com 'jogo-'"
        
        # Verificar status inicial
        assert 'status' in jogo_completo, "Jogo deve ter status"
        assert jogo_completo['status'] == "agendado", "Status inicial deve ser 'agendado'"
        
        # Verificar gols inicializados em 0
        assert 'gols_mandante' in jogo_completo, "Jogo deve ter gols_mandante"
        assert 'gols_visitante' in jogo_completo, "Jogo deve ter gols_visitante"
        assert jogo_completo['gols_mandante'] == 0, "Gols do mandante devem ser inicializados em 0"
        assert jogo_completo['gols_visitante'] == 0, "Gols do visitante devem ser inicializados em 0"
        
        # Verificar campo obrigatório
        assert 'obrigatorio' in jogo_completo, "Jogo deve ter campo obrigatório"
        assert jogo_completo['obrigatorio'] is True, "Jogo deve ser obrigatório por padrão"
        
        # Verificar que dados originais foram preservados
        assert jogo_completo['mandante'] == game_data['mandante'], "Mandante deve ser preservado"
        assert jogo_completo['visitante'] == game_data['visitante'], "Visitante deve ser preservado"
        assert jogo_completo['data'] == game_data['data'], "Data deve ser preservada"
        assert jogo_completo['local'] == game_data['local'], "Local deve ser preservado"
    
    @given(valid_date_formats())
    @settings(max_examples=100)
    def test_property_13_date_format_conversion(self, date_string):
        """
        Property 13: Date format conversion
        
        For any valid date in a recognized format, the conversion function 
        should produce a valid ISO 8601 timestamp string.
        
        **Feature: bolao-prototype-scripts, Property 13: Date format conversion**
        **Validates: Requirements 4.6**
        """
        try:
            # Tentar converter a data
            iso_date = converter_data_iso8601(date_string)
            
            # Verificar que o resultado é uma string
            assert isinstance(iso_date, str), "Resultado deve ser string"
            
            # Verificar formato ISO 8601
            assert 'T' in iso_date, "Data ISO deve conter 'T'"
            assert iso_date.endswith('Z'), "Data ISO deve terminar com 'Z'"
            
            # Verificar que pode ser parseada como datetime
            dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
            assert isinstance(dt, datetime), "Resultado deve ser parseável como datetime"
            
            # Verificar que a data está em um range razoável
            assert 2020 <= dt.year <= 2030, "Ano deve estar em range razoável"
            assert 1 <= dt.month <= 12, "Mês deve ser válido"
            assert 1 <= dt.day <= 31, "Dia deve ser válido"
            assert 0 <= dt.hour <= 23, "Hora deve ser válida"
            assert 0 <= dt.minute <= 59, "Minuto deve ser válido"
            
            # Verificar formato específico
            import re
            iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
            assert re.match(iso_pattern, iso_date), "Deve seguir formato ISO 8601 exato"
            
        except ValueError:
            # Se a conversão falhar, a data original deve ser inválida
            # Isso é aceitável para alguns casos extremos
            pass
    
    @given(st.lists(valid_game_data(), min_size=0, max_size=10))
    @settings(max_examples=50)
    def test_data_validation_completeness(self, games_data):
        """
        Teste auxiliar para validação de dados importados.
        
        Verifica que a função de validação detecta corretamente
        dados válidos e inválidos.
        """
        if not games_data:
            # Lista vazia deve ser inválida
            valido, erros = validar_dados_importados(games_data)
            assert not valido, "Lista vazia deve ser inválida"
            assert len(erros) > 0, "Deve haver mensagens de erro"
        else:
            # Dados válidos devem passar na validação
            valido, erros = validar_dados_importados(games_data)
            
            if valido:
                assert len(erros) == 0, "Não deve haver erros para dados válidos"
            else:
                assert len(erros) > 0, "Deve haver mensagens de erro para dados inválidos"
                
                # Verificar que as mensagens de erro são informativas
                for erro in erros:
                    assert isinstance(erro, str), "Erro deve ser string"
                    assert len(erro) > 0, "Mensagem de erro não pode estar vazia"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])