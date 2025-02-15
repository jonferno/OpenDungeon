from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # System status
        status_label = QLabel("System Status")
        status_label.setStyleSheet("font-weight: bold; color: #ffd700;")
        layout.addWidget(status_label)
        
        # API status
        api_status = "Available" if self.game_manager.has_api_key() else "API Key Missing"
        api_label = QLabel(f"OpenRouter API: {api_status}")
        layout.addWidget(api_label)
        
        # Model status
        model_label = QLabel(f"Models Set: {self.game_manager.has_models()}")
        layout.addWidget(model_label)
        
        # Help section
        help_text = """
        <h3>How to Play</h3>
        <ol>
            <li>Generate New Party</li>
            <li>Start New Adventure</li>
            <li>Play Next Turn</li>
        </ol>
        <p>May your dice roll high!</p>
        """
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Set sidebar styling
        self.setStyleSheet("""
            QWidget {
                background-color: #16213e;
                color: #e0e0e0;
                padding: 10px;
            }
            QLabel {
                padding: 5px;
            }
        """)
