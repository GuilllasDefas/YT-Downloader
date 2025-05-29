import os
import re
import sys
from yt_dlp import YoutubeDL
from PyQt5.QtCore import QObject, pyqtSignal
from utils import logger, validar_url_youtube, sanitizar_nome_arquivo
from metadata import aplicar_metadados, extrair_artista_do_titulo, baixar_thumbnail
from history import adicionar_ao_historico

def configurar_ffmpeg():
    """Configura o FFmpeg para o yt-dlp funcionar em executáveis compilados."""
    try:
        import ffmpeg
        # Verificar se ffmpeg-python está funcionando
        ffmpeg.probe('NUL' if os.name == 'nt' else '/dev/null')
        return True
    except:
        logger.warning("ffmpeg-python não encontrado. Tentando FFmpeg do sistema...")
        return False

class GerenciadorDownload(QObject):
    sinal_progresso = pyqtSignal(int, dict)
    sinal_erro = pyqtSignal(str)
    sinal_sucesso = pyqtSignal(str, dict)
    sinal_info = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.download_atual = None
        self.deve_cancelar = False
    
    def extrair_info(self, url):
        """Extrai informações do vídeo sem baixar."""
        is_valid, msg = validar_url_youtube(url)
        if not is_valid:
            self.sinal_erro.emit(msg)
            return None
            
        ydl_opts = {
            'quiet': True,
            'no_warnings': True
        }
        
        # Configurar FFmpeg se disponível
        if configurar_ffmpeg():
            try:
                import ffmpeg
                ydl_opts['ffmpeg_location'] = ffmpeg.__file__.replace('__init__.py', 'ffmpeg.exe')
            except:
                pass
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.sinal_info.emit(info)
                return info
        except Exception as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            self.sinal_erro.emit(f"Erro ao obter informações do vídeo: {str(e)}")
            return None
    
    def gancho(self, d):
        """Atualizar o progresso de download."""
        if self.deve_cancelar:
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
            
            self.sinal_progresso.emit(int(progress_float), info)
    
    def cancelar_download(self):
        """Cancela o download atual."""
        self.deve_cancelar = True
        logger.info("Download cancelado pelo usuário")
    
    def baixar_audio(self, url, caminho, quality="320"):
        """Baixa áudio de vídeo do YouTube."""
        self.deve_cancelar = False
        
        is_valid, msg_or_url = validar_url_youtube(url)
        if not is_valid:
            self.sinal_erro.emit(msg_or_url)
            return
        
        url = msg_or_url  # URL validada
        
        if not os.path.isdir(caminho):
            try:
                os.makedirs(caminho, exist_ok=True)
            except Exception as e:
                error_msg = f"Não foi possível criar a pasta: {str(e)}"
                logger.error(error_msg)
                self.sinal_erro.emit(error_msg)
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
            'progress_hooks': [self.gancho],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Language': 'pt-BR,pt;q=0.9'
            }
        }
        
        # Configurar FFmpeg se disponível
        if configurar_ffmpeg():
            try:
                import ffmpeg
                # Para executáveis compilados, usar path absoluto
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                    ffmpeg_path = os.path.join(base_path, '_internal', 'ffmpeg', 'bin', 'ffmpeg.exe')
                    if os.path.exists(ffmpeg_path):
                        ydl_opts['ffmpeg_location'] = ffmpeg_path
                    else:
                        # Fallback para biblioteca
                        ydl_opts['prefer_ffmpeg'] = True
                else:
                    ydl_opts['prefer_ffmpeg'] = True
            except Exception as e:
                logger.warning(f"Erro ao configurar FFmpeg: {e}")
        
        try:
            # Primeiro extrair informações
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                thumbnail = info.get('thumbnail')
                
                # Baixar thumbnail
                thumbnail_data = None
                if thumbnail:
                    thumbnail_data = baixar_thumbnail(thumbnail)
                
                # Baixar áudio
                if not self.deve_cancelar:
                    ydl.download([url])
                    
                    # Caminho do arquivo baixado
                    filename = sanitizar_nome_arquivo(f"{title}.mp3")
                    file_path = os.path.join(caminho, filename)
                    
                    # Extrair artista e aplicar metadados
                    artist, song_title = extrair_artista_do_titulo(title)
                    aplicar_metadados(file_path, song_title, artist, "YouTube Download", thumbnail_data)
                    
                    # Adicionar ao histórico
                    adicionar_ao_historico(url, title, "audio", file_path)
                    
                    # Emitir sinal de sucesso com informações
                    success_info = {
                        'title': title,
                        'format': 'mp3',
                        'path': file_path,
                        'has_metadata': True
                    }
                    self.sinal_sucesso.emit(caminho, success_info)
        except Exception as e:
            error_msg = f"Erro ao baixar áudio: {str(e)}"
            logger.error(error_msg)
            self.sinal_erro.emit(error_msg)
    
    def baixar_video(self, url, caminho, format="mp4", quality="720p"):
        """Baixa vídeo do YouTube."""
        self.deve_cancelar = False
        
        is_valid, msg_or_url = validar_url_youtube(url)
        if not is_valid:
            self.sinal_erro.emit(msg_or_url)
            return
        
        url = msg_or_url  # URL validada
        
        if not os.path.isdir(caminho):
            try:
                os.makedirs(caminho, exist_ok=True)
            except Exception as e:
                error_msg = f"Não foi possível criar a pasta: {str(e)}"
                logger.error(error_msg)
                self.sinal_erro.emit(error_msg)
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
            'progress_hooks': [self.gancho],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Language': 'pt-BR,pt;q=0.9'
            }
        }
        
        # Configurar FFmpeg se disponível
        if configurar_ffmpeg():
            try:
                import ffmpeg
                # Para executáveis compilados, usar path absoluto
                if getattr(sys, 'frozen', False):
                    base_path = os.path.dirname(sys.executable)
                    ffmpeg_path = os.path.join(base_path, '_internal', 'ffmpeg', 'bin', 'ffmpeg.exe')
                    if os.path.exists(ffmpeg_path):
                        ydl_opts['ffmpeg_location'] = ffmpeg_path
                    else:
                        # Fallback para biblioteca
                        ydl_opts['prefer_ffmpeg'] = True
                else:
                    ydl_opts['prefer_ffmpeg'] = True
            except Exception as e:
                logger.warning(f"Erro ao configurar FFmpeg: {e}")
        
        try:
            # Primeiro extrair informações
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Title')
                
                # Baixar vídeo
                if not self.deve_cancelar:
                    ydl.download([url])
                    
                    # Caminho do arquivo baixado
                    filename = sanitizar_nome_arquivo(f"{title}.{format.lower()}")
                    file_path = os.path.join(caminho, filename)
                    
                    # Adicionar ao histórico
                    adicionar_ao_historico(url, title, "video", file_path)
                    
                    # Emitir sinal de sucesso com informações
                    success_info = {
                        'title': title,
                        'format': format.lower(),
                        'path': file_path,
                        'quality': quality
                    }
                    self.sinal_sucesso.emit(caminho, success_info)
        except Exception as e:
            error_msg = f"Erro ao baixar vídeo: {str(e)}"
            logger.error(error_msg)
            self.sinal_erro.emit(error_msg)

# Função de compatibilidade com a versão anterior
def baixar_audio(url, caminho, progress_callback=None):
    """Função de compatibilidade para versões anteriores."""
    gerenciador = GerenciadorDownload()
    if progress_callback:
        gerenciador.sinal_progresso.connect(
            lambda value, _: progress_callback.emit(value)
        )
    gerenciador.baixar_audio(url, caminho)