#!/usr/bin/env python3
"""
Testes de propriedade para processamento de resultados em modo final.

Este módulo contém testes baseados em propriedades (Property-Based Testing) 
para validar o comportamento do script de processamento de resultados em modo final.
"""

import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from hypothesis import given, strategies as st, assume
import pytest
import sys

# Adicionar src ao path para imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

from scripts.processar_resultados import (
    criar_backup_tabela,
    atualizar_rodada_atual,
    salvar_relatorio_rodada,
    processar_resultados_modo_final
)


# Estratégias para geração de dados de teste
@st.composite
def tabela_valida(draw):
    """Gera uma estrutura de tabela válida."""
    return {
        "campeonato": draw(st.text(min_size=1, max_size=50)),
        "temporada": draw(st.integers(min_value=2020, max_value=2030)),
        "rodada_atual": draw(st.integers(min_value=1, max_value=38)),
        "codigo_campeonato": draw(st.text(min_size=1, max_size=10)),
        "rodadas": []
    }


@st.composite
def relatorio_conteudo(draw):
    """Gera conteúdo de relatório válido."""
    # Gerar texto sem caracteres de controle problemáticos
    alphabet = st.characters(min_codepoint=32, max_codepoint=126, blacklist_characters='\r\n\t')
    return {
        "relatorio": draw(st.text(alphabet=alphabet, min_size=10, max_size=1000)),
        "resumo": draw(st.text(alphabet=alphabet, min_size=10, max_size=500))
    }


