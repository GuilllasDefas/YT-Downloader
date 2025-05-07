import json
import os
from datetime import datetime
from utils import logger

ARQUIVO_HISTORICO = "download_history.json"

def carregar_historico():
    """Carrega o histórico de downloads."""
    try:
        if os.path.exists(ARQUIVO_HISTORICO):
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"downloads": []}
    except Exception as e:
        logger.error(f"Erro ao carregar histórico: {str(e)}")
        return {"downloads": []}

def salvar_historico(history_data):
    """Salva o histórico de downloads."""
    try:
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar histórico: {str(e)}")
        return False

def adicionar_ao_historico(url, title, format_type, file_path):
    """Adiciona um download ao histórico."""
    historico = carregar_historico()
    
    # Criar novo registro
    novo_registro = {
        "url": url,
        "title": title,
        "format": format_type,  # "audio" ou "video"
        "path": file_path,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Adicionar ao início da lista (mais recente primeiro)
    historico["downloads"].insert(0, novo_registro)
    
    # Limitar o histórico a 100 itens
    if len(historico["downloads"]) > 100:
        historico["downloads"] = historico["downloads"][:100]
    
    # Salvar histórico atualizado
    return salvar_historico(historico)

def limpar_historico():
    """Limpa todo o histórico de downloads."""
    return salvar_historico({"downloads": []})

def obter_downloads_recentes(limit=10):
    """Retorna os downloads mais recentes."""
    historico = carregar_historico()
    return historico["downloads"][:limit]
