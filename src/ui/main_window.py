from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar, 
                            QMessageBox, QComboBox, QTabWidget, QAction)
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
import os
import subprocess
import platform

from src.core.downloader import GerenciadorDownload
from src.config.config import carregar_config, salvar_config, get_app_version
from src.utils.helpers import verificar_dependencias, logger, validar_url_youtube, get_resource_path
from src.services.updater import AutoUpdater
from src.ui.widgets.download_thread import ThreadDownload
from src.ui.dialogs.config_dialog import DialogoConfiguracoes
from src.ui.dialogs.history_dialog import DialogoHistorico


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
        version = get_app_version()
        self.setWindowTitle(f"YouTube Downloader v{version}")
        self.aplicar_tema(self.dados_config.get("theme", "dark"))
        self.resize(600, 300)
        
        # Inicializar updater
        self.updater = AutoUpdater()
        
        # Criar menu e widgets
        self.criar_menu()
        self.criar_widgets()
    
    def carregar_icone_aplicacao(self):
        """Carrega o ícone do aplicativo independente do ambiente de execução."""
        # Possíveis nomes de arquivo de ícone
        nome_icone = 'logo.ico'
        
        # Tentar na raiz
        caminho_icone = get_resource_path(nome_icone)
        if os.path.exists(caminho_icone):
            logger.info(f"Ícone encontrado: {caminho_icone}")
            self.setWindowIcon(QtGui.QIcon(caminho_icone))
            return
            
        # Tentar na pasta resources
        caminho_icone = get_resource_path(f"resources/{nome_icone}")
        if os.path.exists(caminho_icone):
            logger.info(f"Ícone encontrado: {caminho_icone}")
            self.setWindowIcon(QtGui.QIcon(caminho_icone))
            return
        
        # Se ainda não encontrou, procurar em locais específicos do sistema
        if os.path.exists("logo.ico"):
            self.setWindowIcon(QtGui.QIcon("logo.ico"))
            return
            
        # Caso o ícone não seja encontrado
        logger.warning("Nenhum ícone encontrado para o aplicativo")
    
    def aplicar_tema(self, tema):
        try:
            tema_arquivo = "dark.qss" if tema == "dark" else "light.qss"
            caminho_estilo = get_resource_path(f"resources/styles/{tema_arquivo}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(caminho_estilo):
                logger.error(f"Arquivo de estilo não encontrado: {caminho_estilo}")
                return
                
            # Carregar o estilo do arquivo
            with open(caminho_estilo, "r", encoding="utf-8") as f:
                estilo = f.read()
                self.setStyleSheet(estilo)
            
            # Salvar preferência
            self.dados_config["theme"] = tema
            salvar_config(self.dados_config)
        
        except Exception as e:
            logger.error(f"Erro ao aplicar tema: {str(e)}")
    
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
        
        acao_verificar_atualizacao = QAction('Verificar Atualização', self)
        acao_verificar_atualizacao.triggered.connect(self.verificar_atualizacao_manual)
        menu_ajuda.addAction(acao_verificar_atualizacao)
        
        menu_ajuda.addSeparator()
        
        acao_sobre = QAction('Sobre', self)
        acao_sobre.triggered.connect(self.mostrar_sobre)
        menu_ajuda.addAction(acao_sobre)
        
        acao_verificar_dependencias = QAction('Verificar Dependências', self)
        acao_verificar_dependencias.triggered.connect(self.verificar_dependencias)
        menu_ajuda.addAction(acao_verificar_dependencias)
    
    def abrir_pasta(self, caminho):
        """Abre a pasta no explorador de arquivos do sistema."""
        if not os.path.exists(caminho):
            QMessageBox.warning(self, "Pasta não encontrada", f"A pasta não existe:\n{caminho}")
            return
        
        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(caminho)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", caminho])
            else:  # Linux
                subprocess.run(["xdg-open", caminho])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir a pasta:\n{str(e)}")
    
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
        
        self.botao_abrir_pasta = QPushButton("Abrir Pasta")
        self.botao_abrir_pasta.clicked.connect(lambda: self.abrir_pasta(self.entrada_arquivo.text()))
        layout_destino.addWidget(self.botao_abrir_pasta)
        
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
        
        self.botao_abrir_pasta_video = QPushButton("Abrir Pasta")
        self.botao_abrir_pasta_video.clicked.connect(lambda: self.abrir_pasta(self.entrada_arquivo_video.text()))
        layout_destino_video.addWidget(self.botao_abrir_pasta_video)
        
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
        version = get_app_version()
        QMessageBox.about(
            self, 
            "Sobre YouTube Downloader",
            f"YouTube Downloader v{version}\n\n"
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
    
    def verificar_atualizacao_manual(self):
        """Verifica atualização manualmente (acionado pelo menu)."""
        self.updater.verificar_e_notificar(parent=self, silencioso=False)
    
    def verificar_atualizacao_automatica(self):
        """Verifica atualização automaticamente (silencioso)."""
        try:
            self.updater.verificar_e_notificar(parent=self, silencioso=True)
        except Exception as e:
            logger.error(f"Erro na verificação automática de atualização: {e}")
    
    def showEvent(self, event):
        """Evento chamado quando a janela é exibida."""
        super().showEvent(event)
        
        # Verificar atualização automaticamente quando a janela abre
        # Fazer isso em um timer para não bloquear a interface
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(2000, self.verificar_atualizacao_automatica)  # 2 segundos após abrir