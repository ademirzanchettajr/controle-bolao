"""
Módulo de parsing de texto para o Sistema de Controle de Bolão.

Este módulo fornece funções para extrair informações estruturadas de texto não estruturado,
especialmente mensagens de WhatsApp com palpites de apostadores.
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

# Import config and normalization with fallback for testing
try:
    from ..config import FORMATOS_PLACAR
    from .normalizacao import normalizar_nome_time, encontrar_time_similar
except ImportError:
    # Fallback for direct testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    try:
        from config import FORMATOS_PLACAR
        from normalizacao import normalizar_nome_time, encontrar_time_similar
    except ImportError:
        # Define constants locally if config is not available
        FORMATOS_PLACAR = [
            r'(.+?)\s+(\d+)\s*x\s*(\d+)\s+(.+)',      # "Time1 2x1 Time2"
            r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)',      # "Time1 2-1 Time2"
            r'(.+?)\s+(\d+)\s*:\s*(\d+)\s+(.+)',      # "Time1 2:1 Time2"
            r'(.+?)\s*\(\s*(\d+)\s*\)\s*x\s*\(\s*(\d+)\s*\)\s*(.+)'  # "Time1 (2) x (1) Time2"
        ]
        
        def normalizar_nome_time(nome):
            """Fallback normalization function"""
            if not nome:
                return ""
            return nome.lower().strip().replace('/', '-').replace(' ', '-')
        
        def encontrar_time_similar(nome, times_validos, limite_distancia=3):
            """Fallback similarity function"""
            return None


def extrair_apostador(texto: str) -> Optional[str]:
    """
    Identifica nome do apostador no texto.
    
    Procura por padrões como "Apostador:", "Nome:", ou nome no início do texto.
    
    Args:
        texto: Texto contendo palpites
        
    Returns:
        Nome do apostador encontrado ou None se não identificado
        
    Examples:
        >>> extrair_apostador("Apostador: Mario Silva\\n1ª Rodada\\nFlamengo 2x1 Palmeiras")
        'Mario Silva'
        >>> extrair_apostador("Mario Silva\\n1ª Rodada\\nFlamengo 2x1 Palmeiras")
        'Mario Silva'
        >>> extrair_apostador("Nome: João da Silva\\nRodada 1\\nSão Paulo 1x0 Corinthians")
        'João da Silva'
    """
    if not texto or not isinstance(texto, str):
        return None
    
    linhas = texto.strip().split('\n')
    if not linhas:
        return None
    
    primeira_linha = linhas[0].strip()
    
    # Padrão 1: "Apostador: Nome"
    match = re.search(r'apostador\s*:\s*(.+)', primeira_linha, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Padrão 2: "Nome: Nome"
    match = re.search(r'nome\s*:\s*(.+)', primeira_linha, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Padrão 3: Nome na primeira linha (sem indicadores de rodada)
    # Verifica se a primeira linha não contém indicadores de rodada ou jogos
    if not re.search(r'rodada|jogo|\d+\s*[x\-]\s*\d+', primeira_linha, re.IGNORECASE):
        # Verifica se parece com um nome (contém letras e possivelmente espaços)
        if re.match(r'^[a-záàâãéêíóôõúç\s]+$', primeira_linha, re.IGNORECASE):
            return primeira_linha
    
    # Padrão 4: Procurar em outras linhas por marcadores
    for linha in linhas[1:3]:  # Verifica até a terceira linha
        linha = linha.strip()
        match = re.search(r'(apostador|nome)\s*:\s*(.+)', linha, re.IGNORECASE)
        if match:
            return match.group(2).strip()
    
    return None


def extrair_rodada(texto: str) -> Optional[int]:
    """
    Extrai número da rodada do texto.
    
    Procura por padrões como "1ª Rodada", "Rodada 2", "R3", etc.
    
    Args:
        texto: Texto contendo indicação de rodada
        
    Returns:
        Número da rodada encontrado ou None se não identificado
        
    Examples:
        >>> extrair_rodada("1ª Rodada\\nFlamengo 2x1 Palmeiras")
        1
        >>> extrair_rodada("Rodada 5\\nSão Paulo 1x0 Corinthians")
        5
        >>> extrair_rodada("R10\\nBotafogo 2x2 Vasco")
        10
    """
    if not texto or not isinstance(texto, str):
        return None
    
    # Padrões para identificar rodadas
    padroes = [
        r'(\d+)[ªº]?\s*rodada',           # "1ª rodada", "2º rodada", "3 rodada"
        r'rodada\s*(\d+)',                # "rodada 1", "rodada 2"
        r'r\s*(\d+)',                     # "r1", "r 2", "R3"
        r'round\s*(\d+)',                 # "round 1" (inglês)
        r'(\d+)[ªº]?\s*jornada',          # "1ª jornada" (português europeu)
        r'jornada\s*(\d+)',               # "jornada 1"
    ]
    
    texto_lower = texto.lower()
    
    for padrao in padroes:
        matches = re.findall(padrao, texto_lower)
        if matches:
            try:
                # Pega o primeiro número encontrado
                numero = int(matches[0])
                if 1 <= numero <= 50:  # Validação básica de range
                    return numero
            except ValueError:
                continue
    
    return None


def extrair_palpites(texto: str) -> List[Dict[str, Any]]:
    """
    Extrai lista de palpites do texto com suporte a múltiplos formatos de placar.
    
    Reconhece formatos como "Time1 2x1 Time2", "Time1 2 x 1 Time2", "Time1 2-1 Time2", etc.
    
    Args:
        texto: Texto contendo palpites
        
    Returns:
        Lista de dicionários com palpites extraídos
        Cada dicionário contém: mandante, visitante, gols_mandante, gols_visitante
        
    Examples:
        >>> extrair_palpites("Flamengo 2x1 Palmeiras\\nSão Paulo 0 x 2 Corinthians")
        [{'mandante': 'Flamengo', 'visitante': 'Palmeiras', 'gols_mandante': 2, 'gols_visitante': 1},
         {'mandante': 'São Paulo', 'visitante': 'Corinthians', 'gols_mandante': 0, 'gols_visitante': 2}]
    """
    if not texto or not isinstance(texto, str):
        return []
    
    palpites = []
    linhas = texto.split('\n')
    
    # Padrões para diferentes formatos de placar
    padroes_placar = [
        r'(.+?)\s+(\d+)\s*x\s*(\d+)\s+(.+)',      # "Time1 2x1 Time2", "Time1 2 x 1 Time2"
        r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)',      # "Time1 2-1 Time2", "Time1 2 - 1 Time2"
        r'(.+?)\s+(\d+)\s*:\s*(\d+)\s+(.+)',      # "Time1 2:1 Time2", "Time1 2 : 1 Time2"
        r'(.+?)\s*\(\s*(\d+)\s*\)\s*x\s*\(\s*(\d+)\s*\)\s*(.+)',  # "Time1 (2) x (1) Time2"
    ]
    
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        
        # Pular linhas que parecem ser cabeçalhos ou metadados
        if re.search(r'(apostador|nome|rodada|jornada|aposta\s+extra)', linha, re.IGNORECASE):
            continue
        
        # Pular linhas que são apostas extras (formato "Jogo X: ...")
        if re.match(r'jogo\s*\d+\s*:', linha, re.IGNORECASE):
            continue
        
        # Tentar cada padrão de placar
        palpite_encontrado = False
        for padrao in padroes_placar:
            match = re.match(padrao, linha, re.IGNORECASE)
            if match:
                mandante = match.group(1).strip()
                gols_mandante = int(match.group(2))
                gols_visitante = int(match.group(3))
                visitante = match.group(4).strip()
                
                # Validações básicas
                if mandante and visitante and 0 <= gols_mandante <= 20 and 0 <= gols_visitante <= 20:
                    palpites.append({
                        'mandante': mandante,
                        'visitante': visitante,
                        'gols_mandante': gols_mandante,
                        'gols_visitante': gols_visitante
                    })
                    palpite_encontrado = True
                    break
        
        # Se não encontrou com padrões de placar, tentar padrão sem placar (para identificação de times)
        if not palpite_encontrado:
            # Padrão "Time1 x Time2" (sem gols especificados)
            match = re.match(r'(.+?)\s+x\s+(.+)', linha, re.IGNORECASE)
            if match:
                mandante = match.group(1).strip()
                visitante = match.group(2).strip()
                
                # Verifica se não são números (evita falsos positivos)
                if not re.match(r'^\d+$', mandante) and not re.match(r'^\d+$', visitante):
                    palpites.append({
                        'mandante': mandante,
                        'visitante': visitante,
                        'gols_mandante': None,  # Placar não especificado
                        'gols_visitante': None
                    })
    
    return palpites


def inferir_rodada(palpites: List[Dict[str, Any]], tabela: Dict[str, Any]) -> Optional[int]:
    """
    Infere rodada baseado em nomes de times mencionados nos palpites.
    
    Compara os times dos palpites com os jogos da tabela para identificar
    a rodada mais provável.
    
    Args:
        palpites: Lista de palpites extraídos
        tabela: Dicionário com dados da tabela do campeonato
        
    Returns:
        Número da rodada inferida ou None se não conseguir inferir
        
    Examples:
        >>> palpites = [{'mandante': 'Flamengo', 'visitante': 'Palmeiras', 'gols_mandante': 2, 'gols_visitante': 1}]
        >>> tabela = {'rodadas': [{'numero': 1, 'jogos': [{'mandante': 'Flamengo', 'visitante': 'Palmeiras'}]}]}
        >>> inferir_rodada(palpites, tabela)
        1
    """
    if not palpites or not tabela or 'rodadas' not in tabela:
        return None
    
    if not isinstance(tabela['rodadas'], list):
        return None
    
    # Extrair todos os times únicos dos palpites
    times_palpites = set()
    for palpite in palpites:
        if 'mandante' in palpite and palpite['mandante']:
            times_palpites.add(normalizar_nome_time(palpite['mandante']))
        if 'visitante' in palpite and palpite['visitante']:
            times_palpites.add(normalizar_nome_time(palpite['visitante']))
    
    if not times_palpites:
        return None
    
    # Calcular score de correspondência para cada rodada
    melhor_rodada = None
    melhor_score = 0
    
    for rodada in tabela['rodadas']:
        if 'numero' not in rodada or 'jogos' not in rodada:
            continue
        
        if not isinstance(rodada['jogos'], list):
            continue
        
        # Extrair times da rodada
        times_rodada = set()
        for jogo in rodada['jogos']:
            if isinstance(jogo, dict):
                if 'mandante' in jogo and jogo['mandante']:
                    times_rodada.add(normalizar_nome_time(jogo['mandante']))
                if 'visitante' in jogo and jogo['visitante']:
                    times_rodada.add(normalizar_nome_time(jogo['visitante']))
        
        if not times_rodada:
            continue
        
        # Calcular score de correspondência
        # Score = número de times dos palpites que aparecem na rodada
        correspondencias = len(times_palpites.intersection(times_rodada))
        
        # Normalizar pelo total de times nos palpites
        score = correspondencias / len(times_palpites) if times_palpites else 0
        
        # Se encontrou correspondência perfeita (todos os times dos palpites estão na rodada)
        if score == 1.0:
            return rodada['numero']
        
        # Atualizar melhor score
        if score > melhor_score:
            melhor_score = score
            melhor_rodada = rodada['numero']
    
    # Retornar rodada com melhor score se for significativo (pelo menos 50% de correspondência)
    if melhor_score >= 0.5:
        return melhor_rodada
    
    return None


def identificar_apostas_extras(texto: str) -> List[Dict[str, Any]]:
    """
    Detecta marcadores de apostas extras no texto.
    
    Procura por seções marcadas como "Aposta Extra:", "Jogo X:", etc.
    
    Args:
        texto: Texto contendo possíveis apostas extras
        
    Returns:
        Lista de dicionários com apostas extras identificadas
        Cada dicionário contém: tipo, identificador, palpite
        
    Examples:
        >>> identificar_apostas_extras("Aposta Extra:\\nJogo 5: Botafogo 2x2 Vasco")
        [{'tipo': 'extra', 'identificador': 'Jogo 5', 'mandante': 'Botafogo', 'visitante': 'Vasco', 'gols_mandante': 2, 'gols_visitante': 2}]
    """
    if not texto or not isinstance(texto, str):
        return []
    
    apostas_extras = []
    linhas = texto.split('\n')
    
    # Flags para controlar parsing
    em_secao_extra = False
    
    for i, linha in enumerate(linhas):
        linha = linha.strip()
        if not linha:
            continue
        
        # Detectar início de seção de apostas extras
        if re.search(r'aposta\s+extra|apostas\s+extras|extra\s*:', linha, re.IGNORECASE):
            em_secao_extra = True
            continue
        
        # Detectar fim de seção de apostas extras (nova seção ou rodada)
        if em_secao_extra and re.search(r'^\d+[ªº]?\s*rodada|^rodada\s*\d+', linha, re.IGNORECASE):
            em_secao_extra = False
            continue
        
        # Se estamos em seção extra, processar linha
        if em_secao_extra:
            # Padrão "Jogo X: Time1 YxZ Time2"
            match = re.match(r'(jogo\s*\d+)\s*:\s*(.+)', linha, re.IGNORECASE)
            if match:
                identificador = match.group(1).strip()
                palpite_texto = match.group(2).strip()
                
                # Extrair palpite da parte após os dois pontos usando padrões de placar
                padroes_placar = [
                    r'(.+?)\s+(\d+)\s*x\s*(\d+)\s+(.+)',      # "Time1 2x1 Time2"
                    r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)',      # "Time1 2-1 Time2"
                    r'(.+?)\s+(\d+)\s*:\s*(\d+)\s+(.+)',      # "Time1 2:1 Time2"
                    r'(.+?)\s*\(\s*(\d+)\s*\)\s*x\s*\(\s*(\d+)\s*\)\s*(.+)'  # "Time1 (2) x (1) Time2"
                ]
                
                for padrao in padroes_placar:
                    match_placar = re.match(padrao, palpite_texto, re.IGNORECASE)
                    if match_placar:
                        mandante = match_placar.group(1).strip()
                        gols_mandante = int(match_placar.group(2))
                        gols_visitante = int(match_placar.group(3))
                        visitante = match_placar.group(4).strip()
                        
                        if mandante and visitante and 0 <= gols_mandante <= 20 and 0 <= gols_visitante <= 20:
                            apostas_extras.append({
                                'mandante': mandante,
                                'visitante': visitante,
                                'gols_mandante': gols_mandante,
                                'gols_visitante': gols_visitante,
                                'tipo': 'extra',
                                'identificador': identificador
                            })
                            break
                continue
        
        # Detectar apostas extras por padrão de ID específico (mesmo fora de seção)
        match = re.match(r'(jogo\s*\d+)\s*:\s*(.+)', linha, re.IGNORECASE)
        if match:
            identificador = match.group(1).strip()
            palpite_texto = match.group(2).strip()
            
            # Extrair palpite usando padrões de placar
            padroes_placar = [
                r'(.+?)\s+(\d+)\s*x\s*(\d+)\s+(.+)',      # "Time1 2x1 Time2"
                r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)',      # "Time1 2-1 Time2"
                r'(.+?)\s+(\d+)\s*:\s*(\d+)\s+(.+)',      # "Time1 2:1 Time2"
                r'(.+?)\s*\(\s*(\d+)\s*\)\s*x\s*\(\s*(\d+)\s*\)\s*(.+)'  # "Time1 (2) x (1) Time2"
            ]
            
            for padrao in padroes_placar:
                match_placar = re.match(padrao, palpite_texto, re.IGNORECASE)
                if match_placar:
                    mandante = match_placar.group(1).strip()
                    gols_mandante = int(match_placar.group(2))
                    gols_visitante = int(match_placar.group(3))
                    visitante = match_placar.group(4).strip()
                    
                    if mandante and visitante and 0 <= gols_mandante <= 20 and 0 <= gols_visitante <= 20:
                        apostas_extras.append({
                            'mandante': mandante,
                            'visitante': visitante,
                            'gols_mandante': gols_mandante,
                            'gols_visitante': gols_visitante,
                            'tipo': 'extra',
                            'identificador': identificador
                        })
                        break
    
    return apostas_extras


def _limpar_nome_time(nome: str) -> str:
    """
    Função auxiliar para limpar nome de time removendo caracteres extras.
    
    Args:
        nome: Nome do time para limpar
        
    Returns:
        Nome limpo
    """
    if not nome:
        return ""
    
    # Remove caracteres extras comuns
    nome = re.sub(r'[()[\]{}]', '', nome)  # Remove parênteses e colchetes
    nome = re.sub(r'\s+', ' ', nome)       # Normaliza espaços
    nome = nome.strip()                    # Remove espaços das bordas
    
    return nome


def _validar_placar(gols_mandante: Any, gols_visitante: Any) -> bool:
    """
    Função auxiliar para validar se um placar é válido.
    
    Args:
        gols_mandante: Gols do time mandante
        gols_visitante: Gols do time visitante
        
    Returns:
        True se o placar é válido, False caso contrário
    """
    try:
        gols_m = int(gols_mandante) if gols_mandante is not None else None
        gols_v = int(gols_visitante) if gols_visitante is not None else None
        
        if gols_m is None or gols_v is None:
            return True  # Placar não especificado é válido
        
        return 0 <= gols_m <= 20 and 0 <= gols_v <= 20
    except (ValueError, TypeError):
        return False


def processar_texto_palpite(texto: str, tabela: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Função principal que processa texto completo de palpite.
    
    Extrai apostador, rodada, palpites regulares e apostas extras de uma só vez.
    
    Args:
        texto: Texto completo do palpite
        tabela: Tabela do campeonato para inferência de rodada (opcional)
        
    Returns:
        Dicionário com todas as informações extraídas:
        - apostador: nome do apostador
        - rodada: número da rodada (extraída ou inferida)
        - rodada_inferida: True se a rodada foi inferida
        - palpites: lista de palpites regulares
        - apostas_extras: lista de apostas extras
        - timestamp: timestamp do processamento
        
    Examples:
        >>> texto = "Mario Silva\\n1ª Rodada\\nFlamengo 2x1 Palmeiras\\nAposta Extra:\\nJogo 5: Botafogo 1x1 Vasco"
        >>> resultado = processar_texto_palpite(texto)
        >>> resultado['apostador']
        'Mario Silva'
        >>> len(resultado['palpites'])
        1
        >>> len(resultado['apostas_extras'])
        1
    """
    resultado = {
        'apostador': None,
        'rodada': None,
        'rodada_inferida': False,
        'palpites': [],
        'apostas_extras': [],
        'timestamp': datetime.now().isoformat(),
        'texto_original': texto
    }
    
    if not texto or not isinstance(texto, str):
        return resultado
    
    # Extrair apostador
    resultado['apostador'] = extrair_apostador(texto)
    
    # Extrair rodada explícita
    rodada_explicita = extrair_rodada(texto)
    if rodada_explicita:
        resultado['rodada'] = rodada_explicita
        resultado['rodada_inferida'] = False
    
    # Extrair palpites regulares
    resultado['palpites'] = extrair_palpites(texto)
    
    # Se não encontrou rodada explícita, tentar inferir
    if not resultado['rodada'] and tabela and resultado['palpites']:
        rodada_inferida = inferir_rodada(resultado['palpites'], tabela)
        if rodada_inferida:
            resultado['rodada'] = rodada_inferida
            resultado['rodada_inferida'] = True
    
    # Extrair apostas extras
    resultado['apostas_extras'] = identificar_apostas_extras(texto)
    
    return resultado


