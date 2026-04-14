import re
from warden import Warden

class Dissector:
    """Quarantine Swarm Dissector - safely analyzes fetched code for dangerous patterns."""
    
    def __init__(self):
        self.warden = Warden()
        print("🔬 Dissector initialized - ready to analyze quarantined content")
    
    def dissect(self, content: str, description: str):
        """Analyze content for dangerous patterns and decide if it's safe to rebuild."""
        print(f"🔬 Dissector analyzing: {description}")
        
        dangerous_patterns = [
            r'exec\(', r'eval\(', r'subprocess', r'os\.system', r'__import__',
            r'requests\.post', r'urllib', r'socket', r'open\(', r'write\(',
            r'requestIdleCallback', r'fingerprint', r'telemetry'
        ]
        
        findings = []
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append(pattern)
        
        risk_level = "high" if len(findings) > 3 else "medium" if findings else "low"
        
        result = {
            "description": description,
            "risk_level": risk_level,
            "dangerous_patterns_found": findings,
            "safe_to_rebuild": risk_level == "low",
            "recommendation": "Burn immediately" if risk_level == "high" else "Safe to rebuild after review" if risk_level == "medium" else "Safe"
        }
        
        print(f"Dissector result: Risk={risk_level}, Patterns found={len(findings)}")
        return result
    
    def rebuild_safe_part(self, content: str, description: str):
        """Rebuild only safe parts into a new Forest tool (placeholder for now)."""
        if not self.dissect(content, description)["safe_to_rebuild"]:
            print("🛑 Rebuild blocked - high risk")
            return None
        
        print(f"🔨 Rebuilding safe parts from {description} into new Forest tool...")
        # In real version this would generate a new Lvl1 worker class
        return f"New tool created from {description} (safe rebuild complete)"

# Quick test
if __name__ == "__main__":
    dissector = Dissector()
    test_content = "print('safe code') # no dangerous patterns"
    result = dissector.dissect(test_content, "Safe test code")
    print(result)
