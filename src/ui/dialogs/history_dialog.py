from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QPushButton, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from src.core.history import obter_downloads_recentes, limpar_historico

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