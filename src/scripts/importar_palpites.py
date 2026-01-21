#!/usr/bin/env python3
"""
Script de importação de palpites para o Sistema de Controle de Bolão.

Este script processa texto de palpites (ex: mensagens do WhatsApp) e atualiza
o arquivo palpites.json do participante correspondente.

Suporta importação de palpites de uma única rodada ou múltiplas rodadas de uma só vez.

Uso:
    python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpite.txt"
    python importar_palpites.py --campeonato "Brasileirao-2025" --texto "Mario Silva\n1ª Rodada\nFlamengo 2x1 Palmeiras"
    python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpites_multiplas_rodadas.txt"
    python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpites_multiplas_rodadas.txt" --rodada 5
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Adicionar o diretório pai ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from config import CAMPEONATOS_DIR, ARQUIVO_PALPITES, ARQUIVO_TABELA
from utils.parser import processar_texto_palpite, processar_texto_multiplas_rodadas
from utils.validacao import validar_id_jogo, validar_participante
from utils.normalizacao import normalizar_nome_time, encontrar_time_similar


def carregar_tabela_campeonato(caminho_campeonato: Path) -> Optional[Dict[str, Any]]:
    """
    Carrega arquivo tabela.json do campeonato.
    
    Args:
        caminho_campeonato: Caminho para o diretório do campeonato
        
    Returns:
        Dicionário com dados da tabela ou None se erro
    """
    arquivo_tabela = caminho_campeonato / "Tabela" / ARQUIVO_TABELA
    
    if not arquivo_tabela.exists():
        print(f"Erro: Arquivo tabela.json não encontrado em {arquivo_tabela}")
        return None
    
    try:
        with open(arquivo_tabela, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Erro: Arquivo tabela.json inválido: {e}")
        return None
    except Exception as e:
        print(f"Erro ao carregar tabela.json: {e}")
        return None


def carregar_palpites_participante(caminho_participante: Path) -> Optional[Dict[str, Any]]:
    """
    Carrega arquivo palpites.json do participante.
    
    Args:
        caminho_participante: Caminho para o diretório do participante
        
    Returns:
        Dicionário com palpites do participante ou None se erro
    """
    arquivo_palpites = caminho_participante / ARQUIVO_PALPITES
    
    if not arquivo_palpites.exists():
        print(f"Erro: Arquivo palpites.json não encontrado em {arquivo_palpites}")
        return None
    
    try:
        with open(arquivo_palpites, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Erro: Arquivo palpites.json inválido: {e}")
        return None
    except Exception as e:
        print(f"Erro ao carregar palpites.json: {e}")
        return None


def salvar_palpites_participante(caminho_participante: Path, dados: Dict[str, Any]) -> bool:
    """
    Salva arquivo palpites.json do participante.
    
    Args:
        caminho_participante: Caminho para o diretório do participante
        dados: Dados dos palpites para salvar
        
    Returns:
        True se salvou com sucesso, False caso contrário
    """
    arquivo_palpites = caminho_participante / ARQUIVO_PALPITES
    
    try:
        with open(arquivo_palpites, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar palpites.json: {e}")
        return False


def identificar_participante(nome_apostador: str, caminho_campeonato: Path) -> Optional[Path]:
    """
    Identifica o diretório do participante baseado no nome do apostador.
    
    Args:
        nome_apostador: Nome do apostador extraído do texto
        caminho_campeonato: Caminho para o diretório do campeonato
        
    Returns:
        Caminho para o diretório do participante ou None se não encontrado
    """
    if not nome_apostador:
        return None
    
    participantes_dir = caminho_campeonato / "Participantes"
    if not participantes_dir.exists():
        print(f"Erro: Diretório Participantes não encontrado em {participantes_dir}")
        return None
    
    # Primeiro, tentar correspondência exata com nome normalizado
    nome_normalizado = nome_apostador.lower().replace(' ', '').replace('-', '').replace('_', '').replace('.', '')
    
    for participante_dir in participantes_dir.iterdir():
        if participante_dir.is_dir():
            nome_dir_normalizado = participante_dir.name.lower().replace(' ', '').replace('-', '').replace('_', '').replace('.', '')
            if nome_normalizado == nome_dir_normalizado:
                return participante_dir
    
    # Se não encontrou correspondência exata, tentar busca por similaridade
    participantes_disponiveis = [d.name for d in participantes_dir.iterdir() if d.is_dir()]
    
    # Buscar por correspondência parcial (nome contido no diretório ou vice-versa)
    for nome_dir in participantes_disponiveis:
        nome_dir_normalizado = nome_dir.lower().replace(' ', '').replace('-', '').replace('_', '').replace('.', '')
        
        # Verificar se o nome do apostador está contido no nome do diretório
        if nome_normalizado in nome_dir_normalizado or nome_dir_normalizado in nome_normalizado:
            return participantes_dir / nome_dir
    
    # Buscar por palavras em comum (para casos como "João da Silva Jr" vs "JoaodaSilvaJr")
    palavras_apostador = set(nome_apostador.lower().replace('-', ' ').replace('_', ' ').split())
    palavras_apostador = {normalizar_nome_time(p) for p in palavras_apostador if len(p) > 2}  # Normalizar e ignorar palavras pequenas
    
    melhor_match = None
    melhor_score = 0
    
    for nome_dir in participantes_disponiveis:
        nome_dir_normalizado = normalizar_nome_time(nome_dir.lower())
        
        # Verificar se todas as palavras principais do apostador estão contidas no nome do diretório
        palavras_encontradas = 0
        for palavra in palavras_apostador:
            if palavra in nome_dir_normalizado:
                palavras_encontradas += 1
        
        # Calcular score baseado na proporção de palavras encontradas
        if palavras_apostador:
            score = palavras_encontradas / len(palavras_apostador)
            
            if score > melhor_score and score >= 0.7:  # Pelo menos 70% das palavras encontradas
                melhor_score = score
                melhor_match = nome_dir
    
    if melhor_match:
        return participantes_dir / melhor_match
    
    # Se ainda não encontrou, mostrar opções disponíveis
    print(f"Participante '{nome_apostador}' não encontrado.")
    print("Participantes disponíveis:")
    for nome_dir in sorted(participantes_disponiveis):
        print(f"  - {nome_dir}")
    
    return None


def normalizar_palpites_times(palpites: List[Dict[str, Any]], tabela: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza nomes de times nos palpites para corresponder aos nomes na tabela.
    
    Args:
        palpites: Lista de palpites com nomes de times
        tabela: Dados da tabela do campeonato
        
    Returns:
        Lista de palpites com nomes de times normalizados
    """
    if not palpites or not tabela or 'rodadas' not in tabela:
        return palpites
    
    # Extrair todos os nomes de times da tabela
    times_tabela = set()
    for rodada in tabela.get('rodadas', []):
        for jogo in rodada.get('jogos', []):
            if 'mandante' in jogo and jogo['mandante']:
                times_tabela.add(jogo['mandante'])
            if 'visitante' in jogo and jogo['visitante']:
                times_tabela.add(jogo['visitante'])
    
    times_tabela_list = list(times_tabela)
    palpites_normalizados = []
    
    for palpite in palpites:
        palpite_normalizado = palpite.copy()
        
        # Normalizar nome do mandante
        if 'mandante' in palpite and palpite['mandante']:
            time_similar = encontrar_time_similar(palpite['mandante'], times_tabela_list)
            if time_similar:
                palpite_normalizado['mandante'] = time_similar
            else:
                print(f"Aviso: Time '{palpite['mandante']}' não encontrado na tabela")
        
        # Normalizar nome do visitante
        if 'visitante' in palpite and palpite['visitante']:
            time_similar = encontrar_time_similar(palpite['visitante'], times_tabela_list)
            if time_similar:
                palpite_normalizado['visitante'] = time_similar
            else:
                print(f"Aviso: Time '{palpite['visitante']}' não encontrado na tabela")
        
        palpites_normalizados.append(palpite_normalizado)
    
    return palpites_normalizados


