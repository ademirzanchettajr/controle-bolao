# Implementation Plan

- [x] 1. Configurar estrutura do projeto e dependências
  - Criar estrutura de diretórios (src/scripts, src/utils, tests)
  - Criar requirements.txt com dependências (hypothesis, pytest, openpyxl, python-dateutil, python-Levenshtein)
  - Criar arquivo de configuração básico
  - _Requirements: Todos_

- [x] 2. Implementar módulo de normalização de nomes
  - Criar função `normalizar_nome_time()` que remove acentos, converte barras/hífens, normaliza case e whitespace
  - Criar função `normalizar_nome_participante()` para nomes de diretórios
  - Criar função `normalizar_nome_campeonato()` para nomes de campeonatos
  - Criar função `encontrar_time_similar()` usando distância de Levenshtein
  - _Requirements: 1.5, 3.4, 4.5, 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2.1 Escrever testes de propriedade para normalização
  - **Property 3: Championship name normalization consistency**
  - **Property 8: Participant name normalization**
  - **Property 12: Team name normalization equivalence**
  - **Validates: Requirements 1.5, 3.4, 4.5, 9.1-9.4**

- [x] 3. Implementar módulo de validação de dados
  - Criar função `validar_estrutura_tabela()` que verifica campos obrigatórios
  - Criar função `validar_estrutura_palpites()` que verifica campos obrigatórios
  - Criar função `validar_estrutura_regras()` que verifica campos obrigatórios
  - Criar função `validar_placar()` que verifica inteiros não-negativos
  - Criar função `validar_data()` que verifica formato de data válido
  - Criar função `validar_id_jogo()` que verifica existência de ID na tabela
  - Criar função `validar_participante()` que verifica registro no campeonato
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [x] 3.1 Escrever testes de propriedade para validação
  - **Property 40: Required fields validation**
  - **Property 41: Date format validation**
  - **Property 42: Score validation**
  - **Property 43: Game ID reference validation**
  - **Property 44: Participant registration validation**
  - **Property 45: Error message clarity**
  - **Validates: Requirements 10.1-10.6**

- [x] 4. Implementar módulo de parsing de texto
  - Criar função `extrair_apostador()` que identifica nome do apostador
  - Criar função `extrair_rodada()` que extrai número da rodada
  - Criar função `extrair_palpites()` que extrai lista de palpites com suporte a múltiplos formatos de placar
  - Criar função `inferir_rodada()` que infere rodada baseado em nomes de times
  - Criar função `identificar_apostas_extras()` que detecta marcadores de apostas extras
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.9_

- [x] 4.1 Escrever testes de propriedade para parsing
  - **Property 14: Participant identification from text**
  - **Property 15: Round extraction from text**
  - **Property 16: Round inference from team names**
  - **Property 17: Score format recognition**
  - **Property 19: Extra bet identification**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.5, 5.9**

- [x] 5. Implementar motor de pontuação
  - Criar função `verificar_resultado_exato()` que verifica placar idêntico
  - Criar função `verificar_vitoria_gols_um_time()` que verifica vencedor + gols de uma equipe
  - Criar função `verificar_vitoria_diferenca_gols()` que verifica vencedor + diferença
  - Criar função `verificar_vitoria_soma_gols()` que verifica vencedor + soma total
  - Criar função `verificar_apenas_vitoria()` que verifica apenas vencedor
  - Criar função `verificar_apenas_empate()` que verifica apenas empate
  - Criar função `verificar_gols_um_time()` que verifica gols de um time sem resultado
  - Criar função `verificar_soma_gols()` que verifica apenas soma total
  - Criar função `verificar_resultado_inverso()` que verifica placar invertido
  - Criar função `calcular_pontuacao()` que aplica hierarquia de regras e retorna (pontos, código)
  - Criar função `calcular_bonus_resultado_exato()` que calcula 1/N para acertos exatos
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11, 8.12_

- [x] 5.1 Escrever testes de propriedade para pontuação - Resultado exato e bônus
  - **Property 29: Exact score bonus calculation**
  - **Validates: Requirements 8.1, 8.2**

- [x] 5.2 Escrever testes de propriedade para pontuação - Hierarquia de regras
  - **Property 30: Scoring rule hierarchy**
  - **Validates: Requirements 8.12**

- [x] 5.3 Escrever testes de propriedade para pontuação - Regras individuais
  - **Property 31: Winner and one team goals scoring**
  - **Property 32: Winner and goal difference scoring**
  - **Property 33: Winner and total goals scoring**
  - **Property 34: Winner only scoring**
  - **Property 35: Draw only scoring**
  - **Property 36: One team goals scoring**
  - **Property 37: Total goals only scoring**
  - **Property 38: Inverted score penalty**
  - **Property 39: Missing prediction penalty**
  - **Validates: Requirements 8.3-8.11**

- [x] 6. Implementar gerador de relatórios
  - Criar função `gerar_tabela_classificacao()` que formata tabela de classificação
  - Criar função `calcular_variacao_posicao()` que calcula variação entre rodadas
  - Criar função `formatar_linha_participante()` que formata linha individual
  - Criar função `gerar_cabecalho_relatorio()` que cria cabeçalho do relatório
  - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6, 7.4, 7.5_

