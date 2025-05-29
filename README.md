# YouTube Downloader

## Descrição

YouTube Downloader é uma aplicação desktop desenvolvida em Python que permite baixar vídeos e áudios do YouTube de forma simples e este aplicativo suporta diferentes formatos e qualidades de download.

## Funcionalidades

- Download de vídeos do YouTube em MP4 ou MKV
- Conversão de vídeos para áudio MP3
- Interface gráfica amigável com temas claro e escuro
- Barra de progresso em tempo real
- Registro de histórico de downloads
- Extração e aplicação automática de thumbnails como capas de álbum
- Aplicação de metadados em arquivos MP3
- Configurações personalizáveis

## Requisitos

- Python 3.7+ (Utilizei a versão 3.12.9)
- FFmpeg (instalado no sistema e acessível pelo PATH)
- Bibliotecas Python (instaláveis via pip):
  - PyQt5 (5.15.11)
  - yt_dlp (2025.3.31)
  - mutagen (1.47.0)
  - Pillow (10.4.0)

## Instalação

1. Clone ou baixe este repositório
2. Instale as dependências: pip install -r requirements.txt
3. Certifique-se de ter o FFmpeg instalado no seu sistema:
   - **Windows**: Baixe em [ffmpeg.org](https://ffmpeg.org/download.html), vá em variáveis de ambiente e adicione ao PATH
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) ou `sudo dnf install ffmpeg` (Fedora)
   - **macOS**: `brew install ffmpeg` (usando Homebrew)

## Como usar

1. Execute o aplicativo:
2. Cole a URL do vídeo do YouTube que deseja baixar
3. Escolha o diretório de destino
4. Selecione o formato e qualidade desejados
5. Clique em "Baixar MP3" ou "Baixar Vídeo"

## Configurações

O aplicativo permite personalizar diversas configurações:

- **Tema**: Escolha entre tema claro ou escuro
- **Qualidade de áudio**: 128, 192 ou 320 kbps
- **Formato de vídeo**: MP4 ou MKV
- **Qualidade de vídeo**: 360p, 480p, 720p ou 1080p
- **Metadados**: Aplicação automática de metadados e capas de álbum

Acesse as configurações através do menu "Configurações > Preferências".

## Estrutura do projeto

- `main.py` - Ponto de entrada da aplicação
- `GUI.py` - Interface pra usar mais fácil
- `downloader.py` - download do YouTube
- `metadata.py` - Gerenciamento de metadados
- `config.py` - Gerenciamento de configurações
- `history.py` - Histórico de downloads
- `utils.py` - Funções utilitárias

## Solução de problemas

Se encontrar problemas:

1. Verifique se o FFmpeg está instalado corretamente
2. Verifique se todas as dependências Python estão instaladas
3. Consulte os logs em `logs/youtube_downloader.log`
4. Use a opção "Ajuda > Verificar Dependências" no aplicativo

## Contribuição

Contribuições são bem-vindas!
