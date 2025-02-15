from PyQt5.QtWidgets import (QWidget, QMessageBox, QLabel, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QSizePolicy)
from PyQt5 import QtWidgets  # Import QtWidgets as a module
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from character_image_handler import CharacterImageHandler
from game_manager import GameManager

class NotificationWidget(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Header layout with close button
        header = QHBoxLayout()
        header.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ECF0F1;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #E74C3C;
            }
        """)
        header.addWidget(close_btn)
        
        # Message label
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(header)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Style the widget
        self.setStyleSheet("""
            NotificationWidget {
                background-color: #334970;
                border: 2px solid #203D72;
                border-radius: 10px;
            }
            QLabel {
                color: #203D72;
                font-size: 14px;
                padding: 10px;
            }
        """)
        
        # Set fixed size
        self.setFixedWidth(300)
        self.adjustSize()
        
        # Setup fade animation
        self.opacity = 1.0
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        
        # Auto-close timer
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.start_fade_out)
        self.close_timer.setSingleShot(True)

    def show_notification(self, duration=2000):
        """Show the notification and start the auto-close timer"""
        # Position the notification under the portrait
        if self.parent():
            portrait = self.parent().portraitDisplay
            pos = portrait.mapToGlobal(portrait.rect().bottomLeft())
            self.move(pos.x() + (portrait.width() - self.width()) // 2, 
                     pos.y() + 10)
        
        # Show with fade in
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.show()
        self.fade_animation.start()
        
        # Start auto-close timer
        self.close_timer.start(duration)

    def start_fade_out(self):
        """Start the fade out animation"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()

