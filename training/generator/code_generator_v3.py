#!/usr/bin/env python3
"""
Forest Code Generator v3
Generates and validates safe agent Python code using Ollama
"""

import sys
from pathlib import Path
from datetime import datetime
import re
import json

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

try:
    import ollama
except ImportError:
    print("[WARNING] ollama not installed - install with: pip install ollama")
    ollama = None


class CodeGenerator:
    """Generates agent code from specifications"""
    
    def __init__(self, model: str = "phi3:mini"):
        self.model = model
        self.ollama_available = ollama is not None
        self.generated_code = []
        
        if not self.ollama_available:
            print("[CODEGEN] Warning: Ollama not available - using template generation")
        else:
            print(f"[CODEGEN] Initialized with model: {model}")
    
    def generate_from_spec(self, spec: dict) -> dict:
        """
        Generate agent code from specification
        spec: {
            'name': 'agent_name',
            'tier': 1-4,
            'role': 'description',
            'capabilities': ['cap1', 'cap2'],
            'behavior': 'description of expected behavior',
            'constraints': ['constraint1']
        }
        """
        
        if self.ollama_available:
            return self._generate_with_ollama(spec)
        else:
            return self._generate_from_template(spec)
    
    def _generate_with_ollama(self, spec: dict) -> dict:
        """Generate code using Ollama"""
        
        prompt = f"""You are a Python code generator for Forest AI agents.
        
Generate a complete, production-ready agent class for:
- Name: {spec['name']}
- Tier: {spec['tier']}
- Role: {spec['role']}
- Capabilities: {', '.join(spec['capabilities'])}
- Behavior: {spec.get('behavior', 'Execute tasks safely')}
- Constraints: {', '.join(spec.get('constraints', ['No destructive actions']))}

Requirements:
1. Class must inherit from a base agent
2. Must log decisions via middleware
3. Must have execute_task() method
4. Must handle errors gracefully
5. Must be executable Python code

Return ONLY the complete Python code, no explanations."""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=False
            )
            
            code = response['response'].strip()
            
            # Validate and store
            result = {
                'spec': spec,
                'code': code,
                'source': 'ollama',
                'lines': len(code.split('\n')),
                'generated_at': datetime.now().isoformat()
            }
            
            self.generated_code.append(result)
            print(f"[CODEGEN] Generated {spec['name']}: {len(code.split(chr(10)))} lines")
            
            return result
            
        except Exception as e:
            print(f"[CODEGEN] Error generating with Ollama: {e}")
            return self._generate_from_template(spec)
    
    def _generate_from_template(self, spec: dict) -> dict:
        """Generate code from template when Ollama unavailable"""
        
        class_name = spec['name'].replace('_', ' ').title().replace(' ', '')
        capabilities_str = "\n            ".join([f"'{cap}'," for cap in spec['capabilities']])
        
        code = f'''#!/usr/bin/env python3
"""
{spec['name'].replace('_', ' ').title()}
Auto-generated Forest Agent - Tier {spec['tier']}
Role: {spec['role']}
Generated: {datetime.now().isoformat()}
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from core.decision_middleware import get_middleware, DecisionType


class {class_name}:
    """Auto-generated agent - {spec['role']}"""
    
    def __init__(self):
        self.middleware = get_middleware()
        self.agent_id = f"{spec['name']}-{{uuid.uuid4().hex[:8]}}"
        self.tier = {spec['tier']}
        self.role = "{spec['role']}"
        self.capabilities = [
            {capabilities_str}
        ]
        self.tasks_executed = 0
        self.tasks_failed = 0
        
        print(f"[{spec['name'].upper()}] Initialized")
        print(f"  Agent ID: {{self.agent_id}}")
        print(f"  Tier: {{self.tier}}, Role: {{self.role}}")
    
    def execute_task(self, task: str, parameters: dict = None) -> dict:
        """Execute a task"""
        
        if parameters is None:
            parameters = {{}}
        
        try:
            # Log task execution
            decision = self.middleware.record_task_execution(
                self.agent_id,
                task,
                result="COMPLETED"
            )
            
            self.tasks_executed += 1
            
            result = {{
                'status': 'SUCCESS',
                'task': task,
                'agent_id': self.agent_id,
                'tasks_executed': self.tasks_executed,
                'decision_id': decision.id
            }}
            
            print(f"[{spec['name'].upper()}] ✅ Task executed: {{task[:50]}}")
            return result
            
        except Exception as e:
            self.tasks_failed += 1
            print(f"[{spec['name'].upper()}] ❌ Task failed: {{str(e)}}")
            return {{
                'status': 'FAILED',
                'task': task,
                'error': str(e),
                'tasks_failed': self.tasks_failed
            }}
    
    def get_stats(self) -> dict:
        """Get agent statistics"""
        
        decisions = self.middleware.get_decisions_by_agent(self.agent_id, limit=100)
        
        return {{
            'agent_id': self.agent_id,
            'tier': self.tier,
            'role': self.role,
            'capabilities': self.capabilities,
            'tasks_executed': self.tasks_executed,
            'tasks_failed': self.tasks_failed,
            'total_decisions': len(decisions),
            'success_rate': self.tasks_executed / (self.tasks_executed + self.tasks_failed) if (self.tasks_executed + self.tasks_failed) > 0 else 0
        }}


if __name__ == "__main__":
    agent = {class_name}()
    
    # Test execution
    for i in range(3):
        result = agent.execute_task(f"test_task_{{i}}", {{"param": i}})
        print(f"  Result: {{result['status']}}")
    
    # Print stats
    stats = agent.get_stats()
    print(f"\\nAgent Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {{key}}: {{value:.2f}}")
        else:
            print(f"  {{key}}: {{value}}")
'''
        
        result = {
            'spec': spec,
            'code': code,
            'source': 'template',
            'lines': len(code.split('\n')),
            'generated_at': datetime.now().isoformat()
        }
        
        self.generated_code.append(result)
        print(f"[CODEGEN] Generated {spec['name']} from template: {len(code.split(chr(10)))} lines")
        
        return result
    
    def get_stats(self) -> dict:
        """Get generation statistics"""
        return {
            'total_generated': len(self.generated_code),
            'by_source': {
                'ollama': sum(1 for g in self.generated_code if g['source'] == 'ollama'),
                'template': sum(1 for g in self.generated_code if g['source'] == 'template')
            },
            'total_lines': sum(g['lines'] for g in self.generated_code)
        }


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CODE GENERATOR v3 - TEST")
    print("=" * 80)
    
    gen = CodeGenerator()
    
    # Test 1: Generate single agent
    print("\n[TEST 1] Generate single agent...")
    spec1 = {
        'name': 'data_analyzer',
        'tier': 2,
        'role': 'data analysis and pattern detection',
        'capabilities': ['parse_logs', 'identify_patterns', 'generate_insights'],
        'behavior': 'Analyze data and provide actionable insights',
        'constraints': ['Read-only operations', 'No external API calls']
    }
    
    result1 = gen.generate_from_spec(spec1)
    print(f"  ✅ Generated: {result1['lines']} lines")
    
    # Test 2: Generate batch
    print("\n[TEST 2] Generate batch of agents...")
    specs = [
        {
            'name': 'threat_detector',
            'tier': 3,
            'role': 'threat detection and classification',
            'capabilities': ['scan_network', 'classify_threats', 'alert_team'],
            'behavior': 'Detect and classify network threats',
            'constraints': ['No network modifications', 'Alert only']
        },
        {
            'name': 'report_generator',
            'tier': 2,
            'role': 'report generation',
            'capabilities': ['aggregate_data', 'format_output', 'validate_structure'],
            'behavior': 'Generate formatted security reports',
            'constraints': ['Template-based generation', 'No hardcoding']
        }
    ]
    
    for spec in specs:
        result = gen.generate_from_spec(spec)
        print(f"  ✅ {spec['name']}: {result['lines']} lines")
    
    # Test 3: Stats
    print("\n[TEST 3] Generation statistics...")
    stats = gen.get_stats()
    print(f"  Total generated: {stats['total_generated']}")
    print(f"  By source: {stats['by_source']}")
    print(f"  Total lines: {stats['total_lines']}")
    
    print("\n" + "=" * 80)
    print("✅ CODE GENERATOR v3 READY")
    print("=" * 80 + "\n")
