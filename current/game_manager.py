import os
import json
import requests
import time  # Add this import
from typing import Dict, Tuple
from npc_manager import NPCManager
from fantasy_names import get_random_name
import random
from tts_manager import TTSManager  # Add this import

class GameManager:
    # Add D&D constants
    DND_RACES = ["Human", "Elf", "Dwarf", "Halfling", "Gnome", "Half-Elf", "Half-Orc", "Dragonborn", "Tiefling"]
    DND_CLASSES = ["Fighter", "Wizard", "Rogue", "Cleric", "Paladin", "Ranger", "Barbarian", "Bard", "Druid", "Monk", "Sorcerer", "Warlock"]
    DND_ALIGNMENTS = ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"]
    DND_BACKGROUNDS = ["Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier", "Merchant", "Entertainer", "Hermit", "Sailor"]

    # Add damage type mapping constants
    DAMAGE_TYPES = {
        'fire': (4, 10),        # d4 to d10 damage
        'cold': (4, 8),         # d4 to d8 damage
        'lightning': (6, 10),    # d6 to d10 damage
        'poison': (4, 8),        # d4 to d8 damage
        'acid': (4, 8),         # d4 to d8 damage
        'force': (4, 12),       # d4 to d12 damage
        'psychic': (4, 10),     # d4 to d10 damage
        'necrotic': (6, 10),    # d6 to d10 damage
        'radiant': (6, 10),     # d6 to d10 damage
        'thunder': (6, 8),      # d6 to d8 damage
        'bludgeoning': (4, 8),  # d4 to d8 damage
        'piercing': (4, 8),     # d4 to d8 damage
        'slashing': (4, 8),     # d4 to d8 damage
        'magical': (6, 12)      # d6 to d12 damage
    }

    def __init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.characters_dir = os.path.join(self.base_path, 'saved_characters')
        self.npcs_dir = os.path.join(self.base_path, 'npc_portraits')  # Add this line
        self.parties_dir = os.path.join(self.base_path, 'saved_parties')  # Add this line
        self.config_file = os.path.join(self.base_path, 'config.json')
        self.npc_manager = NPCManager(self.base_path)
        
        self.game_state = None
        self.party = None
        self.player_character = None
        
        # Create directories if they don't exist
        os.makedirs(self.characters_dir, exist_ok=True)
        os.makedirs(self.npcs_dir, exist_ok=True)  # Create NPCs directory
        os.makedirs(self.parties_dir, exist_ok=True)  # Create Parties directory
        
        # Load config first
        self.load_config()
        
        # Now we can initialize dm_model from config
        self.dm_model = self.config.get('last_dm_model', '')
        
        # Initialize TTS manager last
        self.tts_manager = TTSManager(self.config)

        # Initialize settings
        self.settings = {
            'tts_voice': 'en-US-DavisNeural',
            'tts_region': 'eastus'
        }
        self.load_settings()

        self.saves_dir = os.path.join(self.base_path, 'saved_games')
        os.makedirs(self.saves_dir, exist_ok=True)

    def get_setting(self, key: str, default=None):
        """Get a setting value with a default fallback"""
        return self.settings.get(key, default)

    def set_setting(self, key: str, value):
        """Set a setting value and save settings"""
        self.settings[key] = value
        self.save_settings()

    def load_settings(self):
        """Load settings from settings.json"""
        settings_path = os.path.join(self.base_path, 'settings.json')
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save settings to settings.json"""
        settings_path = os.path.join(self.base_path, 'settings.json')
        try:
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "last_dm_model": "",
                "npc_models": {},
                "saved_characters": {}
            }
            self.save_config()
            
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def save_character(self, character: Dict) -> str:
        try:
            filename = f"{character['name'].replace(' ', '_').lower()}.json"
            filepath = os.path.join(self.characters_dir, filename)
            
            # Save character file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character, f, indent=2)
            
            # Add to config
            self.config['saved_characters'][character['name']] = filename
            self.save_config()
            
            return filepath
        except Exception as e:
            raise Exception(f"Error saving character: {str(e)}")

    def load_character(self, filename: str) -> Dict:
        try:
            filepath = os.path.join(self.characters_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Error loading character: {str(e)}")

    def list_saved_characters(self) -> list:
        try:
            return [f for f in os.listdir(self.characters_dir) if f.endswith('.json')]
        except Exception:
            return []

    def save_dm_model(self, model: str):
        self.config['last_dm_model'] = model
        self.dm_model = model
        self.save_config()

    def save_npc_model(self, slot: int, model: str):
        self.config['npc_models'][f'npc_{slot}'] = model
        self.save_config()

    def get_dm_model(self) -> str:
        return self.config.get('last_dm_model', '')

    def get_npc_model(self, slot: int) -> str:
        return self.config['npc_models'].get(f'npc_{slot}', '')

    def has_api_key(self) -> bool:
        return bool(os.getenv('OPENROUTER_API_KEY'))
        
    def has_models(self) -> bool:
        return bool(self.config.get('last_dm_model')) and bool(self.config.get('npc_models'))
        
    def list_available_models(self) -> list:
        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "TD-LLM-DND"
            }
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers
            )
            if response.status_code == 200:
                models = response.json()
                return [model['id'] for model in models['data']]
            return []
        except:
            return []
            
    def reset_game(self):
        self.game_state = None
        self.party = None
        
    def process_turn(self, action: str) -> str:
        if not self.game_state:
            raise Exception("No active game")

        # Record the action in the game state
        self.game_state['actions'].append(action)

        # Build updated prompt
        prompt = self._build_dm_prompt()

        # Get DM response using the new prompt
        response = self.get_dm_response_from_api(prompt)
        self.game_state['responses'].append(response)

        return response

    def generate_party(self) -> Dict[str, str]:
        """Generate exactly 3 NPC characters using their pre-selected models"""
        self.party = {}
        
        for i in range(3):
            try:
                # Get the specific model for this NPC slot
                model = self.config['npc_models'].get(f"npc_{i}", self.dm_model)
                character = self.generate_character(model)
                
                # Extract name from the generated character
                name_lines = [line for line in character.split('\n') if line.startswith('Name:')]
                if name_lines:
                    name = name_lines[0].split('Name:')[1].strip()
                else:
                    name = f"Adventurer {i + 1}"
                    
                # Store the character and save model preference
                self.party[name] = character
                self.npc_manager.save_npc_model(name, model)
                
            except Exception as e:
                name = f"Adventurer {i + 1}"
                self.party[name] = self.generate_fallback_character(name)
        
        return self.party

    def start_new_adventure(self) -> Tuple[Dict, str]:
        """Create a new adventure with the current party"""
        if not self.party:
            raise Exception("No party available")

        # Create detailed party information
        party_details = []
        for name, char_data in self.party.items():
            if isinstance(char_data, str):
                # Parse string character data into meaningful sections
                sections = {}
                current_section = None
                for line in char_data.split('\n'):
                    if ':' in line:
                        key = line.split(':', 1)[0].strip()
                        value = line.split(':', 1)[1].strip()
                        if key in ['Name', 'Race', 'Class', 'Background', 'Alignment']:
                            sections[key] = value
                        elif key == 'Personality':
                            current_section = 'Personality'
                            sections[current_section] = []
                        elif key == 'Equipment':
                            current_section = 'Equipment'
                            sections[current_section] = []
                        elif key == 'Backstory':
                            current_section = 'Backstory'
                            sections[current_section] = []
                    elif current_section and line.strip():
                        sections[current_section].append(line.strip())
                
                char_summary = (
                    f"{sections.get('Name', name)} - {sections.get('Race', 'Unknown')} "
                    f"{sections.get('Class', 'Unknown')}, {sections.get('Background', 'Unknown')}, "
                    f"Personality: {' '.join(sections.get('Personality', []))}. "
                    f"Equipment: {', '.join(sections.get('Equipment', []))}. "
                    f"Backstory: {' '.join(sections.get('Backstory', []))}"
                )
                party_details.append(char_summary)

        intro_prompt = f"""You are the Dungeon Master for a D&D 5e game.
