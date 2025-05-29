import re
import logging
import subprocess
from pathlib import Path
import urllib.parse
import os
import sys

def configurar_logging():
    """Configura o sistema de logging para diagnóstico do aplicativo."""
    # Determinar o diretório base (funciona tanto para script quanto para executável)
    if getattr(sys, 'frozen', False):
        # Executável compilado
        base_dir = Path(sys.executable).parent
    else:
        # Script Python
        base_dir = Path(__file__).parent
    
    log_dir = base_dir / 'logs'
    
    # Tentar criar o diretório de logs com tratamento de erro
    try:
        log_dir.mkdir(exist_ok=True, parents=True)
        log_file = log_dir / 'youtube_downloader.log'
        file_handler = logging.FileHandler(log_file)
    except (OSError, PermissionError) as e:
        # Fallback: usar diretório temporário do usuário
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / 'youtube_downloader_logs'
        try:
            temp_dir.mkdir(exist_ok=True, parents=True)
            log_file = temp_dir / 'youtube_downloader.log'
            file_handler = logging.FileHandler(log_file)
        except (OSError, PermissionError):
            # Último recurso: apenas console
            file_handler = None
    
    # Configurar handlers
    handlers = [logging.StreamHandler()]
    if file_handler:
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logger = logging.getLogger('youtube_downloader')
    if file_handler:
        logger.info(f"Log sendo salvo em: {log_file}")
    else:
        logger.warning("Não foi possível criar arquivo de log. Usando apenas console.")
    
    return logger

logger = configurar_logging()

def verificar_dependencias():
    """Verifica se todas as dependências necessárias estão instaladas."""
    missing_deps = []
    
    # Verificar FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        missing_deps.append("FFmpeg")
    
    # Verificar yt-dlp
    try:
        import yt_dlp
    except ImportError:
        missing_deps.append("yt-dlp")
    
    # Verificar PyQt5
    try:
        from PyQt5 import QtWidgets
    except ImportError:
        missing_deps.append("PyQt5")
    
    return missing_deps

def validar_url_youtube(url):
    """Valida se a URL é uma URL válida do YouTube."""
    if not url:
        return False, "URL não pode estar vazia"
        
    # Normalizar a URL
    try:
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme:
            url = "https://" + url
            parsed_url = urllib.parse.urlparse(url)
    except Exception:
        return False, "URL mal formatada"
    
    # Verificar se é uma URL do YouTube
    youtube_regex = r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$'
    match = re.match(youtube_regex, url)
    
    if not match:
        return False, "URL não parece ser do YouTube"
    
    return True, url

def sanitizar_nome_arquivo(filename):
    """Remove caracteres inválidos de nomes de arquivos."""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '_', filename)

def obter_tamanho_arquivo_str(size_in_bytes):
    """Converte tamanho em bytes para formato legível."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes/1024:.2f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_in_bytes/(1024*1024*1024):.2f} GB"
