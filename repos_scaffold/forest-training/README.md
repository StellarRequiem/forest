# forest-training

![Build](https://github.com/forest-ai/forest-training/workflows/tests/badge.svg)
![Version](https://img.shields.io/badge/version-1.0.0--alpha-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)

**Forest Training — Automated AI Agent Code Generation & Model Management**

Complete training pipeline for generating production-ready agent code, validating safety and quality, and managing trained models with versioning and deployment tracking.

## Features

- 🤖 **Code Generation**: Generate Python agent code from specifications
- 🔍 **Code Validation**: Security, syntax, and quality checks (0-100 scoring)
- 📈 **Training Loop**: Full cycle with convergence detection
- 📦 **Model Management**: Registry, versioning (semver), deployment tracking
- 🚀 **CI/CD Ready**: GitHub Actions workflow included
- 💾 **Persistent Storage**: All models and metrics saved to ForestVault

## Installation

```bash
pip install forest-training
```

## Quick Start

```python
from forest_training import CodeGenerator, CodeValidator, TrainingLoop, ModelManager

# Generate code
gen = CodeGenerator()
spec = {
    'name': 'threat_detector',
    'tier': 2,
    'role': 'threat detection',
    'capabilities': ['scan', 'classify', 'alert'],
    'behavior': 'Detect security threats',
    'constraints': ['Read-only']
}
result = gen.generate_from_spec(spec)
print(result['code'])  # 100+ lines of agent code

# Validate code
validator = CodeValidator()
validation = validator.validate(result['code'])
print(f"Score: {validation['score']}/100")
print(f"Valid: {validation['valid']}")

# Train with convergence
training = TrainingLoop('threat_detector', max_iterations=10)
training_result = training.run(spec)
print(training.get_report())

# Manage models
manager = ModelManager()
manager.register_model('threat_detector_v1', code_path, spec, metrics)
manager.deploy_model('threat_detector_v1', target='production')
models = manager.list_models()
```

## Components

### Code Generator
Generates production-ready agent code from specifications:
- Ollama LLM integration (phi3:mini, llama3.1:8b)
- Template fallback when Ollama unavailable
- Batch generation support
- Statistics tracking

### Code Validator
Validates generated code with multi-level checks:
- **Syntax**: AST parsing
- **Security**: Forbidden patterns, dangerous imports
- **Quality**: Line length, docstrings, indentation
- **Best Practices**: Type hints, error handling, logging
- **Score**: 0-100 scale

### Training Loop
Orchestrates full training pipeline:
- Generate → Validate → Improve cycle
- Convergence detection (stable scores, improvement tracking)
- Iteration history tracking
- Best code selection and saving

### Model Manager
Manages trained models:
- **Registry**: All models tracked and versioned
- **Versioning**: Semantic versioning (v1.0.0)
- **Deployment**: Production/staging tracking
- **History**: Full deployment audit trail

## Training Scenarios

Built-in scenarios for:
- Network scanning and monitoring
- Phishing detection
- Threat classification
- Log analysis
- Performance optimization

## CI/CD Integration

Trigger training via GitHub Actions:

```bash
git tag train-2026-04-14
git push origin train-2026-04-14
# → Automatically trains agents and releases models
```

Workflow:
1. Starts Ollama service
2. Trains all scenarios
3. Validates all code
4. Generates training reports
5. Creates GitHub Release with models
6. Posts results to workflow summary

## API Reference

### CodeGenerator
```python
gen = CodeGenerator(model="phi3:mini")
result = gen.generate_from_spec(spec)
stats = gen.get_stats()
```

### CodeValidator
```python
validator = CodeValidator()
result = validator.validate(code, verbose=True)
stats = validator.get_stats()
```

### TrainingLoop
```python
training = TrainingLoop('scenario_name', max_iterations=10, convergence_threshold=0.95)
result = training.run(spec)
report = training.get_report()
```

### ModelManager
```python
manager = ModelManager()
manager.register_model(id, code_path, spec, metrics)
manager.deploy_model(id, target='production')
models = manager.list_models()
comparison = manager.compare_models([id1, id2])
history = manager.get_deployment_history()
```

## Testing

```bash
pytest tests/
pytest --cov=forest_training tests/
```

## Examples

See `examples/` for:
- Basic code generation
- Code validation workflow
- Full training loop
- Model management and deployment
- Batch generation

## Documentation

- [Code Generation Guide](docs/generation.md)
- [Validation Rules](docs/validation.md)
- [Training Pipeline](docs/training.md)
- [Model Management](docs/models.md)
- [CI/CD Setup](docs/cicd.md)

## Requirements

- Python 3.10+
- forest-core >= 1.0.0-alpha
- LangChain >= 0.1.0
- Ollama >= 0.1.0 (optional, template fallback available)

## License

MIT

## Contributing

Pull requests welcome. Please see CONTRIBUTING.md

## Support

- Issues: [GitHub Issues](https://github.com/forest-ai/forest-training/issues)
- Discussions: [GitHub Discussions](https://github.com/forest-ai/forest-training/discussions)
