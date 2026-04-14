import requests
import time
import os
from urllib.parse import urlparse
from warden import Warden

class Scout:
    """Quarantine Swarm Scout - safely fetches public data for analysis."""
    
    def __init__(self):
        self.warden = Warden()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Forest-Scout/1.0 (Sovereign Local AI - https://github.com/StellarRequiem/forest-ai-organism)'
        })
        print("🔍 Scout initialized - safe public data mining ready")
    
    def safe_fetch(self, url: str, description: str, timeout: int = 15):
        """Fetch content safely and hand it to Warden for isolation."""
        print(f"🔍 Scout fetching: {description} from {url}")
        
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            content = response.text[:50000]  # Limit size for safety
            
            # Hand to Warden for isolation and analysis
            isolated_result = self.warden.isolate_and_run(
                f"# Fetched content from {url}\n# Description: {description}\n\nprint('Content length:', len('''{content}'''))\n# TODO: Add real analysis here",
                f"Scouted content: {description}"
            )
            
            return {
                "status": "fetched",
                "url": url,
                "content_length": len(content),
                "warden_result": isolated_result
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def burn_all(self):
        """Clean up all quarantined files."""
        self.warden.burn("quarantine_swarm/isolation")

# Quick test - safe public fetch example
if __name__ == "__main__":
    scout = Scout()
    # Test with a safe, public security-related page (no malicious code)
    result = scout.safe_fetch(
        "https://raw.githubusercontent.com/ublockorigin/uAssets/master/filters/privacy.txt",
        "uBlock Origin privacy filter list - safe reference"
    )
    print(result)
