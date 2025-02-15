from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QPushButton, QLineEdit)
from PyQt5.QtCore import Qt

class ModelsTab(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.init_ui()
        self.load_saved_models()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Model filter
        filter_layout = QHBoxLayout()
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("🔍 Filter Models")
        self.filter_input.textChanged.connect(self.filter_models)
        filter_layout.addWidget(self.filter_input)
        
        # DM Model selection
        dm_layout = QVBoxLayout()
        dm_layout.addWidget(QLabel("Dungeon Master Model"))
        self.dm_model_combo = QComboBox()
        self.save_dm_btn = QPushButton("Save DM Model")
        self.save_dm_btn.clicked.connect(self.save_dm_model)
        dm_layout.addWidget(self.dm_model_combo)
        dm_layout.addWidget(self.save_dm_btn)
        
        # NPC Model selection
        npc_layout = QVBoxLayout()
        npc_layout.addWidget(QLabel("NPC Models"))
        self.npc_models = []
        for i in range(3):
            combo = QComboBox()
            self.npc_models.append(combo)
            npc_layout.addWidget(QLabel(f"NPC #{i+1} Model"))
            npc_layout.addWidget(combo)
            
        self.save_npc_btn = QPushButton("Save NPC Models")
        self.save_npc_btn.clicked.connect(self.save_npc_models)
        npc_layout.addWidget(self.save_npc_btn)
        
        # Add all layouts to main layout
        layout.addLayout(filter_layout)
        layout.addLayout(dm_layout)
        layout.addLayout(npc_layout)
        
        self.setLayout(layout)
        self.load_available_models()
        
    def load_available_models(self):
        models = self.game_manager.list_available_models()
        self.dm_model_combo.addItems(models)
        for combo in self.npc_models:
            combo.addItems(models)
            
    def filter_models(self, text):
        # TODO: Implement model filtering
        pass
        
    def load_saved_models(self):
        # Load previously saved models
        dm_model = self.game_manager.get_dm_model()
        if dm_model:
            index = self.dm_model_combo.findText(dm_model)
            if index >= 0:
                self.dm_model_combo.setCurrentIndex(index)
        
        # Load NPC models
        for i, combo in enumerate(self.npc_models):
            model = self.game_manager.get_npc_model(i)
            if model:
                index = combo.findText(model)
                if index >= 0:
                    combo.setCurrentIndex(index)
    
    def save_dm_model(self):
        model = self.dm_model_combo.currentText()
        self.game_manager.save_dm_model(model)
        
    def save_npc_models(self):
        for i, combo in enumerate(self.npc_models):
            model = combo.currentText()
            self.game_manager.save_npc_model(i, model)
