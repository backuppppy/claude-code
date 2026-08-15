# Spec-Kit Scripts

**Source:** https://github.com/github/spec-kit

GitHub's spec-kit is a comprehensive toolkit for managing specifications and features. This directory contains both Bash and Python implementations of spec-kit utilities.

## 📂 Directory Structure

```
spec-kit/
├── bash/           ← Shell script implementations
│   ├── check-prerequisites.sh
│   ├── common.sh
│   ├── create-new-feature.sh
│   ├── resolve-template.sh
│   ├── setup-plan.sh
│   └── setup-tasks.sh
└── python/         ← Python implementations
    ├── check_prerequisites.py
    ├── common.py
    ├── create_new_feature.py
    ├── resolve_template.py
    ├── setup_plan.py
    └── setup_tasks.py
```

## 🎯 Main Scripts

### check-prerequisites / check_prerequisites
Verifies that your environment meets all required dependencies.

```bash
# Bash version
bash scripts/spec-kit/bash/check-prerequisites.sh

# Python version
python scripts/spec-kit/python/check_prerequisites.py
```

### create-new-feature / create_new_feature
Scaffolds a new feature with proper structure and templates.

```bash
# Bash version
bash scripts/spec-kit/bash/create-new-feature.sh "my-feature-name"

# Python version
python scripts/spec-kit/python/create_new_feature.py "my-feature-name"
```

### common / common
Shared utilities used by other scripts (don't run directly).

### setup-plan / setup_plan
Creates and manages setup plans for orchestrating complex tasks.

### setup-tasks / setup_tasks
Manages task configuration and execution.

### resolve-template / resolve_template
Resolves template variables and placeholders.

## 🔧 Usage Examples

### Environment Validation
```bash
# Check if all prerequisites are met
./scripts/spec-kit/bash/check-prerequisites.sh
echo $?  # Exit code 0 = all good
```

### Feature Creation
```bash
# Create a new feature with scaffolding
bash scripts/spec-kit/bash/create-new-feature.sh "auth-redesign"

# This creates:
# - Feature branch
# - Documentation structure
# - Test stubs
# - Configuration templates
```

### Plan Setup
```bash
# Create a setup plan for coordinating work
python scripts/spec-kit/python/setup_plan.py
```

## ✅ Supported Environments

Both Bash and Python implementations are compatible with:
- macOS (Darwin)
- Linux (Ubuntu, Debian, Fedora, Alpine, etc.)
- Windows (WSL2, Git Bash)
- Docker/Containers

## 📚 Documentation

For full spec-kit documentation, see: https://github.com/github/spec-kit

## 🔗 Related

- Main repo: [`../.`](..)
- Audiobook-dl scripts: [`../audiobook-dl`](../audiobook-dl)
- STIPS Monitor: [`../../projects/stips-monitor`](../../projects/stips-monitor)
