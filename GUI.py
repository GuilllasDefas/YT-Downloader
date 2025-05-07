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

from downloader import DownloadManager
from config import load_config, save_config, update_config_value
from history import get_recent_downloads, clear_history
from utils import check_dependencies, logger, validate_youtube_url
from metadata import extract_artist_from_title

class DownloadThread(QThread):
    progress_signal = pyqtSignal(int, dict)
    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal(str, dict)
    info_signal = pyqtSignal(dict)

    def __init__(self, download_manager, url, caminho, is_audio=True, quality="320", video_format="mp4", video_quality="720p"):
        super().__init__()
        self.download_manager = download_manager
        self.url = url
        self.caminho = caminho
        self.is_audio = is_audio
        self.audio_quality = quality
        self.video_format = video_format
        self.video_quality = video_quality
        
        # Conectar sinais do gerenciador
        self.download_manager.progress_signal.connect(self.progress_signal)
        self.download_manager.error_signal.connect(self.error_signal)
        self.download_manager.success_signal.connect(self.success_signal)
        self.download_manager.info_signal.connect(self.info_signal)

    def run(self):
        try:
            if self.is_audio:
                self.download_manager.download_audio(self.url, self.caminho, self.audio_quality)
            else:
                self.download_manager.download_video(self.url, self.caminho, self.video_format, self.video_quality)
        except Exception as e:
            self.error_signal.emit(str(e))
    
    def cancel(self):
        self.download_manager.cancel_download()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.config = load_config()
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tema
        theme_group = QGroupBox("Tema da Interface")
        theme_layout = QHBoxLayout()
        
        self.theme_dark = QRadioButton("Escuro")
        self.theme_light = QRadioButton("Claro")
        
        if self.config["theme"] == "dark":
            self.theme_dark.setChecked(True)
        else:
            self.theme_light.setChecked(True)
        
        theme_layout.addWidget(self.theme_dark)
        theme_layout.addWidget(self.theme_light)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Qualidade de Áudio
        audio_group = QGroupBox("Qualidade de Áudio")
        audio_layout = QGridLayout()
        
        audio_layout.addWidget(QLabel("Qualidade MP3:"), 0, 0)
        self.audio_quality = QComboBox()
        self.audio_quality.addItems(["128 kbps", "192 kbps", "320 kbps"])
        
        # Definir qualidade padrão
        quality_map = {"128": 0, "192": 1, "320": 2}
        self.audio_quality.setCurrentIndex(quality_map.get(self.config["audio_quality"], 2))
        
        audio_layout.addWidget(self.audio_quality, 0, 1)
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Opções de Vídeo
        video_group = QGroupBox("Opções de Vídeo")
        video_layout = QGridLayout()
        
        video_layout.addWidget(QLabel("Formato:"), 0, 0)
        self.video_format = QComboBox()
        self.video_format.addItems(["MP4", "MKV"])
        
        format_index = 0 if self.config["video_format"].lower() == "mp4" else 1
        self.video_format.setCurrentIndex(format_index)
        
        video_layout.addWidget(self.video_format, 0, 1)
        
        video_layout.addWidget(QLabel("Qualidade Padrão:"), 1, 0)
        self.video_quality = QComboBox()
        self.video_quality.addItems(["360p", "480p", "720p", "1080p"])
        
        quality_index = {"360p": 0, "480p": 1, "720p": 2, "1080p": 3}
        self.video_quality.setCurrentIndex(quality_index.get(self.config["video_quality"], 2))
        
        video_layout.addWidget(self.video_quality, 1, 1)
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # Metadados
        metadata_group = QGroupBox("Metadados")
        metadata_layout = QVBoxLayout()
        
        self.apply_metadata = QCheckBox("Aplicar metadados automaticamente")
        self.apply_metadata.setChecked(self.config.get("apply_metadata", True))
        
        self.save_thumbnails = QCheckBox("Salvar thumbnails como capas de álbum")
        self.save_thumbnails.setChecked(self.config.get("save_thumbnails", True))
        
        metadata_layout.addWidget(self.apply_metadata)
        metadata_layout.addWidget(self.save_thumbnails)
        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def save_settings(self):
        # Tema
        new_theme = "dark" if self.theme_dark.isChecked() else "light"
        
        # Qualidade de áudio
        quality_map = {0: "128", 1: "192", 2: "320"}
        new_audio_quality = quality_map[self.audio_quality.currentIndex()]
        
        # Formato de vídeo
        new_video_format = "mp4" if self.video_format.currentIndex() == 0 else "mkv"
        
        # Qualidade de vídeo
        quality_map = {0: "360p", 1: "480p", 2: "720p", 3: "1080p"}
        new_video_quality = quality_map[self.video_quality.currentIndex()]
        
        # Atualizar configurações
        self.config["theme"] = new_theme
        self.config["audio_quality"] = new_audio_quality
        self.config["video_format"] = new_video_format
        self.config["video_quality"] = new_video_quality
        self.config["apply_metadata"] = self.apply_metadata.isChecked()
        self.config["save_thumbnails"] = self.save_thumbnails.isChecked()
        
        # Salvar
        save_config(self.config)
        
        # Aplicar tema
        if self.parent:
            self.parent.apply_theme(new_theme)
        
        self.accept()

