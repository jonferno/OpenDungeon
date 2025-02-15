
# OpenDungeon


OpenDungeon is a PyQT-based application that delivers an immersive Dungeons \& Dragons experience using advanced AI tools. The Dungeon Master is fully controlled by an LLM of your choice from OpenRouter, and each NPC can be individually configured with its own LLM. Generate and save complete parties—with all normal D\&D details—seamlessly integrated with dynamic image and voice enhancements.


## Features

- **Customizable Dungeon Master**: The DM is entirely controlled by an LLM selected from OpenRouter, offering flexible narrative styles.
- **Dynamic NPC Configuration**: Configure each NPC with separate LLM choices in the settings for varied character interactions.
- **Full Party Generation and Management**: Generate and save parties complete with normal Dungeons \& Dragons stats and details.
- **Advanced DM Logic**: The Dungeon Master LLM understands complex game logic, though it is still in the process of being perfected.
- **Visual Enhancements**: Integrates FLUX.1 image generation via Playwright. Webshare proxies (1GB free) are used to avoid generation limits, ensuring smooth portrait creation.
- **Realistic Image Generation**: Each portrait typically takes about a minute to generate, with plans to add an option for image generation with every DM message to enhance scene ambience.
- **Seamless API Integration**: Easily add all API keys in the settings—no hassle.
- **Immersive Voice Feedback**: Utilizes free Azure TTS with excellent neural voice options for a captivating auditory experience.


## Requirements

- Python 3.10+
- API access for OpenRouter, Azure TTS, FLUX.1, and Webshare


## Installation

1. **Clone the repository**:

```
git clone https://github.com/jonferno/OpenDungeon.git
cd OpenDungeon
```

2. **Run the installer**:

```
install_app.bat
```
**Subsequent Launches**:
Use `start.bat` to open the application.

## Start your Adventure

1. **Configure API Keys & Proxy Credentials**:
Open the settings and add your API keys for OpenRouter, Azure TTS, and Webshare. Also grab your proxy username and password from webshare and enter it there.

2. **Create Character**:
Go to the character tab and create your character and wait for the portrait to be generated.

3. **Create Party**:
Generate a random party with full Dungeons \& Dragons stats, and save your character details for future adventures.

4. **Generate Party Portraits**(optional):
Go to the party status tab and generate a portrait for each character.

## Contributing

- Contributions are welcome!
- Feel free to submit issues or pull requests to help improve D\&D AI Companion.

Enjoy your enhanced Dungeons \& Dragons adventures with AI-powered storytelling and immersive gameplay!

