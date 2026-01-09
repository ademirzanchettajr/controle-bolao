"""
Testes de propriedade para o script de processamento de resultados.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de processamento de resultados definidas no design document.
"""

import json
import os
import pytest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

from hypothesis import given, settings, strategies as st, assume

# Importar módulos do sistema
import sys
sys.path.append(str(Path(__file__).parent.parent / "src"))

from scripts.processar_resultados import (
    carregar_dados_campeonato,
    obter_jogos_rodada,
    validar_jogos_obrigatorios_finalizados,
    processar_resultados_modo_teste,
    calcular_pontuacao_participante,
    gerar_classificacao_ordenada,
    calcular_pontuacao_acumulada
)


# Generators para property-based testing
@st.composite
def championship_data(draw):
    """
    Gera dados completos de um campeonato para testes.
    
    Returns:
        Tuple com (tabela, regras, palpites_participantes)
    """
    # Gerar dados básicos do campeonato
    campeonato_nome = draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    temporada = str(draw(st.integers(min_value=2020, max_value=2030)))
    
    # Gerar jogos para uma rodada
    num_jogos = draw(st.integers(min_value=2, max_value=6))
    jogos = []
    
    for i in range(num_jogos):
        jogo_id = f"jogo-{i+1:03d}"
        mandante = draw(st.sampled_from(["Flamengo", "Palmeiras", "Corinthians", "São Paulo", "Botafogo", "Vasco"]))
        visitante = draw(st.sampled_from(["Flamengo", "Palmeiras", "Corinthians", "São Paulo", "Botafogo", "Vasco"]))
        assume(mandante != visitante)  # Times diferentes
        
        # Gerar resultado finalizado
        gols_mandante = draw(st.integers(min_value=0, max_value=5))
        gols_visitante = draw(st.integers(min_value=0, max_value=5))
        
        jogo = {
            "id": jogo_id,
            "mandante": mandante,
            "visitante": visitante,
            "data": "2024-04-13T16:00:00Z",
            "local": "Estádio",
            "gols_mandante": gols_mandante,
            "gols_visitante": gols_visitante,
            "status": "finalizado",
            "obrigatorio": True
        }
        jogos.append(jogo)
    
    # Estrutura da tabela
    tabela = {
        "campeonato": campeonato_nome,
        "temporada": temporada,
        "rodada_atual": 0,
        "data_atualizacao": "2024-01-01T00:00:00Z",
        "codigo_campeonato": "12345",
        "rodadas": [
            {
                "numero": 1,
                "jogos": jogos
            }
        ]
    }
    
    # Estrutura das regras
    regras = {
        "campeonato": campeonato_nome,
        "temporada": temporada,
        "versao": "1.0",
        "data_criacao": "2024-01-01T00:00:00Z",
        "regras": {
            "resultado_exato": {
                "pontos_base": 12,
                "bonus_divisor": True,
                "descricao": "Resultado exato (placar idêntico)",
                "codigo": "AR"
            },
            "vitoria_gols_um_time": {
                "pontos": 7,
                "descricao": "Vencedor + gols de uma equipe",
                "codigo": "VG"
            },
            "vitoria_diferenca_gols": {
                "pontos": 6,
                "descricao": "Vencedor + diferença de gols",
                "codigo": "VD"
            },
            "vitoria_soma_gols": {
                "pontos": 6,
                "descricao": "Vencedor + soma total de gols",
                "codigo": "VS"
            },
            "apenas_vitoria": {
                "pontos": 5,
                "descricao": "Apenas vencedor",
                "codigo": "V"
            },
            "apenas_empate": {
                "pontos": 5,
                "descricao": "Apenas empate",
                "codigo": "E"
            },
            "gols_um_time": {
                "pontos": 2,
                "descricao": "Gols de um time (sem resultado)",
                "codigo": "G"
            },
            "soma_gols": {
                "pontos": 1,
                "descricao": "Apenas soma total de gols",
                "codigo": "S"
            },
            "resultado_inverso": {
                "pontos": -3,
                "descricao": "Resultado invertido (penalidade)",
                "codigo": "RI"
            },
            "palpite_ausente": {
                "pontos": -1,
                "descricao": "Palpite não enviado (jogo obrigatório)",
                "codigo": "PA"
            }
        }
    }
    
    # Gerar participantes com palpites
    num_participantes = draw(st.integers(min_value=2, max_value=8))
    palpites_participantes = []
    
    for i in range(num_participantes):
        participante_nome = f"Participante{i+1}"
        
        # Gerar palpites para os jogos
        jogos_palpites = []
        for jogo in jogos:
            # Nem todos os participantes precisam ter palpites para todos os jogos
            if draw(st.booleans()):
                palpite_mandante = draw(st.integers(min_value=0, max_value=5))
                palpite_visitante = draw(st.integers(min_value=0, max_value=5))
                
                jogo_palpite = {
                    "id": jogo["id"],
                    "mandante": jogo["mandante"],
                    "visitante": jogo["visitante"],
                    "palpite_mandante": palpite_mandante,
                    "palpite_visitante": palpite_visitante
                }
                jogos_palpites.append(jogo_palpite)
        
        palpites = {
            "apostador": participante_nome,
            "codigo_apostador": f"{i+1:04d}",
            "campeonato": campeonato_nome,
            "temporada": temporada,
            "palpites": [
                {
                    "rodada": 1,
                    "data_palpite": "2024-01-01T00:00:00Z",
                    "jogos": jogos_palpites
                }
            ]
        }
        palpites_participantes.append(palpites)
    
    return tabela, regras, palpites_participantes