class HistoryDialog(QDialog):
    url_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Histórico de Downloads")
        self.setMinimumSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabela de histórico
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["Título", "Formato", "Data", "Caminho"])
        self.history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.history_table)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Limpar Histórico")
        self.clear_button.clicked.connect(self.clear_history)
        
        self.use_url_button = QPushButton("Usar URL Selecionada")
        self.use_url_button.clicked.connect(self.use_selected_url)
        
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.use_url_button)
        buttons_layout.addWidget(self.close_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Carregar histórico
        self.load_history()
    
    def load_history(self):
        downloads = get_recent_downloads(100)
        self.history_table.setRowCount(len(downloads))
        
        for i, download in enumerate(downloads):
            self.history_table.setItem(i, 0, QTableWidgetItem(download['title']))
            self.history_table.setItem(i, 1, QTableWidgetItem(download['format']))
            self.history_table.setItem(i, 2, QTableWidgetItem(download['date']))
            self.history_table.setItem(i, 3, QTableWidgetItem(download['path']))
            
            # Armazenar URL como dados de item
            self.history_table.item(i, 0).setData(Qt.UserRole, download['url'])
    
    def on_item_double_clicked(self, index):
        row = index.row()
        url = self.history_table.item(row, 0).data(Qt.UserRole)
        self.url_selected.emit(url)
        self.accept()
    
    def use_selected_url(self):
        selected_rows = self.history_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            url = self.history_table.item(row, 0).data(Qt.UserRole)
            self.url_selected.emit(url)
            self.accept()
    
    def clear_history(self):
        reply = QMessageBox.question(self, 'Confirmação', 
                                     "Tem certeza que deseja limpar todo o histórico?",
                                     QMessageBox.Yes | QMessageBox.No, 
                                     QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            clear_history()
            self.history_table.setRowCount(0)

class YouTubeDownloaderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Verificar dependências
        missing_deps = check_dependencies()
        if missing_deps:
            QMessageBox.critical(
                self, 
                "Dependências Ausentes",
                f"As seguintes dependências estão faltando:\n{', '.join(missing_deps)}\n\n"
                "Por favor, instale-as antes de continuar."
            )
        
        self.download_manager = DownloadManager()
        self.thread = None
        self.config_data = load_config()
        self.default_path = self.config_data.get("default_path", "C:/downloads")
        
        # Configurar interface - com busca robusta de ícone
        self.load_application_icon()
        self.setWindowTitle("YouTube Downloader")
        self.apply_theme(self.config_data.get("theme", "dark"))
        self.resize(600, 300)
        
        # Criar menu e widgets
        self.create_menu()
        self.create_widgets()
    
    def load_application_icon(self):
        """Tenta carregar o ícone do aplicativo de vários locais possíveis."""
        # Lista de possíveis nomes de arquivo de ícone
        icon_names = ['logo.ico', 'Youtube.ico', 'youtube.ico', 'icon.ico']
        
        # Lista de possíveis diretórios onde o ícone pode estar
        possible_dirs = [
            os.path.dirname(os.path.abspath(__file__)),  # Diretório atual
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # Diretório pai
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources'),  # Pasta de recursos
            os.path.join(os.getenv('APPDATA', ''), 'YouTubeDownloader')  # AppData para Windows
        ]
        
        # Tentar cada combinação
        for dir_path in possible_dirs:
            for icon_name in icon_names:
                icon_path = os.path.join(dir_path, icon_name)
                if os.path.exists(icon_path):
                    logger.info(f"Ícone encontrado: {icon_path}")
                    self.setWindowIcon(QtGui.QIcon(icon_path))
                    return
        
        # Caso o ícone não seja encontrado, usar um ícone padrão ou nenhum
        logger.warning("Nenhum ícone encontrado para o aplicativo")
    
    def apply_theme(self, theme):
        if theme == "dark":
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
        self.config_data["theme"] = theme
        save_config(self.config_data)
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu('Arquivo')
        
        open_history_action = QAction('Histórico de Downloads', self)
        open_history_action.triggered.connect(self.show_history)
        file_menu.addAction(open_history_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Sair', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Configurações
        settings_menu = menubar.addMenu('Configurações')
        
        preferences_action = QAction('Preferências', self)
        preferences_action.triggered.connect(self.show_settings)
        settings_menu.addAction(preferences_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu('Ajuda')
        
        about_action = QAction('Sobre', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        check_deps_action = QAction('Verificar Dependências', self)
        check_deps_action.triggered.connect(self.check_dependencies)
        help_menu.addAction(check_deps_action)
    
    def create_widgets(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Área principal com abas
        self.tabs = QTabWidget()
        
        # Tab de Áudio
        audio_tab = QWidget()
        audio_layout = QVBoxLayout(audio_tab)
        
        # Descrição
        self.label_description = QLabel("Baixe e converta vídeos do YouTube em MP3")
        #self.label_description.setStyleSheet("font-weight: bold; font-size: 16px;")
        audio_layout.addWidget(self.label_description)
        
        # URL
        url_layout = QHBoxLayout()
        
        self.label_url = QLabel("Cole o link do vídeo:")
        url_layout.addWidget(self.label_url)
        
        self.entry_url = QLineEdit()
        url_layout.addWidget(self.entry_url)
        
        audio_layout.addLayout(url_layout)
        
        # Pasta destino
        dest_layout = QHBoxLayout()
        
        self.label_arquivo_desc = QLabel("Pasta destino:")
        dest_layout.addWidget(self.label_arquivo_desc)
        
        self.entry_arquivo = QLineEdit(self.default_path)
        dest_layout.addWidget(self.entry_arquivo)
        
        self.botao_pasta = QPushButton("Escolher")
        self.botao_pasta.clicked.connect(self.escolher_pasta)
        dest_layout.addWidget(self.botao_pasta)
        
        audio_layout.addLayout(dest_layout)
        
        # Qualidade do áudio
        quality_layout = QHBoxLayout()
        
        self.label_quality = QLabel("Qualidade:")
        quality_layout.addWidget(self.label_quality)
        
        self.combo_quality = QComboBox()
        self.combo_quality.addItems(["128 kbps", "192 kbps", "320 kbps"])
        
        # Definir qualidade padrão
        quality_map = {"128": 0, "192": 1, "320": 2}
        self.combo_quality.setCurrentIndex(quality_map.get(self.config_data.get("audio_quality", "320"), 2))
        
        quality_layout.addWidget(self.combo_quality)
        quality_layout.addStretch()
        
        audio_layout.addLayout(quality_layout)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.botao_baixar = QPushButton("Baixar MP3")
        self.botao_baixar.clicked.connect(self.iniciar_download_audio)
        button_layout.addWidget(self.botao_baixar)
        
        self.botao_cancelar = QPushButton("Cancelar")
        self.botao_cancelar.clicked.connect(self.cancelar_download)
        self.botao_cancelar.setEnabled(False)
        button_layout.addWidget(self.botao_cancelar)
        
        audio_layout.addLayout(button_layout)
        
        # Tab de Vídeo
        video_tab = QWidget()
        video_layout = QVBoxLayout(video_tab)
        
        # Descrição
        video_layout.addWidget(QLabel("Baixe vídeos do YouTube em MP4 ou MKV"))

        # URL
        video_url_layout = QHBoxLayout()
        
        video_url_layout.addWidget(QLabel("Cole o link do vídeo:"))
        
        self.video_entry_url = QLineEdit()
        video_url_layout.addWidget(self.video_entry_url)
        
        video_layout.addLayout(video_url_layout)
        
        # Pasta destino para vídeos
        video_dest_layout = QHBoxLayout()
        
        video_dest_layout.addWidget(QLabel("Pasta destino:"))
        
        self.video_entry_arquivo = QLineEdit(self.default_path)
        video_dest_layout.addWidget(self.video_entry_arquivo)
        
        self.video_botao_pasta = QPushButton("Escolher")
        self.video_botao_pasta.clicked.connect(self.escolher_pasta_video)
        video_dest_layout.addWidget(self.video_botao_pasta)
        
        video_layout.addLayout(video_dest_layout)
        
        # Opções de vídeo
        video_options_layout = QHBoxLayout()
        
        # Formato
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        
        self.combo_format = QComboBox()
        self.combo_format.addItems(["MP4", "MKV"])
        
        format_index = 0 if self.config_data.get("video_format", "mp4").lower() == "mp4" else 1
        self.combo_format.setCurrentIndex(format_index)
        
        format_layout.addWidget(self.combo_format)
        video_options_layout.addLayout(format_layout)
        
        # Qualidade
        video_quality_layout = QVBoxLayout()
        video_quality_layout.addWidget(QLabel("Qualidade:"))
        
        self.combo_video_quality = QComboBox()
        self.combo_video_quality.addItems(["360p", "480p", "720p", "1080p"])
        
        quality_index = {"360p": 0, "480p": 1, "720p": 2, "1080p": 3}
        self.combo_video_quality.setCurrentIndex(quality_index.get(self.config_data.get("video_quality", "720p"), 2))
        
        video_quality_layout.addWidget(self.combo_video_quality)
        video_options_layout.addLayout(video_quality_layout)
        
        video_options_layout.addStretch()
        
        video_layout.addLayout(video_options_layout)
        
        # Botões para vídeo
        video_button_layout = QHBoxLayout()
        
        self.botao_baixar_video = QPushButton("Baixar Vídeo")
        self.botao_baixar_video.clicked.connect(self.iniciar_download_video)
        video_button_layout.addWidget(self.botao_baixar_video)
        
        self.botao_cancelar_video = QPushButton("Cancelar")
        self.botao_cancelar_video.clicked.connect(self.cancelar_download)
        self.botao_cancelar_video.setEnabled(False)
        video_button_layout.addWidget(self.botao_cancelar_video)
        
        video_layout.addLayout(video_button_layout)
        
        # Adicionar abas
        self.tabs.addTab(audio_tab, "Áudio")
        self.tabs.addTab(video_tab, "Vídeo")
        
        main_layout.addWidget(self.tabs)
        
        # Barra de progresso e informações
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.label_status = QLabel("Pronto para download")
        progress_layout.addWidget(self.label_status)
        
        main_layout.addLayout(progress_layout)
        
        self.setCentralWidget(central_widget)
    
    def escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino", self.default_path)
        if pasta:
            self.entry_arquivo.setText(pasta)
            self.default_path = pasta
            self.config_data["default_path"] = pasta
            save_config(self.config_data)
    
    def escolher_pasta_video(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta de destino", self.default_path)
        if pasta:
            self.video_entry_arquivo.setText(pasta)
            self.default_path = pasta
            self.config_data["default_path"] = pasta
            save_config(self.config_data)
    
    def iniciar_download_audio(self):
        url = self.entry_url.text().strip()
        caminho = self.entry_arquivo.text().strip()
        
        # Qualidade selecionada
        quality_map = {0: "128", 1: "192", 2: "320"}
        quality = quality_map[self.combo_quality.currentIndex()]
        
        if not self.validar_entrada(url, caminho):
            return
        
        self.config_data["default_path"] = caminho
        self.config_data["audio_quality"] = quality
        save_config(self.config_data)
        
        self.iniciar_download(url, caminho, True, quality)
    
    def iniciar_download_video(self):
        url = self.video_entry_url.text().strip()
        caminho = self.video_entry_arquivo.text().strip()
        
        # Formato e qualidade selecionados
        video_format = "mp4" if self.combo_format.currentIndex() == 0 else "mkv"
        quality_map = {0: "360p", 1: "480p", 2: "720p", 3: "1080p"}
        video_quality = quality_map[self.combo_video_quality.currentIndex()]
        
        if not self.validar_entrada(url, caminho):
            return
        
        self.config_data["default_path"] = caminho
        self.config_data["video_format"] = video_format
        self.config_data["video_quality"] = video_quality
        save_config(self.config_data)
        
        self.iniciar_download(url, caminho, False, None, video_format, video_quality)
    
    def validar_entrada(self, url, caminho):
        is_valid, msg = validate_youtube_url(url)
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
        self.progress_bar.setValue(0)
        
        self.thread = DownloadThread(
            self.download_manager, url, caminho, is_audio, 
            audio_quality, video_format, video_quality
        )
        
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.error_signal.connect(self.download_error)
        self.thread.success_signal.connect(self.download_success)
        self.thread.info_signal.connect(self.show_info)
        
        self.thread.start()
    
    def cancelar_download(self):
        if self.thread and self.thread.isRunning():
            self.label_status.setText("Cancelando download...")
            self.thread.cancel()
    
    def update_progress(self, value, info):
        self.progress_bar.setValue(value)
        
        # Mostrar informações detalhadas
        status_text = f"Progresso: {value}% | "
        if 'speed' in info:
            status_text += f"Velocidade: {info['speed']} | "
        if 'eta' in info:
            status_text += f"Tempo restante: {info['eta']}"
            
        self.label_status.setText(status_text)
    
    def download_error(self, error_message):
        QMessageBox.critical(self, "Erro", f"Falha na operação:\n{error_message}")
        self.reset_ui()
    
    def download_success(self, destino, info):
        title = info.get('title', 'Arquivo')
        format_type = info.get('format', 'desconhecido')
        
        QMessageBox.information(
            self, "Sucesso", 
            f"Download concluído!\n\nTítulo: {title}\nFormato: {format_type.upper()}\nSalvo em:\n{destino}"
        )
        
        self.reset_ui()
        
        # Limpar campo de URL para facilitar um novo download
        if self.tabs.currentIndex() == 0:
            self.entry_url.clear()
        else:
            self.video_entry_url.clear()
    
    def show_info(self, info):
        title = info.get('title', 'Vídeo desconhecido')
        self.label_status.setText(f"Preparando download: {title}")
    
    def reset_ui(self):
        self.botao_baixar.setEnabled(True)
        self.botao_baixar_video.setEnabled(True)
        self.botao_cancelar.setEnabled(False)
        self.botao_cancelar_video.setEnabled(False)
        self.progress_bar.setValue(0)
        self.label_status.setText("Pronto para download")
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.url_selected.connect(self.set_url_from_history)
        dialog.exec_()
    
    def set_url_from_history(self, url):
        if self.tabs.currentIndex() == 0:
            self.entry_url.setText(url)
        else:
            self.video_entry_url.setText(url)
    
    def show_about(self):
        QMessageBox.about(
            self, 
            "Sobre YouTube Downloader",
            "YouTube Downloader v3.0\n\n"
            "Uma aplicação para download de áudios e vídeos do YouTube.\n\n"
            "Desenvolvido com PyQt5, mutagen e yt-dlp.\n\n"
            "Por Guilherme de Freitas Moreira"
        )
    
    def check_dependencies(self):
        missing_deps = check_dependencies()
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