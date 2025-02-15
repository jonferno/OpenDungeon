from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QScrollArea, QFrame, QPushButton, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from character_image_handler import CharacterImageHandler
import os  # Added missing import

class CharacterStatusCard(QFrame):
    def __init__(self, character_data, game_manager, parent=None):
        super().__init__(parent)
        self.game_manager = game_manager
        self.character_data = character_data
        self.image_handler = CharacterImageHandler(game_manager)
        self.init_ui()
        self.setStyleSheet("""
            QFrame {
                background-color: #203D72;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 16px;
            }
            QLabel[title=true] {
                font-family: MedievalSharp;
                font-size: 32px;
                color: #FFE0B2;
                padding: 10px;
                margin-bottom: 15px;
            }
            QLabel[section=true] {
                font-size: 18px;
                font-weight: bold;
                margin-top: 10px;
            }
            QWidget {
                background-color: #203D72;
            }
            QScrollArea {
                border: none;
                background-color: #FFECCC;
            }
            QTextEdit {
                font-size: 16px;
                line-height: 1.4;
            }
        """)

        # Add HP update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_hp_updates)
        self.update_timer.start(1000)  # Check every second
        
        # Store last known HP
        self.last_known_hp = self.get_current_hp()

    def find_portrait_file(self) -> str:
        """Find matching portrait file for this character"""
        try:
            # Get character details for filename matching
            char_name = self.character_data.get('name', '').replace(' ', '_').lower()
            char_race = self.character_data.get('race', '').lower()
            char_class = self.character_data.get('class', '').lower()
            expected_filename = f"{char_name}_{char_race}_{char_class}_portrait.png"

            # Check in NPCs directory first
            npc_path = os.path.join(self.game_manager.npcs_dir, expected_filename)
            if os.path.exists(npc_path):
                return npc_path

            # Then check in characters directory
            char_path = os.path.join(self.game_manager.characters_dir, expected_filename)
            if os.path.exists(char_path):
                return char_path

            return None
        except Exception as e:
            print(f"Error finding portrait: {e}")
            return None

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Name container at the top
        name_container = QWidget()
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 10)
        
        # Character name centered with larger font
        name = QLabel(self.character_data.get('name', 'Unknown'))
        name.setProperty('title', True)
        name.setAlignment(Qt.AlignCenter)
        name_layout.addWidget(name)
        
        layout.addWidget(name_container)
        
        # Portrait section with preserved aspect ratio
        self.portrait_label = QLabel()
        self.portrait_label.setFixedWidth(300)
        self.portrait_label.setMaximumHeight(400)
        self.portrait_label.setStyleSheet("""
            QLabel {
                background-color: #334970;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid #FFE0B2;
            }
        """)
        self.portrait_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.portrait_label, alignment=Qt.AlignCenter)

        # Try to find existing portrait first
        if isinstance(self.character_data, dict):
            # First check if image_path is directly specified
            if 'image_path' in self.character_data and os.path.exists(self.character_data['image_path']):
                self.display_portrait(self.character_data['image_path'])
            else:
                # Try to find matching portrait file
                portrait_path = self.find_portrait_file()
                if portrait_path:
                    self.display_portrait(portrait_path)
                    # Update character data with found image path
                    self.character_data['image_path'] = portrait_path
        
        # Character info
        self.display_character_info(layout)
        
        # Generate Portrait button at bottom for NPCs
        if not self.is_player_character():
            generate_btn = QPushButton("Generate Portrait")
            generate_btn.clicked.connect(self.generate_portrait)
            generate_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                    font-family: 'MedievalSharp';
                    margin-top: 10px;
                }
                QPushButton:hover {
                    background-color: #2980B9;
                }
            """)
            layout.addWidget(generate_btn)
        
        self.setLayout(layout)
        
    def is_player_character(self):
        """Check if this card represents the player character"""
        if not isinstance(self.character_data, dict):
            return False
        player_char = self.game_manager.get_player_character()
        if not player_char:
            return False
        return self.character_data.get('name') == player_char.get('name')

    def generate_portrait(self):
        """Generate a portrait for this character"""
        try:
            char_data = self.parse_character_data()
            
            # Use NPCs directory for non-player characters
            if self.is_player_character():
                save_dir = self.game_manager.characters_dir
            else:
                save_dir = self.game_manager.npcs_dir
            
            image_path = self.image_handler.generate_and_save_image(char_data, save_dir)
            
            if image_path:
                # Update character data with image path
                self.character_data['image_path'] = image_path
                
                # Only save to character file if it's a player character
                if self.is_player_character():
                    self.game_manager.save_character(char_data)
                else:
                    # For NPCs, update the party data to include image path
                    self.game_manager.party[char_data['name']] = {
                        **char_data,
                        'image_path': image_path
                    }
                
                # Display the new portrait
                self.display_portrait(image_path)
                
        except Exception as e:
            print(f"Error generating portrait: {e}")

    def parse_character_data(self):
        """Convert string character data to dictionary format"""
        if isinstance(self.character_data, dict):
            return self.character_data
            
        char_dict = {
            'name': 'Unknown',
            'race': 'Unknown',
            'class': 'Unknown',
            'equipment': [],
            'personality': '',
            'image_path': self.find_portrait_file()  # Add existing portrait if found
        }
        
        # Parse the character string
        lines = self.character_data.split('\n')
        current_section = None
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'name':
                    char_dict['name'] = value
                elif key == 'race':
                    char_dict['race'] = value
                elif key == 'class':
                    char_dict['class'] = value
                elif key == 'personality':
                    current_section = 'personality'
                    char_dict['personality'] = value
                elif key == 'equipment':
                    current_section = 'equipment'
                    char_dict['equipment'] = []
            elif current_section == 'equipment' and line.strip().startswith('-'):
                char_dict['equipment'].append(line.strip('- ').strip())
                
        return char_dict

    def display_portrait(self, image_path):
        """Display the portrait image with preserved aspect ratio"""
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Scale to fit within 300x400 box while preserving aspect ratio
            scaled_pixmap = pixmap.scaled(300, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.portrait_label.setPixmap(scaled_pixmap)
            self.portrait_label.setToolTip("Character Portrait")

    def parse_hp_value(self, hp_string: str) -> int:
        """Parse HP value from various string formats"""
        try:
            # If it's already a number, return it
            if isinstance(hp_string, (int, float)):
                return int(hp_string)
                
            # Clean up the string
            hp_string = hp_string.strip()
            
            # If it's a simple number string
            if hp_string.isdigit():
                return int(hp_string)
                
            # Handle formats like "34 (5d8 + 14 CON mod)"
            if '(' in hp_string:
                # Take only the first number before parentheses
                base_hp = hp_string.split('(')[0].strip()
                if base_hp.isdigit():
                    return int(base_hp)
                    
            # Try to extract the first number from the string
            import re
            numbers = re.findall(r'\d+', hp_string)
            if numbers:
                return int(numbers[0])
                
            # If all else fails, return default HP
            return 30
            
        except Exception as e:
            print(f"Error parsing HP value '{hp_string}': {e}")
            return 30

    def get_current_hp(self) -> int:
        """Get current HP from character data"""
        if isinstance(self.character_data, dict):
            hp_value = self.character_data.get('hp', 30)
            return self.parse_hp_value(hp_value)
        else:
            # Parse HP from string format
            for line in self.character_data.split('\n'):
                if line.startswith('HP:'):
                    try:
                        hp_str = line.split(':')[1].strip().split('/')[0].strip()
                        return self.parse_hp_value(hp_str)
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing HP line '{line}': {e}")
                        return 30
        return 30

    def display_character_info(self, layout):
        """Display the character information"""
        info = QTextEdit()
        info.setReadOnly(True)
        info.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable scroll
        info.setFixedHeight(300)  # Fixed height to prevent scrolling
        
        # Format character info with larger text and section headers
        equipment_list = self.character_data.get('equipment', ['Basic adventuring gear'])
        if isinstance(equipment_list, str):
            equipment_items = [item.strip() for item in equipment_list.split(',')]
        else:
            equipment_items = equipment_list
            
        # Create formatted HTML text with larger font and section headers
        current_hp = self.get_current_hp()
        max_hp = current_hp  # Use current as max if not specified
        
        # Try to get max HP if available
        if isinstance(self.character_data, dict):
            max_hp_str = self.character_data.get('max_hp', current_hp)
            max_hp = self.parse_hp_value(str(max_hp_str))
        
        hp_percent = (current_hp / max_hp) * 100 if max_hp > 0 else 0
        
        if hp_percent <= 25:
            hp_color = '#E74C3C'  # Red for low HP
        elif hp_percent <= 50:
            hp_color = '#F39C12'  # Orange for medium HP
        else:
            hp_color = '#2ECC71'  # Green for high HP
            
        # Format HP display with current/max if available
        hp_text = f"""<p><span style='font-size: 18px; font-weight: bold; color: #FFE0B2;'>HP:</span> 
                     <span style='color: {hp_color};'>{current_hp}</span>"""
        if max_hp != current_hp:
            hp_text += f"<span style='color: {hp_color};'>/{max_hp}</span>"
        hp_text += "</p>"
        
        info_html = f"""
        <div style='font-size: 16px; line-height: 1.4;'>
            <p><span style='font-size: 18px; font-weight: bold; color: #FFE0B2;'>Race:</span> {self.character_data.get('race', 'Unknown')}</p>
            <p><span style='font-size: 18px; font-weight: bold; color: #FFE0B2;'>Class:</span> {self.character_data.get('class', 'Unknown')}</p>
            {hp_text}
            <p><span style='font-size: 18px; font-weight: bold; color: #FFE0B2;'>AC:</span> {self.character_data.get('ac', '?')}</p>
            
            <p style='font-size: 18px; font-weight: bold; color: #FFE0B2; margin-top: 15px;'>Ability Scores:</p>
            <p>STR: {self.character_data.get('ability_scores', {}).get('STR', '10')}</p>
            <p>DEX: {self.character_data.get('ability_scores', {}).get('DEX', '10')}</p>
            <p>CON: {self.character_data.get('ability_scores', {}).get('CON', '10')}</p>
            <p>INT: {self.character_data.get('ability_scores', {}).get('INT', '10')}</p>
            <p>WIS: {self.character_data.get('ability_scores', {}).get('WIS', '10')}</p>
            <p>CHA: {self.character_data.get('ability_scores', {}).get('CHA', '10')}</p>
            
            <p style='font-size: 18px; font-weight: bold; color: #FFE0B2; margin-top: 15px;'>Equipment:</p>
            {''.join(f'<p>• {item}</p>' for item in equipment_items)}
        </div>
        """
        
        info.setHtml(info_html)
        info.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #ECF0F1;
            }
        """)
        layout.addWidget(info)

    def check_hp_updates(self):
        """Check if HP has changed and update display"""
        current_hp = self.get_current_hp()
        if current_hp != self.last_known_hp:
            self.display_character_info(self.layout())
            if current_hp < self.last_known_hp:
                # Flash red for damage
                self.setStyleSheet("""
                    QFrame {
                        background-color: #722020;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 5px;
                    }
                """)
                QTimer.singleShot(500, self.restore_style)
            self.last_known_hp = current_hp

    def restore_style(self):
        """Restore original style after damage flash"""
        self.setStyleSheet("""
            QFrame {
                background-color: #203D72;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """)

