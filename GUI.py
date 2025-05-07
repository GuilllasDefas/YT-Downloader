from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar, 
                            QMessageBox, QComboBox, QTabWidget, QRadioButton, 
                            QGroupBox, QCheckBox, QListWidget, QMenuBar, QMenu, 
                            QAction, QDialog, QGridLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtGui
import os
import sys
from functools import partial

from downloader import GerenciadorDownload
from config import carregar_config, salvar_config, atualizar_valor_config
from history import obter_downloads_recentes, limpar_historico
from utils import verificar_dependencias, logger, validar_url_youtube
from metadata import extrair_artista_do_titulo

class ThreadDownload(QThread):
    sinal_progresso = pyqtSignal(int, dict)
    sinal_erro = pyqtSignal(str)
    sinal_sucesso = pyqtSignal(str, dict)
    sinal_info = pyqtSignal(dict)

    def __init__(self, gerenciador_download, url, caminho, is_audio=True, quality="320", video_format="mp4", video_quality="720p"):
        super().__init__()
        self.gerenciador_download = gerenciador_download
        self.url = url
        self.caminho = caminho
        self.is_audio = is_audio
        self.audio_quality = quality
        self.video_format = video_format
        self.video_quality = video_quality
        
        # Conectar sinais do gerenciador
        self.gerenciador_download.sinal_progresso.connect(self.sinal_progresso)
        self.gerenciador_download.sinal_erro.connect(self.sinal_erro)
        self.gerenciador_download.sinal_sucesso.connect(self.sinal_sucesso)
        self.gerenciador_download.sinal_info.connect(self.sinal_info)

    def run(self):
        try:
            if self.is_audio:
                self.gerenciador_download.baixar_audio(self.url, self.caminho, self.audio_quality)
            else:
                self.gerenciador_download.baixar_video(self.url, self.caminho, self.video_format, self.video_quality)
        except Exception as e:
            self.sinal_erro.emit(str(e))
    
    def cancelar(self):
        self.gerenciador_download.cancelar_download()

