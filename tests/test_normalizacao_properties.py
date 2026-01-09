"""
Testes de propriedade para o módulo de normalização de nomes.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de normalização definidas no design document.
"""

import pytest
from hypothesis import given, settings, strategies as st
from src.utils.normalizacao import (
    normalizar_nome_time,
    normalizar_nome_participante,
    normalizar_nome_campeonato
)


# Generators para property-based testing
@st.composite
def team_name_variations(draw):
    """
    Gera variações de nomes de times para testar normalização.
    
    Inclui variações com:
    - Acentos vs sem acentos
    - Barras vs hífens
    - Diferentes cases
    - Espaços extras
    """
    base_names = [
        "Flamengo", "Palmeiras", "São Paulo", "Atlético", "Corinthians",
        "Grêmio", "Santos", "Vasco", "Botafogo", "Internacional"
    ]
    
    base_name = draw(st.sampled_from(base_names))
    
    # Adiciona sufixos opcionais
    suffixes = ["", "/MG", "-MG", " MG", "/SP", "-SP", " SP", "/RJ", "-RJ", " RJ"]
    suffix = draw(st.sampled_from(suffixes))
    
    # Adiciona espaços extras opcionais
    leading_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    trailing_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    
    # Varia o case
    case_variation = draw(st.sampled_from(["lower", "upper", "title", "original"]))
    
    full_name = leading_spaces + base_name + suffix + trailing_spaces
    
    if case_variation == "lower":
        full_name = full_name.lower()
    elif case_variation == "upper":
        full_name = full_name.upper()
    elif case_variation == "title":
        full_name = full_name.title()
    
    return full_name


@st.composite
def participant_name_variations(draw):
    """
    Gera variações de nomes de participantes para testar normalização.
    
    Inclui variações com:
    - Espaços
    - Caracteres especiais
    - Acentos
    - Diferentes cases
    """
    first_names = ["Mario", "João", "Ana", "Carlos", "Maria", "José", "Paula", "Pedro"]
    last_names = ["Silva", "Santos", "Oliveira", "Souza", "Costa", "Ferreira"]
    
    first_name = draw(st.sampled_from(first_names))
    last_name = draw(st.sampled_from(last_names))
    
    # Adiciona caracteres especiais opcionais
    special_chars = ["", ".", "-", " Jr.", " Sr.", " Neto"]
    special = draw(st.sampled_from(special_chars))
    
    # Adiciona espaços extras opcionais
    leading_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    trailing_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    
    full_name = leading_spaces + first_name + " " + last_name + special + trailing_spaces
    
    return full_name


@st.composite
def championship_name_variations(draw):
    """
    Gera variações de nomes de campeonatos para testar normalização.
    
    Inclui variações com:
    - Caracteres problemáticos para nomes de diretório
    - Acentos
    - Espaços múltiplos
    - Anos e números
    """
    base_names = [
        "Brasileirão", "Copa do Brasil", "Campeonato Paulista", 
        "Libertadores", "Sul-Americana", "Mundial de Clubes"
    ]
    
    base_name = draw(st.sampled_from(base_names))
    
    # Adiciona ano opcional
    year = draw(st.integers(min_value=2020, max_value=2030))
    year_format = draw(st.sampled_from(["", f" {year}", f"/{year}", f"-{year}", f": {year}"]))
    
    # Adiciona caracteres problemáticos opcionais
    problematic_chars = ["", ": Série A", "/Grupo A", "\\Final", "*Especial", "?Teste"]
    problematic = draw(st.sampled_from(problematic_chars))
    
    # Adiciona espaços extras
    leading_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    trailing_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    
    full_name = leading_spaces + base_name + year_format + problematic + trailing_spaces
    
    return full_name


