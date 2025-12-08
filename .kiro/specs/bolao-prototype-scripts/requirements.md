# Requirements Document

## Introduction

Este documento define os requisitos para a fase inicial de prototipagem do Sistema de Controle de Bolão. O objetivo é criar scripts Python locais que automatizem tarefas administrativas essenciais para gerenciar campeonatos de apostas esportivas. Os scripts serão executados localmente pelo administrador e processarão dados em formato JSON, permitindo a criação de campeonatos, importação de tabelas, processamento de palpites e cálculo de resultados.

## Glossary

- **Sistema**: O conjunto de scripts Python para gerenciamento de bolão
- **Administrador**: Usuário que executa os scripts localmente para gerenciar campeonatos
- **Campeonato**: Competição esportiva com tabela de jogos, regras e participantes
- **Participante**: Apostador registrado em um ou mais campeonatos
- **Palpite**: Previsão de resultado de um jogo feita por um participante
- **Rodada**: Conjunto de jogos agrupados em um período específico
- **Tabela**: Arquivo JSON contendo todos os jogos do campeonato organizados por rodadas
- **Regras**: Arquivo JSON definindo o sistema de pontuação do campeonato
- **Parser**: Componente que converte texto não estruturado em dados JSON
- **Normalização**: Processo de padronizar nomes de times para garantir consistência

## Requirements

### Requirement 1

**User Story:** Como administrador, quero criar a estrutura inicial de um novo campeonato, para que eu possa começar a gerenciar apostas de forma organizada.

#### Acceptance Criteria

1. WHEN o administrador executa o script de criação de campeonato com nome válido, THEN o Sistema SHALL criar um diretório com o nome do campeonato dentro de "Campeonatos"
2. WHEN o diretório do campeonato é criado, THEN o Sistema SHALL criar os subdiretórios "Regras", "Tabela", "Resultados" e "Participantes"
3. WHEN os subdiretórios são criados, THEN o Sistema SHALL criar arquivos JSON vazios "regras.json" e "tabela.json" com estrutura básica válida
4. WHEN o administrador tenta criar um campeonato com nome já existente, THEN o Sistema SHALL rejeitar a operação e exibir mensagem de erro
5. WHEN o nome do campeonato contém caracteres especiais inválidos, THEN o Sistema SHALL normalizar o nome removendo ou substituindo caracteres problemáticos

### Requirement 2

**User Story:** Como administrador, quero gerar o arquivo de regras automaticamente a partir do template padrão, para que eu não precise criar manualmente a configuração de pontuação.

#### Acceptance Criteria

1. WHEN o administrador executa o script de criação de regras para um campeonato, THEN o Sistema SHALL gerar o arquivo "regras.json" com todas as 10 regras de pontuação padrão
2. WHEN o arquivo de regras é gerado, THEN o Sistema SHALL incluir os campos obrigatórios "campeonato", "versao" e "regras"
3. WHEN cada regra é criada, THEN o Sistema SHALL incluir os campos "pontos" (ou "pontos_base"), "descricao" e "codigo"
4. WHEN o arquivo de regras já existe, THEN o Sistema SHALL solicitar confirmação antes de sobrescrever
5. WHEN o administrador fornece nome e temporada do campeonato, THEN o Sistema SHALL incluir essas informações no arquivo de regras

### Requirement 3

**User Story:** Como administrador, quero criar a estrutura de dados dos participantes a partir de uma lista, para que eu possa registrar todos os apostadores rapidamente.

#### Acceptance Criteria

1. WHEN o administrador fornece uma lista de nomes em arquivo texto, THEN o Sistema SHALL criar um subdiretório para cada participante dentro de "Participantes"
2. WHEN o administrador fornece uma planilha Excel com nomes, THEN o Sistema SHALL extrair os nomes e criar a estrutura de participantes
3. WHEN um subdiretório de participante é criado, THEN o Sistema SHALL criar o arquivo "palpites.json" com estrutura básica válida
4. WHEN o nome do participante contém espaços ou caracteres especiais, THEN o Sistema SHALL normalizar o nome para o formato do diretório
5. WHEN o arquivo "palpites.json" é criado, THEN o Sistema SHALL incluir os campos "apostador", "codigo_apostador", "campeonato" e "palpites" vazio

