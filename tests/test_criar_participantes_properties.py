"""
Testes de propriedade para o script de criação de participantes.

Este módulo contém property-based tests usando hypothesis para validar
as propriedades de criação de participantes definidas no design document.
"""

import json
import pytest
import shutil
import tempfile
from pathlib import Path
from hypothesis import given, settings, strategies as st

from src.scripts.criar_participantes import (
    criar_participantes,
    processar_lista_participantes,
    criar_estrutura_basica_palpites,
    gerar_codigo_participante
)
from src.scripts.criar_campeonato import criar_campeonato
from src.config import ARQUIVO_PALPITES
from src.utils.validacao import validar_estrutura_palpites
from src.utils.normalizacao import normalizar_nome_participante


# Generators para property-based testing
@st.composite
def valid_participant_names(draw):
    """
    Gera lista de nomes válidos de participantes.
    
    Returns:
        Lista de nomes de participantes realistas
    """
    # Nomes brasileiros comuns
    first_names = [
        "Mario", "João", "Maria", "Ana", "Carlos", "Fernanda", 
        "Pedro", "Juliana", "Roberto", "Carla", "José", "Patricia",
        "Antonio", "Lucia", "Francisco", "Mariana", "Paulo", "Beatriz"
    ]
    
    last_names = [
        "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira",
        "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro",
        "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes"
    ]
    
    # Gera entre 1 e 10 participantes
    num_participants = draw(st.integers(min_value=1, max_value=10))
    
    participants = []
    for _ in range(num_participants):
        first = draw(st.sampled_from(first_names))
        last = draw(st.sampled_from(last_names))
        
        # Algumas variações de formato
        name_formats = [
            f"{first} {last}",
            f"{first} da {last}",
            f"{first} {last} Jr",
            f"{first} {last} Filho",
            f"{first}-{last}",
        ]
        
        name = draw(st.sampled_from(name_formats))
        participants.append(name)
    
    return participants


@st.composite
def participant_names_with_special_chars(draw):
    """
    Gera nomes de participantes com caracteres especiais para testar normalização.
    """
    base_names = ["João Silva", "Ana Paula", "José Santos", "Maria José"]
    base_name = draw(st.sampled_from(base_names))
    
    # Adiciona caracteres problemáticos
    special_variations = [
        base_name,
        f"  {base_name}  ",  # espaços extras
        f"{base_name}.",     # ponto final
        f"{base_name} Jr.",  # sufixo com ponto
        base_name.replace(" ", "-"),  # hífen
        base_name.replace(" ", "_"),  # underscore
    ]
    
    return draw(st.sampled_from(special_variations))


@st.composite
def championship_setup_data(draw):
    """
    Gera dados para configurar um campeonato de teste.
    """
    championships = ["Brasileirao-2025", "Copa-Brasil-2025", "Paulistao-2025"]
    championship = draw(st.sampled_from(championships))
    season = "2025"
    
    return championship, season


