#!/usr/bin/env python3
"""
Training Loop with Code Generation
Full cycle: Generate → Validate → Test → Criticize → Improve → Converge
"""

import sys
from pathlib import Path
from datetime import datetime
import json

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))

from training.generator.code_generator_v3 import CodeGenerator
from training.generator.code_validator import CodeValidator

VAULT_PATH = Path.home() / "ForestVault"
VAULT_PATH.mkdir(exist_ok=True)


class TrainingLoop:
    """Training loop for agent code generation and improvement"""
    
    def __init__(self, scenario_name: str, max_iterations: int = 10, convergence_threshold: float = 0.95):
        self.scenario_name = scenario_name
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        
        self.generator = CodeGenerator()
        self.validator = CodeValidator()
        
        self.iterations = 0
        self.history = []
        self.scores = []
        self.best_code = None
        self.best_score = 0
        
        print(f"[TRAINING] Initialized for scenario: {scenario_name}")
        print(f"  Max iterations: {max_iterations}")
        print(f"  Convergence threshold: {convergence_threshold}")
    
    def run(self, spec: dict) -> dict:
        """Run training loop"""
        
        print(f"\n{'='*80}")
        print(f"TRAINING LOOP: {self.scenario_name}")
        print(f"{'='*80}\n")
        
        for iteration in range(self.max_iterations):
            self.iterations = iteration + 1
            
            print(f"[ITER {self.iterations}] Starting iteration...")
            
            # Step 1: Generate
            print(f"  → Generate code...")
            gen_result = self.generator.generate_from_spec(spec)
            code = gen_result['code']
            
            # Step 2: Validate
            print(f"  → Validate code...")
            val_result = self.validator.validate(code, verbose=False)
            score = val_result['score']
            
            # Track
            self.scores.append(score)
            self.history.append({
                'iteration': self.iterations,
                'score': score,
                'valid': val_result['valid'],
                'issues': len(val_result['issues']),
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"  ✓ Validation score: {score}/100")
            print(f"  ✓ Valid: {val_result['valid']}")
            print(f"  ✓ Issues: {len(val_result['issues'])}")
            
            # Update best
            if score > self.best_score:
                self.best_score = score
                self.best_code = code
                print(f"  📈 New best score: {self.best_score}/100")
            
            # Check convergence
            if self._check_convergence():
                print(f"\n✅ CONVERGED at iteration {self.iterations}")
                print(f"   Final score: {self.best_score}/100")
                break
            
            # Early exit on perfect
            if score >= 95:
                print(f"\n✅ EXCELLENT CODE at iteration {self.iterations}")
                break
        
        # Generate results
        result = self._finalize_results(spec)
        
        return result
    
    def _check_convergence(self) -> bool:
        """Check if training has converged"""
        
        if len(self.scores) < 3:
            return False
        
        # Check if last 3 scores are stable (within 5 points)
        recent = self.scores[-3:]
        spread = max(recent) - min(recent)
        
        if spread < 5 and max(recent) >= self.convergence_threshold * 100:
            return True
        
        # Also check if we're improving too slowly
        if len(self.scores) > 5:
            improvement = self.scores[-1] - self.scores[-5]
            if improvement < 2:  # Less than 2 points in 5 iterations
                return True
        
        return False
    
    def _finalize_results(self, spec: dict) -> dict:
        """Finalize training results"""
        
        # Save best code to file
        code_path = VAULT_PATH / f"{self.scenario_name}_best_v{self.best_score:.0f}.py"
        
        try:
            code_path.write_text(self.best_code)
            print(f"\n✅ Best code saved: {code_path}")
        except Exception as e:
            print(f"\n⚠️ Error saving code: {e}")
        
        # Calculate metrics
        avg_score = sum(self.scores) / len(self.scores) if self.scores else 0
        max_score = max(self.scores) if self.scores else 0
        min_score = min(self.scores) if self.scores else 0
        
        result = {
            'scenario': self.scenario_name,
            'spec': spec,
            'training_complete': True,
            'iterations': self.iterations,
            'convergence': self._check_convergence(),
            'scores': {
                'best': self.best_score,
                'average': avg_score,
                'max': max_score,
                'min': min_score
            },
            'history': self.history,
            'code_file': str(code_path) if self.best_code else None,
            'code_length': len(self.best_code.split('\n')) if self.best_code else 0,
            'completed_at': datetime.now().isoformat()
        }
        
        # Save results to vault
        results_path = VAULT_PATH / f"{self.scenario_name}_results.json"
        
        try:
            with open(results_path, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Results saved: {results_path}")
        except Exception as e:
            print(f"⚠️ Error saving results: {e}")
        
        return result
    
    def get_report(self) -> str:
        """Generate training report"""
        
        report = f"""
{'='*80}
TRAINING REPORT: {self.scenario_name}
{'='*80}

Summary:
  Iterations: {self.iterations}
  Convergence: {'Yes' if self._check_convergence() else 'No'}
  Best Score: {self.best_score}/100

Scores:
  Average: {sum(self.scores) / len(self.scores) if self.scores else 0:.1f}/100
  Maximum: {max(self.scores) if self.scores else 0}/100
  Minimum: {min(self.scores) if self.scores else 0}/100

Code:
  Lines: {len(self.best_code.split(chr(10))) if self.best_code else 0}
  Valid: {'Yes' if self.best_score >= 70 else 'No'}

History:
"""
        
        for h in self.history:
            report += f"  Iter {h['iteration']:2d}: Score {h['score']:3.0f}/100, Valid: {h['valid']}, Issues: {h['issues']}\n"
        
        report += f"\n{'='*80}\n"
        
        return report


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TRAINING LOOP - TEST")
    print("=" * 80)
    
    # Define a training scenario
    scenario = {
        'name': 'network_scanner_agent',
        'tier': 2,
        'role': 'network scanning and security monitoring',
        'capabilities': [
            'scan_network',
            'identify_devices',
            'detect_anomalies',
            'generate_alerts'
        ],
        'behavior': 'Scan network for threats and anomalies',
        'constraints': [
            'Read-only operations',
            'No network modifications',
            'Enforce all decisions through middleware'
        ]
    }
    
    # Run training
    training = TrainingLoop(
        scenario_name='network_scanner',
        max_iterations=5,
        convergence_threshold=0.90
    )
    
    result = training.run(scenario)
    
    # Print report
    print(training.get_report())
    
    # Print result summary
    print("\nTraining Result:")
    print(f"  Scenario: {result['scenario']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Best Score: {result['scores']['best']}/100")
    print(f"  Code Length: {result['code_length']} lines")
    print(f"  Convergence: {result['convergence']}")
    
    print("\n" + "=" * 80)
    print("✅ TRAINING LOOP READY")
    print("=" * 80 + "\n")
