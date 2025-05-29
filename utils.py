import re
import logging
import subprocess
from pathlib import Path
import urllib.parse

def configurar_logging():
    """Configura o sistema de logging para diagnóstico do aplicativo."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / 'youtube_downloader.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('youtube_downloader')

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