class TestParticipantCreationProperties:
    """Testes de propriedade para criação de participantes."""
    
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
        
        import src.scripts.criar_participantes
        src.scripts.criar_participantes.CAMPEONATOS_DIR = src.config.CAMPEONATOS_DIR
    
    def teardown_method(self):
        """Limpa ambiente de teste."""
        # Restaura diretório original
        if self.original_campeonatos_dir:
            import src.config
            src.config.CAMPEONATOS_DIR = self.original_campeonatos_dir
            
            import src.scripts.criar_campeonato
            src.scripts.criar_campeonato.CAMPEONATOS_DIR = self.original_campeonatos_dir
            
            import src.scripts.criar_participantes
            src.scripts.criar_participantes.CAMPEONATOS_DIR = self.original_campeonatos_dir
        
        # Remove diretório temporário
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    @given(championship_setup_data(), valid_participant_names())
    @settings(max_examples=50)
    def test_property_6_participant_structure_creation(self, championship_data, participant_names):
        """
        Property 6: Participant structure creation
        
        For any list of participant names, the number of subdirectories created 
        in "Participantes" should equal the number of unique normalized names 
        in the input list.
        
        **Feature: bolao-prototype-scripts, Property 6: Participant structure creation**
        **Validates: Requirements 3.1, 3.2**
        """
        championship_name, season = championship_data
        
        # Primeiro cria o campeonato
        sucesso_campeonato = criar_campeonato(championship_name, season, forcar=True)
        assert sucesso_campeonato, f"Criação do campeonato '{championship_name}' deve ter sucesso"
        
        # Processa a lista para determinar quantos participantes únicos esperamos
        nomes_processados, duplicados = processar_lista_participantes(participant_names)
        nomes_unicos_esperados = len(nomes_processados)
        
        # Executa criação dos participantes
        sucesso = criar_participantes(championship_name, participant_names, forcar=True)
        assert sucesso, f"Criação dos participantes deve ter sucesso"
        
        # Importa configuração atualizada
        from src.config import CAMPEONATOS_DIR
        
        # Verifica diretório de participantes
        caminho_participantes = CAMPEONATOS_DIR / championship_name / "Participantes"
        assert caminho_participantes.exists(), "Diretório de participantes deve existir"
        
        # Conta subdiretórios criados (ignora arquivos como formulario_palpites.md)
        subdirs_encontrados = []
        for item in caminho_participantes.iterdir():
            if item.is_dir():
                subdirs_encontrados.append(item.name)
        
        # O número de subdiretórios deve ser igual ao número de nomes únicos processados
        assert len(subdirs_encontrados) == nomes_unicos_esperados, (
            f"Número de subdiretórios criados ({len(subdirs_encontrados)}) "
            f"deve ser igual ao número de nomes únicos ({nomes_unicos_esperados}). "
            f"Subdiretórios: {subdirs_encontrados}, "
            f"Nomes processados: {[nome_norm for _, nome_norm in nomes_processados]}"
        )
        
        # Verifica que cada nome normalizado tem seu diretório
        nomes_normalizados_esperados = {nome_norm for _, nome_norm in nomes_processados}
        subdirs_encontrados_set = set(subdirs_encontrados)
        
        assert subdirs_encontrados_set == nomes_normalizados_esperados, (
            f"Subdiretórios encontrados {subdirs_encontrados_set} "
            f"devem corresponder aos nomes normalizados {nomes_normalizados_esperados}"
        )
    
    @given(championship_setup_data(), valid_participant_names())
    @settings(max_examples=50)
    def test_property_7_participant_palpites_file_structure(self, championship_data, participant_names):
        """
        Property 7: Participant palpites file structure
        
        For any created participant, the "palpites.json" file should be valid JSON 
        containing the required fields "apostador", "codigo_apostador", "campeonato", 
        and an empty "palpites" array.
        
        **Feature: bolao-prototype-scripts, Property 7: Participant palpites file structure**
        **Validates: Requirements 3.3, 3.5**
        """
        championship_name, season = championship_data
        
        # Primeiro cria o campeonato
        sucesso_campeonato = criar_campeonato(championship_name, season, forcar=True)
        assert sucesso_campeonato, f"Criação do campeonato '{championship_name}' deve ter sucesso"
        
        # Executa criação dos participantes
        sucesso = criar_participantes(championship_name, participant_names, forcar=True)
        assert sucesso, f"Criação dos participantes deve ter sucesso"
        
        # Importa configuração atualizada
        from src.config import CAMPEONATOS_DIR
        
        # Processa lista para obter participantes únicos
        nomes_processados, _ = processar_lista_participantes(participant_names)
        
        # Verifica cada participante criado
        caminho_participantes = CAMPEONATOS_DIR / championship_name / "Participantes"
        
        for nome_original, nome_normalizado in nomes_processados:
            # Verifica se diretório do participante existe
            caminho_participante = caminho_participantes / nome_normalizado
            assert caminho_participante.exists(), f"Diretório do participante '{nome_normalizado}' deve existir"
            assert caminho_participante.is_dir(), f"'{nome_normalizado}' deve ser um diretório"
            
            # Verifica se arquivo palpites.json existe
            arquivo_palpites = caminho_participante / ARQUIVO_PALPITES
            assert arquivo_palpites.exists(), f"Arquivo {ARQUIVO_PALPITES} deve existir para '{nome_normalizado}'"
            
            # Carrega e valida JSON dos palpites
            with open(arquivo_palpites, 'r', encoding='utf-8') as f:
                dados_palpites = json.load(f)
            
            # Deve ser um dicionário válido
            assert isinstance(dados_palpites, dict), f"Dados dos palpites de '{nome_normalizado}' devem ser um dicionário"
            
            # Valida estrutura usando função de validação
            valido, erros = validar_estrutura_palpites(dados_palpites)
            assert valido, f"Estrutura dos palpites de '{nome_normalizado}' deve ser válida. Erros: {erros}"
            
            # Verifica campos obrigatórios específicos
            campos_obrigatorios = ["apostador", "codigo_apostador", "campeonato", "temporada", "palpites"]
            for campo in campos_obrigatorios:
                assert campo in dados_palpites, f"Campo '{campo}' deve estar presente nos palpites de '{nome_normalizado}'"
            
            # Verifica que os valores dos campos fazem sentido
            assert dados_palpites["apostador"] == nome_original, (
                f"Nome do apostador deve corresponder ao nome original: "
                f"esperado '{nome_original}', encontrado '{dados_palpites['apostador']}'"
            )
            
            assert dados_palpites["campeonato"] == championship_name, (
                f"Nome do campeonato deve corresponder: "
                f"esperado '{championship_name}', encontrado '{dados_palpites['campeonato']}'"
            )
            
            assert dados_palpites["temporada"] == season, (
                f"Temporada deve corresponder: "
                f"esperado '{season}', encontrado '{dados_palpites['temporada']}'"
            )
            
            # Verifica que código do apostador é uma string não vazia
            assert isinstance(dados_palpites["codigo_apostador"], str), (
                f"Código do apostador de '{nome_normalizado}' deve ser string"
            )
            assert len(dados_palpites["codigo_apostador"]) > 0, (
                f"Código do apostador de '{nome_normalizado}' não pode estar vazio"
            )
            
            # Verifica que palpites é uma lista vazia
            assert isinstance(dados_palpites["palpites"], list), (
                f"Palpites de '{nome_normalizado}' devem ser uma lista"
            )
            assert len(dados_palpites["palpites"]) == 0, (
                f"Lista de palpites de '{nome_normalizado}' deve estar vazia inicialmente"
            )