def validar_palpites_contra_tabela(palpites: List[Dict[str, Any]], rodada: int, tabela: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Valida palpites contra a tabela do campeonato e gera IDs de jogos.
    
    Args:
        palpites: Lista de palpites para validar
        rodada: Número da rodada
        tabela: Dados da tabela do campeonato
        
    Returns:
        Tupla (palpites_validados, lista_de_erros)
    """
    erros = []
    palpites_validados = []
    
    if not tabela or 'rodadas' not in tabela:
        erros.append("Tabela do campeonato inválida")
        return palpites_validados, erros
    
    # Encontrar a rodada na tabela
    rodada_encontrada = None
    for r in tabela['rodadas']:
        if r.get('numero') == rodada:
            rodada_encontrada = r
            break
    
    if not rodada_encontrada:
        erros.append(f"Rodada {rodada} não encontrada na tabela")
        return palpites_validados, erros
    
    jogos_rodada = rodada_encontrada.get('jogos', [])
    
    for palpite in palpites:
        # Pular palpites sem placar especificado
        if palpite.get('gols_mandante') is None or palpite.get('gols_visitante') is None:
            erros.append(f"Palpite sem placar especificado: {palpite.get('mandante', '?')} x {palpite.get('visitante', '?')}")
            continue
        
        # Procurar jogo correspondente na rodada
        jogo_encontrado = None
        for jogo in jogos_rodada:
            if (jogo.get('mandante') == palpite.get('mandante') and 
                jogo.get('visitante') == palpite.get('visitante')):
                jogo_encontrado = jogo
                break
        
        if not jogo_encontrado:
            erros.append(f"Jogo não encontrado na rodada {rodada}: {palpite.get('mandante', '?')} x {palpite.get('visitante', '?')}")
            continue
        
        # Criar palpite validado com ID do jogo
        palpite_validado = {
            'id': jogo_encontrado['id'],
            'mandante': jogo_encontrado['mandante'],
            'visitante': jogo_encontrado['visitante'],
            'palpite_mandante': palpite['gols_mandante'],
            'palpite_visitante': palpite['gols_visitante']
        }
        
        # Adicionar informações extras se for aposta extra
        if 'tipo' in palpite:
            palpite_validado['tipo'] = palpite['tipo']
        if 'identificador' in palpite:
            palpite_validado['identificador'] = palpite['identificador']
        
        palpites_validados.append(palpite_validado)
    
    return palpites_validados, erros


def atualizar_palpites_participante(dados_participante: Dict[str, Any], rodada: int, 
                                   palpites_validados: List[Dict[str, Any]], 
                                   apostas_extras: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Atualiza dados do participante com novos palpites.
    
    Args:
        dados_participante: Dados atuais do participante
        rodada: Número da rodada
        palpites_validados: Lista de palpites validados
        apostas_extras: Lista de apostas extras
        
    Returns:
        Dados atualizados do participante
    """
    if 'palpites' not in dados_participante:
        dados_participante['palpites'] = []
    
    # Procurar se já existe entrada para esta rodada
    entrada_rodada = None
    for entrada in dados_participante['palpites']:
        if entrada.get('rodada') == rodada:
            entrada_rodada = entrada
            break
    
    # Se não existe, criar nova entrada
    if not entrada_rodada:
        entrada_rodada = {
            'rodada': rodada,
            'data_palpite': datetime.now().isoformat(),
            'jogos': []
        }
        dados_participante['palpites'].append(entrada_rodada)
    else:
        # Atualizar timestamp
        entrada_rodada['data_palpite'] = datetime.now().isoformat()
    
    # Adicionar palpites regulares
    if 'jogos' not in entrada_rodada:
        entrada_rodada['jogos'] = []
    
    # Remover palpites existentes para os mesmos jogos (evitar duplicatas)
    ids_novos_palpites = {p['id'] for p in palpites_validados}
    entrada_rodada['jogos'] = [j for j in entrada_rodada['jogos'] if j.get('id') not in ids_novos_palpites]
    
    # Adicionar novos palpites
    entrada_rodada['jogos'].extend(palpites_validados)
    
    # Adicionar apostas extras se houver
    if apostas_extras:
        if 'apostas_extras' not in entrada_rodada:
            entrada_rodada['apostas_extras'] = []
        
        # Remover apostas extras existentes com mesmo identificador
        identificadores_novos = {ae.get('identificador') for ae in apostas_extras if 'identificador' in ae}
        entrada_rodada['apostas_extras'] = [
            ae for ae in entrada_rodada['apostas_extras'] 
            if ae.get('identificador') not in identificadores_novos
        ]
        
        # Adicionar novas apostas extras
        entrada_rodada['apostas_extras'].extend(apostas_extras)
    
    return dados_participante


def confirmar_sobrescrita(participante: str, rodada: int, palpites_existentes: List[Dict[str, Any]], forcar: bool = False) -> bool:
    """
    Solicita confirmação do usuário para sobrescrever palpites existentes.
    
    Args:
        participante: Nome do participante
        rodada: Número da rodada
        palpites_existentes: Lista de palpites já existentes
        forcar: Se True, não solicita confirmação
        
    Returns:
        True se usuário confirmar ou se forçado, False caso contrário
    """
    if forcar:
        return True
        
    print(f"\nO participante '{participante}' já possui palpites para a rodada {rodada}:")
    
    for palpite in palpites_existentes:
        mandante = palpite.get('mandante', '?')
        visitante = palpite.get('visitante', '?')
        gols_m = palpite.get('palpite_mandante', '?')
        gols_v = palpite.get('palpite_visitante', '?')
        print(f"  {mandante} {gols_m}x{gols_v} {visitante}")
    
    resposta = input("\nDeseja sobrescrever os palpites existentes? (s/n): ").strip().lower()
    return resposta in ['s', 'sim', 'y', 'yes']


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Importa palpites de participantes para o campeonato",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  # Importar palpites de uma rodada
  python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpite.txt"
  
  # Importar palpites de múltiplas rodadas
  python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpites_completos.txt"
  
  # Importar apenas uma rodada específica de um arquivo com múltiplas rodadas
  python importar_palpites.py --campeonato "Brasileirao-2025" --arquivo "palpites_completos.txt" --rodada 5
  
  # Usar texto direto
  python importar_palpites.py --campeonato "Brasileirao-2025" --texto "Mario Silva\\n1ª Rodada\\nFlamengo 2x1 Palmeiras"
        """
    )
    
    parser.add_argument(
        '--campeonato',
        required=True,
        help='Nome do campeonato'
    )
    
    parser.add_argument(
        '--arquivo',
        help='Arquivo texto com palpite'
    )
    
    parser.add_argument(
        '--texto',
        help='Texto direto do palpite'
    )
    
    parser.add_argument(
        '--rodada',
        type=int,
        help='Forçar número da rodada específica (opcional). Para arquivos com múltiplas rodadas, processa apenas a rodada especificada.'
    )
    
    parser.add_argument(
        '--forcar',
        action='store_true',
        help='Força importação sem confirmação'
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.arquivo and not args.texto:
        print("Erro: É necessário fornecer --arquivo ou --texto")
        return 1
    
    if args.arquivo and args.texto:
        print("Erro: Forneça apenas --arquivo OU --texto, não ambos")
        return 1
    
    # Verificar se campeonato existe
    caminho_campeonato = CAMPEONATOS_DIR / args.campeonato
    if not caminho_campeonato.exists():
        print(f"Erro: Campeonato '{args.campeonato}' não encontrado em {CAMPEONATOS_DIR}")
        return 1
    
    # Carregar tabela do campeonato
    tabela = carregar_tabela_campeonato(caminho_campeonato)
    if not tabela:
        return 1
    
    # Obter texto do palpite
    if args.arquivo:
        arquivo_palpite = Path(args.arquivo)
        if not arquivo_palpite.exists():
            print(f"Erro: Arquivo '{args.arquivo}' não encontrado")
            return 1
        
        try:
            with open(arquivo_palpite, 'r', encoding='utf-8') as f:
                texto_palpite = f.read()
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return 1
    else:
        texto_palpite = args.texto
    
    # Processar texto do palpite - detectar se há múltiplas rodadas
    print("Processando texto do palpite...")
    
    # Primeiro, tentar processar como múltiplas rodadas
    resultados_multiplas_rodadas = processar_texto_multiplas_rodadas(texto_palpite, tabela)
    
    # Se encontrou múltiplas rodadas, processar cada uma
    if len(resultados_multiplas_rodadas) > 1:
        print(f"Detectadas {len(resultados_multiplas_rodadas)} rodadas no texto")
        
        # Verificar se foi especificada uma rodada específica
        if args.rodada:
            # Filtrar apenas a rodada especificada
            resultados_filtrados = [r for r in resultados_multiplas_rodadas if r['rodada'] == args.rodada]
            if not resultados_filtrados:
                print(f"Erro: Rodada {args.rodada} não encontrada no texto")
                print(f"Rodadas disponíveis: {[r['rodada'] for r in resultados_multiplas_rodadas]}")
                return 1
            resultados_multiplas_rodadas = resultados_filtrados
            print(f"Processando apenas a rodada {args.rodada} conforme especificado")
        
        # Processar cada rodada
        apostador_principal = None
        caminho_participante = None
        total_palpites_processados = 0
        
        for i, resultado_parsing in enumerate(resultados_multiplas_rodadas):
            rodada = resultado_parsing['rodada']
            print(f"\n--- Processando Rodada {rodada} ({i+1}/{len(resultados_multiplas_rodadas)}) ---")
            
            # Verificar apostador (deve ser o mesmo para todas as rodadas)
            if not apostador_principal:
                if not resultado_parsing['apostador']:
                    print("Erro: Não foi possível identificar o apostador no texto")
                    print("Certifique-se de que o nome está na primeira linha ou marcado com 'Apostador:'")
                    return 1
                
                apostador_principal = resultado_parsing['apostador']
                print(f"Apostador identificado: {apostador_principal}")
                
                # Identificar participante
                caminho_participante = identificar_participante(apostador_principal, caminho_campeonato)
                if not caminho_participante:
                    return 1
                
                print(f"Participante encontrado: {caminho_participante.name}")
            
            # Verificar se há palpites para processar nesta rodada
            if not resultado_parsing['palpites']:
                print(f"Aviso: Nenhum palpite encontrado para a rodada {rodada}")
                if not resultado_parsing['apostas_extras']:
                    print("Nenhuma aposta extra encontrada também")
                    continue
            
            # Normalizar nomes de times nos palpites
            palpites_normalizados = normalizar_palpites_times(resultado_parsing['palpites'], tabela)
            apostas_extras_normalizadas = normalizar_palpites_times(resultado_parsing['apostas_extras'], tabela)
            
            # Validar palpites contra tabela
            palpites_validados, erros_palpites = validar_palpites_contra_tabela(palpites_normalizados, rodada, tabela)
            apostas_extras_validadas, erros_extras = validar_palpites_contra_tabela(apostas_extras_normalizadas, rodada, tabela)
            
            # Mostrar erros se houver
            todos_erros = erros_palpites + erros_extras
            if todos_erros:
                print(f"Erros encontrados na rodada {rodada}:")
                for erro in todos_erros:
                    print(f"  - {erro}")
            
            # Verificar se há palpites válidos para processar
            if not palpites_validados and not apostas_extras_validadas:
                print(f"Aviso: Nenhum palpite válido encontrado para a rodada {rodada}")
                continue
            
            print(f"Palpites válidos encontrados na rodada {rodada}: {len(palpites_validados)}")
            if apostas_extras_validadas:
                print(f"Apostas extras válidas encontradas na rodada {rodada}: {len(apostas_extras_validadas)}")
            
            # Carregar dados atuais do participante (apenas na primeira vez)
            if i == 0:
                dados_participante = carregar_palpites_participante(caminho_participante)
                if not dados_participante:
                    return 1
            
            # Verificar se já existem palpites para esta rodada
            palpites_existentes = []
            for entrada in dados_participante.get('palpites', []):
                if entrada.get('rodada') == rodada:
                    palpites_existentes = entrada.get('jogos', [])
                    break
            
            if palpites_existentes:
                if not confirmar_sobrescrita(apostador_principal, rodada, palpites_existentes, args.forcar):
                    print(f"Rodada {rodada} pulada pelo usuário")
                    continue
            
            # Atualizar dados do participante
            dados_participante = atualizar_palpites_participante(
                dados_participante, rodada, palpites_validados, apostas_extras_validadas
            )
            
            total_palpites_processados += len(palpites_validados)
            
            # Mostrar resumo da rodada
            print(f"Resumo da rodada {rodada}:")
            for palpite in palpites_validados:
                mandante = palpite['mandante']
                visitante = palpite['visitante']
                gols_m = palpite['palpite_mandante']
                gols_v = palpite['palpite_visitante']
                print(f"  {mandante} {gols_m}x{gols_v} {visitante}")
            
            if apostas_extras_validadas:
                print(f"Apostas extras da rodada {rodada}:")
                for aposta in apostas_extras_validadas:
                    identificador = aposta.get('identificador', 'Extra')
                    mandante = aposta['mandante']
                    visitante = aposta['visitante']
                    gols_m = aposta['palpite_mandante']
                    gols_v = aposta['palpite_visitante']
                    print(f"  {identificador}: {mandante} {gols_m}x{gols_v} {visitante}")
        
        # Salvar arquivo atualizado (uma vez no final)
        if total_palpites_processados > 0:
            if salvar_palpites_participante(caminho_participante, dados_participante):
                rodadas_processadas = [r['rodada'] for r in resultados_multiplas_rodadas if r['palpites']]
                print(f"\n✅ Palpites salvos com sucesso para {apostador_principal}")
                print(f"Rodadas processadas: {rodadas_processadas}")
                print(f"Total de palpites processados: {total_palpites_processados}")
                return 0
            else:
                print("Erro ao salvar palpites")
                return 1
        else:
            print("Nenhum palpite foi processado")
            return 1
    
    # Se não encontrou múltiplas rodadas, processar como rodada única (comportamento original)
    elif len(resultados_multiplas_rodadas) == 1:
        resultado_parsing = resultados_multiplas_rodadas[0]
    else:
        # Fallback para o método original se não conseguiu processar
        resultado_parsing = processar_texto_palpite(texto_palpite, tabela)
    
    # Verificar se conseguiu extrair apostador
    if not resultado_parsing['apostador']:
        print("Erro: Não foi possível identificar o apostador no texto")
        print("Certifique-se de que o nome está na primeira linha ou marcado com 'Apostador:'")
        return 1
    
    print(f"Apostador identificado: {resultado_parsing['apostador']}")
    
    # Identificar participante
    caminho_participante = identificar_participante(resultado_parsing['apostador'], caminho_campeonato)
    if not caminho_participante:
        return 1
    
    print(f"Participante encontrado: {caminho_participante.name}")
    
    # Determinar rodada
    rodada = args.rodada if args.rodada else resultado_parsing['rodada']
    
    if not rodada:
        print("Erro: Não foi possível determinar a rodada")
        print("Use --rodada para especificar manualmente ou inclua indicação de rodada no texto")
        return 1
    
    if resultado_parsing['rodada_inferida'] and not args.rodada:
        print(f"Rodada inferida automaticamente: {rodada}")
        if not args.forcar:
            resposta = input("Confirma esta rodada? (s/n): ").strip().lower()
            if resposta not in ['s', 'sim', 'y', 'yes']:
                print("Operação cancelada")
                return 1
    
    print(f"Processando rodada: {rodada}")
    
    # Verificar se há palpites para processar
    if not resultado_parsing['palpites']:
        print("Aviso: Nenhum palpite encontrado no texto")
        if not resultado_parsing['apostas_extras']:
            print("Nenhuma aposta extra encontrada também")
            return 1
    
    # Normalizar nomes de times nos palpites
    palpites_normalizados = normalizar_palpites_times(resultado_parsing['palpites'], tabela)
    apostas_extras_normalizadas = normalizar_palpites_times(resultado_parsing['apostas_extras'], tabela)
    
    # Validar palpites contra tabela
    palpites_validados, erros_palpites = validar_palpites_contra_tabela(palpites_normalizados, rodada, tabela)
    apostas_extras_validadas, erros_extras = validar_palpites_contra_tabela(apostas_extras_normalizadas, rodada, tabela)
    
    # Mostrar erros se houver
    todos_erros = erros_palpites + erros_extras
    if todos_erros:
        print("\nErros encontrados:")
        for erro in todos_erros:
            print(f"  - {erro}")
    
    # Verificar se há palpites válidos para processar
    if not palpites_validados and not apostas_extras_validadas:
        print("Erro: Nenhum palpite válido encontrado")
        return 1
    
    print(f"\nPalpites válidos encontrados: {len(palpites_validados)}")
    if apostas_extras_validadas:
        print(f"Apostas extras válidas encontradas: {len(apostas_extras_validadas)}")
    
    # Carregar dados atuais do participante
    dados_participante = carregar_palpites_participante(caminho_participante)
    if not dados_participante:
        return 1
    
    # Verificar se já existem palpites para esta rodada
    palpites_existentes = []
    for entrada in dados_participante.get('palpites', []):
        if entrada.get('rodada') == rodada:
            palpites_existentes = entrada.get('jogos', [])
            break
    
    if palpites_existentes:
        if not confirmar_sobrescrita(resultado_parsing['apostador'], rodada, palpites_existentes, args.forcar):
            print("Operação cancelada")
            return 1
    
    # Atualizar dados do participante
    dados_atualizados = atualizar_palpites_participante(
        dados_participante, rodada, palpites_validados, apostas_extras_validadas
    )
    
    # Salvar arquivo atualizado
    if salvar_palpites_participante(caminho_participante, dados_atualizados):
        print(f"\nPalpites salvos com sucesso para {resultado_parsing['apostador']} na rodada {rodada}")
        
        # Mostrar resumo
        print("\nResumo dos palpites processados:")
        for palpite in palpites_validados:
            mandante = palpite['mandante']
            visitante = palpite['visitante']
            gols_m = palpite['palpite_mandante']
            gols_v = palpite['palpite_visitante']
            print(f"  {mandante} {gols_m}x{gols_v} {visitante}")
        
        if apostas_extras_validadas:
            print("\nApostas extras:")
            for aposta in apostas_extras_validadas:
                identificador = aposta.get('identificador', 'Extra')
                mandante = aposta['mandante']
                visitante = aposta['visitante']
                gols_m = aposta['palpite_mandante']
                gols_v = aposta['palpite_visitante']
                print(f"  {identificador}: {mandante} {gols_m}x{gols_v} {visitante}")
        
        return 0
    else:
        print("Erro ao salvar palpites")
        return 1


if __name__ == "__main__":
    sys.exit(main())