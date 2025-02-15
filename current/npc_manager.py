import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class NPCManager:
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Get the path relative to the current script
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.npc_path = os.path.join(base_path, "npcs")
        self.memory_path = os.path.join(self.npc_path, "memory")
        self.models_path = os.path.join(self.npc_path, "models")
        
        # Create necessary directories
        for path in [self.npc_path, self.memory_path, self.models_path]:
            os.makedirs(path, exist_ok=True)
    
    def save_npc_model(self, npc_name: str, model: str):
        """Save the model preference for an NPC"""
        filepath = os.path.join(self.models_path, f"{npc_name.lower()}_model.json")
        with open(filepath, 'w') as f:
            json.dump({"model": model, "updated_at": datetime.now().isoformat()}, f)
    
    def get_npc_model(self, npc_name: str, default_model: str) -> str:
        """Get the preferred model for an NPC"""
        filepath = os.path.join(self.models_path, f"{npc_name.lower()}_model.json")
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data["model"]
        except (FileNotFoundError, json.JSONDecodeError):
            return default_model
    
    def save_npc_memory(self, npc_name: str, memory_type: str, content: Dict):
        """Save a memory entry for an NPC"""
        # Sanitize the NPC name for file system
        safe_name = "".join(c for c in npc_name if c.isalnum() or c in ('-', '_'))
        npc_memory_path = os.path.join(self.memory_path, safe_name)
        os.makedirs(npc_memory_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(npc_memory_path, f"{memory_type}_{timestamp}.json")
        
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "type": memory_type,
                "content": content
            }, f, indent=2)
    
    def get_npc_memories(self, npc_name: str, memory_type: Optional[str] = None) -> List[Dict]:
        """Get all memories for an NPC, optionally filtered by type"""
        npc_memory_path = os.path.join(self.memory_path, npc_name.lower())
        if not os.path.exists(npc_memory_path):
            return []
        
        memories = []
        for filename in os.listdir(npc_memory_path):
            if filename.endswith('.json'):
                if memory_type and not filename.startswith(f"{memory_type}_"):
                    continue
                    
                with open(os.path.join(npc_memory_path, filename), 'r') as f:
                    memories.append(json.load(f))
        
        return sorted(memories, key=lambda x: x['timestamp'])