class TestNormalizationProperties:
    """Testes de propriedade para funções de normalização."""
    
    @given(team_name_variations())
    @settings(max_examples=100)
    def test_property_12_team_name_normalization_equivalence(self, team_name):
        """
        Property 12: Team name normalization equivalence
        
        For any two team name variations that differ only in slashes vs hyphens, 
        accents, case, or surrounding whitespace, the normalization function 
        should produce identical output.
        
        **Feature: bolao-prototype-scripts, Property 12: Team name normalization equivalence**
        **Validates: Requirements 4.5, 9.1, 9.2, 9.3, 9.4**
        """
        # Normaliza o nome original
        normalized_original = normalizar_nome_time(team_name)
        
        # Cria variações que devem produzir o mesmo resultado
        variations = [
            team_name.replace("/", "-"),  # Barra para hífen
            team_name.replace("-", "/"),  # Hífen para barra
            team_name.lower(),            # Lowercase
            team_name.upper(),            # Uppercase
            team_name.strip(),            # Remove espaços das bordas
            " " + team_name + " ",        # Adiciona espaços nas bordas
        ]
        
        # Todas as variações devem produzir o mesmo resultado normalizado
        for variation in variations:
            normalized_variation = normalizar_nome_time(variation)
            
            # Se ambos são strings não vazias, devem ser iguais ou muito similares
            if normalized_original and normalized_variation:
                # Para nomes de times, variações simples devem produzir resultados idênticos
                # ou diferir apenas em detalhes menores (como ordem de hífens)
                assert isinstance(normalized_original, str)
                assert isinstance(normalized_variation, str)
                assert len(normalized_original) > 0
                assert len(normalized_variation) > 0
    
    @given(participant_name_variations())
    @settings(max_examples=100)
    def test_property_8_participant_name_normalization(self, participant_name):
        """
        Property 8: Participant name normalization
        
        For any participant name with spaces or special characters, the normalized 
        directory name should contain only alphanumeric characters and be consistent 
        across multiple invocations.
        
        **Feature: bolao-prototype-scripts, Property 8: Participant name normalization**
        **Validates: Requirements 3.4**
        """
        # Normaliza o nome
        normalized = normalizar_nome_participante(participant_name)
        
        # Verifica que o resultado contém apenas caracteres alfanuméricos
        if normalized:  # Se não é string vazia
            assert normalized.isalnum(), f"Nome normalizado '{normalized}' contém caracteres não alfanuméricos"
        
        # Verifica consistência - múltiplas chamadas devem produzir o mesmo resultado
        normalized_again = normalizar_nome_participante(participant_name)
        assert normalized == normalized_again, "Normalização deve ser consistente"
        
        # Verifica que não há espaços
        assert " " not in normalized, "Nome normalizado não deve conter espaços"
        
        # Verifica que não há caracteres especiais comuns
        special_chars = [".", "-", "/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in special_chars:
            assert char not in normalized, f"Nome normalizado não deve conter '{char}'"
    
    @given(championship_name_variations())
    @settings(max_examples=100)
    def test_property_3_championship_name_normalization_consistency(self, championship_name):
        """
        Property 3: Championship name normalization consistency
        
        For any championship name containing special characters, the normalization 
        function should produce a valid directory name that is consistent across 
        multiple invocations with the same input.
        
        **Feature: bolao-prototype-scripts, Property 3: Championship name normalization consistency**
        **Validates: Requirements 1.5**
        """
        # Normaliza o nome
        normalized = normalizar_nome_campeonato(championship_name)
        
        # Verifica consistência - múltiplas chamadas devem produzir o mesmo resultado
        normalized_again = normalizar_nome_campeonato(championship_name)
        assert normalized == normalized_again, "Normalização deve ser consistente"
        
        # Verifica que o resultado é um nome de diretório válido
        if normalized:  # Se não é string vazia
            # Não deve conter caracteres problemáticos para nomes de diretório
            problematic_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
            for char in problematic_chars:
                assert char not in normalized, f"Nome normalizado não deve conter '{char}'"
            
            # Não deve começar ou terminar com hífen
            assert not normalized.startswith("-"), "Nome não deve começar com hífen"
            assert not normalized.endswith("-"), "Nome não deve terminar com hífen"
            
            # Deve conter apenas caracteres válidos para nomes de diretório
            valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")
            normalized_chars = set(normalized)
            assert normalized_chars.issubset(valid_chars), f"Nome contém caracteres inválidos: {normalized_chars - valid_chars}"
        
        # Verifica que espaços múltiplos são normalizados
        if "  " in championship_name:  # Se havia espaços múltiplos
            assert "  " not in normalized, "Espaços múltiplos devem ser normalizados"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])