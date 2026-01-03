# Contributing to Stinger V2

Thank you for your interest in contributing to Stinger V2! This document provides guidelines for contributing to the project.

## 🎯 Philosophy

**Diamond Hands. No Shortcuts. No Jeets.**

This project values:
- **Quality over speed** — We don't ship quick fixes
- **Sovereignty** — Data stays on your infrastructure
- **Verifiability** — Every claim can be proven
- **Clinical accuracy** — Medical AI must be correct

## 🏗️ Architecture

Before contributing, understand the architecture:

```
Client → Stinger → QueenBee → Bumble70B → PDF → Client
         (Gateway)  (Prompts)   (70B)     (Report)
```

Each component has an ENS identity:
- `stinger.swarmbee.eth` — Gateway
- `queenbee.swarmbee.eth` — Prompt orchestrator
- `bumble.swarmbee.eth` — Inference
- `swarmpool.swarmbee.eth` — Ledger
- `merlin.swarmbee.eth` — Signer

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip
- Git

### Setup

```bash
# Clone the repo
git clone https://github.com/swarmhealth/stinger-v2.git
cd stinger-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/
```

## 📝 Making Changes

### Branch Naming

- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation
- `refactor/` — Code refactoring

Example: `feature/ecg-foundation-encoder`

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `refactor` — Code refactoring
- `test` — Tests
- `chore` — Maintenance

Example:
```
feat(parser): add support for WFDB ECG format

Added WFDB format detection and parsing to the ECG parser.
This enables ingestion of PhysioNet ECG datasets.

Closes #42
```

### Code Style

- Use `black` for formatting
- Use `ruff` for linting
- Type hints are required
- Docstrings follow Google style

```bash
# Format
black stinger/

# Lint
ruff check stinger/

# Type check
mypy stinger/
```

## 🧪 Testing

All changes must include tests:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=stinger

# Run specific test
python -m pytest tests/test_e2e.py -v
```

### Test Requirements

- Unit tests for new functions
- Integration tests for new endpoints
- E2E tests for pipeline changes

## 📦 Pull Requests

1. Fork the repo
2. Create a branch
3. Make changes
4. Run tests
5. Submit PR

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted with `black`
- [ ] No `ruff` warnings
- [ ] Docstrings for new functions
- [ ] CHANGELOG updated (if user-facing)
- [ ] README updated (if applicable)

## 🔐 Security

**Never commit:**
- Private keys
- API tokens
- Patient data
- Model weights (use LFS or external storage)

If you find a security issue, email security@trustcat.ai privately.

## 📋 Areas for Contribution

### High Priority

- [ ] Vision encoder (Medical-ViT)
- [ ] ECG transformer (signal encoder)
- [ ] CGM transformer (time series)
- [ ] Additional gold prompts
- [ ] Kubernetes Helm charts

### Documentation

- API documentation
- Deployment guides
- Clinical validation guides

### Testing

- More unit tests
- Performance benchmarks
- Clinical validation test cases

## 💬 Communication

- **GitHub Issues** — Bug reports, feature requests
- **GitHub Discussions** — Questions, ideas
- **Matrix** — Real-time chat (coming soon)

## 📜 License

By contributing, you agree that your contributions will be licensed under Apache 2.0.

---

💎 **Diamond Hands. Full Stack. No Jeets.** 💎
