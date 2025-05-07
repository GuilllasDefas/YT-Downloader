import os
import requests
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from mutagen.mp3 import MP3
from PIL import Image
import io
from utils import logger

def baixar_thumbnail(thumbnail_url):
    """Baixa a thumbnail do vídeo."""
    try:
        response = requests.get(thumbnail_url, stream=True)
        if response.status_code == 200:
            return response.content
        else:
            logger.warning(f"Não foi possível baixar a thumbnail: HTTP {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Erro ao baixar thumbnail: {str(e)}")
        return None

def aplicar_metadados(mp3_path, title, artist=None, album=None, thumbnail_data=None):
    """Aplica metadados a um arquivo MP3."""
    try:
        # Inicializar tags ID3
        audio = MP3(mp3_path, ID3=ID3)
        
        # Se não houver tags ID3, criar
        try:
            audio.add_tags()
        except:
            pass  # Tags já existem
        
        # Definir título
        if title:
            audio.tags.add(TIT2(encoding=3, text=title))
        
        # Definir artista
        if artist:
            audio.tags.add(TPE1(encoding=3, text=artist))
        
        # Definir álbum
        if album:
            audio.tags.add(TALB(encoding=3, text=album))
        
        # Adicionar thumbnail como capa
        if thumbnail_data:
            try:
                # Processar e otimizar a imagem
                img = Image.open(io.BytesIO(thumbnail_data))
                # Redimensionar se for muito grande
                if max(img.size) > 800:
                    img.thumbnail((800, 800))
                
                # Converter para JPEG
                thumb_io = io.BytesIO()
                img.convert('RGB').save(thumb_io, 'JPEG', quality=90)
                thumb_data = thumb_io.getvalue()
                
                # Adicionar capa
                audio.tags.add(APIC(
                    encoding=3,  # UTF-8
                    mime='image/jpeg',
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=thumb_data
                ))
            except Exception as e:
                logger.error(f"Erro ao processar thumbnail: {str(e)}")
        
        # Salvar alterações
        audio.save()
        logger.info(f"Metadados aplicados com sucesso a {os.path.basename(mp3_path)}")
        return True
    except Exception as e:
        logger.error(f"Erro ao aplicar metadados: {str(e)}")
        return False

def extrair_artista_do_titulo(title):
    """Tenta extrair o artista do título do vídeo."""
    if ' - ' in title:
        parts = title.split(' - ', 1)
        return parts[0].strip(), parts[1].strip()
    return None, title
