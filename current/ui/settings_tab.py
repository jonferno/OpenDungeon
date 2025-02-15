from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QGroupBox, QFormLayout,
                           QComboBox, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import uic  # Add this import
from dotenv import load_dotenv, set_key, find_dotenv
import os
import dotenv

class SettingsTab(QWidget):  # Renamed from ModelsTab
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.tts_manager = game_manager.tts_manager
        self.tts_manager.speech_completed.connect(self.on_speech_completed)
        
        # Define the allowed env variables
        self.env_vars = [
            ('OPENROUTER_API_KEY', 'OpenRouter API Key'),
            ('AZURE_SPEECH_KEY', 'Azure Speech Key'),
            ('WEBSHARE_API_KEY', 'Webshare API Key'),
            ('PROXY_USERNAME', 'Proxy Username'),
            ('PROXY_PASSWORD', 'Proxy Password')
        ]
        
        # Load UI first
        uic.loadUi('current/ui/designer/settings_tab.ui', self)
        
        # Create secure input fields
        self.env_fields = {}
        for env_key, display_name in self.env_vars:
            field = QLineEdit()
            field.setEchoMode(QLineEdit.Password)
            self.env_fields[env_key] = field
            
            # Create row layout
            row_layout = QHBoxLayout()
            row_layout.addWidget(field)
            
            # Add show/hide button
            show_btn = QPushButton("👁")
            show_btn.setFixedWidth(30)
            show_btn.clicked.connect(lambda checked, f=field: self.toggle_password_visibility(f))
            row_layout.addWidget(show_btn)
            
            # Add to form layout
            self.credentialsLayout.addRow(display_name + ":", row_layout)

        # Store references to UI elements with correct names
        self.dm_combo = self.dmCombo
        self.save_dm_btn = self.saveDMBtn
        self.npc_combos = [self.npcCombo0, self.npcCombo1, self.npcCombo2]
        self.save_npc_btn = self.saveNPCBtn
        self.region_combo = self.regionCombo
        self.voice_combo = self.voiceCombo
        self.test_text = self.testText
        self.speak_btn = self.speakBtn
        self.stop_btn = self.stopBtn
        
        # Initialize TTS settings
        self.setup_tts_settings()
        
        # Connect signals after UI loading
        self.saveCredentialsBtn.clicked.connect(self.save_credentials)
        self.save_dm_btn.clicked.connect(self.save_dm_model)
        self.save_npc_btn.clicked.connect(self.save_models)
        self.speak_btn.clicked.connect(self.test_voice)
        self.stop_btn.clicked.connect(self.toggle_volume)
        self.saveTTSBtn.clicked.connect(self.save_tts_settings)
        
        # Connect TTS signals
        self.tts_manager.speech_started.connect(self.on_speech_started)
        self.tts_manager.speech_completed.connect(self.on_speech_completed)
        
        # Update initial button states
        self.update_button_states()
        
        # Load data
        self.load_current_env()
        self.load_existing_models()
        self.apply_styles()
        self.setup_tts_controls()
        self.update_button_states()  # Add initial state update

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 1. API Keys Section
        api_section = self.create_api_section()
        main_layout.addWidget(api_section)
        
        # 2. Models Section
        models_section = self.create_models_section()
        main_layout.addWidget(models_section)
        
        # 3. TTS Section
        tts_section = self.create_tts_section()
        main_layout.addWidget(tts_section)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
        
        # Load existing data
        self.load_current_env()
        self.load_existing_models()
        
        self.apply_styles()

    def create_tts_section(self):
        """Create TTS settings section"""
        tts_group = QGroupBox("Text-to-Speech Settings")
        tts_layout = QVBoxLayout()
        
        # Region selection
        region_layout = QFormLayout()
        self.region_combo = QComboBox()
        regions = ['eastus', 'westus', 'westeurope', 'uksouth']
        self.region_combo.addItems(regions)
        self.region_combo.setCurrentText(self.tts_manager.service_region)
        region_layout.addRow("Azure Region:", self.region_combo)
        tts_layout.addLayout(region_layout)
        
        # Voice selection
        self.voice_combo = QComboBox()
        available_voices = self.tts_manager.get_available_voices()
        self.voice_combo.addItems(available_voices)
        region_layout.addRow("Azure Voice:", self.voice_combo)
        
        # Test area
        test_group = QGroupBox("Test Voice")
        test_layout = QVBoxLayout()
        
        self.test_text = QTextEdit()
        self.test_text.setPlaceholderText("Enter text to test the voice...")
        self.test_text.setMaximumHeight(100)
        test_layout.addWidget(self.test_text)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        self.speak_btn = QPushButton("🔊 Speak")
        self.speak_btn.clicked.connect(self.test_voice)
        self.stop_btn = QPushButton("🔊 Volume")
        self.stop_btn.clicked.connect(self.toggle_volume)
        btn_layout.addWidget(self.speak_btn)
        btn_layout.addWidget(self.stop_btn)
        test_layout.addLayout(btn_layout)
        
        test_group.setLayout(test_layout)
        tts_layout.addWidget(test_group)
        
        # Save button
        save_btn = QPushButton("Save TTS Settings")
        save_btn.clicked.connect(self.save_tts_settings)
        tts_layout.addWidget(save_btn)
        
        tts_group.setLayout(tts_layout)
        return tts_group

    def apply_styles(self):
        """Apply consistent styling across all sections"""
        self.setStyleSheet("""
            QGroupBox {
                background-color: #203D72;
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
                color: #ECF0F1;
                font-weight: bold;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 14px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #334970;
                color: #ECF0F1;
                border: none;
                border-radius: 5px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton {
                background-color: #2980B9;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:disabled {
                background-color: #334970;
            }
        """)

    def toggle_password_visibility(self, field):
        """Toggle password visibility for a field"""
        if field.echoMode() == QLineEdit.Password:
            field.setEchoMode(QLineEdit.Normal)
        else:
            field.setEchoMode(QLineEdit.Password)

    def load_current_env(self):
        """Load only the specified environment variables"""
        load_dotenv()
        for env_key, _ in self.env_vars:
            if env_key in self.env_fields:
                self.env_fields[env_key].setText(os.getenv(env_key, ''))

    def save_credentials(self):
        """Save only the specified credentials to .env file"""
        try:
            env_file = find_dotenv()
            if not env_file:
                env_file = os.path.join(os.path.dirname(self.game_manager.base_path), '.env')
            
            # Save only the specified fields
            for env_key, _ in self.env_vars:
                if env_key in self.env_fields:
                    value = self.env_fields[env_key].text().strip()
                    if value:  # Only save non-empty values
                        set_key(env_file, env_key, value)
            
            # Reload environment
            load_dotenv()
            
            QMessageBox.information(self, "Success", "Credentials saved successfully!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save credentials: {str(e)}")

    def create_api_section(self):
        """Create the API keys section"""
        api_group = QGroupBox("API Keys and Credentials")
        api_layout = QFormLayout()
        
        # Create secure input fields
        self.env_fields = {}
        
        for env_key, display_name in self.env_vars:
            field = QLineEdit()
            field.setEchoMode(QLineEdit.Password)
            self.env_fields[env_key] = field
            
            # Create row layout
            row_layout = QHBoxLayout()
            row_layout.addWidget(field)
            
            # Add show/hide button
            show_btn = QPushButton("👁")
            show_btn.setFixedWidth(30)
            show_btn.clicked.connect(lambda checked, f=field: self.toggle_password_visibility(f))
            row_layout.addWidget(show_btn)
            
            # Add to form layout
            api_layout.addRow(display_name + ":", row_layout)
        
        api_group.setLayout(api_layout)
        return api_group

    def create_models_section(self):
        models_group = QGroupBox("AI Models")
        models_group.setStyleSheet("""
            QGroupBox {
                background-color: #203D72;
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
                color: #ECF0F1;
            }
            QLabel {
                color: #ECF0F1;
                font-family: 'MedievalSharp';
                font-size: 20px;
            }
            QComboBox {
                background-color: #334970;
                color: #ECF0F1;
                border: none;
                border-radius: 5px;
                padding: 5px;
                min-height: 30px;
            }
            QPushButton {
                background-color: #2980B9;
                color: #ECF0F1;
                border: none;
                border-radius: 5px;
                padding: 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:disabled {
                background-color: #334970;
            }
            QTextEdit {
                background-color: #203D72;
                color: #ECF0F1;
                border: none;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        models_layout = QVBoxLayout()
        
        # DM Model selection
        dm_layout = QVBoxLayout()
        dm_layout.addWidget(QLabel("DM Model:"))
        self.dm_combo = QComboBox()
        self.dm_combo.setEditable(True)  # Allow manual entry
        dm_layout.addWidget(self.dm_combo)
        
        # Save DM model button
        self.save_dm_btn = QPushButton("Save DM Model")
        self.save_dm_btn.clicked.connect(self.save_dm_model)
        dm_layout.addWidget(self.save_dm_btn)
        models_layout.addLayout(dm_layout)
        
        # NPC Model selection
        self.npc_combos = []
        for i in range(3):
            row = QVBoxLayout()
            row.addWidget(QLabel(f"NPC {i} Model:"))
            combo = QComboBox()
            combo.setEditable(True)  # Allow manual entry
            row.addWidget(combo)
            self.npc_combos.append(combo)
            models_layout.addLayout(row)
            
        # Save NPC models button
        self.save_npc_btn = QPushButton("Save NPC Models")
        self.save_npc_btn.clicked.connect(self.save_models)
        models_layout.addWidget(self.save_npc_btn)
        
        models_group.setLayout(models_layout)
        return models_group

    def test_voice(self):
        """Test the selected voice with custom text"""
        try:
            text = self.test_text.toPlainText().strip()
            if not text:
                text = "Hello! I am your Dungeon Master. How does my voice sound?"
            
            self.tts_manager.speak(text)
            
        except Exception as e:
            self.update_button_states()
            QMessageBox.warning(self, "Error", f"TTS Error: {str(e)}")

    def stop_voice(self):
        """Stop current TTS playback"""
        try:
            if self.tts_manager:
                self.tts_manager.stop()
            self.speak_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        except Exception as e:
            print(f"Error stopping TTS: {e}")

    def save_tts_settings(self):
        """Save the current TTS settings"""
        try:
            # Get current selections
            selected_voice = self.voice_combo.currentText()
            selected_region = self.region_combo.currentText()
            
            # Update game manager settings
            self.game_manager.set_setting('tts_voice', selected_voice)
            self.game_manager.set_setting('tts_region', selected_region)
            
            # Update TTS manager directly
            self.tts_manager.update_settings(voice=selected_voice, region=selected_region)
            
            # Test the new settings
            test_text = "Voice settings have been updated successfully."
            self.tts_manager.speak(test_text)
            
            QMessageBox.information(self, "Success", "TTS settings saved and tested!")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save TTS settings: {str(e)}")

    def load_available_models(self):
        models = self.game_manager.list_available_models()
        self.dm_combo.addItems(models)
        for combo in self.npc_combos:
            combo.addItems(models)
            
    def filter_models(self, text):
        # TODO: Implement model filtering
        pass
        
    def load_existing_models(self):
        """Load current model settings"""
        # Load available models first
        models = self.game_manager.list_available_models()
        self.dm_combo.addItems(models)
        for combo in self.npc_combos:
            combo.addItems(models)
        
        # Set current selections
        dm_model = self.game_manager.get_dm_model()
        if dm_model:
            self.dm_combo.setCurrentText(dm_model)
            
        for i, combo in enumerate(self.npc_combos):
            npc_model = self.game_manager.get_npc_model(i)
            if npc_model:
                combo.setCurrentText(npc_model)

    def save_dm_model(self):
        """Save DM model only"""
        dm_model = self.dm_combo.currentText().strip()
        if dm_model:
            print(f"Saving DM model: {dm_model}")  # Debug print
            self.game_manager.save_dm_model(dm_model)
            self.game_manager.dm_model = dm_model  # Set it directly as well
            QMessageBox.information(self, "Success", f"DM model saved: {dm_model}")
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid model name!")

    def save_models(self):
        """Save both DM and NPC models"""
        # Save DM model
        dm_model = self.dm_combo.currentText().strip()
        if dm_model:
            print(f"Saving DM model: {dm_model}")  # Debug print
            self.game_manager.save_dm_model(dm_model)
            self.game_manager.dm_model = dm_model  # Set it directly as well
            
        # Save NPC models
        for i, combo in enumerate(self.npc_combos):
            npc_model = combo.currentText().strip()
            if npc_model:
                self.game_manager.save_npc_model(i, npc_model)
                
        # Show confirmation
        QMessageBox.information(self, "Success", "Model settings saved!")

    def setup_tts_settings(self):
        """Initialize TTS settings with current values"""
        # Setup regions
        regions = ['eastus', 'westus', 'westeurope', 'uksouth']
        self.regionCombo.clear()
        self.regionCombo.addItems(regions)
        self.regionCombo.setCurrentText(self.tts_manager.service_region)
        
        # Setup voices
        available_voices = self.tts_manager.get_available_voices()
        self.voiceCombo.clear()
        self.voiceCombo.addItems(available_voices)
        current_voice = self.game_manager.get_setting('tts_voice', 'en-US-DavisNeural')
        self.voiceCombo.setCurrentText(current_voice)

    def setup_tts_controls(self):
        """Setup TTS controls with volume control"""
        # Change stop button to volume button
        self.stop_btn.setText("🔇 Stop")
        self.stop_btn.clicked.connect(self.toggle_volume)
        
    def toggle_volume(self):
        """Toggle TTS volume between full and muted"""
        try:
            is_muted = self.tts_manager.toggle_mute()
            self.stop_btn.setText("🔈 Unmute" if is_muted else "🔊 Volume")
            self.update_button_states()  # Update all button states after toggling
        except Exception as e:
            print(f"Error toggling volume: {e}")
            self.update_button_states()

    def on_speech_completed(self):
        """Handle speech completion"""
        self.update_button_states()  # Use the central button state update method

    def update_button_states(self):
        """Update button states based on TTS status"""
        is_speaking = self.tts_manager.speaking
        is_muted = self.tts_manager.muted
        
        self.speak_btn.setEnabled(not is_speaking)  # Enable speak button when not speaking
        self.stop_btn.setEnabled(True)  # Always keep volume button enabled
        self.stop_btn.setText("🔈 Unmute" if is_muted else "🔊 Volume")

    def on_speech_started(self):
        """Handle speech start"""
        self.update_button_states()  # Use the central button state update method
