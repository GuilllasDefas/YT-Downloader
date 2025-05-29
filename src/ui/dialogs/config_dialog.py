from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout,
                            QHBoxLayout, QComboBox,QRadioButton, 
                            QGroupBox, QCheckBox, QDialog, QGridLayout,
                            )

from src.config.config import carregar_config, salvar_config

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