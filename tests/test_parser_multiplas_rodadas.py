#!/usr/bin/env python3
"""
Testes para funcionalidade de múltiplas rodadas no parser.

Este módulo testa especificamente a capacidade do parser de processar
texto contendo palpites de múltiplas rodadas de uma só vez.
"""

import unittest
import sys
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils.parser import (
    dividir_texto_por_rodadas,
    processar_texto_multiplas_rodadas
)


class TestParserMultiplasRodadas(unittest.TestCase):
    """Testes para processamento de múltiplas rodadas."""
    
    def test_dividir_texto_batman_format(self):
        """Testa divisão de texto no formato Batman (🦇)."""
        texto = """Batman
Palpites Completos

🦇 RODADA 1 🦇
São Paulo 2x1 Palmeiras
Corinthians 1x0 Santos

🦇 RODADA 2 🦇
Palmeiras 2x1 Corinthians
Santos 3x0 Ponte Preta"""
        
        secoes = dividir_texto_por_rodadas(texto)
        
        self.assertEqual(len(secoes), 2)
        self.assertEqual(secoes[0]['rodada'], 1)
        self.assertEqual(secoes[1]['rodada'], 2)
        self.assertEqual(secoes[0]['apostador'], 'Batman')
        self.assertEqual(secoes[1]['apostador'], 'Batman')
        
        # Verificar conteúdo das seções
        self.assertIn('São Paulo 2x1 Palmeiras', secoes[0]['texto'])
        self.assertIn('Corinthians 1x0 Santos', secoes[0]['texto'])
        self.assertIn('Palmeiras 2x1 Corinthians', secoes[1]['texto'])
        self.assertIn('Santos 3x0 Ponte Preta', secoes[1]['texto'])
    
    def test_dividir_texto_robin_format(self):
        """Testa divisão de texto no formato Robin (⚡)."""
        texto = """Robin
Palpites Completos

⚡ RODADA 1 ⚡
São Paulo 1x2 Palmeiras
Corinthians 2-1 Santos

⚡ RODADA 2 ⚡
Palmeiras 1-1 Corinthians
Santos 2x1 Ponte Preta"""
        
        secoes = dividir_texto_por_rodadas(texto)
        
        self.assertEqual(len(secoes), 2)
        self.assertEqual(secoes[0]['rodada'], 1)
        self.assertEqual(secoes[1]['rodada'], 2)
        self.assertEqual(secoes[0]['apostador'], 'Robin')
        self.assertEqual(secoes[1]['apostador'], 'Robin')
    
    def test_dividir_texto_formato_simples(self):
        """Testa divisão de texto com formato simples (RODADA X)."""
        texto = """Superman
Palpites

RODADA 1
São Paulo 3x0 Palmeiras
Corinthians 2x1 Santos

RODADA 2
Palmeiras 1x1 Corinthians
Santos 1x0 Ponte Preta"""
        
        secoes = dividir_texto_por_rodadas(texto)
        
        self.assertEqual(len(secoes), 2)
        self.assertEqual(secoes[0]['rodada'], 1)
        self.assertEqual(secoes[1]['rodada'], 2)
        self.assertEqual(secoes[0]['apostador'], 'Superman')
    
    def test_processar_multiplas_rodadas_completo(self):
        """Testa processamento completo de múltiplas rodadas."""
        texto = """Flash
Palpites Teste

RODADA 1
São Paulo 2x1 Palmeiras
Corinthians 1x0 Santos

RODADA 2
Palmeiras 2x1 Corinthians
Santos 3x0 Ponte Preta"""
        
        resultados = processar_texto_multiplas_rodadas(texto)
        
        self.assertEqual(len(resultados), 2)
        
        # Verificar primeira rodada
        resultado1 = resultados[0]
        self.assertEqual(resultado1['apostador'], 'Flash')
        self.assertEqual(resultado1['rodada'], 1)
        self.assertEqual(len(resultado1['palpites']), 2)
        self.assertFalse(resultado1['rodada_inferida'])
        
        # Verificar palpites da primeira rodada
        palpite1 = resultado1['palpites'][0]
        self.assertEqual(palpite1['mandante'], 'São Paulo')
        self.assertEqual(palpite1['visitante'], 'Palmeiras')
        self.assertEqual(palpite1['gols_mandante'], 2)
        self.assertEqual(palpite1['gols_visitante'], 1)
        
        # Verificar segunda rodada
        resultado2 = resultados[1]
        self.assertEqual(resultado2['apostador'], 'Flash')
        self.assertEqual(resultado2['rodada'], 2)
        self.assertEqual(len(resultado2['palpites']), 2)
        self.assertFalse(resultado2['rodada_inferida'])
    
    def test_processar_rodada_unica_fallback(self):
        """Testa que rodada única ainda funciona (fallback)."""
        texto = """Aquaman
1ª Rodada
São Paulo 2x1 Palmeiras
Corinthians 1x0 Santos"""
        
        resultados = processar_texto_multiplas_rodadas(texto)
        
        self.assertEqual(len(resultados), 1)
        resultado = resultados[0]
        self.assertEqual(resultado['apostador'], 'Aquaman')
        self.assertEqual(resultado['rodada'], 1)
        self.assertEqual(len(resultado['palpites']), 2)
    
    def test_texto_vazio_ou_invalido(self):
        """Testa comportamento com texto vazio ou inválido."""
        # Texto vazio
        resultados = processar_texto_multiplas_rodadas("")
        self.assertEqual(len(resultados), 0)
        
        # Texto None
        resultados = processar_texto_multiplas_rodadas(None)
        self.assertEqual(len(resultados), 0)
        
        # Texto sem palpites válidos
        texto = """Teste
RODADA 1
Texto inválido sem palpites"""
        
        resultados = processar_texto_multiplas_rodadas(texto)
        self.assertEqual(len(resultados), 0)
    
    def test_rodadas_nao_sequenciais(self):
        """Testa processamento de rodadas não sequenciais."""
        texto = """Cyborg
Palpites

RODADA 1
São Paulo 2x1 Palmeiras

RODADA 3
Corinthians 1x0 Santos

RODADA 5
Palmeiras 2x1 Corinthians"""
        
        resultados = processar_texto_multiplas_rodadas(texto)
        
        self.assertEqual(len(resultados), 3)
        self.assertEqual(resultados[0]['rodada'], 1)
        self.assertEqual(resultados[1]['rodada'], 3)
        self.assertEqual(resultados[2]['rodada'], 5)
    
    def test_formatos_placar_misturados(self):
        """Testa diferentes formatos de placar em múltiplas rodadas."""
        texto = """Lanterna Verde
Palpites

RODADA 1
São Paulo 2x1 Palmeiras
Corinthians 1-0 Santos

RODADA 2
Palmeiras 2:1 Corinthians
Santos 3 x 0 Ponte Preta"""
        
        resultados = processar_texto_multiplas_rodadas(texto)
        
        self.assertEqual(len(resultados), 2)
        
        # Verificar que todos os formatos foram reconhecidos
        self.assertEqual(len(resultados[0]['palpites']), 2)
        self.assertEqual(len(resultados[1]['palpites']), 2)
        
        # Verificar placares específicos
        palpites_r1 = resultados[0]['palpites']
        self.assertEqual(palpites_r1[0]['gols_mandante'], 2)
        self.assertEqual(palpites_r1[0]['gols_visitante'], 1)
        self.assertEqual(palpites_r1[1]['gols_mandante'], 1)
        self.assertEqual(palpites_r1[1]['gols_visitante'], 0)


if __name__ == '__main__':
    unittest.main()