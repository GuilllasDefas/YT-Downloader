import json
import os
from utils import logger

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "default_path": "C:/downloads",
    "audio_quality": "320",  # Opções: "128", "192", "320"
    "theme": "dark",  # Opções: "dark", "light"
    "video_format": "mp4",  # Opções: "mp4", "mkv"
    "video_quality": "720p",  # Opções: "360p", "480p", "720p", "1080p"
    "apply_metadata": True,
    "save_thumbnails": True
}

def load_config():
    """Carrega configurações do arquivo ou retorna padrões."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                
                # Garantir que todas as chaves padrão existam
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                
                return config
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}")
        return DEFAULT_CONFIG.copy()

def save_config(data):
    """Salva configurações no arquivo."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {str(e)}")
        return False

def get_config_value(key, default=None):
    """Recupera um valor específico das configurações."""
    config = load_config()
    return config.get(key, default)

def update_config_value(key, value):
    """Atualiza um valor específico nas configurações."""
    config = load_config()
    config[key] = value
    return save_config(config)

def reset_to_defaults():
    """Redefine configurações para os valores padrão."""
    return save_config(DEFAULT_CONFIG.copy())