@st.composite
def championship_with_unfinished_games(draw):
    """
    Gera dados de campeonato com jogos obrigatórios não finalizados.
    
    Returns:
        Tuple com (tabela, regras, palpites_participantes)
    """
    tabela, regras, palpites = draw(championship_data())
    
    # Modificar pelo menos um jogo para não estar finalizado
    jogos = tabela["rodadas"][0]["jogos"]
    if jogos:
        jogo_index = draw(st.integers(min_value=0, max_value=len(jogos)-1))
        jogos[jogo_index]["status"] = "agendado"
        jogos[jogo_index]["gols_mandante"] = 0
        jogos[jogo_index]["gols_visitante"] = 0
    
    return tabela, regras, palpites


class TestProcessarResultadosProperties:
    """Testes de propriedade para processamento de resultados."""
    
    def setup_method(self):
        """Setup para cada teste - criar diretório temporário."""
        self.temp_dir = tempfile.mkdtemp()
        self.campeonatos_dir = Path(self.temp_dir) / "Campeonatos"
        self.campeonatos_dir.mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup após cada teste."""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_championship_files(self, nome_campeonato: str, tabela: Dict, regras: Dict, palpites_list: List[Dict]):
        """Cria arquivos de campeonato no diretório temporário."""
        campeonato_dir = self.campeonatos_dir / nome_campeonato
        campeonato_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar subdiretórios
        (campeonato_dir / "Tabela").mkdir(exist_ok=True)
        (campeonato_dir / "Regras").mkdir(exist_ok=True)
        (campeonato_dir / "Participantes").mkdir(exist_ok=True)
        (campeonato_dir / "Resultados").mkdir(exist_ok=True)
        
        # Criar arquivo de tabela
        with open(campeonato_dir / "Tabela" / "tabela.json", 'w', encoding='utf-8') as f:
            json.dump(tabela, f, indent=2, ensure_ascii=False)
        
        # Criar arquivo de regras
        with open(campeonato_dir / "Regras" / "regras.json", 'w', encoding='utf-8') as f:
            json.dump(regras, f, indent=2, ensure_ascii=False)
        
        # Criar arquivos de palpites
        for palpites in palpites_list:
            participante_nome = palpites["apostador"].replace(" ", "")
            participante_dir = campeonato_dir / "Participantes" / participante_nome
            participante_dir.mkdir(exist_ok=True)
            
            with open(participante_dir / "palpites.json", 'w', encoding='utf-8') as f:
                json.dump(palpites, f, indent=2, ensure_ascii=False)
    
    @given(championship_data())
    @settings(max_examples=100)
    def test_property_20_test_mode_file_immutability(self, championship_data_tuple):
        """
        Property 20: Test mode file immutability
        
        For any championship and round, after executing result processing in test mode, 
        no JSON files should be modified (file modification timestamps should remain unchanged).
        
        **Feature: bolao-prototype-scripts, Property 20: Test mode file immutability**
        **Validates: Requirements 6.1**
        """
        tabela, regras, palpites_participantes = championship_data_tuple
        nome_campeonato = tabela["campeonato"]
        
        # Criar arquivos do campeonato
        self.create_championship_files(nome_campeonato, tabela, regras, palpites_participantes)
        
        # Obter timestamps dos arquivos antes do processamento
        campeonato_dir = self.campeonatos_dir / nome_campeonato
        tabela_path = campeonato_dir / "Tabela" / "tabela.json"
        regras_path = campeonato_dir / "Regras" / "regras.json"
        
        timestamps_antes = {
            "tabela": os.path.getmtime(tabela_path),
            "regras": os.path.getmtime(regras_path)
        }
        
        # Obter timestamps dos arquivos de palpites
        palpites_timestamps = {}
        for palpites in palpites_participantes:
            participante_nome = palpites["apostador"].replace(" ", "")
            palpites_path = campeonato_dir / "Participantes" / participante_nome / "palpites.json"
            palpites_timestamps[participante_nome] = os.path.getmtime(palpites_path)
        
        # Executar processamento em modo teste
        with patch('scripts.processar_resultados.CAMPEONATOS_DIR', self.campeonatos_dir):
            sucesso = processar_resultados_modo_teste(nome_campeonato, 1)
        
        # Verificar que o processamento foi bem-sucedido
        assert sucesso, "Processamento em modo teste deve ser bem-sucedido"
        
        # Verificar que os timestamps dos arquivos não mudaram
        timestamps_depois = {
            "tabela": os.path.getmtime(tabela_path),
            "regras": os.path.getmtime(regras_path)
        }
        
        assert timestamps_antes["tabela"] == timestamps_depois["tabela"], \
            "Arquivo tabela.json não deve ser modificado em modo teste"
        assert timestamps_antes["regras"] == timestamps_depois["regras"], \
            "Arquivo regras.json não deve ser modificado em modo teste"
        
        # Verificar timestamps dos arquivos de palpites
        for palpites in palpites_participantes:
            participante_nome = palpites["apostador"].replace(" ", "")
            palpites_path = campeonato_dir / "Participantes" / participante_nome / "palpites.json"
            timestamp_depois = os.path.getmtime(palpites_path)
            
            assert palpites_timestamps[participante_nome] == timestamp_depois, \
                f"Arquivo palpites.json de {participante_nome} não deve ser modificado em modo teste"
        
        # Verificar que nenhum arquivo de backup foi criado
        backup_files = list(campeonato_dir.rglob("*backup*"))
        assert len(backup_files) == 0, "Nenhum arquivo de backup deve ser criado em modo teste"
        
        # Verificar que nenhum relatório foi salvo
        relatorio_files = list((campeonato_dir / "Resultados").glob("*.txt"))
        assert len(relatorio_files) == 0, "Nenhum relatório deve ser salvo em modo teste"

    @given(championship_data())
    @settings(max_examples=100)
    def test_property_21_ranking_completeness(self, championship_data_tuple):
        """
        Property 21: Ranking completeness
        
        For any round processed, the generated ranking should include an entry 
        for every registered participant in the championship.
        
        **Feature: bolao-prototype-scripts, Property 21: Ranking completeness**
        **Validates: Requirements 6.2**
        """
        tabela, regras, palpites_participantes = championship_data_tuple
        nome_campeonato = tabela["campeonato"]
        
        # Criar arquivos do campeonato
        self.create_championship_files(nome_campeonato, tabela, regras, palpites_participantes)
        
        # Obter lista de participantes registrados
        participantes_registrados = set()
        for palpites in palpites_participantes:
            participantes_registrados.add(palpites["apostador"])
        
        # Executar processamento em modo teste e capturar output
        with patch('scripts.processar_resultados.CAMPEONATOS_DIR', self.campeonatos_dir):
            with patch('builtins.print') as mock_print:
                sucesso = processar_resultados_modo_teste(nome_campeonato, 1)
        
        # Verificar que o processamento foi bem-sucedido
        assert sucesso, "Processamento deve ser bem-sucedido para testar completude do ranking"
        
        # Analisar o output capturado para verificar se todos os participantes estão presentes
        output_lines = []
        for call in mock_print.call_args_list:
            if call[0]:  # Se há argumentos posicionais
                # Dividir strings multi-linha em linhas individuais
                lines = str(call[0][0]).split('\n')
                output_lines.extend(lines)
        
        output_text = "\n".join(output_lines)
        
        # Verificar que cada participante registrado aparece no ranking
        for participante in participantes_registrados:
            assert participante in output_text, \
                f"Participante '{participante}' deve aparecer no ranking gerado"
        
        # Verificar que o número de participantes no ranking corresponde ao número registrado
        # Contar linhas de ranking válidas (contêm posição "Nº" e nome de participante)
        import re
        linhas_ranking = []
        for linha in output_lines:
            # Procurar por padrão de linha de ranking: "Nº Nome ..."
            match = re.match(r'^\s*(\d+)º\s+(\w+)', linha.strip())
            if match:
                posicao, nome_na_linha = match.groups()
                # Verificar se o nome corresponde a um participante registrado
                for participante in participantes_registrados:
                    if participante in linha:
                        linhas_ranking.append(linha)
                        break
        
        assert len(linhas_ranking) == len(participantes_registrados), \
            f"Ranking deve conter {len(participantes_registrados)} entradas, mas contém {len(linhas_ranking)}. " \
            f"Participantes registrados: {sorted(participantes_registrados)}. " \
            f"Linhas de ranking encontradas: {len(linhas_ranking)}"

    @given(championship_data())
    @settings(max_examples=100)
    def test_property_22_ranking_entry_completeness(self, championship_data_tuple):
        """
        Property 22: Ranking entry completeness
        
        For any participant in a generated ranking, the entry should include 
        match codes, points per game, round total, and accumulated total.
        
        **Feature: bolao-prototype-scripts, Property 22: Ranking entry completeness**
        **Validates: Requirements 6.3, 6.4**
        """
        tabela, regras, palpites_participantes = championship_data_tuple
        nome_campeonato = tabela["campeonato"]
        
        # Criar arquivos do campeonato
        self.create_championship_files(nome_campeonato, tabela, regras, palpites_participantes)
        
        # Executar processamento em modo teste e capturar output
        with patch('scripts.processar_resultados.CAMPEONATOS_DIR', self.campeonatos_dir):
            with patch('builtins.print') as mock_print:
                sucesso = processar_resultados_modo_teste(nome_campeonato, 1)
        
        # Verificar que o processamento foi bem-sucedido
        assert sucesso, "Processamento deve ser bem-sucedido para testar completude das entradas"
        
        # Analisar o output capturado
        output_lines = []
        for call in mock_print.call_args_list:
            if call[0]:
                # Dividir strings multi-linha em linhas individuais
                lines = str(call[0][0]).split('\n')
                output_lines.extend(lines)
        
        # Encontrar linhas do ranking (contêm posição com "º")
        linhas_ranking = []
        for linha in output_lines:
            if "º" in linha:
                # Verificar se a linha contém nome de participante
                for palpites in palpites_participantes:
                    if palpites["apostador"] in linha:
                        linhas_ranking.append(linha)
                        break
        
        # Verificar que cada linha de ranking contém as informações obrigatórias
        for linha in linhas_ranking:
            # Deve conter posição (número seguido de º)
            assert any(char.isdigit() for char in linha) and "º" in linha, \
                f"Linha de ranking deve conter posição: {linha}"
            
            # Deve conter pontos (números decimais)
            import re
            pontos_pattern = r'\d+\.\d+'
            pontos_matches = re.findall(pontos_pattern, linha)
            assert len(pontos_matches) >= 2, \
                f"Linha de ranking deve conter pelo menos 2 valores de pontos (rodada e acumulado): {linha}"
            
            # Deve conter códigos de acerto (letras maiúsculas após "|")
            if "|" in linha:
                parte_codigos = linha.split("|")[1] if len(linha.split("|")) > 1 else ""
                # Verificar se há códigos (letras maiúsculas)
                codigos_pattern = r'[A-Z]{1,3}'
                codigos_matches = re.findall(codigos_pattern, parte_codigos)
                # Pode não haver códigos se o participante não fez palpites
                # Mas se há "|", deve haver algum conteúdo
                if "|" in linha:
                    assert len(parte_codigos.strip()) > 0, \
                        f"Se há separador '|', deve haver códigos de acerto: {linha}"

    @given(championship_data())
    @settings(max_examples=100)
    def test_property_23_ranking_sort_order(self, championship_data_tuple):
        """
        Property 23: Ranking sort order
        
        For any generated ranking, participants should be ordered by accumulated 
        total score in descending order (highest score first).
        
        **Feature: bolao-prototype-scripts, Property 23: Ranking sort order**
        **Validates: Requirements 6.6**
        """
        tabela, regras, palpites_participantes = championship_data_tuple
        nome_campeonato = tabela["campeonato"]
        
        # Criar arquivos do campeonato
        self.create_championship_files(nome_campeonato, tabela, regras, palpites_participantes)
        
        # Executar processamento em modo teste e capturar output
        with patch('scripts.processar_resultados.CAMPEONATOS_DIR', self.campeonatos_dir):
            with patch('builtins.print') as mock_print:
                sucesso = processar_resultados_modo_teste(nome_campeonato, 1)
        
        # Verificar que o processamento foi bem-sucedido
        assert sucesso, "Processamento deve ser bem-sucedido para testar ordenação"
        
        # Analisar o output capturado para extrair pontuações
        output_lines = []
        for call in mock_print.call_args_list:
            if call[0]:
                # Dividir strings multi-linha em linhas individuais
                lines = str(call[0][0]).split('\n')
                output_lines.extend(lines)
        
        # Extrair pontuações acumuladas das linhas de ranking
        pontuacoes_acumuladas = []
        import re
        
        for linha in output_lines:
            if "º" in linha and any(palpites["apostador"] in linha for palpites in palpites_participantes):
                # Extrair pontuações usando regex mais específico
                # Formato: "posº nome pontos_rodada pontos_acumulados variacao"
                match = re.search(r'(\d+)º\s+(\w+)\s+(\d+\.\d+)\s+(\d+\.\d+)', linha)
                if match:
                    pontuacao_acumulada = float(match.group(4))  # Quarto grupo é pontos acumulados
                    pontuacoes_acumuladas.append(pontuacao_acumulada)
        
        # Verificar que as pontuações estão em ordem decrescente
        if len(pontuacoes_acumuladas) > 1:
            for i in range(len(pontuacoes_acumuladas) - 1):
                assert pontuacoes_acumuladas[i] >= pontuacoes_acumuladas[i + 1], \
                    f"Pontuações devem estar em ordem decrescente: {pontuacoes_acumuladas[i]} >= {pontuacoes_acumuladas[i + 1]}"
        
        # Verificar que a ordenação é estável (mesma pontuação mantém ordem)
        # Isso é implícito no algoritmo de ordenação do Python
        pontuacoes_unicas = list(set(pontuacoes_acumuladas))
        pontuacoes_unicas.sort(reverse=True)
        
        # Verificar que a maior pontuação está na primeira posição
        if pontuacoes_acumuladas:
            assert pontuacoes_acumuladas[0] == max(pontuacoes_acumuladas), \
                "Maior pontuação deve estar na primeira posição"
            
            # Verificar que a menor pontuação está na última posição
            assert pontuacoes_acumuladas[-1] == min(pontuacoes_acumuladas), \
                "Menor pontuação deve estar na última posição"

    @given(championship_with_unfinished_games())
    @settings(max_examples=100)
    def test_property_24_mandatory_games_validation(self, championship_data_tuple):
        """
        Property 24: Mandatory games validation
        
        For any round, the system should reject processing if any game marked as 
        "obrigatorio: true" has status other than "finalizado".
        
        **Feature: bolao-prototype-scripts, Property 24: Mandatory games validation**
        **Validates: Requirements 6.7**
        """
        tabela, regras, palpites_participantes = championship_data_tuple
        nome_campeonato = tabela["campeonato"]
        
        # Criar arquivos do campeonato
        self.create_championship_files(nome_campeonato, tabela, regras, palpites_participantes)
        
        # Verificar que há pelo menos um jogo obrigatório não finalizado
        jogos = tabela["rodadas"][0]["jogos"]
        jogos_obrigatorios_nao_finalizados = [
            jogo for jogo in jogos 
            if jogo.get("obrigatorio", False) and jogo.get("status") != "finalizado"
        ]
        
        assume(len(jogos_obrigatorios_nao_finalizados) > 0)  # Precisa haver jogos não finalizados
        
        # Executar processamento em modo teste
        with patch('scripts.processar_resultados.CAMPEONATOS_DIR', self.campeonatos_dir):
            sucesso = processar_resultados_modo_teste(nome_campeonato, 1)
        
        # Verificar que o processamento foi rejeitado
        assert not sucesso, \
            "Processamento deve ser rejeitado quando há jogos obrigatórios não finalizados"
        
        # Testar também a função de validação diretamente
        todos_finalizados, jogos_pendentes = validar_jogos_obrigatorios_finalizados(jogos)
        
        assert not todos_finalizados, \
            "Validação deve retornar False quando há jogos obrigatórios não finalizados"
        
        assert len(jogos_pendentes) > 0, \
            "Lista de jogos pendentes deve conter pelo menos um jogo"
        
        # Verificar que todos os jogos pendentes são realmente obrigatórios e não finalizados
        for jogo_info in jogos_pendentes:
            # Encontrar o jogo correspondente na lista usando o ID do jogo
            jogo_encontrado = False
            # Extrair ID do jogo da string de informação (formato: "Time1 x Time2 (ID: jogo-XXX)")
            import re
            id_match = re.search(r'\(ID: ([^)]+)\)', jogo_info)
            if id_match:
                jogo_id = id_match.group(1)
                
                # Procurar o jogo pelo ID
                for jogo in jogos:
                    if jogo.get("id") == jogo_id:
                        assert jogo.get("obrigatorio", False), \
                            f"Jogo pendente deve ser obrigatório: {jogo_info}"
                        assert jogo.get("status") != "finalizado", \
                            f"Jogo pendente não deve estar finalizado: {jogo_info}"
                        jogo_encontrado = True
                        break
                
                assert jogo_encontrado, f"Jogo pendente deve existir na lista: {jogo_info}"
            else:
                # Se não conseguir extrair ID, verificar se pelo menos os nomes dos times estão corretos
                # Extrair nomes dos times da string (formato: "Time1 x Time2")
                teams_match = re.match(r'^([^x]+) x ([^(]+)', jogo_info.strip())
                if teams_match:
                    mandante_info = teams_match.group(1).strip()
                    visitante_info = teams_match.group(2).strip()
                    
                    # Procurar jogo pelos nomes dos times
                    for jogo in jogos:
                        if (jogo.get("mandante") == mandante_info and 
                            jogo.get("visitante") == visitante_info and
                            jogo.get("obrigatorio", False) and
                            jogo.get("status") != "finalizado"):
                            jogo_encontrado = True
                            break
                    
                    assert jogo_encontrado, f"Jogo pendente deve existir na lista: {jogo_info}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])