You are to create an exciting D&D adventure introduction.
Keep the total response under 700 words.

Use this detailed information about the party members to craft an engaging and personalized story:

PARTY DETAILS:
{chr(10).join(f"- {detail}" for detail in party_details)}

Create an introduction with these sections:

1. World Setting (2-3 sentences):
Describe the world and current situation.

2. Initial Scene (2-3 sentences):
Set the immediate scene where the party meets, incorporating their backgrounds.

3. Party Introduction:
Introduce each character using their specific traits, equipment, and backgrounds.

4. Opening Challenge:
Present an initial quest that connects to at least one character's backstory.

End with a clear question or choice for the party.

Do not use any * for emphasis or any other reason.
Do not use any bolding or italics.
Do not use any markdown formatting.
Do not make the introduction too long.

End with a clear question or choice for the party.
"""

        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "TD-LLM-DND"
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.dm_model,
                    "messages": [{"role": "user", "content": intro_prompt}],
                    "max_tokens": 2000,  # Increased to 2000
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
            dm_intro = response.json()['choices'][0]['message']['content']
            
            self.game_state = {
                "turn": 1,
                "actions": [],
                "responses": [],
                "story_progression": [dm_intro],
                "turn_participation": {name: False for name in self.party},
                "party_members": self.party
            }
            
            return self.game_state, dm_intro
            
        except Exception as e:
            raise Exception(f"Failed to start adventure: {str(e)}")

    def generate_character(self, model: str) -> str:
        """Generate a single character using the specified model"""
        race = random.choice(self.DND_RACES)
        name = get_random_name(race)
        
        prompt = f"""You are a D&D character creator. Create a level 5 character using EXACTLY this format.
