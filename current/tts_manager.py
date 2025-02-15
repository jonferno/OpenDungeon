import os
import azure.cognitiveservices.speech as speechsdk
from PyQt5.QtCore import QObject, QMutex, pyqtSignal
from typing import Optional

class TTSManager(QObject):
    speech_completed = pyqtSignal()  # Add signal for completion
    speech_started = pyqtSignal()  # Add new signal

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.current_voice = config.get('tts_voice', "en-US-DavisNeural")
        self.service_region = config.get('tts_region', "eastus")
        self.speech_key = os.getenv('AZURE_SPEECH_KEY')
        self.mutex = QMutex()
        self.current_synthesizer = None
        self.is_muted = False
        self.speaking = False
        self.muted = False  # Add muted state
        self.initialize_speech_config()

    def initialize_speech_config(self):
        """Initialize speech config with current settings"""
        try:
            if not self.speech_key:
                raise ValueError("Azure Speech key not found")

            # Create base speech config
            self.speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.service_region
            )
            self.speech_config.speech_synthesis_voice_name = self.current_voice
            
            # Create audio config without volume (not supported directly)
            self.audio_config = speechsdk.audio.AudioOutputConfig(
                use_default_speaker=True
            )
            
            # Create synthesizer with current config
            self.current_synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=self.audio_config
            )
            
            # Set up event handlers
            self.current_synthesizer.synthesis_completed.connect(self.on_synthesis_completed)
            self.current_synthesizer.synthesis_canceled.connect(self.on_synthesis_canceled)
            
        except Exception as e:
            print(f"Error initializing speech config: {e}")
            self.speech_config = None
            self.current_synthesizer = None

    def on_synthesis_completed(self, evt):
        """Handle synthesis completion"""
        self.speaking = False
        self.speech_completed.emit()

    def on_synthesis_canceled(self, evt):
        """Handle synthesis cancellation"""
        self.speaking = False
        self.speech_completed.emit()
        print(f"Speech synthesis canceled: {evt.result.cancellation_details.reason}")

    def speak(self, text: str):
        """Speak text asynchronously"""
        try:
            if not self.current_synthesizer:
                self.initialize_speech_config()
            
            if not self.current_synthesizer or self.speaking:
                return

            if self.muted:
                # Skip speech if muted but still emit completed signal
                self.speech_completed.emit()
                return

            self.speaking = True
            self.speech_started.emit()  # Emit when speech starts
            
            # Configure callbacks
            def on_speech_end(evt):
                self.speaking = False
                self.speech_completed.emit()
            
            self.current_synthesizer.synthesis_completed.connect(on_speech_end)
            self.current_synthesizer.synthesis_canceled.connect(on_speech_end)
            
            # Speak asynchronously
            self.current_synthesizer.speak_text_async(text)
                
        except Exception as e:
            print(f"Error in TTS: {e}")
            self.speaking = False
            self.speech_completed.emit()
            raise

    def update_settings(self, voice: Optional[str] = None, region: Optional[str] = None):
        """Update settings and reinitialize if needed"""
        changed = False
        
        if voice and voice != self.current_voice:
            self.current_voice = voice
            changed = True
            
        if region and region != self.service_region:
            self.service_region = region
            changed = True
            
        if changed:
            self.initialize_speech_config()

    def get_available_voices(self) -> list:
        """Get available voices"""
        try:
            if not self.speech_config:
                self.initialize_speech_config()
            
            if not self.speech_config:
                return ['en-US-DavisNeural']

            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.speech_config,
                audio_config=None  # Don't need audio output for getting voices
            )
            voices = synthesizer.get_voices_async().get()
            return [voice.short_name for voice in voices.voices]
        except Exception as e:
            print(f"Error getting voices: {e}")
            return ['en-US-DavisNeural']

    def toggle_mute(self) -> bool:
        """Toggle mute state and return new state"""
        self.muted = not self.muted
        if self.speaking and self.muted:
            # If currently speaking and we're muting, stop current speech
            self.current_synthesizer.stop_speaking_async()
        return self.muted

