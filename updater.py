import requests
import webbrowser
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import Qt
from packaging import version
from config import get_app_version, get_repo_info
from utils import logger

class DialogoAtualizacao(QDialog):
    def __init__(self, release_info, parent=None):
        super().__init__(parent)
        self.release_info = release_info
        self.setWindowTitle("Atualização Disponível")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self.iniciar_ui()
    
    def iniciar_ui(self):
        layout = QVBoxLayout()
        
        # Título
        versao = self.release_info.get('tag_name', 'Desconhecida')
        titulo = QLabel(f"Nova versão {versao} disponível!")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Informações da release
        info_label = QLabel("Novidades desta versão:")
        info_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(info_label)
        
        # Descrição da release
        descricao = QTextEdit()
        descricao.setPlainText(self.release_info.get('body', 'Sem informações disponíveis.'))
        descricao.setReadOnly(True)
        descricao.setMaximumHeight(200)
        layout.addWidget(descricao)
        
        # URL de download
        download_url = self.release_info.get('download_url', '')
        if download_url:
            url_label = QLabel(f"Link de download:\n{download_url}")
            url_label.setWordWrap(True)
            url_label.setStyleSheet("color: blue; margin-top: 10px;")
            layout.addWidget(url_label)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        self.botao_baixar = QPushButton("Baixar Atualização")
        self.botao_baixar.clicked.connect(self.abrir_download)
        
        self.botao_depois = QPushButton("Talvez Depois")
        self.botao_depois.clicked.connect(self.reject)
        
        self.botao_ignorar = QPushButton("Ignorar Esta Versão")
        self.botao_ignorar.clicked.connect(self.ignorar_versao)
        
        layout_botoes.addWidget(self.botao_ignorar)
        layout_botoes.addWidget(self.botao_depois)
        layout_botoes.addWidget(self.botao_baixar)
        
        layout.addLayout(layout_botoes)
        self.setLayout(layout)
    
    def abrir_download(self):
        """Abre o link de download no navegador."""
        download_url = self.release_info.get('download_url', '')
        if download_url:
            webbrowser.open(download_url)
            logger.info(f"Abrindo URL de download: {download_url}")
        self.accept()
    
    def ignorar_versao(self):
        """Marca esta versão para ser ignorada."""
        # TODO: Implementar lógica para ignorar versão
        logger.info(f"Versão {self.release_info.get('tag_name')} ignorada pelo usuário")
        self.reject()

class AutoUpdater:
    def __init__(self, modo_teste=False):
        # Configurações do repositório GitHub
        repo_info = get_repo_info()
        self.repo_owner = repo_info["owner"]
        self.repo_name = repo_info["name"]
        self.debug = True  # Ativar/desativar debug
        self.modo_teste = modo_teste  # Parâmetro para teste
        
        # Obtém a versão atual
        self.current_version = get_app_version()
        if self.debug:
            logger.info(f"DEBUG: Versão atual carregada: {self.current_version}")
    
    def verificar_atualizacao(self):
        """Verifica se tem atualização disponível."""
        # Se estiver em modo de teste, simula uma atualização
        if self.modo_teste:
            if self.debug:
                logger.info("DEBUG: Usando modo de teste - simulando atualização")
            return True, {
                'tag_name': 'v9.9.9',
                'html_url': f'https://github.com/{self.repo_owner}/{self.repo_name}/releases/latest',
                'download_url': f'https://github.com/{self.repo_owner}/{self.repo_name}/releases/latest',
                'body': 'Esta é uma versão de teste simulada para verificar a funcionalidade do updater.'
            }
        
        # Código para verificação real
        try:
            # Pega informações da última release do GitHub
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                release_info = response.json()
                versao_github = release_info['tag_name']
                
                # Remove 'v' se existir e limpa espaços
                versao_nova = versao_github.replace('v', '').strip()
                versao_atual = self.current_version.strip()
                
                if self.debug:
                    logger.info(f"DEBUG: Versão atual: '{versao_atual}'")
                    logger.info(f"DEBUG: Versão no GitHub: '{versao_github}' -> '{versao_nova}'")
                
                # Encontra a URL de download - prioriza .exe, depois .zip
                download_url = None
                
                # Primeiro procura por arquivo .exe (instalador)
                for asset in release_info.get('assets', []):
                    if asset['name'].endswith('.exe') and 'setup' in asset['name'].lower():
                        download_url = asset['browser_download_url']
                        if self.debug:
                            logger.info(f"DEBUG: Encontrado instalador: {asset['name']}")
                        break
                
                # Se não encontrou instalador, procura por .exe normal
                if not download_url:
                    for asset in release_info.get('assets', []):
                        if asset['name'].endswith('.exe'):
                            download_url = asset['browser_download_url']
                            if self.debug:
                                logger.info(f"DEBUG: Encontrado arquivo .exe: {asset['name']}")
                            break
                
                # Se não encontrou .exe, procura por .zip
                if not download_url:
                    for asset in release_info.get('assets', []):
                        if asset['name'].endswith('.zip'):
                            download_url = asset['browser_download_url']
                            if self.debug:
                                logger.info(f"DEBUG: Encontrado arquivo .zip: {asset['name']}")
                            break
                
                # Define a URL de download ou usa a URL da release como fallback
                if download_url:
                    release_info['download_url'] = download_url
                else:
                    release_info['download_url'] = release_info.get('html_url')
                    if self.debug:
                        logger.info("DEBUG: Nenhum arquivo .exe ou .zip encontrado, usando URL da release")
                
                # Compara versões usando packaging
                try:
                    if version.parse(versao_nova) > version.parse(versao_atual):
                        if self.debug:
                            logger.info("DEBUG: Atualização disponível!")
                        return True, release_info
                    else:
                        if self.debug:
                            logger.info("DEBUG: Nenhuma atualização disponível - app está na versão mais recente")
                        return False, None
                except Exception as e:
                    # Se der erro no parse, faz comparação simples
                    if self.debug:
                        logger.warning(f"DEBUG: Erro no parse de versão: {e}")
                    if versao_nova != versao_atual:
                        return True, release_info
                    return False, None
            else:
                if self.debug:
                    logger.error(f"DEBUG: Erro HTTP {response.status_code} ao verificar atualizações")
                return False, None
                
        except Exception as e:
            if self.debug:
                logger.error(f"DEBUG: Erro ao verificar atualização: {e}")
            return False, None
    
    def mostrar_dialogo_atualizacao(self, release_info, parent=None):
        """Mostra o diálogo de atualização usando PyQt5."""
        dialogo = DialogoAtualizacao(release_info, parent)
        return dialogo.exec_()
    
    def verificar_e_notificar(self, parent=None, silencioso=True):
        """Verifica atualizações e notifica o usuário se encontrar."""
        tem_atualizacao, release_info = self.verificar_atualizacao()
        
        if tem_atualizacao:
            self.mostrar_dialogo_atualizacao(release_info, parent)
            return True
        elif not silencioso:
            QMessageBox.information(
                parent,
                "Verificação de Atualização",
                "Você já está usando a versão mais recente!"
            )
        
        return False
