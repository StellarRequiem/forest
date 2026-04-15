#!/usr/bin/env python3
"""
Model Manager
Manages trained agent models, versioning, and deployment
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import shutil

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

VAULT_PATH = Path.home() / "ForestVault"
MODELS_PATH = VAULT_PATH / "trained_models"
MODELS_PATH.mkdir(parents=True, exist_ok=True)


class ModelManager:
    """Manages trained agent models"""
    
    def __init__(self):
        self.models_path = MODELS_PATH
        self.registry = self._load_registry()
        
        print(f"[MODEL_MANAGER] Initialized - Path: {self.models_path}")
    
    def _load_registry(self) -> dict:
        """Load model registry"""
        registry_path = self.models_path / "registry.json"
        
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'models': {},
            'deployments': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_registry(self):
        """Save model registry"""
        registry_path = self.models_path / "registry.json"
        
        self.registry['last_updated'] = datetime.now().isoformat()
        
        try:
            with open(registry_path, 'w') as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"[MODEL_MANAGER] Error saving registry: {e}")
    
    def register_model(self, model_id: str, code_path: str, spec: dict, metrics: dict) -> dict:
        """Register a trained model"""
        
        # Create model directory
        model_dir = self.models_path / model_id
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy code file
        code_file = model_dir / "agent_code.py"
        try:
            shutil.copy(code_path, code_file)
        except Exception as e:
            print(f"[MODEL_MANAGER] Error copying code: {e}")
            return {'success': False, 'error': str(e)}
        
        # Create metadata
        metadata = {
            'model_id': model_id,
            'version': self._next_version(model_id),
            'registered_at': datetime.now().isoformat(),
            'spec': spec,
            'metrics': metrics,
            'code_file': str(code_file),
            'status': 'registered'
        }
        
        # Save metadata
        metadata_file = model_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Update registry
        self.registry['models'][model_id] = metadata
        self._save_registry()
        
        print(f"[MODEL_MANAGER] Registered model: {model_id}")
        print(f"  Version: {metadata['version']}")
        print(f"  Path: {model_dir}")
        
        return {
            'success': True,
            'model_id': model_id,
            'version': metadata['version'],
            'metadata': metadata
        }
    
    def _next_version(self, model_id: str) -> str:
        """Get next version number"""
        
        existing = [m for m in self.registry['models'].values() if m.get('model_id') == model_id]
        
        if not existing:
            return "v1.0.0"
        
        # Simple versioning: v1.0.0 → v1.0.1 → v1.1.0 → v2.0.0
        versions = [m['version'] for m in existing]
        
        # Parse latest version
        if versions:
            latest = versions[-1]
            parts = latest.replace('v', '').split('.')
            
            if len(parts) >= 3:
                major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
                patch += 1
                return f"v{major}.{minor}.{patch}"
        
        return "v1.0.0"
    
    def deploy_model(self, model_id: str, target: str = "production") -> dict:
        """Deploy a model"""
        
        if model_id not in self.registry['models']:
            return {'success': False, 'error': 'Model not found'}
        
        model_info = self.registry['models'][model_id]
        
        deployment = {
            'model_id': model_id,
            'version': model_info['version'],
            'target': target,
            'deployed_at': datetime.now().isoformat(),
            'status': 'deployed'
        }
        
        self.registry['deployments'].append(deployment)
        
        # Update model status
        model_info['status'] = 'deployed'
        model_info['deployment_time'] = deployment['deployed_at']
        
        self._save_registry()
        
        print(f"[MODEL_MANAGER] Deployed {model_id} (v{model_info['version']}) to {target}")
        
        return {
            'success': True,
            'deployment': deployment
        }
    
    def get_model(self, model_id: str) -> dict:
        """Get model information"""
        
        if model_id not in self.registry['models']:
            return None
        
        model_info = self.registry['models'][model_id]
        
        # Load code if requested
        code_file = Path(model_info['code_file'])
        if code_file.exists():
            with open(code_file, 'r') as f:
                code = f.read()
            model_info['code'] = code
        
        return model_info
    
    def list_models(self) -> list:
        """List all registered models"""
        
        models = []
        for model_id, model_info in self.registry['models'].items():
            models.append({
                'model_id': model_id,
                'version': model_info['version'],
                'status': model_info.get('status', 'unknown'),
                'registered_at': model_info['registered_at'],
                'metrics': model_info.get('metrics', {})
            })
        
        return models
    
    def compare_models(self, model_ids: list) -> dict:
        """Compare multiple models"""
        
        comparison = {
            'models': [],
            'comparison_date': datetime.now().isoformat()
        }
        
        for model_id in model_ids:
            model = self.get_model(model_id)
            if model:
                comparison['models'].append({
                    'model_id': model_id,
                    'version': model['version'],
                    'metrics': model.get('metrics', {}),
                    'status': model.get('status', 'unknown')
                })
        
        return comparison
    
    def get_deployment_history(self) -> list:
        """Get deployment history"""
        
        return self.registry.get('deployments', [])
    
    def get_stats(self) -> dict:
        """Get manager statistics"""
        
        models = list(self.registry['models'].values())
        
        return {
            'total_models': len(models),
            'total_deployments': len(self.registry.get('deployments', [])),
            'by_status': {
                'registered': sum(1 for m in models if m.get('status') == 'registered'),
                'deployed': sum(1 for m in models if m.get('status') == 'deployed'),
                'archived': sum(1 for m in models if m.get('status') == 'archived')
            },
            'latest_deployment': self.registry['deployments'][-1]['deployed_at'] if self.registry.get('deployments') else None
        }


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("MODEL MANAGER - TEST")
    print("=" * 80)
    
    manager = ModelManager()
    
    # Test 1: Create dummy code file
    print("\n[TEST 1] Creating test code file...")
    test_code_path = VAULT_PATH / "test_agent.py"
    test_code_path.write_text("""