Do not add any extra text or explanations.

Name: {name}
Race: {race}
Class: [Pick one: Fighter/Wizard/Rogue/Cleric/Paladin/Ranger/Barbarian/Bard/Druid/Monk/Sorcerer/Warlock]
Level: 5

Ability Scores:
STR: [roll 10-18]
DEX: [roll 10-18]
CON: [roll 10-18]
INT: [roll 10-18]
WIS: [roll 10-18]
CHA: [roll 10-18]

HP: [Calculate based on class and CON]
AC: [10 + DEX mod + armor]

Background: [Pick one D&D background]
Alignment: [Pick one D&D alignment]

Personality:
[2-3 clear personality traits]

Equipment:
- [Specific main weapon]
- [Specific armor type]
- [2-3 specific items]

Backstory:
[3-4 sentences, be specific and concise]"""

        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "TD-LLM-DND"
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a D&D character creator. Generate characters following the EXACT format provided. Do not add ANY additional commentary."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "presence_penalty": 0.6,
                    "frequency_penalty": 0.3
                }
            )
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code}")  # Debug print
                return self.generate_fallback_character(name)
                
            content = response.json()['choices'][0]['message']['content'].strip()
            
            # Validate response has required fields
            required_fields = ["Name:", "Race:", "Class:", "Level:", "Ability Scores:", "HP:", "AC:", "Background:", "Alignment:", "Personality:", "Equipment:", "Backstory:"]
            
            if all(field in content for field in required_fields):
                if "HP:" not in content:
                    content += "\nHP: 30"
                if "AC:" not in content:
                    content += "\nAC: 10"
                if "Equipment:" not in content:
                    content += "\nEquipment:\n- Basic adventuring gear"
                return content
            else:
                print(f"Invalid response format: {content}")  # Debug print
                return self.generate_fallback_character(name)
                
        except Exception as e:
            print(f"Character generation error: {str(e)}")  # Debug print
            return self.generate_fallback_character(name)

    def generate_fallback_character(self, name: str) -> str:
        """Generate a basic character template if generation fails"""
        return f"""Name: {name}