def dividir_texto_por_rodadas(texto: str) -> List[Dict[str, Any]]:
    """
    Divide texto com múltiplas rodadas em seções separadas.
    
    Procura por marcadores de rodada (ex: "🦇 RODADA 1 🦇", "RODADA 2", etc.)
    e divide o texto em seções, cada uma contendo os palpites de uma rodada.
    
    Args:
        texto: Texto completo com múltiplas rodadas
        
    Returns:
        Lista de dicionários, cada um contendo:
        - rodada: número da rodada
        - texto: texto da seção dessa rodada
        - apostador: nome do apostador (extraído do início)
        
    Examples:
        >>> texto = "Batman\\n🦇 RODADA 1 🦇\\nFlamengo 2x1 Palmeiras\\n🦇 RODADA 2 🦇\\nSantos 1x0 Corinthians"
        >>> secoes = dividir_texto_por_rodadas(texto)
        >>> len(secoes)
        2
        >>> secoes[0]['rodada']
        1
    """
    if not texto or not isinstance(texto, str):
        return []
    
    # Extrair apostador do início do texto
    apostador = extrair_apostador(texto)
    
    # Padrões para identificar início de rodada
    padroes_rodada = [
        r'🦇\s*RODADA\s+(\d+)\s*🦇',           # "🦇 RODADA 1 🦇"
        r'⚡\s*RODADA\s+(\d+)\s*⚡',           # "⚡ RODADA 1 ⚡"
        r'RODADA\s+(\d+)',                     # "RODADA 1"
        r'(\d+)[ªº]?\s*RODADA',                # "1ª RODADA"
        r'R\s*(\d+)',                          # "R1", "R 2"
    ]
    
    secoes = []
    linhas = texto.split('\n')
    secao_atual = None
    texto_secao = []
    
    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue
        
        # Verificar se é início de nova rodada
        rodada_encontrada = None
        for padrao in padroes_rodada:
            match = re.search(padrao, linha_limpa, re.IGNORECASE)
            if match:
                try:
                    rodada_encontrada = int(match.group(1))
                    if 1 <= rodada_encontrada <= 50:  # Validação básica
                        break
                except (ValueError, IndexError):
                    continue
        
        if rodada_encontrada:
            # Salvar seção anterior se existir
            if secao_atual is not None and texto_secao:
                secoes.append({
                    'rodada': secao_atual,
                    'texto': '\n'.join(texto_secao),
                    'apostador': apostador
                })
            
            # Iniciar nova seção
            secao_atual = rodada_encontrada
            texto_secao = []
        else:
            # Adicionar linha à seção atual
            if secao_atual is not None:
                # Pular linhas que são apenas decorativas
                if not re.match(r'^[🦇⚡🌃🚀]+.*[🦇⚡🌃🚀]+$', linha_limpa):
                    # Verificar se é linha de palpite válida
                    if any(char in linha_limpa for char in ['x', '-', ':']) and any(char.isdigit() for char in linha_limpa):
                        texto_secao.append(linha_limpa)
    
    # Salvar última seção
    if secao_atual is not None and texto_secao:
        secoes.append({
            'rodada': secao_atual,
            'texto': '\n'.join(texto_secao),
            'apostador': apostador
        })
    
    return secoes