class TestParticipantCreationHelpers:
    """Testes de propriedade para funções auxiliares de criação de participantes."""
    
    @given(participant_names_with_special_chars())
    @settings(max_examples=50)
    def test_property_8_participant_name_normalization(self, participant_name):
        """
        Property 8: Participant name normalization
        
        For any participant name with spaces or special characters, the normalized 
        directory name should contain only alphanumeric characters and be consistent 
        across multiple invocations.
        
        **Feature: bolao-prototype-scripts, Property 8: Participant name normalization**
        **Validates: Requirements 3.4**
        """
        # Normaliza o nome múltiplas vezes
        normalized_1 = normalizar_nome_participante(participant_name)
        normalized_2 = normalizar_nome_participante(participant_name)
        normalized_3 = normalizar_nome_participante(participant_name)
        
        # Deve ser consistente entre invocações
        assert normalized_1 == normalized_2 == normalized_3, (
            f"Normalização deve ser consistente: {normalized_1} != {normalized_2} != {normalized_3}"
        )
        
        # Deve conter apenas caracteres alfanuméricos
        assert normalized_1.isalnum(), (
            f"Nome normalizado '{normalized_1}' deve conter apenas caracteres alfanuméricos"
        )
        
        # Não deve estar vazio (a menos que o input seja inválido)
        if participant_name and participant_name.strip():
            assert len(normalized_1) > 0, (
                f"Nome normalizado não deve estar vazio para input válido '{participant_name}'"
            )
    
    @given(st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=50), st.text(min_size=4, max_size=4))
    @settings(max_examples=50)
    def test_estrutura_basica_palpites_validity(self, nome_participante, nome_campeonato, temporada):
        """
        Testa que a estrutura básica dos palpites é sempre válida.
        """
        codigo = gerar_codigo_participante()
        estrutura = criar_estrutura_basica_palpites(nome_participante, codigo, nome_campeonato, temporada)
        
        # Deve ser um dicionário
        assert isinstance(estrutura, dict)
        
        # Deve passar na validação
        valido, erros = validar_estrutura_palpites(estrutura)
        assert valido, f"Estrutura básica deve ser válida. Erros: {erros}"
        
        # Campos devem corresponder aos parâmetros
        assert estrutura["apostador"] == nome_participante
        assert estrutura["codigo_apostador"] == codigo
        assert estrutura["campeonato"] == nome_campeonato
        assert estrutura["temporada"] == temporada
        assert estrutura["palpites"] == []
    
    @settings(max_examples=100)
    @given(st.integers(min_value=1, max_value=100))
    def test_gerar_codigo_participante_format(self, _):
        """
        Testa que o código de participante gerado sempre tem o formato correto.
        """
        codigo = gerar_codigo_participante()
        
        # Deve ser string de 4 caracteres
        assert isinstance(codigo, str)
        assert len(codigo) == 4
        
        # Deve conter apenas letras maiúsculas e dígitos
        assert codigo.isalnum()
        assert all(c.isupper() or c.isdigit() for c in codigo)
    
    @given(valid_participant_names())
    @settings(max_examples=50)
    def test_processar_lista_participantes_uniqueness(self, participant_names):
        """
        Testa que o processamento de lista de participantes remove duplicados corretamente.
        """
        nomes_processados, duplicados = processar_lista_participantes(participant_names)
        
        # Nomes normalizados devem ser únicos
        nomes_normalizados = [nome_norm for _, nome_norm in nomes_processados]
        assert len(nomes_normalizados) == len(set(nomes_normalizados)), (
            f"Nomes normalizados devem ser únicos: {nomes_normalizados}"
        )
        
        # Total de nomes processados + duplicados deve ser <= total de nomes originais
        # (pode ser menor se alguns nomes resultarem em strings vazias após normalização)
        total_processados = len(nomes_processados) + len(duplicados)
        assert total_processados <= len(participant_names), (
            f"Total processados ({total_processados}) não pode exceder total original ({len(participant_names)})"
        )
        
        # Cada nome processado deve ter nome original e normalizado não vazios
        for nome_original, nome_normalizado in nomes_processados:
            assert nome_original and nome_original.strip(), f"Nome original não deve estar vazio: '{nome_original}'"
            assert nome_normalizado and nome_normalizado.strip(), f"Nome normalizado não deve estar vazio: '{nome_normalizado}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])