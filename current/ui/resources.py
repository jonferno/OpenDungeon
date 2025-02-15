import os
from PyQt5.QtGui import QFontDatabase

def load_fonts(base_path):
    """Load all custom fonts from the fonts directory"""
    fonts_dir = os.path.join(base_path, 'fonts')
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)
        
    font_files = {
        'MedievalSharp': 'MedievalSharp-Regular.ttf',
    }
    
    loaded_fonts = {}
    for font_name, font_file in font_files.items():
        font_path = os.path.join(fonts_dir, font_file)
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id >= 0:
                loaded_fonts[font_name] = font_id
            else:
                print(f"Failed to load font: {font_name}")
                
    return loaded_fonts
