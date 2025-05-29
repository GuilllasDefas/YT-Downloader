from PyQt5.QtCore import QThread, pyqtSignal

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