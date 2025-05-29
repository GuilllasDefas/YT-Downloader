# Guia de Instalação

Este guia fornece instruções detalhadas para instalar o YouTube Downloader em diferentes sistemas operacionais.

## Requisitos de Sistema

- **Sistema Operacional**: Windows 7 ou superior, macOS 10.12+, Ubuntu 18.04+ ou distribuição Linux equivalente
- **Python**: Versão 3.7 ou superior (recomendado 3.12+)
- **Espaço em Disco**: Mínimo de 100MB para a aplicação
- **Memória**: Mínimo de 2GB RAM
- **FFmpeg**: Instalado e configurado no PATH

## Instalação do Python

1. Baixe o instalador do Python em [python.org](https://www.python.org/downloads/)
2. Execute o instalador e **marque a opção "Add Python to PATH"**
3. Clique em "Install Now"
4. Verifique a instalação abrindo o Prompt de Comando e digitando:

   ```bash
   python --version
   ```

## Instalação do FFmpeg

1. Baixe o FFmpeg de [ffmpeg.org](https://ffmpeg.org/download.html) (versão estática)
2. Extraia os arquivos para uma pasta, por exemplo: `C:\ffmpeg`
3. Adicione ao PATH:
   - Abra "Sistema" nas Configurações do Windows
   - Clique em "Informações do sistema" > "Configurações avançadas do sistema"
   - Clique em "Variáveis de ambiente"
   - Em "Variáveis do sistema", selecione "Path" e clique em "Editar"
   - Clique em "Novo" e adicione o caminho para a pasta bin, ex: `C:\ffmpeg\bin`
   - Clique em "OK" para fechar todas as janelas
4. Verifique a instalação:

   ```bash
   ffmpeg -version
   ```

## Instalação do YouTube Downloader

### Método 1: Instalação a partir do código-fonte

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/YT-Downloader.git
   cd YT-Downloader
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):

   ```bash
   python -m venv venv
   
   # Ativar no Windows
   venv\Scripts\activate
   
   # Ativar no macOS/Linux
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute o aplicativo:

   ```bash
   python main.py
   ```

### Método 2: Instalação a partir do executável (Windows)

1. Baixe o instalador da seção "Releases" no GitHub
2. Execute o instalador e siga as instruções na tela
3. Após a instalação, inicie o aplicativo a partir do atalho criado

## Verificando a Instalação

Para verificar se tudo está funcionando corretamente:

1. Inicie o aplicativo
2. Vá para o menu "Ajuda" > "Verificar Dependências"
3. O aplicativo deve informar que todas as dependências estão instaladas corretamente

## Solução de Problemas

### FFmpeg não encontrado

- Verifique se o FFmpeg está no PATH do sistema
- Reinicie o computador após adicionar o FFmpeg ao PATH
- No Windows, tente reinstalar o FFmpeg com a opção de adicionar ao PATH
