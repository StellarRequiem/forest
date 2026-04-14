# core/dify_manager.py
# v5.0 - Clean Dify Manager for RAG + Agent Workflows (fixed)

import requests
import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

class DifyManager:
    def __init__(self, base_url: str = "http://localhost:3000", api_key: str = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("DIFY_API_KEY", "app-")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()

    def check_health(self) -> bool:
        """Check if Dify is running"""
        try:
            r = self.session.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except:
            return False

    def run_rag_query(self, query: str, dataset_id: str = None) -> Dict:
        """Run a RAG query through Dify"""
        if not self.check_health():
            return {"error": "Dify is not running. Start with: cd ~/Forest/dify && docker compose up -d"}
        
        payload = {
            "inputs": {"query": query},
            "response_mode": "blocking",
            "user": "cus_user"
        }
        try:
            r = self.session.post(f"{self.base_url}/v1/chat-messages", json=payload, headers=self.headers)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def trigger_workflow(self, workflow_id: str, inputs: Dict) -> Dict:
        """Trigger a visual workflow in Dify"""
        if not self.check_health():
            return {"error": "Dify not running. Start with docker compose up -d in ~/Forest/dify/"}
        
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": "cus_user"
        }
        try:
            r = self.session.post(f"{self.base_url}/v1/workflows/run", json=payload, headers=self.headers)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def get_status(self) -> Dict:
        return {
            "healthy": self.check_health(),
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key and self.api_key != "app-")
        }

# Simple test
if __name__ == "__main__":
    print("=== Dify Manager Test ===")
    dify = DifyManager()
    print("Dify healthy:", dify.check_health())
    print("Status:", dify.get_status())
    print("\nTo use full features:")
    print("  cd ~/Forest/dify")
    print("  docker compose up -d")