### Requirement 4

**User Story:** Como administrador, quero importar a tabela de jogos a partir de um arquivo externo, para que eu não precise digitar manualmente todos os jogos do campeonato.

#### Acceptance Criteria

1. WHEN o administrador fornece um arquivo texto com jogos, THEN o Sistema SHALL extrair informações de mandante, visitante, data e local
2. WHEN o administrador fornece uma planilha Excel com jogos, THEN o Sistema SHALL processar as colunas e extrair os dados estruturados
3. WHEN os jogos são processados, THEN o Sistema SHALL atualizar o arquivo "tabela.json" organizando jogos por rodadas
4. WHEN um jogo é adicionado à tabela, THEN o Sistema SHALL gerar um ID único, definir status como "agendado" e inicializar gols em 0
5. WHEN nomes de times são processados, THEN o Sistema SHALL normalizar variações do mesmo time para um formato consistente
6. WHEN a data do jogo está em formato não-ISO, THEN o Sistema SHALL converter para o formato ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
7. WHEN o arquivo "tabela.json" já contém jogos, THEN o Sistema SHALL solicitar confirmação antes de sobrescrever ou mesclar dados

### Requirement 5

**User Story:** Como administrador, quero importar palpites de participantes em formato texto, para que eu possa processar mensagens do WhatsApp facilmente.

#### Acceptance Criteria

1. WHEN o administrador fornece texto de palpite com nome do apostador, THEN o Sistema SHALL identificar o participante correspondente
2. WHEN o texto contém indicação de rodada, THEN o Sistema SHALL associar os palpites à rodada especificada
3. WHEN o texto NÃO contém indicação de rodada, THEN o Sistema SHALL inferir a rodada através dos nomes dos times mencionados
4. WHEN o Sistema infere a rodada, THEN o Sistema SHALL sugerir a rodada identificada e solicitar confirmação do administrador
5. WHEN palpites são extraídos do texto, THEN o Sistema SHALL reconhecer diferentes formatos de placar (ex: "2x1", "2 x 1", "2-1")
6. WHEN nomes de times nos palpites são processados, THEN o Sistema SHALL normalizar para corresponder aos nomes na tabela
7. WHEN o palpite é validado, THEN o Sistema SHALL atualizar o arquivo "palpites.json" do participante correspondente
8. WHEN o participante já possui palpite para o mesmo jogo, THEN o Sistema SHALL solicitar confirmação antes de sobrescrever
9. WHEN apostas extras são identificadas no texto, THEN o Sistema SHALL processar e armazenar separadamente com marcação apropriada

### Requirement 6

**User Story:** Como administrador, quero processar resultados de uma rodada em modo teste, para que eu possa verificar os cálculos antes de finalizar.

#### Acceptance Criteria

1. WHEN o administrador executa o processamento em modo teste, THEN o Sistema SHALL calcular pontuações sem modificar arquivos
2. WHEN os resultados são calculados, THEN o Sistema SHALL exibir no output a classificação completa da rodada
3. WHEN a classificação é exibida, THEN o Sistema SHALL mostrar para cada participante os códigos de acerto, pontos por jogo e total da rodada
4. WHEN a classificação é exibida, THEN o Sistema SHALL incluir a pontuação acumulada total até a rodada atual
5. WHEN a classificação é exibida, THEN o Sistema SHALL mostrar a variação de posição em relação à rodada anterior
6. WHEN a classificação é exibida, THEN o Sistema SHALL ordenar participantes por pontuação total decrescente
7. WHEN o modo teste é executado, THEN o Sistema SHALL validar que todos os jogos obrigatórios da rodada estão finalizados

### Requirement 7

**User Story:** Como administrador, quero processar resultados de uma rodada em modo final, para que eu possa atualizar oficialmente os dados do campeonato.

#### Acceptance Criteria

