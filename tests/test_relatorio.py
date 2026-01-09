"""
Testes unitários para o módulo de geração de relatórios.
"""

import pytest
from src.utils.relatorio import (
    gerar_cabecalho_relatorio,
    calcular_variacao_posicao,
    formatar_linha_participante,
    gerar_tabela_classificacao,
    gerar_resumo_rodada
)


class TestGerarCabecalhoRelatorio:
    """Testes para a função gerar_cabecalho_relatorio."""
    
    def test_cabecalho_basico(self):
        """Testa geração de cabeçalho básico."""
        resultado = gerar_cabecalho_relatorio("Brasileirão", 1)
        
        assert "RELATÓRIO DE CLASSIFICAÇÃO - RODADA 01" in resultado
        assert "Campeonato: Brasileirão" in resultado
        assert "Gerado em:" in resultado
        assert "=" * 80 in resultado
    
    def test_cabecalho_com_temporada(self):
        """Testa geração de cabeçalho com temporada."""
        resultado = gerar_cabecalho_relatorio("Brasileirão", 5, "2025")
        
        assert "RODADA 05" in resultado
        assert "Campeonato: Brasileirão" in resultado
        assert "Temporada: 2025" in resultado
    
    def test_formatacao_rodada(self):
        """Testa formatação do número da rodada com zero à esquerda."""
        resultado = gerar_cabecalho_relatorio("Copa", 3)
        assert "RODADA 03" in resultado
        
        resultado = gerar_cabecalho_relatorio("Copa", 15)
        assert "RODADA 15" in resultado


class TestCalcularVariacaoPosicao:
    """Testes para a função calcular_variacao_posicao."""
    
    def test_participante_inexistente(self):
        """Testa participante que não existe no histórico."""
        historico = {}
        variacao = calcular_variacao_posicao("Mario", 1, historico)
        assert variacao == 0
    
    def test_sem_historico_anterior(self):
        """Testa participante sem histórico de rodadas anteriores."""
        historico = {"Mario": {3: 2}}  # Apenas rodada atual
        variacao = calcular_variacao_posicao("Mario", 1, historico)
        assert variacao == 0
    
    def test_subiu_posicao(self):
        """Testa quando participante subiu de posição."""
        historico = {"Mario": {1: 5, 2: 3}}  # Era 5º na rodada 1, agora é 2º
        variacao = calcular_variacao_posicao("Mario", 2, historico)
        assert variacao == 3  # Subiu da 5ª para 2ª posição (5 - 2 = 3)
    
    def test_desceu_posicao(self):
        """Testa quando participante desceu de posição."""
        historico = {"Mario": {1: 2, 2: 5}}  # Era 2º na rodada 1, agora é 4º
        variacao = calcular_variacao_posicao("Mario", 4, historico)
        assert variacao == -2  # Desceu da 2ª para 4ª posição (2 - 4 = -2)
    
    def test_manteve_posicao(self):
        """Testa quando participante manteve a posição."""
        historico = {"Mario": {1: 3, 2: 3}}  # Era 3º, continua 3º
        variacao = calcular_variacao_posicao("Mario", 3, historico)
        assert variacao == 0
    
    def test_multiplas_rodadas(self):
        """Testa com múltiplas rodadas no histórico."""
        historico = {"Mario": {1: 8, 2: 5, 3: 2}}  # Considera apenas a rodada anterior mais recente
        variacao = calcular_variacao_posicao("Mario", 1, historico)
        assert variacao == 4  # Da rodada 2 (5º) para atual (1º) = 5 - 1 = 4


