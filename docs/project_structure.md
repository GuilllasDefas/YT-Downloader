# Estrutura do Projeto

Este documento descreve a estrutura e organização do código-fonte do YouTube Downloader.

## Visão Geral

O YouTube Downloader segue uma arquitetura modular organizada em diferentes diretórios e arquivos com responsabilidades específicas. A aplicação é construída principalmente com Python e PyQt5 para a interface gráfica.

## Árvore de Diretórios

```md
YT-Downloader/
├── main.py                # Ponto de entrada da aplicação
├── requirements.txt       # Dependências do projeto
├── README.md              # Documentação principal
├── config.json            # Arquivo de configuração
├── download_history.json  # Histórico de downloads
├── src/                   # Código-fonte principal
│   ├── ui/                # Componentes de interface gráfica
│   ├── core/              # Funcionalidades principais
│   └── utils/             # Utilitários e helpers
├── resources/             # Recursos estáticos
│   ├── styles/            # Arquivos de estilo (QSS)
│   └── images/            # Ícones e imagens
├── docs/                  # Documentação
└── logs/                  # Arquivos de log
```

## Componentes Principais

### Módulo Principal

- **main.py**: Ponto de entrada da aplicação, inicializa a interface e conecta os componentes

### Diretório `src/`

#### Subdiretório `src/ui/`

Contém os componentes da interface gráfica:

- **GUI.py**: Interface principal do aplicativo
- **settings_dialog.py**: Diálogo de configurações
- **history_window.py**: Janela de histórico de downloads
- **about_dialog.py**: Diálogo "Sobre"
- **theme_manager.py**: Gerenciamento de temas da interface

#### Subdiretório `src/core/`

Contém a lógica principal da aplicação:

- **downloader.py**: Responsável pelo download de vídeos usando yt-dlp
- **metadata.py**: Manipulação de metadados de áudio/vídeo
- **converter.py**: Conversão entre formatos de mídia
- **validator.py**: Validação de URLs e entradas

#### Subdiretório `src/utils/`

Contém utilitários e funções auxiliares:

- **config.py**: Gerenciamento de configurações
- **history.py**: Gerenciamento do histórico de downloads
- **logger.py**: Sistema de logs
- **ffmpeg_handler.py**: Interface para operações com FFmpeg
- **file_utils.py**: Funções para manipulação de arquivos

### Recursos e Arquivos de Configuração

- **config.json**: Armazena configurações do usuário
- **download_history.json**: Mantém registro dos downloads realizados
- **resources/styles/**: Contém arquivos QSS para estilização da interface
- **resources/images/**: Ícones e imagens usados na interface

## Fluxo de Execução

1. **Inicialização**: O arquivo `main.py` inicializa a aplicação
2. **Carregamento de Configurações**: As configurações são carregadas de `config.json`
3. **Interface**: A interface gráfica é inicializada e exibida
4. **Download**:
   - O usuário fornece uma URL e configurações
   - O `downloader.py` faz o download usando yt-dlp
   - Se necessário, o `converter.py` converte o arquivo
   - O `metadata.py` aplica metadados
5. **Finalização**:
   - O download é registrado no histórico
   - Os arquivos são salvos no diretório especificado

## Diagrama de Classes

```md
[MainWindow] ─┬─ [DownloaderWorker]
               │       │
               │       ├─ [YTDLPWrapper]
               │       └─ [FFmpegHandler]
               │
               ├─ [SettingsManager] ── [ConfigHandler]
               │
               ├─ [HistoryManager]
               │
               └─ [ThemeManager]
```

## Padrões de Projeto Utilizados

- **Singleton**: Para gerenciadores de configuração e logger
- **Observer**: Para notificações de progresso de download
- **Factory**: Para criação de objetos de download
- **Strategy**: Para diferentes estratégias de download e conversão

## Convenções de Código

- **Nomenclatura**: CamelCase para classes, snake_case para funções e variáveis
- **Docstrings**: Todas as classes e funções principais possuem docstrings
- **Tipagem**: Uso de type hints para parâmetros e retornos
- **Importações**: Organizadas por módulos da biblioteca padrão, módulos externos e módulos locais

## Extensibilidade

O projeto foi projetado para ser facilmente extensível:

- **Novos formatos**: Adicione suporte estendendo as classes em `converter.py`
- **Novos temas**: Adicione arquivos QSS em `resources/styles/`
- **Recursos adicionais**: Implemente novos workers e conecte-os à interface

## Áreas para Contribuição

- **Melhorias de UI/UX**: Refinamento da interface
- **Otimizações de performance**: Especialmente para conversão de arquivos grandes
- **Suporte a playlists**: Melhorar o suporte para download de playlists
- **Metadados avançados**: Melhorar a extração e aplicação de metadados
- **Internacionalização**: Adicionar suporte a múltiplos idiomas