Race: Human
Class: Fighter
Level: 5
Ability Scores:
STR: 10
DEX: 10
CON: 10
INT: 10
WIS: 10
CHA: 10
HP: 30
AC: 10
Background: Soldier
Alignment: Neutral Good
Personality: Reserved but loyal.
Equipment:
- Longsword
- Chain mail
- Basic adventuring gear
Backstory: A simple warrior seeking adventure."""

    def format_character_string(self, character: Dict) -> str:
        hp = character.get('hp', 30)
        ac = character.get('ac', 10)
        eq = character.get('equipment')
        if isinstance(eq, list):
            eq_str = '\n'.join(f"- {item}" for item in eq if item.strip())
        else:
            eq_str = eq or "Basic adventuring gear"
        formatted = f"""Name: {character['name']}
Race: {character['race']}
Class: {character['class']}
Background: {character['background']}
Alignment: {character['alignment']}

Ability Scores:
STR: {character['ability_scores']['STR']}
DEX: {character['ability_scores']['DEX']}
CON: {character['ability_scores']['CON']}
INT: {character['ability_scores']['INT']}
WIS: {character['ability_scores']['WIS']}
CHA: {character['ability_scores']['CHA']}

HP: {hp}
AC: {ac}

Personality: {character['personality']}

Equipment:
{eq_str}

Backstory: {character['backstory']}"""
        return formatted.replace('*', '')

    def get_player_character(self) -> Dict:
        """Get the current player character"""
        if not self.player_character:
            print("No player character set!")  # Debug print
            return None
        return self.player_character
        
    def set_player_character(self, character: Dict):
        """Set the current player character"""
        # Validate character has all required fields
        required_fields = ['name', 'race', 'class', 'background', 'alignment', 'ability_scores', 
                         'personality', 'backstory', 'equipment']
        
        # Add any missing fields with defaults
        if 'background' not in character:
            character['background'] = 'Soldier'
        if 'alignment' not in character:
            character['alignment'] = 'True Neutral'
            
        # Ensure all ability scores exist
        if 'ability_scores' not in character:
            character['ability_scores'] = {
                'STR': 10, 'DEX': 10, 'CON': 10,
                'INT': 10, 'WIS': 10, 'CHA': 10
            }
            
        # Add default values for empty strings
        if not character.get('personality'):
            character['personality'] = 'A brave adventurer'
        if not character.get('backstory'):
            character['backstory'] = 'Seeking fortune and glory'
        if not character.get('equipment'):
            character['equipment'] = 'Basic adventuring gear'
            
        self.player_character = character
        print(f"Set player character: {character['name']}")  # Debug print
        
    def generate_party_with_player(self, player_character: Dict) -> Dict[str, str]:
        """Generate party including the player character"""
        if not player_character:
            raise Exception("No player character available!")
            
        self.party = {}
        self.party[player_character['name']] = self.format_character_string(player_character)
        print(f"Added player to party: {player_character['name']}")  # Debug print
        
        # Generate NPCs
        for i in range(3):
            try:
                model = self.config['npc_models'].get(f"npc_{i}", self.dm_model)
                character = self.generate_character(model)
                name_lines = [line for line in character.split('\n') if line.startswith('Name:')]
                name = name_lines[0].split('Name:')[1].strip() if name_lines else f"Adventurer {i + 1}"
                self.party[name] = character
                self.npc_manager.save_npc_model(name, model)
            except Exception as e:
                print(f"Error generating NPC: {str(e)}")
                name = f"Adventurer {i + 1}"
                self.party[name] = self.generate_fallback_character(name)
        return self.party
        
    def get_npc_names(self) -> list:
        """Get list of NPC names in the party"""
        if not self.party or not self.player_character:
            return []
        return [name for name in self.party.keys() 
                if name != self.player_character['name']]
                
    def submit_dice_roll(self, result: int):
        """Submit a dice roll result to the game state"""
        if self.game_state:
            self.game_state['last_roll'] = result
            self.game_state['waiting_for_roll'] = False
            
    def process_player_action(self, action: str) -> str:
        """Process player action and get DM response"""
        if not self.game_state:
            raise Exception("No active game")
            
        if not self.dm_model:
            raise Exception("No DM model selected")

        try:
            # Check if this is a dice roll result
            if "rolled a" in action.lower():
                # Extract only the first number found in the text
                numbers = [int(num) for num in ''.join(c if c.isdigit() else ' ' for c in action).split()]
                roll_result = numbers[0] if numbers else 0
                
                # Get the last DM response that requested a roll
                last_response = self.game_state.get('responses', [''])[-1]
                if "DC" in last_response:
                    # Extract DC value from the last response
                    dc = int(''.join(filter(str.isdigit, last_response.split("DC")[1].split()[0])))
                    
                    # Create a prompt that includes the roll result and DC
                    prompt = f"""The player rolled {roll_result} on a d20 against DC {dc}.

