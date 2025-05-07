import json
import os
from datetime import datetime
from utils import logger

HISTORY_FILE = "download_history.json"

def load_history():
    """Carrega o histórico de downloads."""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"downloads": []}
    except Exception as e:
        logger.error(f"Erro ao carregar histórico: {str(e)}")
        return {"downloads": []}

def save_history(history_data):
    """Salva o histórico de downloads."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar histórico: {str(e)}")
        return False

def add_to_history(url, title, format_type, file_path):
    """Adiciona um download ao histórico."""
    history = load_history()
    
    # Criar novo registro
    new_entry = {
        "url": url,
        "title": title,
        "format": format_type,  # "audio" ou "video"
        "path": file_path,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Adicionar ao início da lista (mais recente primeiro)
    history["downloads"].insert(0, new_entry)
    
    # Limitar o histórico a 100 itens
    if len(history["downloads"]) > 100:
        history["downloads"] = history["downloads"][:100]
    
    # Salvar histórico atualizado
    return save_history(history)

def clear_history():
    """Limpa todo o histórico de downloads."""
    return save_history({"downloads": []})

def get_recent_downloads(limit=10):
    """Retorna os downloads mais recentes."""
    history = load_history()
    return history["downloads"][:limit]
