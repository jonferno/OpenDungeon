import json
import os
from pathlib import Path
import aigirl_generator
from llm_handler import LLMHandler

class CharacterImageGenerator:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler

    def format_character_prompt(self, character_data):
        """Format character data into a prompt for the LLM"""
        char_description = f"""
        Race: {character_data.get('race')}
        Class: {character_data.get('class')}
        Gender: {character_data.get('gender')}
        Background: {character_data.get('background')}
        Appearance details: {character_data.get('appearance', '')}
        """
        prompt = f"Create a detailed but concise image generation prompt for a D&D character with these details: {char_description}"
        return prompt

    def generate_character_image(self, character_data, save_path):
        """Generate and save character image"""
        # Get optimized prompt from LLM
        character_prompt = self.format_character_prompt(character_data)
        optimized_prompt = self.llm_handler.get_response(character_prompt)
        
        # Generate image using aigirl_generator
        image_path = aigirl_generator.generate_image(optimized_prompt, save_path)
        return image_path
