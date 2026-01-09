"""
Testes básicos para o módulo de parsing de texto.

Este arquivo contém testes unitários simples para verificar o funcionamento
das funções de parsing de texto do sistema de bolão.
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.parser import (
    extrair_apostador, extrair_rodada, extrair_palpites, 
    identificar_apostas_extras, inferir_rodada, processar_texto_palpite
)


class TestParserBasico(unittest.TestCase):
    """Testes básicos para funções de parsing"""
    
    def test_extrair_apostador_com_marcador(self):
        """Testa extração de apostador com marcador explícito"""
        texto = "Apostador: Mario Silva\n1ª Rodada\nFlamengo 2x1 Palmeiras"
        resultado = extrair_apostador(texto)
        self.assertEqual(resultado, "Mario Silva")
    
    def test_extrair_apostador_primeira_linha(self):
        """Testa extração de apostador na primeira linha"""
        texto = "João da Silva\n1ª Rodada\nFlamengo 2x1 Palmeiras"
        resultado = extrair_apostador(texto)
        self.assertEqual(resultado, "João da Silva")
    
    def test_extrair_rodada_formato_ordinal(self):
        """Testa extração de rodada em formato ordinal"""
        texto = "1ª Rodada\nFlamengo 2x1 Palmeiras"
        resultado = extrair_rodada(texto)
        self.assertEqual(resultado, 1)
    
    def test_extrair_rodada_formato_simples(self):
        """Testa extração de rodada em formato simples"""
        texto = "Rodada 5\nSão Paulo 1x0 Corinthians"
        resultado = extrair_rodada(texto)
        self.assertEqual(resultado, 5)
    
    def test_extrair_palpites_formato_x(self):
        """Testa extração de palpites no formato 'x'"""
        texto = "Flamengo 2x1 Palmeiras\nSão Paulo 0 x 2 Corinthians"
        resultado = extrair_palpites(texto)
        
        self.assertEqual(len(resultado), 2)
        
        # Primeiro palpite
        self.assertEqual(resultado[0]['mandante'], 'Flamengo')
        self.assertEqual(resultado[0]['visitante'], 'Palmeiras')
        self.assertEqual(resultado[0]['gols_mandante'], 2)
        self.assertEqual(resultado[0]['gols_visitante'], 1)
        
        # Segundo palpite
        self.assertEqual(resultado[1]['mandante'], 'São Paulo')
        self.assertEqual(resultado[1]['visitante'], 'Corinthians')
        self.assertEqual(resultado[1]['gols_mandante'], 0)
        self.assertEqual(resultado[1]['gols_visitante'], 2)
    
    def test_extrair_palpites_formato_hifen(self):
        """Testa extração de palpites no formato '-'"""
        texto = "Botafogo 1-1 Vasco"
        resultado = extrair_palpites(texto)
        
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['mandante'], 'Botafogo')
        self.assertEqual(resultado[0]['visitante'], 'Vasco')
        self.assertEqual(resultado[0]['gols_mandante'], 1)
        self.assertEqual(resultado[0]['gols_visitante'], 1)
    
    def test_identificar_apostas_extras(self):
        """Testa identificação de apostas extras"""
        texto = """Aposta Extra:
Jogo 5: Botafogo 2x2 Vasco
Jogo 10: Santos 1x0 Grêmio"""
        
        resultado = identificar_apostas_extras(texto)
        
        self.assertEqual(len(resultado), 2)
        
        # Primeira aposta extra
        self.assertEqual(resultado[0]['tipo'], 'extra')
        self.assertEqual(resultado[0]['identificador'], 'Jogo 5')
        self.assertEqual(resultado[0]['mandante'], 'Botafogo')
        self.assertEqual(resultado[0]['visitante'], 'Vasco')
        
        # Segunda aposta extra
        self.assertEqual(resultado[1]['tipo'], 'extra')
        self.assertEqual(resultado[1]['identificador'], 'Jogo 10')
        self.assertEqual(resultado[1]['mandante'], 'Santos')
        self.assertEqual(resultado[1]['visitante'], 'Grêmio')
    
    def test_inferir_rodada_correspondencia_perfeita(self):
        """Testa inferência de rodada com correspondência perfeita"""
        palpites = [
            {'mandante': 'Flamengo', 'visitante': 'Palmeiras', 'gols_mandante': 2, 'gols_visitante': 1}
        ]
        
        tabela = {
            'rodadas': [
                {
                    'numero': 1,
                    'jogos': [
                        {'mandante': 'Flamengo', 'visitante': 'Palmeiras'},
                        {'mandante': 'São Paulo', 'visitante': 'Corinthians'}
                    ]
                }
            ]
        }
        
        resultado = inferir_rodada(palpites, tabela)
        self.assertEqual(resultado, 1)
    
    def test_processar_texto_palpite_completo(self):
        """Testa processamento completo de texto de palpite"""
        texto = """Mario Silva
1ª Rodada:
Flamengo 2x1 Palmeiras
São Paulo 0x2 Corinthians

Aposta Extra:
Jogo 15: Santos 2x0 Grêmio"""
        
        resultado = processar_texto_palpite(texto)
        
        # Verificar dados extraídos
        self.assertEqual(resultado['apostador'], 'Mario Silva')
        self.assertEqual(resultado['rodada'], 1)
        self.assertFalse(resultado['rodada_inferida'])
        self.assertEqual(len(resultado['palpites']), 2)  # Duas previsões regulares
        self.assertEqual(len(resultado['apostas_extras']), 1)
        
        # Verificar aposta extra
        extra = resultado['apostas_extras'][0]
        self.assertEqual(extra['tipo'], 'extra')
        self.assertEqual(extra['identificador'], 'Jogo 15')
        self.assertEqual(extra['mandante'], 'Santos')
        self.assertEqual(extra['visitante'], 'Grêmio')


if __name__ == '__main__':
    unittest.main()