class TestFormatarLinhaParticipante:
    """Testes para a função formatar_linha_participante."""
    
    def test_formatacao_basica(self):
        """Testa formatação básica de linha."""
        linha = formatar_linha_participante(1, "Mario Silva", 8.5, 25.3, 2)
        
        assert "1º" in linha
        assert "Mario Silva" in linha
        assert "8.5" in linha
        assert "25.3" in linha
        assert "↑2" in linha
    
    def test_variacao_positiva(self):
        """Testa formatação de variação positiva (subiu)."""
        linha = formatar_linha_participante(2, "Ana", 5.0, 15.0, 3)
        assert "↑3" in linha
    
    def test_variacao_negativa(self):
        """Testa formatação de variação negativa (desceu)."""
        linha = formatar_linha_participante(5, "João", 3.0, 12.0, -2)
        assert "↓2" in linha
    
    def test_variacao_zero(self):
        """Testa formatação quando não houve variação."""
        linha = formatar_linha_participante(3, "Pedro", 6.0, 18.0, 0)
        assert "=" in linha
    
    def test_com_codigos_acerto(self):
        """Testa formatação com códigos de acerto."""
        codigos = ["AR", "V", "G", "N"]
        linha = formatar_linha_participante(1, "Mario", 10.0, 30.0, 1, codigos)
        
        assert "AR V G N" in linha
        assert "|" in linha
    
    def test_com_jogos_participados(self):
        """Testa formatação com número de jogos participados."""
        linha = formatar_linha_participante(2, "Ana", 7.0, 21.0, 0, jogos_participados=8)
        
        assert "(8 jogos)" in linha
    
    def test_formatacao_completa(self):
        """Testa formatação com todos os campos opcionais."""
        codigos = ["VG", "E"]
        linha = formatar_linha_participante(3, "Carlos", 4.5, 13.5, -1, codigos, 6)
        
        assert "3º" in linha
        assert "Carlos" in linha
        assert "4.5" in linha
        assert "13.5" in linha
        assert "↓1" in linha
        assert "VG E" in linha
        assert "(6 jogos)" in linha


class TestGerarTabelaClassificacao:
    """Testes para a função gerar_tabela_classificacao."""
    
    def test_tabela_vazia(self):
        """Testa geração de tabela com lista vazia."""
        resultado = gerar_tabela_classificacao([], 1)
        assert "Nenhum resultado encontrado" in resultado
    
    def test_ordenacao_por_pontuacao(self):
        """Testa ordenação correta por pontuação acumulada."""
        resultados = [
            {"participante": "Ana", "total_rodada": 5.0, "total_acumulado": 15.0},
            {"participante": "Mario", "total_rodada": 8.0, "total_acumulado": 25.0},
            {"participante": "João", "total_rodada": 3.0, "total_acumulado": 20.0}
        ]
        
        tabela = gerar_tabela_classificacao(resultados, 2)
        
        # Verifica se Mario (25.0) aparece primeiro
        linhas = tabela.split('\n')
        linha_mario = next(l for l in linhas if "Mario" in l)
        linha_joao = next(l for l in linhas if "João" in l)
        linha_ana = next(l for l in linhas if "Ana" in l)
        
        assert "1º" in linha_mario
        assert "2º" in linha_joao
        assert "3º" in linha_ana
    
    def test_cabecalho_da_tabela(self):
        """Testa presença do cabeçalho da tabela."""
        resultados = [
            {"participante": "Mario", "total_rodada": 8.0, "total_acumulado": 25.0}
        ]
        
        tabela = gerar_tabela_classificacao(resultados, 1)
        
        assert "Pos Nome" in tabela
        assert "Rodada" in tabela
        assert "Total" in tabela
        assert "Var" in tabela
    
    def test_com_cabecalho_campeonato(self):
        """Testa geração com cabeçalho do campeonato."""
        resultados = [
            {"participante": "Mario", "total_rodada": 8.0, "total_acumulado": 25.0}
        ]
        
        tabela = gerar_tabela_classificacao(resultados, 3, "Brasileirão", "2025")
        
        assert "RELATÓRIO DE CLASSIFICAÇÃO - RODADA 03" in tabela
        assert "Campeonato: Brasileirão" in tabela
        assert "Temporada: 2025" in tabela
    
    def test_com_codigos_acerto(self):
        """Testa inclusão de códigos de acerto."""
        resultados = [
            {
                "participante": "Mario", 
                "total_rodada": 8.0, 
                "total_acumulado": 25.0,
                "codigos_regra": ["AR", "V", "G"]
            }
        ]
        
        tabela = gerar_tabela_classificacao(resultados, 1, incluir_codigos=True)
        
        assert "Códigos de Acerto" in tabela
        assert "AR V G" in tabela
        assert "LEGENDA DOS CÓDIGOS:" in tabela
        assert "AR = Resultado Exato" in tabela
    
    def test_sem_codigos_acerto(self):
        """Testa tabela sem códigos de acerto."""
        resultados = [
            {"participante": "Mario", "total_rodada": 8.0, "total_acumulado": 25.0}
        ]
        
        tabela = gerar_tabela_classificacao(resultados, 1, incluir_codigos=False)
        
        assert "Códigos de Acerto" not in tabela
        assert "LEGENDA DOS CÓDIGOS:" not in tabela
    
    def test_com_historico_posicoes(self):
        """Testa cálculo de variação com histórico de posições."""
        resultados = [
            {"participante": "Mario", "total_rodada": 8.0, "total_acumulado": 25.0},
            {"participante": "Ana", "total_rodada": 5.0, "total_acumulado": 20.0}
        ]
        
        historico = {
            "Mario": {1: 2, 2: 1},  # Era 2º, agora é 1º
            "Ana": {1: 1, 2: 2}     # Era 1ª, agora é 2ª
        }
        
        tabela = gerar_tabela_classificacao(resultados, 2, historico_posicoes=historico)
        
        # Mario deve mostrar ↑1 (subiu da 2ª para 1ª posição)
        # Ana deve mostrar ↓1 (desceu da 1ª para 2ª posição)
        assert "↑1" in tabela or "↓1" in tabela
    
    def test_rodape_tabela(self):
        """Testa presença do rodapé com total de participantes."""
        resultados = [
            {"participante": "Mario", "total_rodada": 8.0, "total_acumulado": 25.0},
            {"participante": "Ana", "total_rodada": 5.0, "total_acumulado": 20.0}
        ]
        
        tabela = gerar_tabela_classificacao(resultados, 1)
        
        assert "Total de participantes: 2" in tabela


