#!/usr/bin/env python3
"""
Code Validator
Validates generated agent code for safety and correctness
"""

import sys
from pathlib import Path
import ast
import re

FOREST_PATH = Path.home() / "Forest"
sys.path.insert(0, str(FOREST_PATH))


class CodeValidator:
    """Validates agent code before deployment"""
    
    # Forbidden patterns for security
    FORBIDDEN_PATTERNS = [
        r'\bos\.system\b',
        r'\bsubprocess\b',
        r'\bexec\b',
        r'\beval\b',
        r'\b__import__\b',
        r'\bpickle\.loads\b',
        r'\bmarshal\b',
        r'\bopen\(.*[\'"]w',  # write operations
        r'\brm\s+-rf',
        r'\bdrop\s+table',
        r'\bdrop\s+database',
    ]
    
    # Required patterns for valid agents
    REQUIRED_PATTERNS = [
        r'class\s+\w+',  # Must define a class
        r'def\s+execute_task',  # Must have execute_task method
        r'get_middleware',  # Must use middleware
    ]
    
    def __init__(self):
        self.validations_passed = 0
        self.validations_failed = 0
        self.issues = []
    
    def validate(self, code: str, verbose: bool = True) -> dict:
        """
        Validate agent code
        Returns: {
            'valid': bool,
            'score': 0-100,
            'issues': [...],
            'warnings': [...],
            'recommendations': [...]
        }
        """
        
        result = {
            'valid': True,
            'score': 100,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Test 1: Syntax validation
        if not self._validate_syntax(code):
            result['valid'] = False
            result['score'] -= 30
            result['issues'].append("Invalid Python syntax")
        
        # Test 2: Security checks
        security_issues = self._check_security(code)
        if security_issues:
            result['valid'] = False
            result['score'] -= 25
            result['issues'].extend(security_issues)
        
        # Test 3: Required patterns
        missing_patterns = self._check_required_patterns(code)
        if missing_patterns:
            result['score'] -= 20
            result['issues'].extend(missing_patterns)
        
        # Test 4: Code quality
        quality_issues = self._check_code_quality(code)
        if quality_issues:
            result['score'] -= 10
            result['warnings'].extend(quality_issues)
        
        # Test 5: Best practices
        bp_issues = self._check_best_practices(code)
        if bp_issues:
            result['recommendations'].extend(bp_issues)
        
        # Ensure score is valid
        result['score'] = max(0, min(100, result['score']))
        
        # Update tracking
        if result['valid']:
            self.validations_passed += 1
        else:
            self.validations_failed += 1
        
        if verbose:
            self._print_validation_report(result)
        
        return result
    
    def _validate_syntax(self, code: str) -> bool:
        """Check if code is valid Python"""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.issues.append(f"Syntax error: {str(e)}")
            return False
    
    def _check_security(self, code: str) -> list:
        """Check for security violations"""
        issues = []
        
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Forbidden pattern detected: {pattern}")
        
        # Check for dangerous imports
        if 'import os' in code and 'os.system' not in code:
            pass  # os is ok if not using system
        
        return issues
    
    def _check_required_patterns(self, code: str) -> list:
        """Check for required patterns"""
        missing = []
        
        for pattern in self.REQUIRED_PATTERNS:
            if not re.search(pattern, code):
                missing.append(f"Missing required pattern: {pattern}")
        
        return missing
    
    def _check_code_quality(self, code: str) -> list:
        """Check code quality metrics"""
        issues = []
        
        lines = code.split('\n')
        
        # Check line length
        long_lines = [i for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            issues.append(f"Lines too long (>120 chars): {len(long_lines)} lines")
        
        # Check for missing docstrings
        if not re.search(r'""".*?"""', code, re.DOTALL):
            issues.append("Missing module docstring")
        
        # Check indentation consistency
        if not self._check_indentation(code):
            issues.append("Inconsistent indentation")
        
        return issues
    
    def _check_indentation(self, code: str) -> bool:
        """Check if indentation is consistent"""
        try:
            ast.parse(code)
            return True
        except IndentationError:
            return False
    
    def _check_best_practices(self, code: str) -> list:
        """Check best practices"""
        recommendations = []
        
        # Check for type hints
        if 'def ' in code and '->' not in code:
            recommendations.append("Consider adding type hints to function definitions")
        
        # Check for error handling
        if 'try:' not in code:
            recommendations.append("Consider adding error handling (try/except blocks)")
        
        # Check for logging
        if 'print(' in code and 'logging' not in code:
            recommendations.append("Consider using logging instead of print()")
        
        return recommendations
    
    def _print_validation_report(self, result: dict):
        """Print validation report"""
        
        status = "✅ PASS" if result['valid'] else "❌ FAIL"
        print(f"\n{status} - Score: {result['score']}/100")
        
        if result['issues']:
            print(f"\n⚠️  Issues ({len(result['issues'])}):")
            for issue in result['issues']:
                print(f"  - {issue}")
        
        if result['warnings']:
            print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
        
        if result['recommendations']:
            print(f"\n💡 Recommendations ({len(result['recommendations'])}):")
            for rec in result['recommendations']:
                print(f"  - {rec}")
    
    def get_stats(self) -> dict:
        """Get validation statistics"""
        total = self.validations_passed + self.validations_failed
        return {
            'total_validations': total,
            'passed': self.validations_passed,
            'failed': self.validations_failed,
            'pass_rate': self.validations_passed / total if total > 0 else 0
        }


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("CODE VALIDATOR - TEST")
    print("=" * 80)
    
    validator = CodeValidator()
    
    # Test 1: Valid code
    print("\n[TEST 1] Validating good code...")
    good_code = '''#!/usr/bin/env python3
"""Valid agent code"""

import sys
from pathlib import Path

def execute_task(task: str) -> dict:
    """Execute a task safely"""
    return {'status': 'SUCCESS', 'task': task}

class MyAgent:
    """A valid agent"""
    
    def __init__(self):
        self.middleware = get_middleware()
    
    def execute_task(self, task: str) -> dict:
        """Execute task"""
        try:
            result = execute_task(task)
            return result
        except Exception as e:
            return {'status': 'FAILED', 'error': str(e)}
'''
    
    result1 = validator.validate(good_code)
    print(f"  Score: {result1['score']}/100")
    print(f"  Valid: {result1['valid']}")
    
    # Test 2: Invalid code (security issue)
    print("\n[TEST 2] Validating code with security issue...")
    bad_code = '''
class BadAgent:
    def execute_task(self):
        os.system("rm -rf /tmp")
'''
    
    result2 = validator.validate(bad_code)
    print(f"  Score: {result2['score']}/100")
    print(f"  Valid: {result2['valid']}")
    
    # Test 3: Invalid syntax
    print("\n[TEST 3] Validating code with syntax error...")
    syntax_error_code = '''
class BrokenAgent
    def method(self)
        pass
'''
    
    result3 = validator.validate(syntax_error_code)
    print(f"  Score: {result3['score']}/100")
    print(f"  Valid: {result3['valid']}")
    
    # Test 4: Stats
    print("\n[TEST 4] Validation statistics...")
    stats = validator.get_stats()
    print(f"  Total validations: {stats['total_validations']}")
    print(f"  Passed: {stats['passed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Pass rate: {stats['pass_rate']:.1%}")
    
    print("\n" + "=" * 80)
    print("✅ CODE VALIDATOR READY")
    print("=" * 80 + "\n")
