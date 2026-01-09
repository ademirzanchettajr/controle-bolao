"""
Testes de propriedade para o script de geração de regras.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de geração de regras definidas no design document.
"""

import json
import pytest
import shutil
import tempfile
from pathlib import Path
from hypothesis import given, settings, strategies as st

from src.scripts.gerar_regras import (
    gerar_regras,
    criar_estrutura_regras_completa,
    carregar_template_regras_padrao,
    escrever_arquivo_regras
)
from src.scripts.criar_campeonato import criar_campeonato
from src.config import REGRAS_PONTUACAO_PADRAO, ARQUIVO_REGRAS
from src.utils.validacao import validar_estrutura_regras


# Generators para property-based testing
@st.composite
def valid_championship_data(draw):
    """
    Gera dados válidos para criação de campeonato.
    
    Returns:
        Tupla (nome, temporada) com dados válidos
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
    
    return nome, temporada


@st.composite
def championship_metadata(draw):
    """
    Gera metadados de campeonato para testes de estrutura de regras.
    """
    # Nomes simples para testes
    nomes = ["Brasileirão", "Copa", "Estadual", "Liga", "Torneio"]
    nome = draw(st.sampled_from(nomes))
    
    # Temporadas válidas
    temporada = str(draw(st.integers(min_value=2020, max_value=2030)))
    
    return nome, temporada


class TestRulesGenerationProperties:
    """Testes de propriedade para geração de regras."""
    
    def setup_method(self):
        """Configura ambiente de teste com diretório temporário."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_campeonatos_dir = None
        
        # Substitui temporariamente o diretório de campeonatos
        import src.config
        self.original_campeonatos_dir = src.config.CAMPEONATOS_DIR
        src.config.CAMPEONATOS_DIR = Path(self.temp_dir) / "Campeonatos"
        
        # Atualiza também nos módulos relevantes
        import src.scripts.criar_campeonato
        src.scripts.criar_campeonato.CAMPEONATOS_DIR = src.config.CAMPEONATOS_DIR
        
        import src.scripts.gerar_regras
        src.scripts.gerar_regras.CAMPEONATOS_DIR = src.config.CAMPEONATOS_DIR
    
    def teardown_method(self):
        """Limpa ambiente de teste."""
        # Restaura diretório original
        if self.original_campeonatos_dir:
            import src.config
            src.config.CAMPEONATOS_DIR = self.original_campeonatos_dir
            
            import src.scripts.criar_campeonato
            src.scripts.criar_campeonato.CAMPEONATOS_DIR = self.original_campeonatos_dir
            
            import src.scripts.gerar_regras
            src.scripts.gerar_regras.CAMPEONATOS_DIR = self.original_campeonatos_dir
        
        # Remove diretório temporário
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @given(valid_championship_data())
    @settings(max_examples=50)
    def test_property_4_rules_file_completeness(self, championship_data):
        """
        Property 4: Rules file completeness
        
        For any championship, the generated rules file should contain exactly 10 
        scoring rules, each with the required fields "pontos" (or "pontos_base"), 
        "descricao", and "codigo".
        
        **Feature: bolao-prototype-scripts, Property 4: Rules file completeness**
        **Validates: Requirements 2.1, 2.3**
        """
        nome, temporada = championship_data
        
        # Primeiro criar o campeonato
        sucesso_campeonato = criar_campeonato(nome, temporada, None, forcar=True)
        assert sucesso_campeonato, f"Criação do campeonato '{nome}' deve ter sucesso"
        
        # Importa configuração atualizada
        from src.config import CAMPEONATOS_DIR
        from src.utils.normalizacao import normalizar_nome_campeonato
        
        # Normalizar nome do campeonato
        nome_normalizado = normalizar_nome_campeonato(nome)
        
        # Executar geração de regras
        sucesso_regras = gerar_regras(nome_normalizado, sobrescrever=True)
        assert sucesso_regras, f"Geração de regras para '{nome}' deve ter sucesso"
        
        # Verificar se arquivo de regras foi criado
        caminho_campeonato = CAMPEONATOS_DIR / nome_normalizado
        arquivo_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
        
        assert arquivo_regras.exists(), f"Arquivo de regras deve existir: {arquivo_regras}"
        
        # Carregar e validar conteúdo
        with open(arquivo_regras, 'r', encoding='utf-8') as f:
            dados_regras = json.load(f)
        
        # Deve ser um dicionário válido
        assert isinstance(dados_regras, dict), "Dados das regras devem ser um dicionário"
        
        # Deve passar na validação estrutural
        valido, erros = validar_estrutura_regras(dados_regras)
        assert valido, f"Estrutura das regras deve ser válida. Erros: {erros}"
        
        # Verificar que contém exatamente 10 regras
        assert "regras" in dados_regras, "Campo 'regras' deve estar presente"
        regras = dados_regras["regras"]
        assert isinstance(regras, dict), "Campo 'regras' deve ser um dicionário"
        
        # Deve ter exatamente 10 regras (conforme REGRAS_PONTUACAO_PADRAO)
        expected_rules_count = len(REGRAS_PONTUACAO_PADRAO)
        actual_rules_count = len(regras)
        assert actual_rules_count == expected_rules_count, (
            f"Deve haver exatamente {expected_rules_count} regras, "
            f"encontradas {actual_rules_count}"
        )
        
        # Verificar que cada regra tem os campos obrigatórios
        for nome_regra, regra in regras.items():
            assert isinstance(regra, dict), f"Regra '{nome_regra}' deve ser um dicionário"
            
            # Deve ter pontos ou pontos_base
            has_pontos = "pontos" in regra
            has_pontos_base = "pontos_base" in regra
            assert has_pontos or has_pontos_base, (
                f"Regra '{nome_regra}' deve ter campo 'pontos' ou 'pontos_base'"
            )
            
            # Campos obrigatórios
            campos_obrigatorios = ["descricao", "codigo"]
            for campo in campos_obrigatorios:
                assert campo in regra, f"Regra '{nome_regra}' deve ter campo '{campo}'"
                assert isinstance(regra[campo], str), (
                    f"Campo '{campo}' da regra '{nome_regra}' deve ser string"
                )
                assert regra[campo].strip(), (
                    f"Campo '{campo}' da regra '{nome_regra}' não pode estar vazio"
                )
            
            # Verificar tipo dos pontos
            if has_pontos:
                assert isinstance(regra["pontos"], (int, float)), (
                    f"Campo 'pontos' da regra '{nome_regra}' deve ser numérico"
                )
            
            if has_pontos_base:
                assert isinstance(regra["pontos_base"], (int, float)), (
                    f"Campo 'pontos_base' da regra '{nome_regra}' deve ser numérico"
                )
        
        # Verificar que as regras correspondem ao template padrão
        template_regras = carregar_template_regras_padrao()
        assert len(regras) == len(template_regras), (
            "Número de regras deve corresponder ao template padrão"
        )
        
        # Verificar que todas as regras do template estão presentes
        for nome_regra_template in template_regras.keys():
            assert nome_regra_template in regras, (
                f"Regra '{nome_regra_template}' do template deve estar presente"
            )
    
    @given(valid_championship_data())
    @settings(max_examples=50)
    def test_property_5_rules_file_metadata_inclusion(self, championship_data):
        """
        Property 5: Rules file metadata inclusion
        
        For any championship name and season provided, the generated rules file 
        should include those exact values in the "campeonato" and "temporada" fields.
        
        **Feature: bolao-prototype-scripts, Property 5: Rules file metadata inclusion**
        **Validates: Requirements 2.2, 2.5**
        """
        nome, temporada = championship_data
        
        # Primeiro criar o campeonato
        sucesso_campeonato = criar_campeonato(nome, temporada, None, forcar=True)
        assert sucesso_campeonato, f"Criação do campeonato '{nome}' deve ter sucesso"
        
        # Importa configuração atualizada
        from src.config import CAMPEONATOS_DIR
        from src.utils.normalizacao import normalizar_nome_campeonato
        
        # Normalizar nome do campeonato
        nome_normalizado = normalizar_nome_campeonato(nome)
        
        # Executar geração de regras
        sucesso_regras = gerar_regras(nome_normalizado, sobrescrever=True)
        assert sucesso_regras, f"Geração de regras para '{nome}' deve ter sucesso"
        
        # Verificar se arquivo de regras foi criado
        caminho_campeonato = CAMPEONATOS_DIR / nome_normalizado
        arquivo_regras = caminho_campeonato / "Regras" / ARQUIVO_REGRAS
        
        assert arquivo_regras.exists(), f"Arquivo de regras deve existir: {arquivo_regras}"
        
        # Carregar conteúdo
        with open(arquivo_regras, 'r', encoding='utf-8') as f:
            dados_regras = json.load(f)
        
        # Deve ser um dicionário válido
        assert isinstance(dados_regras, dict), "Dados das regras devem ser um dicionário"
        
        # Verificar campos de metadados obrigatórios
        campos_metadata = ["campeonato", "temporada", "versao"]
        for campo in campos_metadata:
            assert campo in dados_regras, f"Campo '{campo}' deve estar presente"
            assert isinstance(dados_regras[campo], str), f"Campo '{campo}' deve ser string"
            assert dados_regras[campo].strip(), f"Campo '{campo}' não pode estar vazio"
        
        # Verificar que nome e temporada correspondem exatamente aos fornecidos
        assert dados_regras["campeonato"] == nome, (
            f"Campo 'campeonato' deve ser '{nome}', "
            f"encontrado '{dados_regras['campeonato']}'"
        )
        
        assert dados_regras["temporada"] == temporada, (
            f"Campo 'temporada' deve ser '{temporada}', "
            f"encontrado '{dados_regras['temporada']}'"
        )
        
        # Verificar que versão tem formato válido
        versao = dados_regras["versao"]
        assert "." in versao, "Versão deve ter formato X.Y"
        partes_versao = versao.split(".")
        assert len(partes_versao) >= 2, "Versão deve ter pelo menos duas partes"
        
        # Verificar campo de data de criação (opcional mas se presente deve ser válido)
        if "data_criacao" in dados_regras:
            from src.utils.validacao import validar_data
            data_criacao = dados_regras["data_criacao"]
            valido, erro = validar_data(data_criacao)
            assert valido, f"Data de criação deve ser válida: {erro}"
        
        # Verificar observações (opcional mas se presente deve ser lista de strings)
        if "observacoes" in dados_regras:
            observacoes = dados_regras["observacoes"]
            assert isinstance(observacoes, list), "Observações devem ser uma lista"
            for i, obs in enumerate(observacoes):
                assert isinstance(obs, str), f"Observação {i+1} deve ser string"
                assert obs.strip(), f"Observação {i+1} não pode estar vazia"