class TestGerarResumoRodada:
    """Testes para a função gerar_resumo_rodada."""
    
    def test_resumo_vazio(self):
        """Testa resumo com lista vazia."""
        resumo = gerar_resumo_rodada([], 1)
        assert "Nenhum dado disponível" in resumo
    
    def test_estatisticas_basicas(self):
        """Testa cálculo de estatísticas básicas."""
        resultados = [
            {"participante": "Mario", "total_rodada": 10.0},
            {"participante": "Ana", "total_rodada": 6.0},
            {"participante": "João", "total_rodada": 8.0}
        ]
        
        resumo = gerar_resumo_rodada(resultados, 2)
        
        assert "RESUMO DA RODADA 02" in resumo
        assert "Participantes: 3" in resumo
        assert "Maior pontuação: 10.0 (Mario)" in resumo
        assert "Menor pontuação: 6.0 (Ana)" in resumo
        assert "Média da rodada: 8.0" in resumo
    
    def test_participante_unico(self):
        """Testa resumo com apenas um participante."""
        resultados = [
            {"participante": "Mario", "total_rodada": 7.5}
        ]
        
        resumo = gerar_resumo_rodada(resultados, 1)
        
        assert "Participantes: 1" in resumo
        assert "Maior pontuação: 7.5 (Mario)" in resumo
        assert "Menor pontuação: 7.5 (Mario)" in resumo
        assert "Média da rodada: 7.5" in resumo
    
    def test_formatacao_numeros(self):
        """Testa formatação correta dos números."""
        resultados = [
            {"participante": "Mario", "total_rodada": 8.333},
            {"participante": "Ana", "total_rodada": 5.666}
        ]
        
        resumo = gerar_resumo_rodada(resultados, 1)
        
        # Verifica se os números estão formatados com 1 casa decimal
        assert "8.3" in resumo
        assert "5.7" in resumo  # 5.666 arredondado para 5.7
        assert "7.0" in resumo  # Média (8.333 + 5.666) / 2 = 7.0


if __name__ == "__main__":
    pytest.main([__file__])