class CharacterTab(QWidget):
    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager
        self.image_handler = CharacterImageHandler(game_manager)
        
        # Load UI
        uic.loadUi('current/ui/designer/character_tab.ui', self)

        # Initialize styles and widgets
        self.setup_ui()
        self.setup_widgets()
        
        # Connect signals
        self.createBtn.clicked.connect(self.create_character)
        self.loadBtn.clicked.connect(self.show_load_dialog)
        self.classCombo.currentTextChanged.connect(self.update_derived_stats)
        self.raceCombo.currentTextChanged.connect(self.update_derived_stats)
        
        self.current_notification = None

    def setup_ui(self):
        """Setup UI elements and styles"""
        # Configure portrait title styling (using existing label from UI)
        self.portraitTitle.setStyleSheet("""
            QLabel {
                font-family: 'MedievalSharp';
                font-size: 28px;
                color: #203D72;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                margin-bottom: 5px;
            }
        """)

        # Configure portrait display
        self.portraitDisplay.setStyleSheet("""
            QLabel {
                background-color: #334970;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid #203D72;
                margin-top: 0px;
            }
        """)
        self.portraitDisplay.setMinimumSize(256, 256)  # Minimum size
        self.portraitDisplay.setMaximumSize(512, 512)  # Maximum size
        self.portraitDisplay.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.portraitDisplay.setScaledContents(False)
        self.portraitDisplay.setAlignment(Qt.AlignCenter)

        # Apply main widget styles
        self.setStyleSheet("""
            QWidget {
                background-color: #ECF0F1;
            }
            QLabel {
                color: #203D72;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #FFE0A8;
                color: #203D72;
                border: 1px solid #203D72;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #203D72;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-family: 'MedievalSharp';
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QSpinBox {
                background-color: #FFE0A8;
                color: #203D72;
                border: 1px solid #203D72;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # Configure personality and backstory text areas
        self.personalityEdit.setStyleSheet("""
            QTextEdit {
                background-color: #FFE0A8;
                color: #203D72;
                border: 1px solid #203D72;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
                line-height: 1.4;
            }
        """)
        self.backstoryEdit.setStyleSheet("""
            QTextEdit {
                background-color: #FFE0A8;
                color: #203D72;
                border: 1px solid #203D72;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
                line-height: 1.4;
            }
        """)

        # Configure section labels
        for label in [self.equipmentLabel, self.personalityLabel, self.backstoryLabel]:
            label.setStyleSheet("""
                QLabel {
                    color: #203D72;
                    font-size: 20px;
                    font-weight: bold;
                }
            """)

        # Equipment input styling to match other text areas
        self.itemsEdit.setStyleSheet("""
            QTextEdit {
                background-color: #FFE0A8;
                color: #203D72;
                border: 1px solid #203D72;
                border-radius: 5px;
                padding: 5px;
                font-size: 16px;
                line-height: 1.4;
            }
        """)

        # Style armor and weapon edit fields to match
        for edit in [self.armorEdit, self.weaponEdit]:
            edit.setStyleSheet("""
                QLineEdit {
                    background-color: #FFE0A8;
                    color: #203D72;
                    border: 1px solid #203D72;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 16px;
                }
            """)

        # Make the main widget resizable
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        # Make text areas resizable
        for widget in [self.personalityEdit, self.backstoryEdit, self.itemsEdit]:
            widget.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )
            widget.setMinimumHeight(100)  # Set minimum height

    def setup_widgets(self):
        """Initialize widget values and properties"""
        # Initialize ability scores dictionary
        self.ability_scores = {
            'STR': self.strengthSpin,
            'DEX': self.dexteritySpin,
            'CON': self.constitutionSpin,
            'INT': self.intelligenceSpin,
            'WIS': self.wisdomSpin,
            'CHA': self.charismaSpin
        }
        
        # Setup ability score widgets
        for spin in self.ability_scores.values():
            spin.valueChanged.connect(self.update_derived_stats)
            spin.setRange(8, 18)
            spin.setValue(10)

        # Add options to combo boxes
        self.raceCombo.addItems(self.game_manager.DND_RACES)
        self.classCombo.addItems(self.game_manager.DND_CLASSES)
        self.backgroundCombo.addItems(self.game_manager.DND_BACKGROUNDS)
        self.alignmentCombo.addItems(self.game_manager.DND_ALIGNMENTS)
        
        # Initial stats update
        self.update_derived_stats()

    def apply_styles(self):
        """Apply custom styling to widgets"""
        self.setStyleSheet("""
            QLabel[heading="true"] {
                font-family: 'MedievalSharp';
                font-size: 34px;
                color: #203D72;
                padding: 5px;
                margin-bottom: 10px;
            }
            QLabel[field="true"] {
                color: #203D72;
                font-weight: bold;
                font-size: 20px;
                padding: 5px 0;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #334970;
                color: #ECF0F1;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-height: 30px;
                font-size: 18px;
            }
        """)

    def show_temporary_notification(self, message: str, duration: int = 2000):
        """Show a temporary notification under the portrait"""
        # Close any existing notification
        if self.current_notification and self.current_notification.isVisible():
            self.current_notification.close()
        
        # Create and show new notification
        self.current_notification = NotificationWidget(message, self)
        self.current_notification.show_notification(duration)

    def show_load_dialog(self):
        saved_chars = self.game_manager.list_saved_characters()
        if not saved_chars:
            self.show_temporary_notification("No saved characters found!")
            return
            
        from ui.dialogs import CharacterSelectDialog
        dialog = CharacterSelectDialog(self.game_manager, self)
        if (dialog.exec_()):
            character = dialog.selected_character
            if character:
                self.fill_character_form(character)
                # Set this as the active player character
                self.game_manager.set_player_character(character)
                self.show_temporary_notification(f"Loaded character: {character['name']}")

    def fill_character_form(self, character):
        """Fill the form with loaded character data"""
        self.nameEdit.setText(character['name'])
        self.raceCombo.setCurrentText(character['race'])
        self.classCombo.setCurrentText(character['class'])
        self.backgroundCombo.setCurrentText(character.get('background', 'Soldier'))
        self.alignmentCombo.setCurrentText(character.get('alignment', 'True Neutral'))
        
        for ability, score in character['ability_scores'].items():
            if ability in self.ability_scores:
                self.ability_scores[ability].setValue(score)
        
        self.personalityEdit.setText(character.get('personality', ''))
        self.backstoryEdit.setText(character.get('backstory', ''))
        
        # Handle equipment loading
        equipment = character.get('equipment', ['Basic adventuring gear'])
        if isinstance(equipment, str):
            equipment = [item.strip() for item in equipment.split(',')]
        
        # Try to identify weapon and armor from equipment list
        weapon = next((item for item in equipment if any(w in item.lower() for w in ['sword', 'axe', 'bow', 'staff', 'dagger', 'mace'])), '')
        armor = next((item for item in equipment if any(a in item.lower() for a in ['armor', 'mail', 'shield', 'plate', 'leather'])), '')
        
        # Remove weapon and armor from the list if found
        other_items = [item for item in equipment if item != weapon and item != armor]
        
        self.weaponEdit.setText(weapon)
        self.armorEdit.setText(armor)
        self.itemsEdit.setText('\n'.join(f"- {item}" for item in other_items))

        # Load character portrait if it exists - move this before UI updates
        if 'image_path' in character and os.path.exists(character['image_path']):
            self.display_character_portrait(character['image_path'])
        else:
            # Clear portrait if no image exists
            self.portraitDisplay.clear()
            print(f"No portrait found for character at {character.get('image_path')}")

    def create_character(self):
        # Validate required fields
        if not self.nameEdit.text():
            self.show_temporary_notification("Please enter a character name!", 3000)
            return
            
        # Parse equipment into a proper list
        equipment = []
        if self.weaponEdit.text().strip():
            equipment.append(self.weaponEdit.text().strip())
        if self.armorEdit.text().strip():
            equipment.append(self.armorEdit.text().strip())
            
        # Add additional items
        additional_items = self.itemsEdit.toPlainText().strip().split('\n')
        for item in additional_items:
            item = item.strip('- ').strip()  # Remove leading/trailing spaces and dashes
            if item:
                equipment.append(item)
                
        if not equipment:
            equipment = ['Basic adventuring gear']
            
        character = {
            "name": self.nameEdit.text(),
            "race": self.raceCombo.currentText(),
            "class": self.classCombo.currentText(),
            "background": self.backgroundCombo.currentText(),  # Use selected background
            "alignment": self.alignmentCombo.currentText(),   # Use selected alignment
            "ability_scores": {
                ability: spin.value() 
                for ability, spin in self.ability_scores.items()
            },
            "personality": self.personalityEdit.toPlainText() or "A brave adventurer",
            "backstory": self.backstoryEdit.toPlainText() or "Seeking fortune and glory",
            "equipment": equipment  # Now it's always a list
        }
        
        try:
            # Save character first to get the filepath
            char_path = self.game_manager.save_character(character)
            
            # Generate and save image - move this before setting as player character
            save_dir = os.path.dirname(char_path)
            image_path = self.image_handler.generate_and_save_image(character, save_dir)
            
            if image_path:
                # Update character data with image path
                character['image_path'] = image_path
                self.game_manager.save_character(character)  # Save again with image path
                
                # Display the image immediately
                self.display_character_portrait(image_path)
            
            # Set as active character after everything is saved
            self.game_manager.set_player_character(character)
            self.show_temporary_notification("Character saved and portrait generated!")
            
        except Exception as e:
            self.show_temporary_notification(f"Error: {str(e)}", 3000)

    def display_character_portrait(self, image_path):
        """Display character portrait in the UI"""
        try:
            if image_path and os.path.exists(image_path):
                print(f"Loading portrait from: {image_path}")  # Debug print
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.portraitDisplay.setPixmap(pixmap)
                    self.portraitDisplay.setAlignment(Qt.AlignCenter)
                else:
                    print("Failed to load portrait pixmap")
            else:
                print(f"Invalid image path or file doesn't exist: {image_path}")
        except Exception as e:
            print(f"Error displaying portrait: {e}")

    def save_party(self):
        self.game_manager.save_party()

    def load_party(self):
        self.game_manager.load_party()
        self.display_party()

    def display_party(self):
        """Show current party in the text area."""
        party_text = ""
        for name, char_data in self.game_manager.party.items():
            party_text += f"{name}\n{char_data}\n\n"
        self.party_display.setText(party_text)

    def update_derived_stats(self):
        """Update HP and AC based on class, race, and ability scores"""
        char_class = self.classCombo.currentText()
        race = self.raceCombo.currentText()
        
        # Base HP per class (at level 5, including average HP per level)
        base_class_hp = {
            'Barbarian': 50,     # d12 hit die + high CON
            'Fighter': 44,       # d10 hit die
            'Paladin': 44,       # d10 hit die
            'Ranger': 40,        # d10 hit die
            'Monk': 38,          # d8 hit die
            'Rogue': 38,         # d8 hit die
            'Bard': 38,          # d8 hit die
            'Cleric': 38,        # d8 hit die
            'Druid': 38,          # d8 hit die
            'Warlock': 38,       # d8 hit die
            'Wizard': 32,        # d6 hit die
            'Sorcerer': 32       # d6 hit die
        }
        
        # Base AC per class (assuming standard starting equipment)
        base_class_ac = {
            'Barbarian': 14,     # Unarmored defense
            'Fighter': 16,       # Chain mail
            'Paladin': 16,       # Chain mail
            'Ranger': 14,        # Scale mail
            'Monk': 14,          # Unarmored defense
            'Rogue': 14,         # Leather armor + DEX
            'Bard': 13,          # Leather armor
            'Cleric': 15,        # Scale mail + shield
            'Druid': 14,         # Hide armor
            'Warlock': 13,       # Leather armor
            'Wizard': 11,        # No armor
            'Sorcerer': 11       # No armor
        }
        
        # Racial bonuses to HP and AC
        race_mods = {
            'Dwarf': {'hp': 2, 'ac': 0},          # Dwarven Toughness
            'Hill Dwarf': {'hp': 3, 'ac': 0},     # Extra HP per level
            'Mountain Dwarf': {'hp': 2, 'ac': 1},  # Medium armor proficiency
            'Elf': {'hp': 0, 'ac': 1},            # DEX bonus
            'High Elf': {'hp': 0, 'ac': 1},       # DEX bonus
            'Wood Elf': {'hp': 0, 'ac': 2},       # DEX bonus + fleet of foot
            'Dark Elf': {'hp': 0, 'ac': 1},       # DEX bonus
            'Halfling': {'hp': 0, 'ac': 1},       # Small size + nimbleness
            'Human': {'hp': 1, 'ac': 0},          # Balanced stats
            'Dragonborn': {'hp': 2, 'ac': 1},     # Draconic ancestry
            'Gnome': {'hp': 0, 'ac': 1},          # Small size + cunning
            'Half-Elf': {'hp': 1, 'ac': 1},       # Adaptable
            'Half-Orc': {'hp': 2, 'ac': 0},       # Relentless Endurance
            'Tiefling': {'hp': 1, 'ac': 0}        # Hellish Resistance
        }
        
        # Calculate base stats from class
        base_hp = base_class_hp.get(char_class, 35)  # Default to average if class not found
        base_ac = base_class_ac.get(char_class, 12)  # Default to basic AC if class not found
        
        # Add racial modifiers
        race_bonus = race_mods.get(race, {'hp': 0, 'ac': 0})  # Default to no bonus if race not found
        final_hp = base_hp + race_bonus['hp']
        final_ac = base_ac + race_bonus['ac']
        
        # Additional class-specific features
        if char_class == 'Barbarian' and not self.weaponEdit.text():
            final_ac += 2  # Unarmored defense bonus if not wearing armor
        elif char_class == 'Monk' and not self.weaponEdit.text():
            final_ac += 2  # Unarmored defense bonus if not wearing armor
            
        # Update displays with calculated values
        self.hpDisplay.setText(str(final_hp))
        self.acDisplay.setText(str(final_ac))