class PartyStatusTab(QWidget):
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.init_ui()
        
    def showEvent(self, event):
        """Called when tab becomes visible"""
        super().showEvent(event)
        self.update_party_status()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Scroll area for character cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.cards_layout = QHBoxLayout(scroll_content)
        self.cards_layout.setSpacing(20)  # Add spacing between cards
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
    def update_party_status(self):
        """Update party status display"""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add card for each party member
        if self.game_manager.party:
            for name, char_data in self.game_manager.party.items():
                # Convert string data to dict if needed
                if isinstance(char_data, str):
                    char_data = self.parse_character_string(char_data)
                # Update image path if it's the player character
                if self.is_player_character(name):
                    player_char = self.game_manager.get_player_character()
                    if player_char and 'image_path' in player_char:
                        char_data['image_path'] = player_char['image_path']
                if char_data:
                    card = CharacterStatusCard(char_data, self.game_manager)
                    self.cards_layout.addWidget(card)

    def is_player_character(self, name: str) -> bool:
        """Check if the given name matches the player character"""
        player_char = self.game_manager.get_player_character()
        return player_char and player_char.get('name') == name

    def parse_character_string(self, char_str: str) -> dict:
        """Parse character string into dictionary with error handling"""
        char_dict = {
            'name': 'Unknown',
            'race': 'Unknown',
            'class': 'Unknown',
            'background': 'Unknown',
            'alignment': 'Unknown',
            'hp': '?',
            'ac': '?',
            'ability_scores': {},
            'equipment': [],
            'personality': '',
            'backstory': ''
        }
        
        try:
            # If it's already a dictionary (player character)
            if isinstance(char_str, dict):
                char_dict.update(char_str)
                # Convert equipment string to list if needed
                if isinstance(char_dict['equipment'], str):
                    items = [item.strip() for item in char_dict['equipment'].split(',')]
                    char_dict['equipment'] = [item for item in items if item]
                return char_dict

            # Parse string format (NPCs)
            lines = char_str.split('\n')
            equipment_section = False
            equipment_items = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for section headers
                if line.startswith('Equipment:'):
                    equipment_section = True
                    continue
                    
                # Parse equipment items
                if equipment_section and line.startswith('-'):
                    item = line.replace('-', '').strip()
                    if item:
                        equipment_items.append(item)
                
                # Parse other attributes
                elif ':' in line and not equipment_section:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'name':
                        char_dict['name'] = value
                    elif key == 'race':
                        char_dict['race'] = value
                    elif key == 'class':
                        char_dict['class'] = value
                    elif key == 'hp':
                        char_dict['hp'] = value.split('/')[0].strip()
                    elif key == 'ac':
                        char_dict['ac'] = value.split()[0].strip()
                    elif key in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
                        if 'ability_scores' not in char_dict:
                            char_dict['ability_scores'] = {}
                        char_dict['ability_scores'][key.upper()] = value.split()[0]
                
                # Stop equipment section if we hit another section
                elif line.endswith(':'):
                    equipment_section = False
            
            # Store equipment
            if equipment_items:
                char_dict['equipment'] = equipment_items
            elif not char_dict['equipment']:
                char_dict['equipment'] = ['Basic adventuring gear']
                
        except Exception as e:
            print(f"Error parsing character data: {e}")
            print(f"Problematic character string: {char_str[:100]}...")  # Debug print
            
        return char_dict
