# Guia de Uso

Este guia explica como usar o YouTube Downloader para baixar vídeos e áudios do YouTube.

## Interface Principal

![Interface Principal](images/main_screen.png)

A interface principal do YouTube Downloader contém:

1. **Campo de URL**: Onde você cola o link do vídeo do YouTube
2. **Botão de Destino**: Para selecionar onde os arquivos serão salvos
3. **Opções de Download**: Para selecionar o formato e qualidade
4. **Botões de Ação**: Para iniciar o download ou acessar outras funções
5. **Barra de Progresso**: Mostra o progresso do download atual
6. **Barra de Status**: Exibe informações sobre a operação atual

## Download Básico

### Baixar um Vídeo

1. Cole a URL do vídeo do YouTube no campo de URL
2. Selecione o diretório de destino clicando no botão "..."
3. Escolha o formato de vídeo (MP4 ou MKV) nas configurações
4. Selecione a qualidade desejada (360p, 480p, 720p, 1080p)
5. Clique no botão "Baixar Vídeo"
6. Aguarde o download ser concluído

### Baixar Apenas o Áudio (MP3)

1. Cole a URL do vídeo do YouTube no campo de URL
2. Selecione o diretório de destino clicando no botão "..."
3. Escolha a qualidade de áudio nas configurações (128, 192 ou 320 kbps)
4. Clique no botão "Baixar MP3"
5. Aguarde o download e a conversão serem concluídos

## Configurações Avançadas

Acesse as configurações através do menu "Configurações > Preferências" ou do ícone de engrenagem.

### Configurações Disponíveis

![Tela de Configurações](images/settings.png)

- **Tema**: Escolha entre temas claro e escuro para a interface
- **Diretório Padrão**: Define o local padrão para salvar os downloads
- **Qualidade de Áudio**: Define a qualidade dos arquivos MP3 (bitrate)
- **Formato de Vídeo**: Escolha entre MP4 e MKV para downloads de vídeo
- **Qualidade de Vídeo**: Define a resolução máxima para downloads de vídeo
- **Metadados**: Ativa/desativa a aplicação automática de metadados em arquivos MP3
- **Thumbnails**: Ativa/desativa o salvamento de thumbnails como capas de álbum

## Gerenciando o Histórico de Downloads

Para acessar seu histórico de downloads:

1. Clique no menu "Histórico" ou no ícone de relógio na interface principal
2. Veja a lista de downloads anteriores com data, título e caminho
3. Use os botões de ação para:
   - Abrir a pasta onde o arquivo está salvo
   - Reproduzir o arquivo
   - Baixar novamente o mesmo vídeo
   - Remover o item do histórico

## Dicas e Truques

### Downloads em Lote

Para fazer downloads em lote:

1. Crie um arquivo de texto com URLs do YouTube (uma por linha)
2. No menu, selecione "Arquivo > Importar URLs"
3. Selecione o arquivo de texto
4. Configure as opções de download
5. Clique em "Iniciar Downloads em Lote"

### Atalhos de Teclado

- **Ctrl+V**: Cola a URL do vídeo
- **Ctrl+O**: Abre o seletor de diretório
- **Ctrl+S**: Acessa as configurações
- **Ctrl+H**: Abre o histórico
- **Ctrl+D**: Inicia o download de vídeo
- **Ctrl+M**: Inicia o download de MP3
- **F1**: Abre a ajuda
- **Esc**: Cancela o download atual

### Extração de Informações

Para apenas extrair informações do vídeo sem baixá-lo:

1. Cole a URL do vídeo
2. Clique no menu "Ferramentas > Informações do Vídeo"
3. Veja detalhes como duração, resolução disponível, canal, etc.
4. Você pode copiar essas informações ou salvá-las em um arquivo

## Resolução de Problemas Comuns

### O download falha com erro

- Verifique sua conexão com a internet
- Verifique se o vídeo não foi removido do YouTube
- Tente um formato ou qualidade diferente
- Verifique os logs em "Ajuda > Logs"

### Metadados ou thumbnail não aplicados

- Verifique se o FFmpeg está instalado corretamente
- Certifique-se de que as opções estão ativadas nas configurações
- Alguns vídeos podem não ter metadados completos disponíveis

### Baixa velocidade de download

- Verifique sua conexão com a internet
- Tente uma qualidade menor
- Verifique se outros programas estão usando a rede

Para mais ajuda, consulte a [documentação de solução de problemas](troubleshooting.md) ou o [guia de instalação](installation.md).
