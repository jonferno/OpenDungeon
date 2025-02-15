import os
from pathlib import Path
from ui.utils import aigirl_generator

class CharacterImageHandler:
    def __init__(self, game_manager):
        self.game_manager = game_manager

    def parse_character_data(self, char_data) -> dict:
        """Parse character data from either dictionary or string format"""
        print("\n=== Character Data Debugging ===")
        print(f"Input data type: {type(char_data)}")
        print("Raw character data:")
        print(char_data)
        
        if isinstance(char_data, dict):
            # Try to find backstory in multiple possible locations
            backstory = ""
            
            # Check if this is a character from party data
            if isinstance(char_data, str) or (not char_data.get('backstory') and char_data.get('name')):
                # Try to find the character in the party data
                party_members = self.game_manager.party or {}
                for member_data in party_members.values():
                    if isinstance(member_data, str):
                        if char_data.get('name', '') in member_data:
                            # Found the character in party data, extract backstory
                            lines = member_data.split('\n')
                            collecting_backstory = False
                            for line in lines:
                                if 'Backstory:' in line:
                                    collecting_backstory = True
                                    backstory += line.split('Backstory:', 1)[1].strip() + " "
                                elif collecting_backstory and line.strip() and not any(key in line for key in ['Equipment:', 'Personality:', 'Name:']):
                                    backstory += line.strip() + " "
                                elif collecting_backstory and any(key in line for key in ['Equipment:', 'Personality:', 'Name:']):
                                    collecting_backstory = False
                            break
            
            # If no backstory found in party data, check direct backstory field
            if not backstory and char_data.get('backstory'):
                backstory = char_data['backstory']
            
            print(f"\nExtracted backstory: {backstory}")
            
            parsed_data = {
                'name': char_data.get('name', ''),
                'race': char_data.get('race', ''),
                'class': char_data.get('class', ''),
                'backstory': backstory.strip(),
                'equipment': char_data.get('equipment', [])
            }
            
            print("\nParsed Data:")
            print(f"Name: {parsed_data['name']}")
            print(f"Race: {parsed_data['race']}")
            print(f"Class: {parsed_data['class']}")
            print(f"Backstory: {parsed_data['backstory']}")
            
            return parsed_data
            
        elif isinstance(char_data, str):
            # Handle string format with better debugging
            print("\nParsing string format:")
            lines = char_data.split('\n')
            parsed_data = {
                'name': '',
                'race': '',
                'class': '',
                'backstory': '',
                'equipment': []
            }
            
            in_backstory = False
            backstory_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if 'Backstory:' in line:
                    in_backstory = True
                    backstory_lines.append(line.split('Backstory:', 1)[1].strip())
                elif in_backstory and not any(key in line for key in ['Name:', 'Race:', 'Class:', 'Equipment:']):
                    backstory_lines.append(line)
                elif 'Name:' in line:
                    parsed_data['name'] = line.split('Name:', 1)[1].strip()
                elif 'Race:' in line:
                    parsed_data['race'] = line.split('Race:', 1)[1].strip()
                elif 'Class:' in line:
                    parsed_data['class'] = line.split('Class:', 1)[1].strip()
            
            parsed_data['backstory'] = ' '.join(backstory_lines)
            
            print("\nParsed string data:")
            print(f"Name: {parsed_data['name']}")
            print(f"Race: {parsed_data['race']}")
            print(f"Class: {parsed_data['class']}")
            print(f"Backstory: {parsed_data['backstory'][:200]}...")
            
            return parsed_data
        
        return char_data

    def determine_gender(self, char_data: dict) -> str:
        """Determine gender from character data"""
        backstory = char_data.get('backstory', '').lower()
        print("\n=== Gender Determination Debugging ===")
        print(f"Analyzing backstory ({len(backstory)} chars):")
        print(backstory)
        
        # Female indicators with weights
        female_indicators = {
            'her': 2, 'hers': 2, 'herself': 2,
            'female': 3, 'woman': 3, 'girl': 2,
            'priestess': 3, 'actress': 3, 'queen': 3
        }
        
        # Male indicators with weights
        male_indicators = {
            'his': 2, 'him': 2, 'himself': 2,
            'male': 3, 'boy': 2
        }
        
        # Count and log each found indicator
        print("\nFound gender indicators:")
        female_score = 0
        male_score = 0
        
        for word, weight in female_indicators.items():
            count = backstory.count(word)
            if count > 0:
                female_score += count * weight
                print(f"Female indicator '{word}' found {count} times (weight: {weight})")
                
        for word, weight in male_indicators.items():
            count = backstory.count(word)
            if count > 0:
                male_score += count * weight
                print(f"Male indicator '{word}' found {count} times (weight: {weight})")
        
        print(f"\nFinal scores - Female: {female_score}, Male: {male_score}")
        
        if female_score > male_score:
            return 'female'
        elif male_score > female_score:
            return 'male'
        else:
            name = char_data.get('name', '').strip()
            gender = 'female' if name.endswith(('a', 'ia', 'ra')) else 'male'
            print(f"No clear winner, using name '{name}' to determine: {gender}")
            return gender

    def generate_character_image_prompt(self, character_data):
        """Generate an optimized prompt for the image generator using a consistent template"""
        # Parse character data and determine gender
        char_data = self.parse_character_data(character_data)
        gender = self.determine_gender(char_data)
        
        # Get basic character details
        name = char_data.get('name', 'Unknown')
        race = char_data.get('race', 'Unknown')
        char_class = char_data.get('class', 'Unknown')
        backstory = char_data.get('backstory', '')
        equipment = char_data.get('equipment', [])
        
        # Extract distinctive physical features from backstory
        distinctive_features = []
        if 'scales' in backstory:
            distinctive_features.append('vibrant scales')
        if 'skin' in backstory:
            distinctive_features.append('unique skin color')
        
        # Create prompt for LLM to customize the template
        llm_prompt = f"""Create a character portrait prompt following this exact format but customize it for the character:
"CGI style [gender] [race] [class], [2-3 distinctive physical features], [main equipment/clothing details], 3D cartoon art style, Pixar-inspired, [expression matching personality], [magical/environmental effects based on class/equipment], fantasy background"

Character Details:
Name: {name}
Gender: {gender}
Race: {race}
Class: {char_class}
Equipment: {equipment}
Backstory: {backstory}

Important requirements:
1. Keep the prompt under 60 words
2. Maintain the CGI style and Pixar-inspired elements
3. Include distinctive features specific to their {race} race
4. Make the effects match their {char_class} class and equipment
5. Must specify {gender} in the prompt
6. Keep the cartoon/CGI style description
7. Make background a fantasy environment based on the character.

Example format: "CGI style male dragonborn bard, vibrant blue scales, light green eyes, simple travel-worn clothes, lute on back, beef jerky pouch, 3D cartoon art style, Pixar-inspired, cheerful expression, musical notes surrounding, fantasy background"

Create a similar prompt for this character."""

        try:
            # Get customized prompt from LLM
            response = self.game_manager.get_dm_response_from_api(llm_prompt)
            print(f"Generated prompt: {response}")  # Debug output
            
            # If LLM response is too verbose, use the template directly
            if len(response.split()) > 60:
                # Fallback to direct template
                response = f"CGI style {gender} {race} {char_class}, {', '.join(distinctive_features)}, wearing {', '.join(equipment[:2]) if isinstance(equipment, list) else equipment}, 3D cartoon art style, Pixar-inspired, determined expression, magical effects surrounding, fantasy background"
            
            return response.strip()
            
        except Exception as e:
            print(f"Error getting LLM prompt: {e}")
            # Simple fallback that maintains the style
            return f"CGI style {gender} {race} {char_class}, {', '.join(distinctive_features)}, 3D cartoon art style, Pixar-inspired, fantasy background"

    def generate_and_save_image(self, character_data, save_dir):
        """Generate and save character image with character-specific filename"""
        try:
            # Create save directory if it doesn't exist
            Path(save_dir).mkdir(parents=True, exist_ok=True)
            
            # Create a character-specific filename
            char_name = character_data['name'].replace(' ', '_').lower()
            char_race = character_data['race'].lower()
            char_class = character_data['class'].lower()
            filename = f"{char_name}_{char_race}_{char_class}_portrait.png"
            
            # Full path for the image
            image_path = os.path.join(save_dir, filename)
            
            # Generate optimized prompt
            image_prompt = self.generate_character_image_prompt(character_data)
            
            # Generate image using aigirl_generator
            image_path = aigirl_generator.generate_image(
                image_prompt, 
                image_path  # Now using the character-specific path
            )
            
            return image_path
            
        except Exception as e:
            print(f"Error generating character image: {e}")
            return None