Determine the outcome:
- On a {roll_result} vs DC {dc}
- If {roll_result} >= {dc}: Success
- If {roll_result} < {dc}: Failure

Last game state: {last_response}

Provide the outcome of this specific roll ({roll_result}), describing success or failure, and move the story forward.
Be concise (max 3 sentences for the outcome).
Then provide a new prompt for the next action.
Do not ask for another roll immediately."""

                else:
                    # Generic roll response if no DC was found
                    prompt = f"""The player rolled {roll_result} on a d20.
The roll result is exactly {roll_result}, not higher or lower.

Last game state: {last_response}

Describe the outcome of this {roll_result} roll and move the story forward.
Be concise (max 3 sentences).
Then provide a new prompt for the next action.
Do not ask for another roll immediately."""

            else:
                # Normal action processing
                self.game_state['actions'].append({
                    'player': self.player_character['name'],
                    'action': action
                })
                prompt = self._build_dm_prompt()
            
            print(f"Sending prompt to API: {prompt}")  # Debug print
            
            dm_response = self.get_dm_response_from_api(prompt)
            
            # Check for damage descriptions in the response
            damage_indicators = [
                'hits', 'strikes', 'blast', 'attack hits', 'slashes',
                'pierces', 'smashes', 'wounds', 'damage'
            ]
            
            if any(indicator in dm_response.lower() for indicator in damage_indicators):
                # Calculate damage
                damage_amount, damage_type = self.calculate_damage(dm_response)
                
                # Identify target (either player or NPC)
                target_name = None
                player_name = self.player_character['name']
                
                # Check if player is the target
                if any(f"hits {player_name}" in dm_response.lower() or 
                       f"strikes {player_name}" in dm_response.lower() or
                       "hitting you" in dm_response.lower() or
                       "strikes you" in dm_response.lower()):
                    target_name = player_name
                else:
                    # Check for NPC targets
                    for npc_name in self.get_npc_names():
                        if npc_name.lower() in dm_response.lower():
                            target_name = npc_name
                            break
                
                if target_name:
                    # Apply the damage
                    self.apply_damage(target_name, damage_amount, dm_response)
                    
                    # Append damage information to response
                    dm_response += f"\n[{target_name} takes {damage_amount} {damage_type} damage!]"
            
            self.game_state['responses'].append(dm_response)
            return dm_response
            
        except Exception as e:
            print(f"Error processing action: {str(e)}")
            raise Exception(f"Error processing action: {str(e)}")

    def update_character_stats(self, char_name: str, updates: Dict):
        """Update a character's stats (HP, AC, Equipment, etc.)"""
        if char_name not in self.party:
            print(f"Character {char_name} not found in party.")
            return
            
        char_data = self.party[char_name]
        if isinstance(char_data, str):
            # Parse existing character data
            lines = char_data.split('\n')
            new_lines = []
            in_equipment = False
            
            for line in lines:
                if line.startswith('HP:') and 'hp' in updates:
                    try:
                        hp_value = updates['hp']
                        if isinstance(hp_value, str):
                            hp_value = hp_value.split(' ')[0]  # Take only the number part
                        new_lines.append(f"HP: {int(hp_value)}")
                    except ValueError as e:
                        print(f"Error parsing character data: {e}")
                        new_lines.append(f"HP: {updates['hp']}")
                elif line.startswith('AC:') and 'ac' in updates:
                    new_lines.append(f"AC: {updates['ac']}")
                elif line.startswith('Equipment:') and 'equipment' in updates:
                    new_lines.append('Equipment:')
                    for item in updates['equipment']:
                        new_lines.append(f"- {item}")
                    in_equipment = True
                elif in_equipment and line.strip() and not line.startswith('-'):
                    in_equipment = False
                    new_lines.append(line)
                elif not in_equipment:
                    new_lines.append(line)
                    
            self.party[char_name] = '\n'.join(new_lines)

    def process_npc_turn(self, npc_name: str) -> str:
        """Process turn for an NPC"""
        if not self.game_state or npc_name not in self.party:
            return ""
        model = self.config['npc_models'].get(f"npc_{list(self.party.keys()).index(npc_name)-1}", self.dm_model)
        return self.generate_npc_action(model)

    def get_dm_response_from_api(self, prompt: str) -> str:
        """Call the OpenRouter API and return the DM's response."""
        try:
            if not self.dm_model:
                raise Exception("Please select a DM model in Settings")

            print(f"Using DM model: {self.dm_model}")  # Debug print
            
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "HTTP-Referer": "https://github.com/your-repo",
                "X-Title": "TD-LLM-DND"
            }
            
            print("Sending request to OpenRouter API...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.dm_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            
            print(f"API Response status: {response.status_code}")  # Debug print
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")
                
            json_response = response.json()
            print(f"API Response JSON: {json_response}")  # Debug print
            
            if not isinstance(json_response, dict):
                raise Exception("API response is not a dictionary")
                
            if 'choices' not in json_response or not isinstance(json_response['choices'], list):
                print(f"Invalid API response: {json_response}")
                raise Exception("No response choices from API")
                
            if not json_response['choices']:
                raise Exception("Empty list of choices in API response")
                
            first_choice = json_response['choices'][0]
            if not isinstance(first_choice, dict):
                raise Exception("First choice is not a dictionary")
                
            if 'message' not in first_choice:
                raise Exception("No 'message' in the first choice")
                
            message = first_choice.get('message')
            if 'content' not in message:
                raise Exception("No 'content' in the message")

            dm_response = message.get('content')
            dm_response = dm_response.replace('*', '')
            return dm_response
            
        except Exception as e:
            print(f"Error generating DM response: {str(e)}")
            raise Exception(f"Failed to get DM response: {str(e)}")

    def _build_dm_prompt(self) -> str:
        """Build the prompt for the DM"""
        recent_actions = self.game_state.get('actions', [])[-3:]
        recent_responses = self.game_state.get('responses', [])[-3:]
        
        party_info = []
        for name, char_data in self.game_state.get('party_members', {}).items():
            if isinstance(char_data, str):
                party_info.append(f"{name}: " + " | ".join(
                    line.strip() for line in char_data.split('\n')
                    if any(key in line for key in ['Class:', 'Race:', 'Equipment:'])
                ))
                
        return f"""You are the Dungeon Master for D&D 5e.
You are controlling the NPCs in the party. The player is controlling only their character.
Your response must not contain any asterisks, markdown, or special formatting.
Write naturally as if speaking to the players.

Party Members:
{chr(10).join(party_info)}

Recent Events: {' '.join(str(r) for r in recent_responses)}
Latest Actions: {' '.join(str(a) for a in recent_actions)}

1. Acknowledge the player's action
2. If the action requires a check or roll, specify:
   "Suggest a [skill] check - DC [number]" or
   "Suggest a [type] saving throw - DC [number]" or
   "Suggest an attack roll" but do not force the player to roll.
3. Only describe the outcome after a roll is made
4. Use game mechanics properly (skill checks, saving throws, etc.)
5. End with a prompt for the next action. Do not ask the NPCs what they want to do. You are controlling them.
6. Do not ask the player to roll for NPC checks. Perform NPC rolls yourself automatically.

Keep response under 250 words. Make sure to include a roll at least every 3 turns.
"""

    def generate_npc_action(self, model: str) -> str:
        """Generate action for an NPC"""
        # TODO: Implement NPC action generation
        return f"{npc_name} watches carefully."

    def save_party(self, party_name: str):
        """Save current party to a file."""
        try:
            party_file = os.path.join(self.parties_dir, f"{party_name}.json")
            with open(party_file, 'w', encoding='utf-8') as f:
                json.dump(self.party, f, indent=2)
            print(f"Party saved successfully: {party_file}")
        except Exception as e:
            print(f"Error saving party: {str(e)}")

    def load_party(self, party_name: str):
        """Load a previously saved party."""
        try:
            party_file = os.path.join(self.parties_dir, f"{party_name}.json")
            with open(party_file, 'r', encoding='utf-8') as f:
                self.party = json.load(f)
            print(f"Party loaded successfully: {party_file}")
        except Exception as e:
            print(f"Error loading party: {str(e)}")

    def list_saved_parties(self) -> list:
        """List all saved parties."""
        try:
            return [f.replace('.json', '') for f in os.listdir(self.parties_dir) if f.endswith('.json')]
        except Exception as e:
            print(f"Error listing saved parties: {str(e)}")
            return []

    def check_for_roll_request(self, response: str) -> bool:
        """More accurate detection of when a roll is actually needed"""
        # Common D&D roll request patterns
        roll_patterns = [
            "roll a d20",
            "make a check",
            "ability check",
            "skill check",
            "saving throw",
            "roll for initiative",
            "attack roll",
            "dc ",  # Usually indicates a required roll
            "difficulty class",
            "make a strength check", # Added
            "make a dexterity check", # Added
            "make a constitution check", # Added
            "make a intelligence check", # Added
            "make a wisdom check", # Added
            "make a charisma check" # Added
        ]
        
        # Skip if the response is asking a question
        if "?" in response:
            return False
            
        # Skip if it's just casual use of "roll" in conversation
        casual_roll_phrases = [
            "ready to roll",
            "roll with it",
            "on a roll",
            "let's roll",
            "roll out",
            "roll along"
        ]
        
        response_lower = response.lower()
        
        # First check if it's just casual usage
        for phrase in casual_roll_phrases:
            if (phrase in response_lower):
                return False
                
        # Then check for actual roll requests
        return any(pattern in response_lower for pattern in roll_patterns)

    def save_game_state(self, save_name: str) -> str:
        """Save current game state to a file"""
        try:
            if not self.game_state:
                raise Exception("No active game to save")
                
            # Create a save state dictionary
            save_data = {
                'game_state': self.game_state,
                'party': self.party,
                'player_character': self.player_character,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create filename with timestamp
            filename = f"{save_name}_{int(time.time())}.json"
            filepath = os.path.join(self.saves_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2)
                
            return filepath
            
        except Exception as e:
            print(f"Error saving game: {str(e)}")
            raise

    def generate_story_recap(self) -> str:
        """Generate a story recap from the recent responses"""
        if not self.game_state or not self.game_state.get('responses'):
            return ""

        # Get initial story and recent responses
        initial_story = self.game_state.get('story_progression', [''])[0]
        recent_responses = self.game_state.get('responses', [])[-3:]  # Get last 3 responses
        
        recap_prompt = f"""As the DM, create a brief recap of the story so far, presenting it as if the player is just waking up from a dream where they remember these events.

Initial story setup:
{initial_story}

Most recent events:
{chr(10).join(f"- {response}" for response in recent_responses)}

Requirements for the recap:
1. Start with "As you slowly wake from your dream, you recall the recent events..."
2. Briefly mention the initial setup (1 sentence)
3. Focus on the most recent events (2-3 paragraphs)
4. End with the current situation/challenge
5. Keep the dream-like quality but make it clear these events really happened
6. Include key character names and important details
7. Keep it under 250 words

Format it naturally as if speaking to the player."""

        try:
            recap = self.get_dm_response_from_api(recap_prompt)
            return recap
        except Exception as e:
            print(f"Error generating recap: {e}")
            return "You wake up, remembering the recent events of your adventure..."

    def load_game_state(self, filename: str) -> bool:
        """Load game state and generate recap"""
        try:
            filepath = os.path.join(self.saves_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            self.game_state = save_data.get('game_state')
            self.party = save_data.get('party')
            self.player_character = save_data.get('player_character')
            
            # Generate recap after loading
            recap = self.generate_story_recap()
            if recap:
                # Add recap to responses so it appears in the game log
                self.game_state['responses'].append(recap)
            
            return True
            
        except Exception as e:
            print(f"Error loading game: {str(e)}")
            raise

    def list_saved_games(self) -> list:
        """Get list of saved games with their timestamps"""
        try:
            saves = []
            for filename in os.listdir(self.saves_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.saves_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                        saves.append({
                            'filename': filename,
                            'timestamp': save_data.get('timestamp', ''),
                            'name': filename.split('_')[0]
                        })
            return saves
        except Exception:
            return []

    def calculate_damage(self, attack_desc: str) -> tuple:
        """Calculate damage based on attack description"""
        damage_amount = 0
        damage_type = 'magical'  # Default to magical damage
        
        # Try to identify damage type from description
        desc_lower = attack_desc.lower()
        for dmg_type in self.DAMAGE_TYPES:
            if dmg_type in desc_lower:
                damage_type = dmg_type
                break
                
        # Get damage dice range for the type
        min_dice, max_dice = self.DAMAGE_TYPES[damage_type]
        base_damage = random.randint(min_dice, max_dice)
        
        # Additional damage based on attack description
        if any(word in desc_lower for word in ['powerful', 'massive', 'intense']):
            damage_amount = base_damage + random.randint(min_dice, max_dice)
        else:
            damage_amount = base_damage
            
        return damage_amount, damage_type

    def apply_damage(self, target_name: str, damage: int, attack_desc: str):
        """Apply damage to a character and update their HP"""
        if target_name not in self.party:
            print(f"Target {target_name} not found in party")
            return
            
        char_data = self.party[target_name]
        
        # Convert string character data to dict if needed
        if isinstance(char_data, str):
            char_dict = self.parse_character_string(char_data)
        else:
            char_dict = char_data
            
        # Get current HP
        current_hp = int(char_dict.get('hp', 30))
        
        # Apply damage
        new_hp = max(0, current_hp - damage)
        char_dict['hp'] = new_hp
        
        # Convert back to string format if needed
        if isinstance(self.party[target_name], str):
            # Update HP in the string representation
            char_lines = self.party[target_name].split('\n')
            updated_lines = []
            for line in char_lines:
                if line.startswith('HP:'):
                    updated_lines.append(f'HP: {new_hp}')
                else:
                    updated_lines.append(line)
            self.party[target_name] = '\n'.join(updated_lines)
        else:
            self.party[target_name] = char_dict
            
        # Add damage event to game state
        if self.game_state:
            if 'combat_log' not in self.game_state:
                self.game_state['combat_log'] = []
            self.game_state['combat_log'].append({
                'target': target_name,
                'damage': damage,
                'attack': attack_desc,
                'new_hp': new_hp,
                'turn': self.game_state.get('turn', 0)
            })

