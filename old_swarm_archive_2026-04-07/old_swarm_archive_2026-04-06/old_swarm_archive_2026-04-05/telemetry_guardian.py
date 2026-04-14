import re
import subprocess
import psutil
import os
from lvl1_worker import Lvl1Worker

class TelemetryGuardian(Lvl1Worker):
    """Upgraded Telemetry Guardian - real privacy defense for the Living Forest."""
    
    def perform_task(self, task: str):
        print(f"[Telemetry Guardian] Starting deep privacy scan: {task}")
        
        findings = []
        recommendations = []
        
        # 1. Process telemetry detection
        suspicious_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'] or ''
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(term in (name + cmdline).lower() for term in ['telemetry', 'beacon', 'tracking', 'fingerprint', 'cloudtelemetry', 'usagetracking']):
                    suspicious_processes.append(name)
            except:
                pass
        
        if suspicious_processes:
            findings.append(f"Suspicious telemetry processes: {suspicious_processes}")
            recommendations.append("Investigate and consider disabling CloudTelemetryService / UsageTrackingAgent")
        
        # 2. Browser extensions check (Chrome/Edge common paths)
        browser_paths = [
            "~/Library/Application Support/Google/Chrome/Default/Extensions",
            "~/Library/Application Support/Microsoft Edge/Default/Extensions",
            "~/Library/Application Support/Firefox/Profiles"
        ]
        for path in browser_paths:
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                findings.append(f"Browser extensions directory detected: {expanded}")
                recommendations.append("Manually review extensions for fingerprinting/tracking behavior")
        
        # 3. Network beacon / telemetry check
        try:
            connections = psutil.net_connections(kind='inet')
            if len(connections) > 60:
                findings.append(f"High network activity ({len(connections)} connections) - possible beacons")
                recommendations.append("Monitor for frequent connections during idle periods")
        except:
            pass
        
        # 4. Pattern detection from task
        patterns = ['requestIdleCallback', 'offscreen', 'hidden.*pixel', 'fingerprint', 'extension.*scan', 
                    'telemetry', 'beacon', 'tracking.*pixel', 'idle.*callback', 'silent.*scan']
        detected_patterns = [p for p in patterns if re.search(p, task.lower())]
        if detected_patterns:
            findings.append(f"Detected tracking patterns: {detected_patterns}")
        
        # Final result
        result = f"Telemetry Guardian deep scan complete.\n" \
                 f"Findings: {len(findings)} items.\n" \
                 f"Key detections: {findings[:5]}{'...' if len(findings)>5 else ''}\n" \
                 f"Recommendations:\n" + "\n".join([f"• {rec}" for rec in recommendations[:5]])
        
        print(f"→ {result}")
        return result

if __name__ == "__main__":
    guardian = TelemetryGuardian()
    guardian.perform_task("Analyze for LinkedIn Project Handshake style tracking and telemetry patterns")
