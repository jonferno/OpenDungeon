from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTextEdit, QListWidget)
from PyQt5.QtCore import Qt

class LoadingDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))
        self.setModal(True)
        
class ConfirmationDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Action")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(message))
        
        buttons = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

class CharacterDialog(QDialog):
    def __init__(self, character_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Character Details")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        details = QTextEdit()
        details.setReadOnly(True)
        details.setHtml(self.format_character_details(character_data))
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        layout.addWidget(details)
        layout.addWidget(close_btn)
        
    def format_character_details(self, character):
        return f"""
        <h2>{character['name']}</h2>
        <p><b>Race:</b> {character['race']}<br>
        <b>Class:</b> {character['class']}<br>
        <b>Background:</b> {character['background']}<br>
        <b>Alignment:</b> {character['alignment']}</p>
        
        <h3>Ability Scores</h3>
        <p>
        STR: {character['ability_scores']['STR']}<br>
        DEX: {character['ability_scores']['DEX']}<br>
        CON: {character['ability_scores']['CON']}<br>
        INT: {character['ability_scores']['INT']}<br>
        WIS: {character['ability_scores']['WIS']}<br>
        CHA: {character['ability_scores']['CHA']}
        </p>
        
        <h3>Personality</h3>
        <p>{character['personality']}</p>
        
        <h3>Backstory</h3>
        <p>{character['backstory']}</p>
        
        <h3>Equipment</h3>
        <p>{character['equipment']}</p>
        """

class CharacterSelectDialog(QDialog):
    def __init__(self, game_manager, parent=None):
        super().__init__(parent)
        self.game_manager = game_manager
        self.selected_character = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Load Character")
        layout = QVBoxLayout(self)
        
        self.char_list = QListWidget()
        for filename in self.game_manager.list_saved_characters():
            name = filename.replace('.json', '').replace('_', ' ').title()
            self.char_list.addItem(name)
            
        load_btn = QPushButton("Load Selected")
        load_btn.clicked.connect(self.load_selected)
        
        layout.addWidget(QLabel("Select a character to load:"))
        layout.addWidget(self.char_list)
        layout.addWidget(load_btn)
        
    def load_selected(self):
        if not self.char_list.currentItem():
            return
        
        name = self.char_list.currentItem().text()
        filename = f"{name.lower().replace(' ', '_')}.json"
        self.selected_character = self.game_manager.load_character(filename)
        if self.selected_character:
            self.accept()