1. WHEN o administrador executa o processamento em modo final, THEN o Sistema SHALL criar uma cópia de backup do arquivo "tabela.json" antes de modificar
2. WHEN o backup é criado, THEN o Sistema SHALL incluir timestamp no nome do arquivo de backup
3. WHEN os resultados são processados, THEN o Sistema SHALL atualizar o campo "rodada_atual" no arquivo "tabela.json"
4. WHEN os resultados são processados, THEN o Sistema SHALL gerar um arquivo de relatório da rodada em formato texto
5. WHEN o relatório é gerado, THEN o Sistema SHALL incluir tabela formatada com classificação, códigos de acerto e pontuações
6. WHEN o relatório é gerado, THEN o Sistema SHALL salvar o arquivo no diretório "Resultados" com nome identificando a rodada
7. WHEN o modo final é executado sem todos os jogos obrigatórios finalizados, THEN o Sistema SHALL rejeitar a operação e exibir mensagem de erro

### Requirement 8

**User Story:** Como administrador, quero que o sistema calcule pontuações seguindo a hierarquia de regras, para que os participantes recebam a maior pontuação aplicável a cada palpite.

#### Acceptance Criteria

1. WHEN um palpite tem placar exato igual ao resultado, THEN o Sistema SHALL atribuir 12 pontos base mais bônus proporcional
2. WHEN o bônus é calculado, THEN o Sistema SHALL dividir 1 pelo número de participantes que acertaram o resultado exato do mesmo jogo
3. WHEN um palpite acerta vencedor e gols de uma equipe, THEN o Sistema SHALL atribuir 7 pontos
4. WHEN um palpite acerta vencedor e diferença de gols, THEN o Sistema SHALL atribuir 6 pontos
5. WHEN um palpite acerta vencedor e soma total de gols, THEN o Sistema SHALL atribuir 6 pontos
6. WHEN um palpite acerta apenas o vencedor, THEN o Sistema SHALL atribuir 5 pontos
7. WHEN um palpite acerta apenas que houve empate, THEN o Sistema SHALL atribuir 5 pontos
8. WHEN um palpite acerta gols de apenas um time sem acertar resultado, THEN o Sistema SHALL atribuir 2 pontos
9. WHEN um palpite acerta apenas a soma total de gols, THEN o Sistema SHALL atribuir 1 ponto
10. WHEN um palpite tem placar exatamente invertido ao resultado, THEN o Sistema SHALL atribuir -3 pontos
11. WHEN um participante não enviou palpite para jogo obrigatório, THEN o Sistema SHALL atribuir -1 ponto
12. WHEN múltiplas regras são aplicáveis a um palpite, THEN o Sistema SHALL atribuir apenas a pontuação de maior valor

### Requirement 9

**User Story:** Como administrador, quero que o sistema normalize nomes de times automaticamente, para que variações de escrita sejam reconhecidas como o mesmo time.

#### Acceptance Criteria

1. WHEN o Sistema processa um nome de time, THEN o Sistema SHALL remover espaços extras no início e fim
2. WHEN o nome contém barras ("/"), THEN o Sistema SHALL considerar equivalente a hífens ("-")
3. WHEN o nome contém acentos, THEN o Sistema SHALL considerar equivalente à versão sem acentos
4. WHEN o nome tem variações de maiúsculas/minúsculas, THEN o Sistema SHALL tratar como equivalentes
5. WHEN o Sistema não encontra correspondência exata, THEN o Sistema SHALL sugerir times similares e solicitar confirmação

### Requirement 10

**User Story:** Como administrador, quero que o sistema valide dados de entrada, para que erros sejam detectados antes de processar informações incorretas.

#### Acceptance Criteria

1. WHEN o Sistema recebe dados de entrada, THEN o Sistema SHALL verificar se campos obrigatórios estão presentes
2. WHEN datas são fornecidas, THEN o Sistema SHALL validar que estão em formato válido
3. WHEN placares são fornecidos, THEN o Sistema SHALL validar que são números inteiros não-negativos
4. WHEN IDs de jogos são referenciados, THEN o Sistema SHALL validar que existem na tabela do campeonato
5. WHEN nomes de participantes são fornecidos, THEN o Sistema SHALL validar que estão registrados no campeonato
6. WHEN dados inválidos são detectados, THEN o Sistema SHALL exibir mensagem de erro clara indicando o problema
7. WHEN operações críticas são solicitadas, THEN o Sistema SHALL solicitar confirmação explícita do administrador
