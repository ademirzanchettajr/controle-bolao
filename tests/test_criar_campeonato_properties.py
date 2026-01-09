"""
Testes de propriedade para o script de criação de campeonato.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de criação de campeonato definidas no design document.
"""

import json
import pytest
import shutil
import tempfile
from pathlib import Path
from hypothesis import given, settings, strategies as st

from src.scripts.criar_campeonato import (
    criar_campeonato,
    criar_estrutura_basica_tabela,
    criar_estrutura_basica_regras,
    gerar_codigo_campeonato
)
from src.config import SUBDIRS_CAMPEONATO, ARQUIVO_REGRAS, ARQUIVO_TABELA
from src.utils.validacao import validar_estrutura_tabela, validar_estrutura_regras


# Generators para property-based testing
@st.composite
def valid_championship_data(draw):
    """
    Gera dados válidos para criação de campeonato.
    
    Returns:
        Tupla (nome, temporada, codigo) com dados válidos
    """
    # Nomes de campeonatos realistas
    base_names = [
        "Brasileirão", "Copa do Brasil", "Campeonato Paulista", 
        "Libertadores", "Sul-Americana", "Mundial de Clubes",
        "Série A", "Série B", "Copa América", "Estadual"
    ]
    
    base_name = draw(st.sampled_from(base_names))
    
    # Adiciona ano opcional
    year = draw(st.integers(min_value=2020, max_value=2030))
    name_formats = [
        base_name,
        f"{base_name} {year}",
        f"{base_name}-{year}",
        f"{base_name} / {year}"
    ]
    
    nome = draw(st.sampled_from(name_formats))
    temporada = str(year)
    
    # Código opcional (5 caracteres alfanuméricos)
    codigo = draw(st.one_of(
        st.none(),
        st.text(min_size=5, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    ))
    
    return nome, temporada, codigo


@st.composite
def championship_name_with_special_chars(draw):
    """
    Gera nomes de campeonatos com caracteres especiais para testar normalização.
    """
    base_names = ["Brasileirão", "Copa do Brasil", "Série A"]
    base_name = draw(st.sampled_from(base_names))
    
    # Adiciona caracteres problemáticos
    special_chars = [": Final", "/Grupo A", "\\Especial", "*Teste", "?Extra", "\"Aspas\""]
    special = draw(st.sampled_from(special_chars))
    
    # Adiciona espaços extras
    leading_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    trailing_spaces = draw(st.text(alphabet=" ", min_size=0, max_size=3))
    
    return leading_spaces + base_name + special + trailing_spaces


class TestChampionshipCreationProperties:
    """Testes de propriedade para criação de campeonatos."""
    
    def setup_method(self):
        """Configura ambiente de teste com diretório temporário."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_campeonatos_dir = None
        
        # Substitui temporariamente o diretório de campeonatos
        import src.config
        self.original_campeonatos_dir = src.config.CAMPEONATOS_DIR
        src.config.CAMPEONATOS_DIR = Path(self.temp_dir) / "Campeonatos"
        
        # Atualiza também no módulo criar_campeonato
        import src.scripts.criar_campeonato
        src.scripts.criar_campeonato.CAMPEONATOS_DIR = src.config.CAMPEONATOS_DIR
    
    def teardown_method(self):
        """Limpa ambiente de teste."""
        # Restaura diretório original
        if self.original_campeonatos_dir:
            import src.config
            src.config.CAMPEONATOS_DIR = self.original_campeonatos_dir
            
            import src.scripts.criar_campeonato
            src.scripts.criar_campeonato.CAMPEONATOS_DIR = self.original_campeonatos_dir
        
        # Remove diretório temporário
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @given(valid_championship_data())
    @settings(max_examples=50)
    def test_property_1_championship_directory_structure_completeness(self, championship_data):
        """
        Property 1: Championship directory structure completeness
        
        For any valid championship name and season, after executing the creation script, 
        the championship directory should contain exactly 4 subdirectories: "Regras", 
        "Tabela", "Resultados", and "Participantes".
        
        **Feature: bolao-prototype-scripts, Property 1: Championship directory structure completeness**
        **Validates: Requirements 1.1, 1.2**
        """
        nome, temporada, codigo = championship_data
        
        # Executa criação do campeonato
        sucesso = criar_campeonato(nome, temporada, codigo, forcar=True)
        
        # Deve ter sucesso
        assert sucesso, f"Criação do campeonato '{nome}' deve ter sucesso"
        
        # Importa configuração atualizada
        from src.config import CAMPEONATOS_DIR
        from src.utils.normalizacao import normalizar_nome_campeonato
        
        # Verifica se diretório do campeonato foi criado
        nome_normalizado = normalizar_nome_campeonato(nome)
        caminho_campeonato = CAMPEONATOS_DIR / nome_normalizado
        
        assert caminho_campeonato.exists(), f"Diretório do campeonato deve existir: {caminho_campeonato}"
        assert caminho_campeonato.is_dir(), "Caminho do campeonato deve ser um diretório"
        
        # Verifica se todos os subdiretórios obrigatórios existem
        subdirs_encontrados = []
        for item in caminho_campeonato.iterdir():
            if item.is_dir():
                subdirs_encontrados.append(item.name)
        
        # Deve conter exatamente os 4 subdiretórios obrigatórios
        subdirs_esperados = set(SUBDIRS_CAMPEONATO)
        subdirs_encontrados_set = set(subdirs_encontrados)
        
        assert subdirs_encontrados_set == subdirs_esperados, (
            f"Subdiretórios encontrados {subdirs_encontrados_set} "
            f"devem ser exatamente {subdirs_esperados}"
        )
        
        # Verifica que cada subdiretório é realmente um diretório
        for subdir in SUBDIRS_CAMPEONATO:
            subdir_path = caminho_campeonato / subdir
            assert subdir_path.exists(), f"Subdiretório '{subdir}' deve existir"
            assert subdir_path.is_dir(), f"'{subdir}' deve ser um diretório"
    
    @given(valid_championship_data())
    @settings(max_examples=50)
    def test_property_2_initial_json_files_validity(self, championship_data):
        """
        Property 2: Initial JSON files validity
        
        For any created championship, the initial "regras.json" and "tabela.json" 
        files should be valid JSON with the required top-level fields present.
        
        **Feature: bolao-prototype-scripts, Property 2: Initial JSON files validity**
        **Validates: Requirements 1.3**
        """
        nome, temporada, codigo = championship_data
        
        # Executa criação do campeonato
        sucesso = criar_campeonato(nome, temporada, codigo, forcar=True)
        
        # Deve ter sucesso
        assert sucesso, f"Criação do campeonato '{nome}' deve ter sucesso"
        
        # Importa configuração atualizada
        from src.config import CAMPEONATOS_DIR
        from src.utils.normalizacao import normalizar_nome_campeonato
        
        # Localiza diretório do campeonato
        nome_normalizado = normalizar_nome_campeonato(nome)
        caminho_campeonato = CAMPEONATOS_DIR / nome_normalizado
        
        # Verifica arquivo tabela.json
        arquivo_tabela = caminho_campeonato / "Tabela" / ARQUIVO_TABELA
        assert arquivo_tabela.exists(), f"Arquivo {ARQUIVO_TABELA} deve existir"
        
        # Carrega e valida JSON da tabela
        with open(arquivo_tabela, 'r', encoding='utf-8') as f:
            dados_tabela = json.load(f)
        
        # Deve ser um dicionário válido
        assert isinstance(dados_tabela, dict), "Dados da tabela devem ser um dicionário"
        
        # Valida estrutura usando função de validação
        valido, erros = validar_estrutura_tabela(dados_tabela)
        assert valido, f"Estrutura da tabela deve ser válida. Erros: {erros}"
        
        # Verifica campos obrigatórios específicos
        campos_obrigatorios_tabela = [
            "campeonato", "temporada", "rodada_atual", 
            "data_atualizacao", "codigo_campeonato", "rodadas"
        ]
        for campo in campos_obrigatorios_tabela:
            assert campo in dados_tabela, f"Campo '{campo}' deve estar presente na tabela"
        
        # Verifica que os valores dos campos fazem sentido
        assert dados_tabela["campeonato"] == nome, "Nome do campeonato deve corresponder"
        assert dados_tabela["temporada"] == temporada, "Temporada deve corresponder"
        assert isinstance(dados_tabela["rodada_atual"], int), "Rodada atual deve ser inteiro"
        assert dados_tabela["rodada_atual"] >= 0, "Rodada atual deve ser não-negativa"
        assert isinstance(dados_tabela["rodadas"], list), "Rodadas deve ser uma lista"
        
        # Verifica arquivo regras.json
        arquivo_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
        assert arquivo_regras.exists(), f"Arquivo {ARQUIVO_REGRAS} deve existir"
        
        # Carrega e valida JSON das regras
        with open(arquivo_regras, 'r', encoding='utf-8') as f:
            dados_regras = json.load(f)
        
        # Deve ser um dicionário válido
        assert isinstance(dados_regras, dict), "Dados das regras devem ser um dicionário"
        
        # Valida estrutura usando função de validação
        valido, erros = validar_estrutura_regras(dados_regras)
        assert valido, f"Estrutura das regras deve ser válida. Erros: {erros}"
        
        # Verifica campos obrigatórios específicos
        campos_obrigatorios_regras = ["campeonato", "temporada", "versao", "regras"]
        for campo in campos_obrigatorios_regras:
            assert campo in dados_regras, f"Campo '{campo}' deve estar presente nas regras"
        
        # Verifica que os valores dos campos fazem sentido
        assert dados_regras["campeonato"] == nome, "Nome do campeonato deve corresponder"
        assert dados_regras["temporada"] == temporada, "Temporada deve corresponder"
        assert isinstance(dados_regras["versao"], str), "Versão deve ser string"
        assert isinstance(dados_regras["regras"], dict), "Regras deve ser um dicionário"
        assert len(dados_regras["regras"]) > 0, "Deve haver pelo menos uma regra"


class TestChampionshipCreationHelpers:
    """Testes de propriedade para funções auxiliares de criação de campeonato."""
    
    @given(st.text(min_size=1, max_size=50), st.text(min_size=4, max_size=4, alphabet="0123456789"))
    @settings(max_examples=50)
    def test_estrutura_basica_tabela_validity(self, nome, temporada):
        """
        Testa que a estrutura básica da tabela é sempre válida.
        """
        codigo = gerar_codigo_campeonato()
        estrutura = criar_estrutura_basica_tabela(nome, temporada, codigo)
        
        # Deve ser um dicionário
        assert isinstance(estrutura, dict)
        
        # Deve passar na validação
        valido, erros = validar_estrutura_tabela(estrutura)
        assert valido, f"Estrutura básica deve ser válida. Erros: {erros}"
        
        # Campos devem corresponder aos parâmetros
        assert estrutura["campeonato"] == nome
        assert estrutura["temporada"] == temporada
        assert estrutura["codigo_campeonato"] == codigo
    
    @given(st.text(min_size=1, max_size=50), st.text(min_size=4, max_size=4, alphabet="0123456789"))
    @settings(max_examples=50)
    def test_estrutura_basica_regras_validity(self, nome, temporada):
        """
        Testa que a estrutura básica das regras é sempre válida.
        """
        estrutura = criar_estrutura_basica_regras(nome, temporada)
        
        # Deve ser um dicionário
        assert isinstance(estrutura, dict)
        
        # Deve passar na validação
        valido, erros = validar_estrutura_regras(estrutura)
        assert valido, f"Estrutura básica deve ser válida. Erros: {erros}"
        
        # Campos devem corresponder aos parâmetros
        assert estrutura["campeonato"] == nome
        assert estrutura["temporada"] == temporada
    
    @settings(max_examples=100)
    @given(st.integers(min_value=1, max_value=100))
    def test_gerar_codigo_campeonato_format(self, _):
        """
        Testa que o código gerado sempre tem o formato correto.
        """
        codigo = gerar_codigo_campeonato()
        
        # Deve ser string de 5 caracteres
        assert isinstance(codigo, str)
        assert len(codigo) == 5
        
        # Deve conter apenas letras maiúsculas e dígitos
        assert codigo.isalnum()
        assert codigo.isupper() or codigo.isdigit() or any(c.isupper() for c in codigo)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])