class TestRulesGenerationHelpers:
    """Testes de propriedade para funções auxiliares de geração de regras."""
    
    @given(championship_metadata())
    @settings(max_examples=50)
    def test_criar_estrutura_regras_completa_validity(self, metadata):
        """
        Testa que a estrutura completa das regras é sempre válida.
        """
        nome, temporada = metadata
        
        # Criar estrutura
        estrutura = criar_estrutura_regras_completa(nome, temporada)
        
        # Deve ser um dicionário
        assert isinstance(estrutura, dict)
        
        # Deve passar na validação
        valido, erros = validar_estrutura_regras(estrutura)
        assert valido, f"Estrutura completa deve ser válida. Erros: {erros}"
        
        # Campos devem corresponder aos parâmetros
        assert estrutura["campeonato"] == nome
        assert estrutura["temporada"] == temporada
        
        # Deve ter todas as regras padrão
        template_regras = carregar_template_regras_padrao()
        assert len(estrutura["regras"]) == len(template_regras)
        
        # Cada regra deve ter estrutura válida
        for nome_regra, regra in estrutura["regras"].items():
            assert isinstance(regra, dict)
            assert "descricao" in regra
            assert "codigo" in regra
            assert "pontos" in regra or "pontos_base" in regra
    
    @settings(max_examples=50)
    @given(st.integers(min_value=1, max_value=100))
    def test_carregar_template_regras_padrao_consistency(self, _):
        """
        Testa que o template de regras padrão é sempre consistente.
        """
        template = carregar_template_regras_padrao()
        
        # Deve ser um dicionário
        assert isinstance(template, dict)
        
        # Deve ter pelo menos uma regra
        assert len(template) > 0
        
        # Deve corresponder à configuração padrão
        assert len(template) == len(REGRAS_PONTUACAO_PADRAO)
        
        # Cada regra deve ter estrutura válida
        for nome_regra, regra in template.items():
            assert isinstance(regra, dict)
            assert "descricao" in regra
            assert "codigo" in regra
            assert "pontos" in regra or "pontos_base" in regra
            
            # Verificar tipos
            assert isinstance(regra["descricao"], str)
            assert isinstance(regra["codigo"], str)
            
            if "pontos" in regra:
                assert isinstance(regra["pontos"], (int, float))
            
            if "pontos_base" in regra:
                assert isinstance(regra["pontos_base"], (int, float))
            
            if "bonus_divisor" in regra:
                assert isinstance(regra["bonus_divisor"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])