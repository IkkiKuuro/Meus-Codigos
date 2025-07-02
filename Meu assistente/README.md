# Kuro - Assistente Pessoal Inteligente

Kuro é um assistente pessoal em linha de comando criado em Python que aprende e se adapta às preferências do usuário. Desenvolvido por Ikki (Iranildo).

## Características

- **Aprendizado Adaptativo**: Kuro aprende com as interações e pode buscar informações na web
- **Personalidade Adaptável**: Muda seu humor, formalidade e estilo de comunicação com base nas interações
- **Gerenciamento de Tarefas**: Adiciona, lista e gerencia suas tarefas e compromissos
- **Gerenciamento de Contatos**: Armazena e recupera informações de contatos
- **Sistema de Notas**: Cria e gerencia notas rápidas
- **Navegação Web**: Abre sites e realiza pesquisas no Google
- **Persistência de Dados**: Salva todas as preferências e dados entre sessões
- **Machine Learning**: Utiliza classificação para entender e responder perguntas similares

## Estrutura do Projeto

```
Meu assistente/
├── kuro.py              # Arquivo principal do assistente
├── modulos/             # Módulos de funcionalidades
│   ├── __init__.py      # Inicialização dos módulos
│   ├── aprendizado.py   # Sistema de aprendizado e busca de informações
│   ├── personalidade.py # Gerenciamento de personalidade e adaptação
│   ├── gerenciador_dados.py # Gerenciamento de tarefas, contatos e notas
│   └── web.py           # Funcionalidades relacionadas à web
├── dados/               # Armazenamento de dados (criado automaticamente)
├── aprendizado/         # Base de conhecimento (criado automaticamente)
│   ├── conhecimento.json # Base de conhecimento armazenada em JSON
│   ├── modelo_ml.joblib  # Modelo de machine learning treinado
│   └── vetorizador.joblib # Vetorizador TF-IDF para processamento de texto
├── gerar_modelo_ml.py   # Script para treinar o modelo de ML
├── inicializar_ml.py    # Script para inicializar arquivos de ML básicos
└── requirements.txt     # Dependências do projeto
```

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Inicialize os arquivos de machine learning (opcional, criados automaticamente na primeira execução):

```bash
python inicializar_ml.py
```

4. Execute o Kuro:

```bash
python kuro.py
# ou
./kuro.py
```

## Comandos Principais

### Personalização

- `seja mais formal/casual/descontraído` - Ajusta o estilo de comunicação
- `use/não use emojis` - Controla o uso de emojis
- `seja mais conciso/detalhado` - Ajusta o nível de detalhes das respostas
- `mude seu humor para animado/sério/engraçado` - Altera o humor do assistente

### Aprendizado

- `aprenda que [conceito] é [definição]` - Ensina algo novo ao Kuro
- `aprenda isso: [pergunta] -> [resposta]` - Formato alternativo de ensino
- `o que é [conceito]` - Pergunta sobre algo que o Kuro saiba ou busca na web

O Kuro utiliza machine learning para identificar a categoria das perguntas e buscar respostas relevantes mesmo quando a pergunta não é exatamente igual à que foi ensinada. Quanto mais você ensina, mais inteligente ele se torna!

### Tarefas

- `adicionar tarefa [descrição]` - Adiciona uma nova tarefa
- `listar tarefas` - Mostra todas as tarefas
- `concluir tarefa [número]` - Marca uma tarefa como concluída
- `remover tarefa [número]` - Remove uma tarefa

### Contatos

- `adicionar contato [nome]: [telefone/email]` - Adiciona um novo contato
- `buscar contato [nome]` - Busca um contato pelo nome
- `listar contatos` - Mostra todos os contatos
- `remover contato [nome]` - Remove um contato

### Notas

- `adicionar nota [conteúdo]` - Adiciona uma nova nota
- `listar notas` - Mostra todas as notas
- `remover nota [número]` - Remove uma nota

### Web

- `abrir [site/aplicativo]` - Abre um site ou aplicativo
- `pesquisar [termos]` - Realiza uma pesquisa no Google

## Contribuições

Sinta-se à vontade para contribuir com este projeto, adicionando novas funcionalidades ou melhorando as existentes.

## Licença

Este projeto é de uso livre.

## Criador

Desenvolvido por Ikki (Iranildo).
