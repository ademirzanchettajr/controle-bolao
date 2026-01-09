"""
Testes para o módulo de normalização de nomes.
"""

import pytest
from src.utils.normalizacao import (
    normalizar_nome_time,
    normalizar_nome_participante,
    normalizar_nome_campeonato,
    encontrar_time_similar
)


class TestNormalizarNomeTime:
    """Testes para a função normalizar_nome_time."""
    
    def test_remove_acentos(self):
        """Testa remoção de acentos."""
        assert normalizar_nome_time("São Paulo") == "sao-paulo"
        assert normalizar_nome_time("Atlético") == "atletico"
        assert normalizar_nome_time("Grêmio") == "gremio"
    
    def test_converte_barras_hifens(self):
        """Testa conversão de barras para hífens."""
        assert normalizar_nome_time("Atlético/MG") == "atletico-mg"
        assert normalizar_nome_time("Atlético-MG") == "atletico-mg"
    
    def test_normaliza_case(self):
        """Testa normalização de maiúsculas/minúsculas."""
        assert normalizar_nome_time("FLAMENGO") == "flamengo"
        assert normalizar_nome_time("FlAmEnGo") == "flamengo"
    
    def test_remove_espacos_extras(self):
        """Testa remoção de espaços extras."""
        assert normalizar_nome_time("  Flamengo  ") == "flamengo"
        assert normalizar_nome_time("São  Paulo") == "sao-paulo"
    
    def test_casos_extremos(self):
        """Testa casos extremos."""
        assert normalizar_nome_time("") == ""
        assert normalizar_nome_time("   ") == ""
        assert normalizar_nome_time(None) == ""


class TestNormalizarNomeParticipante:
    """Testes para a função normalizar_nome_participante."""
    
    def test_remove_espacos(self):
        """Testa remoção de espaços."""
        assert normalizar_nome_participante("Mario Silva") == "MarioSilva"
        assert normalizar_nome_participante("Ana Paula") == "AnaPaula"
    
    def test_remove_caracteres_especiais(self):
        """Testa remoção de caracteres especiais."""
        assert normalizar_nome_participante("João da Silva Jr.") == "JoaodaSilvaJr"
        assert normalizar_nome_participante("Ana-Paula") == "AnaPaula"
    
    def test_remove_acentos(self):
        """Testa remoção de acentos."""
        assert normalizar_nome_participante("José") == "Jose"
        assert normalizar_nome_participante("María") == "Maria"
    
    def test_casos_extremos(self):
        """Testa casos extremos."""
        assert normalizar_nome_participante("") == ""
        assert normalizar_nome_participante("   ") == ""
        assert normalizar_nome_participante(None) == ""


class TestNormalizarNomeCampeonato:
    """Testes para a função normalizar_nome_campeonato."""
    
    def test_substitui_caracteres_problematicos(self):
        """Testa substituição de caracteres problemáticos."""
        assert normalizar_nome_campeonato("Copa do Brasil/2025") == "Copa-do-Brasil-2025"
        assert normalizar_nome_campeonato("Campeonato: Série A") == "Campeonato-Serie-A"
    
    def test_remove_acentos(self):
        """Testa remoção de acentos."""
        assert normalizar_nome_campeonato("Brasileirão 2025") == "Brasileirao-2025"
    
    def test_normaliza_espacos(self):
        """Testa normalização de espaços."""
        assert normalizar_nome_campeonato("Copa  do   Brasil") == "Copa-do-Brasil"
    
    def test_casos_extremos(self):
        """Testa casos extremos."""
        assert normalizar_nome_campeonato("") == ""
        assert normalizar_nome_campeonato("   ") == ""
        assert normalizar_nome_campeonato(None) == ""


class TestEncontrarTimeSimilar:
    """Testes para a função encontrar_time_similar."""
    
    def test_correspondencia_exata(self):
        """Testa correspondência exata."""
        times = ["Flamengo", "Palmeiras", "São Paulo"]
        assert encontrar_time_similar("Flamengo", times) == "Flamengo"
        assert encontrar_time_similar("São Paulo", times) == "São Paulo"
    
    def test_correspondencia_aproximada(self):
        """Testa correspondência aproximada."""
        times = ["Flamengo", "Palmeiras", "São Paulo"]
        assert encontrar_time_similar("Flamego", times) == "Flamengo"
        assert encontrar_time_similar("Palmerias", times) == "Palmeiras"
    
    def test_sem_correspondencia(self):
        """Testa quando não há correspondência suficientemente similar."""
        times = ["Flamengo", "Palmeiras", "São Paulo"]
        assert encontrar_time_similar("XYZ", times) is None
        assert encontrar_time_similar("Completely Different", times) is None
    
    def test_casos_extremos(self):
        """Testa casos extremos."""
        times = ["Flamengo", "Palmeiras"]
        assert encontrar_time_similar("", times) is None
        assert encontrar_time_similar(None, times) is None
        assert encontrar_time_similar("Flamengo", []) is None
        assert encontrar_time_similar("Flamengo", None) is None


if __name__ == "__main__":
    pytest.main([__file__])