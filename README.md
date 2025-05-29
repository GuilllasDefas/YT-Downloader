# YouTube Downloader

![Versão](https://img.shields.io/badge/versão-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Licença](https://img.shields.io/badge/licença-MIT-green)

## Descrição

YouTube Downloader é uma aplicação desktop desenvolvida em Python que permite baixar vídeos e áudios do YouTube de forma simples e rápida. Este aplicativo suporta diferentes formatos e qualidades de download, oferecendo uma experiência completa para gerenciar seus conteúdos do YouTube.

## 🚀 Funcionalidades

- Download de vídeos do YouTube em MP4 ou MKV
- Conversão de vídeos para áudio MP3
- Interface gráfica amigável com temas claro e escuro
- Barra de progresso em tempo real
- Registro de histórico de downloads
- Extração e aplicação automática de thumbnails como capas de álbum
- Aplicação de metadados em arquivos MP3
- Configurações personalizáveis

## 📋 Requisitos

- Python 3.7+ (Recomendado: 3.12+)
- FFmpeg (instalado no sistema e acessível pelo PATH)
- Bibliotecas Python (instaláveis via pip):
  - PyQt5 (5.15.11)
  - yt_dlp (2025.5.22)
  - mutagen (1.47.0)
  - Pillow (11.2.1)
  - requests (2.32.3)

## 💻 Instalação

1. Clone ou baixe este repositório

   ```bash
   git clone https://github.com/seu-usuario/YT-Downloader.git
   cd YT-Downloader
   ```

2. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

3. Certifique-se de ter o FFmpeg instalado no seu sistema:
   - **Windows**: Baixe em [ffmpeg.org](https://ffmpeg.org/download.html), adicione ao PATH nas variáveis de ambiente
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) ou `sudo dnf install ffmpeg` (Fedora)
   - **macOS**: `brew install ffmpeg` (usando Homebrew)

## 🎮 Como usar

1. Execute o aplicativo:

   ```bash
   python main.py
   ```

   Ou use o executável criado pelo PyInstaller (se disponível)

2. Cole a URL do vídeo do YouTube que deseja baixar
3. Escolha o diretório de destino
4. Selecione o formato e qualidade desejados
5. Clique em "Baixar MP3" ou "Baixar Vídeo"

## ⚙️ Configurações

O aplicativo permite personalizar diversas configurações:

- **Tema**: Escolha entre tema claro ou escuro
- **Qualidade de áudio**: 128, 192 ou 320 kbps
- **Formato de vídeo**: MP4 ou MKV
- **Qualidade de vídeo**: 360p, 480p, 720p ou 1080p
- **Metadados**: Aplicação automática de metadados e capas de álbum

Acesse as configurações através do menu "Configurações > Preferências".

## 📂 Estrutura do projeto

```md
YT-Downloader/
├── main.py              # Ponto de entrada da aplicação
├── src/
│   ├── ui/              # Componentes da interface
│   ├── core/            # Lógica principal  
│   └── utils/           # Funções utilitárias
├── resources/           # Recursos gráficos e estilos
├── docs/                # Documentação
└── logs/                # Arquivos de log
```

Arquivos principais:

- `main.py` - Ponto de entrada da aplicação
- `src/ui/GUI.py` - Interface gráfica
- `src/core/downloader.py` - Gerenciamento de download do YouTube
- `src/core/metadata.py` - Gerenciamento de metadados
- `src/utils/config.py` - Gerenciamento de configurações
- `src/utils/history.py` - Histórico de downloads

## 🔧 Solução de problemas

Se encontrar problemas:

1. Verifique se o FFmpeg está instalado corretamente e disponível no PATH
2. Certifique-se de que todas as dependências Python estão instaladas
3. Consulte os logs em `logs/youtube_downloader.log`
4. Use a opção "Ajuda > Verificar Dependências" no aplicativo
5. Consulte a [documentação detalhada]

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

Consulte nossa [documentação para contribuidores](docs/CONTRIBUTING.md) para mais detalhes.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes.

## 📸 Screenshots

![Tela Principal](docs/images/main_screen.png)
![Configurações](docs/images/settings.png)
