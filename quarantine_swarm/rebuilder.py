from .dissector import Dissector

class Rebuilder:
    """Rebuilder - turns safe dissected content into new Forest tools."""
    
    def __init__(self):
        self.dissector = Dissector()
        print("🔨 Rebuilder initialized - ready to create new Forest tools from safe content")
    
    def rebuild(self, content: str, description: str):
        """Analyze with Dissector and rebuild if safe."""
        analysis = self.dissector.dissect(content, description)
        
        if not analysis["safe_to_rebuild"]:
            print(f"🛑 Rebuild blocked for {description}: {analysis['recommendation']}")
            return None
        
        print(f"🔨 Rebuilding safe content from {description}...")
        
        new_tool_name = description.replace(" ", "_").lower()[:40]
        print(f"✅ New tool stub created: {new_tool_name}")
        
        return {
            "status": "rebuilt",
            "new_tool_name": new_tool_name,
            "source_description": description,
            "risk_level": analysis["risk_level"]
        }

# Quick test
if __name__ == "__main__":
    rebuilder = Rebuilder()
    safe_content = "print('This is safe code for a new privacy tool')"
    result = rebuilder.rebuild(safe_content, "Safe privacy filter example")
    print(result)