class TestAgent:
    def execute_task(self):
        pass
""")
    print(f"  ✅ Created: {test_code_path}")
    
    # Test 2: Register model
    print("\n[TEST 2] Registering models...")
    spec = {
        'name': 'network_scanner',
        'tier': 2,
        'role': 'scanning'
    }
    metrics = {
        'training_score': 92.5,
        'convergence_iterations': 5,
        'validation_pass': True
    }
    
    result = manager.register_model(
        'network_scanner_agent',
        str(test_code_path),
        spec,
        metrics
    )
    print(f"  ✅ Registered: {result['model_id']} (v{result['version']})")
    
    # Test 3: Register another version
    print("\n[TEST 3] Registering second version...")
    result2 = manager.register_model(
        'network_scanner_agent',
        str(test_code_path),
        spec,
        {'training_score': 95.0, 'convergence_iterations': 4}
    )
    print(f"  ✅ Registered: v{result2['version']}")
    
    # Test 4: Deploy model
    print("\n[TEST 4] Deploying models...")
    deploy = manager.deploy_model('network_scanner_agent', target='production')
    print(f"  ✅ Deployed to {deploy['deployment']['target']}")
    
    # Test 5: List models
    print("\n[TEST 5] Listing models...")
    models = manager.list_models()
    for model in models:
        print(f"  - {model['model_id']} (v{model['version']}): {model['status']}")
    
    # Test 6: Compare models
    print("\n[TEST 6] Model comparison...")
    comparison = manager.compare_models(['network_scanner_agent'])
    print(f"  Comparing {len(comparison['models'])} models")
    
    # Test 7: Stats
    print("\n[TEST 7] Manager statistics...")
    stats = manager.get_stats()
    print(f"  Total models: {stats['total_models']}")
    print(f"  Total deployments: {stats['total_deployments']}")
    print(f"  By status: {stats['by_status']}")
    
    print("\n" + "=" * 80)
    print("✅ MODEL MANAGER READY")
    print("=" * 80 + "\n")