class TestProcessarResultadosModoFinalProperties:
    """Testes de propriedade para processamento de resultados em modo final."""
    
    @given(tabela_valida())
    def test_property_25_backup_creation_with_timestamp(self, tabela_data):
        """
        Property 25: Backup creation with timestamp
        
        Verifica que o backup da tabela é criado com timestamp no nome
        e contém os mesmos dados do arquivo original.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar arquivo de tabela temporário
            caminho_tabela = Path(temp_dir) / "tabela.json"
            with open(caminho_tabela, 'w', encoding='utf-8') as f:
                json.dump(tabela_data, f, ensure_ascii=False, indent=2)
            
            # Criar backup
            nome_backup = criar_backup_tabela(caminho_tabela)
            
            # Verificar que backup foi criado
            caminho_backup = caminho_tabela.parent / nome_backup
            assert caminho_backup.exists(), "Arquivo de backup deve ser criado"
            
            # Verificar formato do nome do backup
            assert nome_backup.startswith("tabela_backup_"), "Nome do backup deve ter prefixo correto"
            assert nome_backup.endswith(".json"), "Nome do backup deve ter extensão .json"
            
            # Verificar que timestamp está no formato correto (YYYYMMDD_HHMMSS)
            timestamp_part = nome_backup.replace("tabela_backup_", "").replace(".json", "")
            assert len(timestamp_part) == 15, "Timestamp deve ter 15 caracteres (YYYYMMDD_HHMMSS)"
            assert timestamp_part[8] == "_", "Timestamp deve ter underscore separando data e hora"
            
            # Verificar que conteúdo do backup é idêntico ao original
            with open(caminho_backup, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            assert backup_data == tabela_data, "Conteúdo do backup deve ser idêntico ao original"
    
    @given(tabela_valida(), st.integers(min_value=1, max_value=50))
    def test_property_26_current_round_update(self, tabela_data, nova_rodada):
        """
        Property 26: Current round update
        
        Verifica que o campo rodada_atual é atualizado corretamente
        no arquivo tabela.json.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar arquivo de tabela temporário
            caminho_tabela = Path(temp_dir) / "tabela.json"
            with open(caminho_tabela, 'w', encoding='utf-8') as f:
                json.dump(tabela_data, f, ensure_ascii=False, indent=2)
            
            # Atualizar rodada atual
            atualizar_rodada_atual(caminho_tabela, nova_rodada)
            
            # Verificar que arquivo foi atualizado
            with open(caminho_tabela, 'r', encoding='utf-8') as f:
                tabela_atualizada = json.load(f)
            
            # Verificar que rodada_atual foi atualizada
            assert tabela_atualizada["rodada_atual"] == nova_rodada, "Campo rodada_atual deve ser atualizado"
            
            # Verificar que outros campos permaneceram inalterados
            for campo in ["campeonato", "temporada", "codigo_campeonato", "rodadas"]:
                assert tabela_atualizada[campo] == tabela_data[campo], f"Campo {campo} não deve ser alterado"
    
    @given(st.integers(min_value=1, max_value=50), relatorio_conteudo())
    def test_property_27_report_file_generation(self, numero_rodada, conteudo):
        """
        Property 27: Report file generation
        
        Verifica que o arquivo de relatório é gerado corretamente
        no diretório Resultados com nome padronizado.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            caminho_resultados = Path(temp_dir) / "Resultados"
            
            # Salvar relatório
            nome_arquivo = salvar_relatorio_rodada(
                caminho_resultados, numero_rodada, 
                conteudo["relatorio"], conteudo["resumo"]
            )
            
            # Verificar que diretório foi criado
            assert caminho_resultados.exists(), "Diretório Resultados deve ser criado"
            assert caminho_resultados.is_dir(), "Resultados deve ser um diretório"
            
            # Verificar formato do nome do arquivo
            nome_esperado = f"rodada{numero_rodada:02d}.txt"
            assert nome_arquivo == nome_esperado, f"Nome do arquivo deve ser {nome_esperado}"
            
            # Verificar que arquivo foi criado
            caminho_arquivo = caminho_resultados / nome_arquivo
            assert caminho_arquivo.exists(), "Arquivo de relatório deve ser criado"
            
            # Verificar que arquivo não está vazio
            assert caminho_arquivo.stat().st_size > 0, "Arquivo de relatório não deve estar vazio"
    
    @given(st.integers(min_value=1, max_value=50), relatorio_conteudo())
    def test_property_28_report_content_completeness(self, numero_rodada, conteudo):
        """
        Property 28: Report content completeness
        
        Verifica que o conteúdo do relatório inclui todas as informações
        necessárias: cabeçalho, timestamp, relatório e resumo.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            caminho_resultados = Path(temp_dir) / "Resultados"
            
            # Salvar relatório
            nome_arquivo = salvar_relatorio_rodada(
                caminho_resultados, numero_rodada,
                conteudo["relatorio"], conteudo["resumo"]
            )
            
            # Ler conteúdo do arquivo
            caminho_arquivo = caminho_resultados / nome_arquivo
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                conteudo_arquivo = f.read()
            
            # Verificar presença do cabeçalho da rodada
            assert f"RELATÓRIO DA RODADA {numero_rodada}" in conteudo_arquivo, "Cabeçalho da rodada deve estar presente"
            
            # Verificar presença do timestamp
            assert "Gerado em:" in conteudo_arquivo, "Timestamp de geração deve estar presente"
            
            # Verificar presença do relatório
            assert conteudo["relatorio"] in conteudo_arquivo, "Conteúdo do relatório deve estar presente"
            
            # Verificar presença do resumo
            assert conteudo["resumo"] in conteudo_arquivo, "Conteúdo do resumo deve estar presente"
            
            # Verificar que timestamp tem formato válido
            linhas = conteudo_arquivo.split('\n')
            linha_timestamp = None
            for linha in linhas:
                if linha.startswith("Gerado em:"):
                    linha_timestamp = linha
                    break
            
            assert linha_timestamp is not None, "Linha de timestamp deve existir"
            
            # Extrair timestamp e verificar formato
            timestamp_str = linha_timestamp.replace("Gerado em: ", "").strip()
            try:
                datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pytest.fail(f"Timestamp deve ter formato válido YYYY-MM-DD HH:MM:SS, recebido: {timestamp_str}")


if __name__ == "__main__":
    # Executar testes específicos se chamado diretamente
    pytest.main([__file__, "-v"])