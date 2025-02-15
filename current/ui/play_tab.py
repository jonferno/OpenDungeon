from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QLabel, QScrollArea, QFrame, QApplication, QSizePolicy)
from PyQt5.QtCore import Qt
from tts_manager import TTSManager

class LogEntry(QFrame):
    def __init__(self, text, entry_type="dm", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)  # Changed to vertical layout
        
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setText(text)
        self.text_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_area.setMinimumHeight(50)
        layout.addWidget(self.text_area)
        
        if entry_type == "dm":
            # Add speak button for DM messages
            self.speak_btn = QPushButton("🔊TTS")
            self.speak_btn.setMinimumWidth(120)
            self.speak_btn.setStyleSheet("font-size: 20px;")
            self.speak_btn.clicked.connect(lambda: self.speak_text(text))
            layout.addWidget(self.speak_btn)
            
            self.stop_btn = QPushButton("Stop")
            self.stop_btn.setMinimumWidth(60)
            layout.addWidget(self.stop_btn)
            self.stop_btn.clicked.connect(self.stop_speaking)
            
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFE0B2;
                    border: 2px solid #325FAD;
                }
                QTextEdit {
                    color: #203D72;
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFE0B2;
                    border: 2px solid #203D72;
                }
                QTextEdit {
                    color: #203D72;
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
                }
            """)
        
        self.setLayout(layout)
        
    def speak_text(self, text):
        main_window = self.parentWidget().parentWidget().parentWidget().parentWidget()
        if main_window:
            main_window.game_manager.tts_manager.speak(text)
        else:
            print("Could not access main window to get game manager!")
    
    def stop_speaking(self):
        main_window = self.parentWidget().parentWidget().parentWidget().parentWidget()
        if main_window:
            main_window.game_manager.tts_manager.stop_speaking()

class PlayTab(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Game log area
        scroll = QScrollArea()
        log_container = QWidget()
        self.log_layout = QVBoxLayout(log_container)
        log_container.setLayout(self.log_layout)
        scroll.setWidget(log_container)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(600)
        
        # Input area at bottom
        input_area = QVBoxLayout()  # Changed to VBoxLayout
        
        # Action input row
        action_row = QHBoxLayout()
        self.action_input = QTextEdit()
        self.action_input.setPlaceholderText("What would you like to do?")
        self.action_input.setMaximumHeight(100)
        self.send_btn = QPushButton("Send Action")
        self.send_btn.setMinimumHeight(45)
        self.send_btn.clicked.connect(self.send_action)
        action_row.addWidget(self.action_input, stretch=4)
        action_row.addWidget(self.send_btn, stretch=1)
        
        # Dice roll button
        self.roll_btn = QPushButton("🎲 Roll Dice")
        self.roll_btn.setMinimumHeight(45)
        self.roll_btn.clicked.connect(self.roll_dice)
        self.roll_btn.setEnabled(False)
        
        # Add rows to input area
        input_area.addLayout(action_row)
        input_area.addWidget(self.roll_btn)        
        
        # Add everything to main layout
        layout.addWidget(scroll, stretch=4)
        layout.addLayout(input_area, stretch=1)
        self.setLayout(layout)

    def add_log_entry(self, text: str, entry_type: str = "normal"):
        entry = LogEntry(text, entry_type)
        self.log_layout.addWidget(entry)
        # Auto scroll to bottom
        QApplication.processEvents()
        scroll_area = entry.parent().parent()
        if isinstance(scroll_area, QScrollArea):
            vsb = scroll_area.verticalScrollBar()
            vsb.setValue(vsb.maximum())
        
    def send_action(self):
        """Send player action to DM"""
        action = self.action_input.toPlainText().strip()
        if not action:
            return
            
        # Log player's action
        self.add_log_entry(f"Your action: {action}")
        
        try:
            # Get DM's response
            response = self.game_manager.process_player_action(action)
            if response:
                # Remove asterisks from DM's response
                response = response.replace('*', '')
                # Log DM's response
                self.add_log_entry(response, "dm")
                # Clear input
                self.action_input.clear()
                # Enable roll button if DM asks for a roll
                self.roll_btn.setEnabled('roll' in response.lower() or 
                                       'check' in response.lower() or 
                                       'saving throw' in response.lower())
        except Exception as e:
            self.add_log_entry(f"Error: {str(e)}", "dm")
            print(f"Error in send_action: {str(e)}")  # Debug print

    def roll_dice(self):
        """Handle dice roll button click"""
        if not self.game_manager.game_state:
            return
        import random
        result = random.randint(1, 20)
        # Show roll result
        self.add_log_entry(f"🎲 You rolled: {result}")
        
        # Send roll result as a message to DM
        dm_response = self.game_manager.process_player_action(f"I rolled a {result}!")
        self.add_log_entry(dm_response, "dm")
        
        # Update controls
        self.roll_btn.setEnabled(False)
        self.action_input.setEnabled(True)
        self.send_btn.setEnabled(True)

    def check_for_roll_request(self, dm_response: str) -> bool:
        """Check if DM is requesting a roll"""
        roll_keywords = [
            "roll", "make a roll", "skill check", 
            "saving throw", "ability check", "attack roll"
        ]
        return any(keyword in dm_response.lower() for keyword in roll_keywords)

    def enable_controls(self, dm_response: str):
        """Enable appropriate controls based on DM response"""
        needs_roll = self.check_for_roll_request(dm_response)
        self.action_input.setEnabled(not needs_roll)
        self.send_btn.setEnabled(not needs_roll)
        self.roll_btn.setEnabled(needs_roll)
