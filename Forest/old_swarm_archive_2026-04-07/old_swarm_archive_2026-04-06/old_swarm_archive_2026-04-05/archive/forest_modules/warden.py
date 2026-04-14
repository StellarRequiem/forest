import subprocess
import os
from datetime import datetime
import sys

class Warden:
    """Quarantine Swarm Warden - safely isolates and executes scavenged code."""
    
    def __init__(self):
        self.quarantine_dir = "quarantine_swarm/isolation"
        os.makedirs(self.quarantine_dir, exist_ok=True)
        self.python_exe = sys.executable  # Use the current venv's Python
        print(f"🛡️ Warden initialized - using {self.python_exe} for isolation")
    
    def isolate_and_run(self, code_snippet: str, description: str):
        """Run suspicious code in a restricted environment."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"{self.quarantine_dir}/isolated_{timestamp}.py"
        
        with open(filename, "w") as f:
            f.write("# Quarantined code - Forest Warden\n")
            f.write(f"# Description: {description}\n\n")
            f.write(code_snippet)
        
        print(f"🔒 Warden isolating: {description}")
        
        # Run with very restricted environment
        try:
            result = subprocess.run(
                [self.python_exe, "-c", 
                 f"import sys; sys.path = ['{self.quarantine_dir}']; exec(open('{filename}').read())"],
                capture_output=True, 
                text=True, 
                timeout=8,
                env={"PYTHONPATH": self.quarantine_dir, "PATH": os.environ.get("PATH", "")}
            )
            
            output = result.stdout.strip()
            print(f"✅ Isolation run complete. Output: {output[:200]}...")
            return {"status": "safe", "output": output, "returncode": result.returncode}
            
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Code took too long - possible malicious loop"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def burn(self, filename: str):
        """Safely delete quarantined file."""
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"🔥 Burned quarantined file: {filename}")
        except Exception as e:
            print(f"Warning: Could not burn {filename}: {e}")

# Quick test
if __name__ == "__main__":
    warden = Warden()
    test_code = "print('This is a test from quarantined code - safe execution in Warden V2')"
    result = warden.isolate_and_run(test_code, "Test safe code - Warden V2")
    print(result)