class DialogoConfiguracoes(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config = carregar_config()
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(400)
        self.iniciar_ui()
    
    def iniciar_ui(self):
        layout = QVBoxLayout()
        
        # Tema
        grupo_tema = QGroupBox("Tema da Interface")
        layout_tema = QHBoxLayout()
        
        self.tema_escuro = QRadioButton("Escuro")
        self.tema_claro = QRadioButton("Claro")
        
        if self.config["theme"] == "dark":
            self.tema_escuro.setChecked(True)
        else:
            self.tema_claro.setChecked(True)
        
        layout_tema.addWidget(self.tema_escuro)
        layout_tema.addWidget(self.tema_claro)
        grupo_tema.setLayout(layout_tema)
        layout.addWidget(grupo_tema)
        
        # Qualidade de Áudio
        grupo_audio = QGroupBox("Qualidade de Áudio")
        layout_audio = QGridLayout()
        
        layout_audio.addWidget(QLabel("Qualidade MP3:"), 0, 0)
        self.qualidade_audio = QComboBox()
        self.qualidade_audio.addItems(["128 kbps", "192 kbps", "320 kbps"])
        
        # Definir qualidade padrão
        mapa_qualidade = {"128": 0, "192": 1, "320": 2}
        self.qualidade_audio.setCurrentIndex(mapa_qualidade.get(self.config["audio_quality"], 2))
        
        layout_audio.addWidget(self.qualidade_audio, 0, 1)
        grupo_audio.setLayout(layout_audio)
        layout.addWidget(grupo_audio)
        
        # Opções de Vídeo
        grupo_video = QGroupBox("Opções de Vídeo")
        layout_video = QGridLayout()
        
        layout_video.addWidget(QLabel("Formato:"), 0, 0)
        self.formato_video = QComboBox()
        self.formato_video.addItems(["MP4", "MKV"])
        
        indice_formato = 0 if self.config["video_format"].lower() == "mp4" else 1
        self.formato_video.setCurrentIndex(indice_formato)
        
        layout_video.addWidget(self.formato_video, 0, 1)
        
        layout_video.addWidget(QLabel("Qualidade Padrão:"), 1, 0)
        self.qualidade_video = QComboBox()
        self.qualidade_video.addItems(["360p", "480p", "720p", "1080p"])
        
        indice_qualidade = {"360p": 0, "480p": 1, "720p": 2, "1080p": 3}
        self.qualidade_video.setCurrentIndex(indice_qualidade.get(self.config["video_quality"], 2))
        
        layout_video.addWidget(self.qualidade_video, 1, 1)
        grupo_video.setLayout(layout_video)
        layout.addWidget(grupo_video)
        
        # Metadados
        grupo_metadados = QGroupBox("Metadados")
        layout_metadados = QVBoxLayout()
        
        self.aplicar_metadados = QCheckBox("Aplicar metadados automaticamente")
        self.aplicar_metadados.setChecked(self.config.get("apply_metadata", True))
        
        self.salvar_thumbnails = QCheckBox("Salvar thumbnails como capas de álbum")
        self.salvar_thumbnails.setChecked(self.config.get("save_thumbnails", True))
        
        layout_metadados.addWidget(self.aplicar_metadados)
        layout_metadados.addWidget(self.salvar_thumbnails)
        grupo_metadados.setLayout(layout_metadados)
        layout.addWidget(grupo_metadados)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        self.botao_salvar = QPushButton("Salvar")
        self.botao_salvar.clicked.connect(self.salvar_configuracoes)
        
        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_cancelar.clicked.connect(self.reject)
        
        layout_botoes.addWidget(self.botao_cancelar)
        layout_botoes.addWidget(self.botao_salvar)
        
        layout.addLayout(layout_botoes)
        self.setLayout(layout)
    
    def salvar_configuracoes(self):
        # Tema
        novo_tema = "dark" if self.tema_escuro.isChecked() else "light"
        
        # Qualidade de áudio
        mapa_qualidade = {0: "128", 1: "192", 2: "320"}
        nova_qualidade_audio = mapa_qualidade[self.qualidade_audio.currentIndex()]
        
        # Formato de vídeo
        novo_formato_video = "mp4" if self.formato_video.currentIndex() == 0 else "mkv"
        
        # Qualidade de vídeo
        mapa_qualidade = {0: "360p", 1: "480p", 2: "720p", 3: "1080p"}
        nova_qualidade_video = mapa_qualidade[self.qualidade_video.currentIndex()]
        
        # Atualizar configurações
        self.config["theme"] = novo_tema
        self.config["audio_quality"] = nova_qualidade_audio
        self.config["video_format"] = novo_formato_video
        self.config["video_quality"] = nova_qualidade_video
        self.config["apply_metadata"] = self.aplicar_metadados.isChecked()
        self.config["save_thumbnails"] = self.salvar_thumbnails.isChecked()
        
        # Salvar
        salvar_config(self.config)
        
        # Aplicar tema
        if self.parent:
            self.parent.aplicar_tema(novo_tema)
        
        self.accept()

class DialogoHistorico(QDialog):
    url_selecionada = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Downloads")
        self.setMinimumSize(600, 400)
        self.iniciar_ui()
    
    def iniciar_ui(self):
        layout = QVBoxLayout()
        
        # Tabela de histórico
        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(4)
        self.tabela_historico.setHorizontalHeaderLabels(["Título", "Formato", "Data", "Caminho"])
        self.tabela_historico.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_historico.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_historico.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_historico.doubleClicked.connect(self.ao_clicar_item_duplo)
        
        layout.addWidget(self.tabela_historico)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        self.botao_limpar = QPushButton("Limpar Histórico")
        self.botao_limpar.clicked.connect(self.limpar_historico)
        
        self.botao_usar_url = QPushButton("Usar URL Selecionada")
        self.botao_usar_url.clicked.connect(self.usar_url_selecionada)
        
        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.clicked.connect(self.reject)
        
        layout_botoes.addWidget(self.botao_limpar)
        layout_botoes.addWidget(self.botao_usar_url)
        layout_botoes.addWidget(self.botao_fechar)
        
        layout.addLayout(layout_botoes)
        self.setLayout(layout)
        
        # Carregar histórico
        self.carregar_historico()
    
    def carregar_historico(self):
        downloads = obter_downloads_recentes(100)
        self.tabela_historico.setRowCount(len(downloads))
        
        for i, download in enumerate(downloads):
            self.tabela_historico.setItem(i, 0, QTableWidgetItem(download['title']))
            self.tabela_historico.setItem(i, 1, QTableWidgetItem(download['format']))
            self.tabela_historico.setItem(i, 2, QTableWidgetItem(download['date']))
            self.tabela_historico.setItem(i, 3, QTableWidgetItem(download['path']))
            
            # Armazenar URL como dados de item
            self.tabela_historico.item(i, 0).setData(Qt.UserRole, download['url'])
    
    def ao_clicar_item_duplo(self, index):
        row = index.row()
        url = self.tabela_historico.item(row, 0).data(Qt.UserRole)
        self.url_selecionada.emit(url)
        self.accept()
    
    def usar_url_selecionada(self):
        linhas_selecionadas = self.tabela_historico.selectionModel().selectedRows()
        if linhas_selecionadas:
            row = linhas_selecionadas[0].row()
            url = self.tabela_historico.item(row, 0).data(Qt.UserRole)
            self.url_selecionada.emit(url)
            self.accept()
    
    def limpar_historico(self):
        resposta = QMessageBox.question(self, 'Confirmação', 
                                     "Tem certeza que deseja limpar todo o histórico?",
                                     QMessageBox.Yes | QMessageBox.No, 
                                     QMessageBox.No)
        
        if resposta == QMessageBox.Yes:
            limpar_historico()
            self.tabela_historico.setRowCount(0)

class JanelaDownloaderYouTube(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Verificar dependências
        missing_deps = verificar_dependencias()
        if missing_deps:
            QMessageBox.critical(
                self, 
                "Dependências Ausentes",
                f"As seguintes dependências estão faltando:\n{', '.join(missing_deps)}\n\n"
                "Por favor, instale-as antes de continuar."
            )
        
        self.gerenciador_download = GerenciadorDownload()
        self.thread = None
        self.dados_config = carregar_config()
        self.caminho_padrao = self.dados_config.get("default_path", "C:/downloads")
        
        # Configurar interface - com busca robusta de ícone
        self.carregar_icone_aplicacao()
        self.setWindowTitle("YouTube Downloader")
        self.aplicar_tema(self.dados_config.get("theme", "dark"))
        self.resize(600, 300)
        
        # Criar menu e widgets
        self.criar_menu()
        self.criar_widgets()
    
    def carregar_icone_aplicacao(self):
        """Tenta carregar o ícone do aplicativo de vários locais possíveis."""
        # Lista de possíveis nomes de arquivo de ícone
        nomes_icone = ['logo.ico', 'Youtube.ico', 'youtube.ico', 'icon.ico']
        
        # Lista de possíveis diretórios onde o ícone pode estar
        diretorios_possiveis = [
            os.path.dirname(os.path.abspath(__file__)),  # Diretório atual
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # Diretório pai
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources'),  # Pasta de recursos
            os.path.join(os.getenv('APPDATA', ''), 'YouTubeDownloader')  # AppData para Windows
        ]
        
        # Tentar cada combinação
        for dir_path in diretorios_possiveis:
            for nome_icone in nomes_icone:
                caminho_icone = os.path.join(dir_path, nome_icone)
                if os.path.exists(caminho_icone):
                    logger.info(f"Ícone encontrado: {caminho_icone}")
                    self.setWindowIcon(QtGui.QIcon(caminho_icone))
                    return
        
        # Caso o ícone não seja encontrado, usar um ícone padrão ou nenhum
        logger.warning("Nenhum ícone encontrado para o aplicativo")
    
    def aplicar_tema(self, tema):
        if tema == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog, QTabWidget, QWidget {
                    background-color: #23272A;
                    color: #f1f1f1;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QLineEdit, QComboBox, QListWidget, QTableWidget {
                    background-color: #2C2F33;
                    color: #f1f1f1;
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #8E0000;
                    color: #fff;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c00;
                }
                QPushButton:disabled {
                    background-color: #555;
                    color: #888;
                }
                QProgressBar {
                    border: 1px solid #444;
                    border-radius: 5px;
                    text-align: center;
                    background: #2C2F33;
                    color: #f1f1f1;
                }
                QProgressBar::chunk {
                    background-color: #FF0D0D;
                }
                QGroupBox {
                    border: 1px solid #444;
                    margin-top: 12px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QRadioButton, QCheckBox {
                    color: #e0e0e0;
                }
                QMenuBar {
                    background-color: #2C2F33;
                    color: #f1f1f1;
                }
                QMenuBar::item:selected {
                    background: #c00;
                }
                QMenu {
                    background-color: #2C2F33;
                    color: #f1f1f1;
                }
                QMenu::item:selected {
                    background: #c00;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                }
                QTabBar::tab {
                    background: #2C2F33;
                    color: #f1f1f1;
                    padding: 8px 12px;
                    border: 1px solid #444;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #c00;
                }
                QHeaderView::section {
                    background-color: #2C2F33;
                    color: #f1f1f1;
                    padding: 4px;
                    border: 1px solid #444;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QDialog, QTabWidget, QWidget {
                    background-color: #f5f5f5;
                    color: #333;
                }
                QLabel {
                    color: #333;
                }
                QLineEdit, QComboBox, QListWidget, QTableWidget {
                    background-color: #fff;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #4a86e8;
                    color: #fff;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a76d8;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                    color: #666;
                }
                QProgressBar {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    text-align: center;
                    background: #fff;
                    color: #333;
                }
                QProgressBar::chunk {
                    background-color: #4a86e8;
                }
                QGroupBox {
                    border: 1px solid #ccc;
                    margin-top: 12px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QRadioButton, QCheckBox {
                    color: #333;
                }
                QMenuBar {
                    background-color: #f5f5f5;
                    color: #333;
                }
                QMenuBar::item:selected {
                    background: #4a86e8;
                    color: #fff;
                }
                QMenu {
                    background-color: #f5f5f5;
                    color: #333;
                }
                QMenu::item:selected {
                    background: #4a86e8;
                    color: #fff;
                }
                QTabWidget::pane {
                    border: 1px solid #ccc;
                }
                QTabBar::tab {
                    background: #e8e8e8;
                    color: #333;
                    padding: 8px 12px;
                    border: 1px solid #ccc;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background: #4a86e8;
                    color: #fff;
                }
                QHeaderView::section {
                    background-color: #e8e8e8;
                    color: #333;
                    padding: 4px;
                    border: 1px solid #ccc;
                }
            """)
        
        # Salvar preferência
        self.dados_config["theme"] = tema
        salvar_config(self.dados_config)
    
    def criar_menu(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        menu_arquivo = menubar.addMenu('Arquivo')
        
        acao_historico = QAction('Histórico de Downloads', self)
        acao_historico.triggered.connect(self.mostrar_historico)
        menu_arquivo.addAction(acao_historico)
        
        menu_arquivo.addSeparator()
        
        acao_sair = QAction('Sair', self)
        acao_sair.triggered.connect(self.close)
        menu_arquivo.addAction(acao_sair)
        
        # Menu Configurações
        menu_configuracoes = menubar.addMenu('Configurações')
        
        acao_preferencias = QAction('Preferências', self)
        acao_preferencias.triggered.connect(self.mostrar_configuracoes)
        menu_configuracoes.addAction(acao_preferencias)
        
        # Menu Ajuda
        menu_ajuda = menubar.addMenu('Ajuda')
        
        acao_sobre = QAction('Sobre', self)
        acao_sobre.triggered.connect(self.mostrar_sobre)
        menu_ajuda.addAction(acao_sobre)
        
        acao_verificar_dependencias = QAction('Verificar Dependências', self)
        acao_verificar_dependencias.triggered.connect(self.verificar_dependencias)
        menu_ajuda.addAction(acao_verificar_dependencias)
    
    def criar_widgets(self):
        widget_central = QWidget()
        layout_principal = QVBoxLayout(widget_central)
        
        # Área principal com abas
        self.abas = QTabWidget()
        
        # Aba de Áudio
        aba_audio = QWidget()
        layout_audio = QVBoxLayout(aba_audio)
        
        # Descrição
        self.label_descricao = QLabel("Baixe e converta vídeos do YouTube em MP3")
        layout_audio.addWidget(self.label_descricao)
        
        # URL
        layout_url = QHBoxLayout()
        
        self.label_url = QLabel("Cole o link do vídeo:")
        layout_url.addWidget(self.label_url)
        
        self.entrada_url = QLineEdit()
        layout_url.addWidget(self.entrada_url)
        
        layout_audio.addLayout(layout_url)
        
        # Pasta destino
        layout_destino = QHBoxLayout()
        
        self.label_arquivo_desc = QLabel("Pasta destino:")
        layout_destino.addWidget(self.label_arquivo_desc)
        
        self.entrada_arquivo = QLineEdit(self.caminho_padrao)
        layout_destino.addWidget(self.entrada_arquivo)
        
        self.botao_pasta = QPushButton("Escolher")
        self.botao_pasta.clicked.connect(self.escolher_pasta)
        layout_destino.addWidget(self.botao_pasta)
        
        layout_audio.addLayout(layout_destino)
        
        # Qualidade do áudio
        layout_qualidade = QHBoxLayout()
        
        self.label_qualidade = QLabel("Qualidade:")
        layout_qualidade.addWidget(self.label_qualidade)
        
        self.combo_qualidade = QComboBox()
        self.combo_qualidade.addItems(["128 kbps", "192 kbps", "320 kbps"])
        
        # Definir qualidade padrão
        mapa_qualidade = {"128": 0, "192": 1, "320": 2}
        self.combo_qualidade.setCurrentIndex(mapa_qualidade.get(self.dados_config.get("audio_quality", "320"), 2))
        
        layout_qualidade.addWidget(self.combo_qualidade)
        layout_qualidade.addStretch()
        
        layout_audio.addLayout(layout_qualidade)
        
        # Botões de ação
        layout_botoes = QHBoxLayout()
        
        self.botao_baixar = QPushButton("Baixar MP3")
        self.botao_baixar.clicked.connect(self.iniciar_download_audio)
        layout_botoes.addWidget(self.botao_baixar)
        
        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_cancelar.clicked.connect(self.cancelar_download)
        self.botao_cancelar.setEnabled(False)
        layout_botoes.addWidget(self.botao_cancelar)
        
        layout_audio.addLayout(layout_botoes)
        
        # Aba de Vídeo
        aba_video = QWidget()
        layout_video = QVBoxLayout(aba_video)
        
        # Descrição
        layout_video.addWidget(QLabel("Baixe vídeos do YouTube em MP4 ou MKV"))

        # URL
        layout_url_video = QHBoxLayout()
        
        layout_url_video.addWidget(QLabel("Cole o link do vídeo:"))
        
        self.entrada_url_video = QLineEdit()
        layout_url_video.addWidget(self.entrada_url_video)
        
        layout_video.addLayout(layout_url_video)
        
        # Pasta destino para vídeos
        layout_destino_video = QHBoxLayout()
        
        layout_destino_video.addWidget(QLabel("Pasta destino:"))
        
        self.entrada_arquivo_video = QLineEdit(self.caminho_padrao)
        layout_destino_video.addWidget(self.entrada_arquivo_video)
        
        self.botao_pasta_video = QPushButton("Escolher")
        self.botao_pasta_video.clicked.connect(self.escolher_pasta_video)
        layout_destino_video.addWidget(self.botao_pasta_video)
        
        layout_video.addLayout(layout_destino_video)
        
        # Opções de vídeo
        layout_opcoes_video = QHBoxLayout()
        
        # Formato
        layout_formato = QVBoxLayout()
        layout_formato.addWidget(QLabel("Formato:"))
        
        self.combo_formato = QComboBox()
        self.combo_formato.addItems(["MP4", "MKV"])
        
        indice_formato = 0 if self.dados_config.get("video_format", "mp4").lower() == "mp4" else 1
        self.combo_formato.setCurrentIndex(indice_formato)
        
        layout_formato.addWidget(self.combo_formato)
        layout_opcoes_video.addLayout(layout_formato)
        
        # Qualidade
        layout_qualidade_video = QVBoxLayout()
        layout_qualidade_video.addWidget(QLabel("Qualidade:"))
        
        self.combo_qualidade_video = QComboBox()
        self.combo_qualidade_video.addItems(["360p", "480p", "720p", "1080p"])
        
        indice_qualidade = {"360p": 0, "480p": 1, "720p": 2, "1080p": 3}
        self.combo_qualidade_video.setCurrentIndex(indice_qualidade.get(self.dados_config.get("video_quality", "720p"), 2))
        
        layout_qualidade_video.addWidget(self.combo_qualidade_video)
        layout_opcoes_video.addLayout(layout_qualidade_video)
        
        layout_opcoes_video.addStretch()
        
        layout_video.addLayout(layout_opcoes_video)
        
        # Botões para vídeo
        layout_botoes_video = QHBoxLayout()
        
        self.botao_baixar_video = QPushButton("Baixar Vídeo")
        self.botao_baixar_video.clicked.connect(self.iniciar_download_video)
        layout_botoes_video.addWidget(self.botao_baixar_video)
        
        self.botao_cancelar_video = QPushButton("Cancelar")
        self.botao_cancelar_video.clicked.connect(self.cancelar_download)
        self.botao_cancelar_video.setEnabled(False)
        layout_botoes_video.addWidget(self.botao_cancelar_video)
        
        layout_video.addLayout(layout_botoes_video)
        
        # Adicionar abas
        self.abas.addTab(aba_audio, "Áudio")
        self.abas.addTab(aba_video, "Vídeo")
        
        layout_principal.addWidget(self.abas)
        
        # Barra de progresso e informações
        layout_progresso = QVBoxLayout()
        
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setValue(0)
        layout_progresso.addWidget(self.barra_progresso)
        
        self.label_status = QLabel("Pronto para download")
        layout_progresso.addWidget(self.label_status)
        
        layout_principal.addLayout(layout_progresso)
        
        self.setCentralWidget(widget_central)
    
    def escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino", self.caminho_padrao)
        if pasta:
            self.entrada_arquivo.setText(pasta)
            self.caminho_padrao = pasta
            self.dados_config["default_path"] = pasta
            salvar_config(self.dados_config)
    
    def escolher_pasta_video(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino", self.caminho_padrao)
        if pasta:
            self.entrada_arquivo_video.setText(pasta)
            self.caminho_padrao = pasta
            self.dados_config["default_path"] = pasta
            salvar_config(self.dados_config)
    
    def iniciar_download_audio(self):
        url = self.entrada_url.text().strip()
        caminho = self.entrada_arquivo.text().strip()
        
        # Qualidade selecionada
        mapa_qualidade = {0: "128", 1: "192", 2: "320"}
        qualidade = mapa_qualidade[self.combo_qualidade.currentIndex()]
        
        if not self.validar_entrada(url, caminho):
            return
        
        self.dados_config["default_path"] = caminho
        self.dados_config["audio_quality"] = qualidade
        salvar_config(self.dados_config)
        
        self.iniciar_download(url, caminho, True, qualidade)
    
    def iniciar_download_video(self):
        url = self.entrada_url_video.text().strip()
        caminho = self.entrada_arquivo_video.text().strip()
        
        # Formato e qualidade selecionados
        formato_video = "mp4" if self.combo_formato.currentIndex() == 0 else "mkv"
        mapa_qualidade = {0: "360p", 1: "480p", 2: "720p", 3: "1080p"}
        qualidade_video = mapa_qualidade[self.combo_qualidade_video.currentIndex()]
        
        if not self.validar_entrada(url, caminho):
            return
        
        self.dados_config["default_path"] = caminho
        self.dados_config["video_format"] = formato_video
        self.dados_config["video_quality"] = qualidade_video
        salvar_config(self.dados_config)
        
        self.iniciar_download(url, caminho, False, None, formato_video, qualidade_video)
    
    def validar_entrada(self, url, caminho):
        is_valid, msg = validar_url_youtube(url)
        if not is_valid:
            QMessageBox.warning(self, "Atenção", msg)
            return False
        
        if not caminho:
            QMessageBox.warning(self, "Atenção", "Por favor, selecione a pasta de destino.")
            return False
        
        return True
    
    def iniciar_download(self, url, caminho, is_audio=True, audio_quality=None, video_format=None, video_quality=None):
        self.botao_baixar.setEnabled(False)
        self.botao_baixar_video.setEnabled(False)
        self.botao_cancelar.setEnabled(True)
        self.botao_cancelar_video.setEnabled(True)
        
        self.label_status.setText("Iniciando download...")
        self.barra_progresso.setValue(0)
        
        self.thread = ThreadDownload(
            self.gerenciador_download, url, caminho, is_audio, 
            audio_quality, video_format, video_quality
        )
        
        self.thread.sinal_progresso.connect(self.atualizar_progresso)
        self.thread.sinal_erro.connect(self.erro_download)
        self.thread.sinal_sucesso.connect(self.sucesso_download)
        self.thread.sinal_info.connect(self.mostrar_info)
        
        self.thread.start()
    
    def cancelar_download(self):
        if self.thread and self.thread.isRunning():
            self.label_status.setText("Cancelando download...")
            self.thread.cancelar()
    
    def atualizar_progresso(self, value, info):
        self.barra_progresso.setValue(value)
        
        # Mostrar informações detalhadas
        texto_status = f"Progresso: {value}% | "
        if 'speed' in info:
            texto_status += f"Velocidade: {info['speed']} | "
        if 'eta' in info:
            texto_status += f"Tempo restante: {info['eta']}"
            
        self.label_status.setText(texto_status)
    
    def erro_download(self, mensagem_erro):
        QMessageBox.critical(self, "Erro", f"Falha na operação:\n{mensagem_erro}")
        self.resetar_ui()
    
    def sucesso_download(self, destino, info):
        titulo = info.get('title', 'Arquivo')
        tipo_formato = info.get('format', 'desconhecido')
        
        QMessageBox.information(
            self, "Sucesso", 
            f"Download concluído!\n\nTítulo: {titulo}\nFormato: {tipo_formato.upper()}\nSalvo em:\n{destino}"
        )
        
        self.resetar_ui()
        
        # Limpar campo de URL para facilitar um novo download
        if self.abas.currentIndex() == 0:
            self.entrada_url.clear()
        else:
            self.entrada_url_video.clear()
    
    def mostrar_info(self, info):
        titulo = info.get('title', 'Vídeo desconhecido')
        self.label_status.setText(f"Preparando download: {titulo}")
    
    def resetar_ui(self):
        self.botao_baixar.setEnabled(True)
        self.botao_baixar_video.setEnabled(True)
        self.botao_cancelar.setEnabled(False)
        self.botao_cancelar_video.setEnabled(False)
        self.barra_progresso.setValue(0)
        self.label_status.setText("Pronto para download")
    
    def mostrar_configuracoes(self):
        dialogo = DialogoConfiguracoes(self)
        dialogo.exec_()
    
    def mostrar_historico(self):
        dialogo = DialogoHistorico(self)
        dialogo.url_selecionada.connect(self.definir_url_do_historico)
        dialogo.exec_()
    
    def definir_url_do_historico(self, url):
        if self.abas.currentIndex() == 0:
            self.entrada_url.setText(url)
        else:
            self.entrada_url_video.setText(url)
    
    def mostrar_sobre(self):
        QMessageBox.about(
            self, 
            "Sobre YouTube Downloader",
            "YouTube Downloader v3.0\n\n"
            "Uma aplicação para download de áudios e vídeos do YouTube.\n\n"
            "Desenvolvido com PyQt5, mutagen e yt-dlp.\n\n"
            "Por Guilherme de Freitas Moreira"
        )
    
    def verificar_dependencias(self):
        missing_deps = verificar_dependencias()
        if missing_deps:
            QMessageBox.warning(
                self, 
                "Dependências Ausentes",
                f"As seguintes dependências estão faltando:\n{', '.join(missing_deps)}\n\n"
                "Por favor, instale-as antes de continuar."
            )
        else:
            QMessageBox.information(
                self,
                "Verificação Concluída",
                "Todas as dependências necessárias estão instaladas corretamente."
            )