def processar_texto_multiplas_rodadas(texto: str, tabela: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Processa texto com múltiplas rodadas, retornando lista de resultados.
    
    Esta função detecta automaticamente se o texto contém múltiplas rodadas
    e processa cada uma separadamente.
    
    Args:
        texto: Texto completo com uma ou múltiplas rodadas
        tabela: Tabela do campeonato para validação (opcional)
        
    Returns:
        Lista de dicionários, cada um com resultado de uma rodada:
        - apostador: nome do apostador
        - rodada: número da rodada
        - palpites: lista de palpites da rodada
        - timestamp: timestamp do processamento
        
    Examples:
        >>> texto = "Batman\\n🦇 RODADA 1 🦇\\nFlamengo 2x1 Palmeiras\\n🦇 RODADA 2 🦇\\nSantos 1x0 Corinthians"
        >>> resultados = processar_texto_multiplas_rodadas(texto)
        >>> len(resultados)
        2
        >>> resultados[0]['rodada']
        1
        >>> resultados[1]['rodada']
        2
    """
    if not texto or not isinstance(texto, str):
        return []
    
    # Tentar dividir por rodadas
    secoes = dividir_texto_por_rodadas(texto)
    
    if not secoes:
        # Se não conseguiu dividir, processar como rodada única
        resultado_unico = processar_texto_palpite(texto, tabela)
        if resultado_unico['apostador'] and (resultado_unico['palpites'] or resultado_unico['apostas_extras']):
            return [resultado_unico]
        else:
            return []
    
    # Processar cada seção separadamente
    resultados = []
    for secao in secoes:
        # Montar texto da seção com apostador
        texto_secao = f"{secao['apostador']}\nRodada {secao['rodada']}\n{secao['texto']}"
        
        # Processar seção
        resultado = processar_texto_palpite(texto_secao, tabela)
        
        # Garantir que a rodada está correta
        resultado['rodada'] = secao['rodada']
        resultado['rodada_inferida'] = False
        
        if resultado['palpites'] or resultado['apostas_extras']:
            resultados.append(resultado)
    
    return resultados