- [x] 6.1 Escrever testes unitários para gerador de relatórios
  - Testar formatação de tabela com dados de exemplo
  - Testar cálculo de variação de posição
  - Testar ordenação de classificação
  - _Requirements: 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 7. Implementar script de criação de campeonato
  - Criar CLI com argumentos --nome, --temporada, --codigo
  - Implementar função que cria diretório do campeonato
  - Implementar função que cria subdiretórios (Regras, Tabela, Resultados, Participantes)
  - Implementar função que cria arquivos JSON vazios com estrutura básica
  - Adicionar validação de nome duplicado
  - Adicionar normalização de nome do campeonato
  - Adicionar mensagens de confirmação e erro
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 7.1 Escrever testes de propriedade para criação de campeonato
  - **Property 1: Championship directory structure completeness**
  - **Property 2: Initial JSON files validity**
  - **Validates: Requirements 1.1, 1.2, 1.3**

- [x] 8. Implementar script de geração de regras
  - Criar CLI com argumentos --campeonato, --sobrescrever
  - Implementar função que carrega template de regras padrão
  - Implementar função que popula campos campeonato e temporada
  - Implementar função que escreve arquivo regras.json
  - Adicionar prompt de confirmação para sobrescrever
  - Adicionar validação de estrutura gerada
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 8.1 Escrever testes de propriedade para geração de regras
  - **Property 4: Rules file completeness**
  - **Property 5: Rules file metadata inclusion**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.5**

- [x] 9. Implementar script de criação de participantes
  - Criar CLI com argumentos --campeonato, --arquivo, --excel, --coluna
  - Implementar função que lê lista de nomes de arquivo texto
  - Implementar função que lê lista de nomes de planilha Excel
  - Implementar função que cria diretório para cada participante
  - Implementar função que cria arquivo palpites.json vazio
  - Implementar função que gera código único de participante
  - Adicionar normalização de nomes para diretórios
  - Adicionar validação de participantes duplicados
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 9.1 Escrever testes de propriedade para criação de participantes
  - **Property 6: Participant structure creation**
  - **Property 7: Participant palpites file structure**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.5**

- [x] 10. Implementar script de importação de tabela
  - Criar CLI com argumentos --campeonato, --arquivo, --excel, --mesclar
  - Implementar função que parseia arquivo texto com jogos
  - Implementar função que parseia planilha Excel com jogos
  - Implementar função que gera IDs únicos para jogos
  - Implementar função que organiza jogos por rodadas
  - Implementar função que converte datas para ISO 8601
  - Implementar função que normaliza nomes de times
  - Implementar função que atualiza tabela.json
  - Adicionar prompt de confirmação para sobrescrever/mesclar
  - Adicionar validação de dados importados
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 10.1 Escrever testes de propriedade para importação de tabela
  - **Property 9: Game data extraction completeness**
  - **Property 10: Game organization by rounds**
  - **Property 11: Game initialization state**
  - **Property 13: Date format conversion**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.6**

- [x] 11. Implementar script de importação de palpites
  - Criar CLI com argumentos --campeonato, --arquivo, --texto, --rodada
  - Implementar função que identifica participante do texto
  - Implementar função que extrai rodada do texto
  - Implementar função que infere rodada quando não especificada
  - Implementar função que extrai palpites do texto
  - Implementar função que normaliza nomes de times nos palpites
  - Implementar função que valida IDs de jogos
  - Implementar função que atualiza arquivo palpites.json do participante
  - Adicionar prompt de confirmação para sobrescrever palpites existentes
  - Adicionar sugestão de rodada quando inferida
  - Adicionar processamento de apostas extras
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9_

- [x] 11.1 Escrever testes de propriedade para importação de palpites
  - **Property 18: Prediction file update**
  - **Validates: Requirements 5.7**

- [x] 12. Implementar script de processamento de resultados - Modo teste
  - Criar CLI com argumentos --campeonato, --rodada, --teste, --final
  - Implementar função que carrega tabela, regras e palpites de todos os participantes
  - Implementar função que valida jogos obrigatórios finalizados
  - Implementar função que calcula pontuação para cada participante
  - Implementar função que conta acertos exatos para cálculo de bônus
  - Implementar função que calcula pontuação acumulada
  - Implementar função que gera classificação ordenada
  - Implementar função que calcula variação de posição
  - Implementar modo teste que apenas exibe resultados sem modificar arquivos
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

- [x] 12.1 Escrever testes de propriedade para processamento modo teste
  - **Property 20: Test mode file immutability**
  - **Property 21: Ranking completeness**
  - **Property 22: Ranking entry completeness**
  - **Property 23: Ranking sort order**
  - **Property 24: Mandatory games validation**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.6, 6.7**

- [x] 13. Implementar script de processamento de resultados - Modo final
  - Implementar função que cria backup de tabela.json com timestamp
  - Implementar função que atualiza campo rodada_atual
  - Implementar função que gera arquivo de relatório em texto
  - Implementar função que salva relatório no diretório Resultados
  - Adicionar validação de jogos obrigatórios antes de processar
  - Adicionar prompt de confirmação para modo final
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [x] 13.1 Escrever testes de propriedade para processamento modo final
  - **Property 25: Backup creation with timestamp**
  - **Property 26: Current round update**
  - **Property 27: Report file generation**
  - **Property 28: Report content completeness**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5, 7.6**

- [x] 14. Checkpoint - Garantir que todos os testes passam
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Criar documentação de uso
  - Criar README.md com instruções de instalação
  - Documentar uso de cada script com exemplos
  - Criar guia de formatos de entrada aceitos
  - Documentar estrutura de diretórios esperada
  - _Requirements: Todos_

- [x] 15.1 Criar exemplos de uso
  - Criar scripts de exemplo para cada operação
  - Criar dados de teste para demonstração
  - _Requirements: Todos_
