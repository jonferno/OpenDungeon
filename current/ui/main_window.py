from PyQt5.QtWidgets import QMainWindow, QTabWidget
from PyQt5.QtCore import Qt
from PyQt5 import uic, QtWidgets
import os
from .character_tab import CharacterTab
from .adventure_tab import AdventureTab
from .play_game_tab import PlayGameTab
from .party_status_tab import PartyStatusTab
from .settings_tab import SettingsTab
from game_manager import GameManager

class MainWindow(QMainWindow):
    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager
        
        # Initialize an empty central widget first
        self.setCentralWidget(QtWidgets.QWidget())
        
        # Load the UI file
        uic.loadUi('current/ui/designer/main_window.ui', self)
        
        # Create and add tabs with game_manager
        self.setup_tabs()
        
        # Set window properties for maximized start and resizing
        self.setWindowState(Qt.WindowMaximized)
        self.setMinimumSize(800, 600)  # Set minimum window size
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        
        # Make tab widget resizable
        self.tabWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        
        # Show the window
        self.show()
        
    def setup_tabs(self):
        """Create and add all tabs with proper game_manager initialization"""
        # Create tab instances
        tabs = [
            (CharacterTab(self.game_manager), "Character"),
            (AdventureTab(self.game_manager), "Adventure"),
            (PlayGameTab(self.game_manager), "Play Game"),
            (PartyStatusTab(self.game_manager), "Party Status"),
            (SettingsTab(self.game_manager), "Settings")
        ]
        
        # Add tabs to widget
        for tab, title in tabs:
            self.tabWidget.addTab(tab, title)
