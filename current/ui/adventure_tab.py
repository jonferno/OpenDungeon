from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QInputDialog, QFrame, 
    QVBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5 import uic
from .play_game_tab import PlayGameTab

class AdventureLogEntry(QFrame):
    def __init__(self, text, entry_type="normal", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(text)
        self.text_area.setMinimumHeight(100)  # Make text areas taller
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        layout.addWidget(self.text_area)
        
        if entry_type == "dm":
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFE0A8;
                    border: none;
                    margin: 5px;
                }
                QTextEdit {
                    color: #203D72;
                    background-color: transparent;
                    border: none;
                    font-family: 'MedievalSharp';
                    font-size: 18px;
                    padding: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #334970;
                    border: none;
                }
                QTextEdit {
                    color: #203D72;
                    background-color: transparent;
                    border: none;
                    font-family: 'Poppins', sans-serif;
                    font-size: 14px;
                }
            """)

class AdventureTab(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.setStyleSheet("""
            QScrollArea {
                background-color: #FFECCC;
                border: none;
                border-radius: 10px;
            }
            QWidget#logWidget {
                background-color: #FFECCC;
            }
        """)
        self.game_manager = game_manager
        
        # Load the UI
        uic.loadUi('current/ui/designer/adventure_tab.ui', self)
        
        # Initialize log layout
        self.log_layout = self.logWidget.layout()
        
        # Connect signals
        self.generatePartyBtn.clicked.connect(self.generate_party)
        self.startAdventureBtn.clicked.connect(self.start_adventure)
        self.resetBtn.clicked.connect(self.reset_game)
        self.savePartyBtn.clicked.connect(self.save_party)
        self.loadPartyBtn.clicked.connect(self.load_party)

    def generate_party(self):
        if not self.game_manager.has_models():
            self.show_error("Please select models first!")
            return
            
        try:
            player_char = self.game_manager.get_player_character()
            if not player_char:
                self.show_error("Please create or load your character first!")
                return
                
            party = self.game_manager.generate_party_with_player(player_char)
            if party:
                for name, info in party.items():
                    self.add_log_entry(f"=== {name} ===\n{info}", "dm")
            else:
                self.show_error("Failed to generate party")
        except Exception as e:
            self.show_error(f"Error generating party: {str(e)}")
    
    def start_adventure(self):
        if not self.game_manager.party:
            self.show_error("Please generate a party first!")
            return
            
        try:
            game_state, intro = self.game_manager.start_new_adventure()
            if game_state and intro:
                # Get reference to PlayGameTab
                play_tab = None
                for i in range(self.parent().parent().count()):
                    tab = self.parent().parent().widget(i)
                    if isinstance(tab, PlayGameTab):
                        play_tab = tab
                        break
                        
                if play_tab:
                    play_tab.add_message(intro, is_dm=True)
                    # Switch to play tab
                    self.parent().parent().setCurrentIndex(2)  # Index of play tab
                else:
                    self.show_error("Could not find Play Game tab!")
            else:
                self.show_error("Failed to start adventure")
        except Exception as e:
            self.show_error(f"Error starting adventure: {str(e)}")
            
    # Remove unused methods that were moved to PlayTab
    def add_log_entry(self, text: str, entry_type: str = "normal"):
        """Format and add a log entry to the adventure log"""
        # If it's a character entry (starts with ===), format it properly
        if text.startswith("==="):
            try:
                # Split name and data
                name_part = text.split("===")[1].strip()
                data_part = text.split("===")[2].strip()
                
                # If data is a dictionary string, parse and format it
                if data_part.startswith("{"):
                    try:
                        char_data = eval(data_part)  # Safely convert string to dict
                        formatted_text = f"=== {name_part} ===\n\n"
                        
                        # Basic Info
                        formatted_text += f"Race: {char_data.get('race', 'Unknown')}\n"
                        formatted_text += f"Class: {char_data.get('class', 'Unknown')}\n"
                        formatted_text += f"Background: {char_data.get('background', 'Unknown')}\n"
                        formatted_text += f"Alignment: {char_data.get('alignment', 'Unknown')}\n"
                        formatted_text += f"HP: {char_data.get('hp', '?')}\n"
                        formatted_text += f"AC: {char_data.get('ac', '?')}\n\n"
                        
                        # Ability Scores
                        formatted_text += "Ability Scores:\n"
                        scores = char_data.get('ability_scores', {})
                        for ability in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
                            formatted_text += f"{ability}: {scores.get(ability, '10')}\n"
                        formatted_text += "\n"
                        
                        # Equipment
                        formatted_text += "Equipment:\n"
                        equipment = char_data.get('equipment', [])
                        if isinstance(equipment, list):
                            for item in equipment:
                                formatted_text += f"- {item}\n"
                        else:
                            formatted_text += f"- {equipment}\n"
                        formatted_text += "\n"
                        
                        # Personality, Background, and Backstory sections
                        if char_data.get('personality'):
                            formatted_text += f"Personality:\n{char_data['personality']}\n\n"
                        if char_data.get('backstory'):
                            formatted_text += f"Backstory:\n{char_data['backstory']}\n"
                            
                        text = formatted_text
                        
                    except Exception as e:
                        print(f"Error formatting character data: {e}")
                        
            except Exception as e:
                print(f"Error processing character entry: {e}")

        # Create and add the entry widget
        entry = AdventureLogEntry(text, entry_type)
        self.log_layout.addWidget(entry)
        
    def reset_game(self):
        self.game_manager.reset_game()
        self.clear_log()
        
    def clear_log(self):
        while self.log_layout.count():
            item = self.log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def show_error(self, message):
        QMessageBox.warning(self, "Error", message)
        
    def save_party(self):
        party_name, ok = QInputDialog.getText(self, "Save Party", "Enter party name:")
        if ok and party_name:
            try:
                self.game_manager.save_party(party_name)
                self.add_log_entry(f"Party '{party_name}' saved successfully!", "dm")
            except Exception as e:
                self.show_error(f"Error saving party: {str(e)}")

    def load_party(self):
        saved_parties = self.game_manager.list_saved_parties()
        if not saved_parties:
            self.show_error("No saved parties found!")
            return
        
        party_name, ok = QInputDialog.getItem(self, "Load Party", "Select party to load:", saved_parties, 0, False)
        if ok and party_name:
            try:
                self.game_manager.load_party(party_name)
                if self.game_manager.party:
                    for name, info in self.game_manager.party.items():
                        self.add_log_entry(f"=== {name} ===\n{info}", "dm")
                else:
                    self.show_error("No party found!")
            except Exception as e:
                self.show_error(f"Error loading party: {str(e)}")