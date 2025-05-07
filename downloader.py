import os
import re
from yt_dlp import YoutubeDL
from PyQt5.QtCore import QObject, pyqtSignal
from utils import logger, validate_youtube_url, sanitize_filename
from metadata import apply_metadata, extract_artist_from_title, download_thumbnail
from history import add_to_history

class DownloadManager(QObject):
    progress_signal = pyqtSignal(int, dict)
    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal(str, dict)
    info_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.current_download = None
        self.should_cancel = False
    
    def extract_info(self, url):
        """Extrai informações do vídeo sem baixar."""
        is_valid, msg = validate_youtube_url(url)
        if not is_valid:
            self.error_signal.emit(msg)
            return None
            
        ydl_opts = {
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.info_signal.emit(info)
                return info
        except Exception as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            self.error_signal.emit(f"Erro ao obter informações do vídeo: {str(e)}")
            return None
    
    def hook(self, d):
        """Callback para atualizar o progresso de download."""
        if self.should_cancel:
            raise Exception("Download cancelado pelo usuário")
            
        if d['status'] == 'downloading':
            progress_str = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_percent_str', '0.0'))
            progress_float = float(progress_str.replace('%','').strip())
            
            # Informações adicionais
            info = {
                'speed': d.get('_speed_str', 'N/A'),
                'eta': d.get('_eta_str', 'N/A'),
                'filename': d.get('filename', 'N/A'),
                'total_bytes': d.get('total_bytes', 0)
            }
            
            self.progress_signal.emit(int(progress_float), info)
    
    def cancel_download(self):
        """Cancela o download atual."""
        self.should_cancel = True
        logger.info("Download cancelado pelo usuário")
    
    def download_audio(self, url, caminho, quality="320"):
        """Baixa áudio de vídeo do YouTube."""
        self.should_cancel = False
        
        is_valid, msg_or_url = validate_youtube_url(url)
        if not is_valid:
            self.error_signal.emit(msg_or_url)
            return
        
        url = msg_or_url  # URL validada
        
        if not os.path.isdir(caminho):
            try:
                os.makedirs(caminho, exist_ok=True)
            except Exception as e:
                error_msg = f"Não foi possível criar a pasta: {str(e)}"
                logger.error(error_msg)
                self.error_signal.emit(error_msg)
                return
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': os.path.join(caminho, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.hook],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Language': 'pt-BR,pt;q=0.9'
            }
        }
        
        try:
            # Primeiro extrair informações
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                thumbnail = info.get('thumbnail')
                
                # Baixar thumbnail
                thumbnail_data = None
                if thumbnail:
                    thumbnail_data = download_thumbnail(thumbnail)
                
                # Baixar áudio
                if not self.should_cancel:
                    ydl.download([url])
                    
                    # Caminho do arquivo baixado
                    filename = sanitize_filename(f"{title}.mp3")
                    file_path = os.path.join(caminho, filename)
                    
                    # Extrair artista e aplicar metadados
                    artist, song_title = extract_artist_from_title(title)
                    apply_metadata(file_path, song_title, artist, "YouTube Download", thumbnail_data)
                    
                    # Adicionar ao histórico
                    add_to_history(url, title, "audio", file_path)
                    
                    # Emitir sinal de sucesso com informações
                    success_info = {
                        'title': title,
                        'format': 'mp3',
                        'path': file_path,
                        'has_metadata': True
                    }
                    self.success_signal.emit(caminho, success_info)
        except Exception as e:
            error_msg = f"Erro ao baixar áudio: {str(e)}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)
    
    def download_video(self, url, caminho, format="mp4", quality="720p"):
        """Baixa vídeo do YouTube."""
        self.should_cancel = False
        
        is_valid, msg_or_url = validate_youtube_url(url)
        if not is_valid:
            self.error_signal.emit(msg_or_url)
            return
        
        url = msg_or_url  # URL validada
        
        if not os.path.isdir(caminho):
            try:
                os.makedirs(caminho, exist_ok=True)
            except Exception as e:
                error_msg = f"Não foi possível criar a pasta: {str(e)}"
                logger.error(error_msg)
                self.error_signal.emit(error_msg)
                return
        
        # Mapear qualidade para formato yt-dlp
        format_map = {
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        }
        
        format_string = format_map.get(quality, "best")
        
        ydl_opts = {
            'format': format_string,
            'merge_output_format': format.lower(),
            'outtmpl': os.path.join(caminho, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self.hook],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Language': 'pt-BR,pt;q=0.9'
            }
        }
        
        try:
            # Primeiro extrair informações
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                
                # Baixar vídeo
                if not self.should_cancel:
                    ydl.download([url])
                    
                    # Caminho do arquivo baixado
                    filename = sanitize_filename(f"{title}.{format.lower()}")
                    file_path = os.path.join(caminho, filename)
                    
                    # Adicionar ao histórico
                    add_to_history(url, title, "video", file_path)
                    
                    # Emitir sinal de sucesso com informações
                    success_info = {
                        'title': title,
                        'format': format.lower(),
                        'path': file_path,
                        'quality': quality
                    }
                    self.success_signal.emit(caminho, success_info)
        except Exception as e:
            error_msg = f"Erro ao baixar vídeo: {str(e)}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)

# Função de compatibilidade com a versão anterior
def baixar_audio(url, caminho, progress_callback=None):
    """Função de compatibilidade para versões anteriores."""
    manager = DownloadManager()
    if progress_callback:
        manager.progress_signal.connect(
            lambda value, _: progress_callback.emit(value)
        )
    manager.download_audio(url, caminho)