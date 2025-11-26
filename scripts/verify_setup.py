#!/usr/bin/env python3
"""Verify project setup and configuration."""

import sys
from pathlib import Path


def check_file_exists(path: Path, description: str) -> bool:
    """Check if file exists."""
    if path.exists():
        print(f"✓ {description}: {path.name}")
        return True
    else:
        print(f"✗ {description}: {path.name} NOT FOUND")
        return False


def main() -> int:
    """Run verification checks."""
    project_root = Path(__file__).parent.parent
    checks_passed = 0
    checks_total = 0

    print("=" * 60)
    print("Project Setup Verification")
    print("=" * 60)

    # Core files
    print("\n📋 Core Files:")
    files = [
        (project_root / "pyproject.toml", "Project config"),
        (project_root / "pytest.ini", "pytest config"),
        (project_root / ".pre-commit-config.yaml", "Pre-commit hooks"),
        (project_root / ".env.example", "Environment template"),
        (project_root / "Makefile", "Build commands"),
    ]

    for file_path, desc in files:
        checks_total += 1
        if check_file_exists(file_path, desc):
            checks_passed += 1

    # Docker files
    print("\n🐳 Docker Configuration:")
    docker_files = [
        (project_root / "Dockerfile", "Docker image"),
        (project_root / "docker-compose.yml", "Docker compose"),
        (project_root / ".dockerignore", "Docker ignore"),
        (project_root / "litellm-config.yaml", "LiteLLM config"),
    ]

    for file_path, desc in docker_files:
        checks_total += 1
        if check_file_exists(file_path, desc):
            checks_passed += 1

    # Source code
    print("\n📦 Source Code:")
    src_files = [
        (project_root / "src" / "__init__.py", "Package init"),
        (project_root / "src" / "agents" / "screenplay_agent.py", "Agent example"),
        (project_root / "src" / "api" / "main.py", "FastAPI app"),
        (project_root / "src" / "api" / "models.py", "API models"),
        (project_root / "src" / "api" / "repository.py", "Repository"),
    ]

    for file_path, desc in src_files:
        checks_total += 1
        if check_file_exists(file_path, desc):
            checks_passed += 1

    # Tests
    print("\n🧪 Tests:")
    test_files = [
        (project_root / "tests" / "conftest.py", "Test fixtures"),
        (project_root / "tests" / "unit" / "test_screenplay_agent.py", "Unit tests"),
        (project_root / "tests" / "integration" / "test_api.py", "Integration tests"),
    ]

    for file_path, desc in test_files:
        checks_total += 1
        if check_file_exists(file_path, desc):
            checks_passed += 1

    # Documentation
    print("\n📚 Documentation:")
    doc_files = [
        (project_root / "README.md", "Project README"),
        (project_root / "QUICKSTART.md", "Quick start"),
        (project_root / "docs" / "DEVELOPMENT.md", "Development guide"),
        (project_root / "docs" / "TESTING.md", "Testing guide"),
        (project_root / "docs" / "EXAMPLES.md", "Code examples"),
        (project_root / "docs" / "ARCHITECTURE.md", "Architecture"),
        (project_root / "docs" / "SUMMARY.md", "Summary"),
        (project_root / "docs" / "INDEX.md", "Doc index"),
    ]

    for file_path, desc in doc_files:
        checks_total += 1
        if check_file_exists(file_path, desc):
            checks_passed += 1

    # CI/CD
    print("\n🚀 CI/CD:")
    ci_files = [
        (project_root / ".github" / "workflows" / "ci.yml", "GitHub Actions"),
    ]

    for file_path, desc in ci_files:
        checks_total += 1
        if check_file_exists(file_path, desc):
            checks_passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)

    if checks_passed == checks_total:
        print("\n✓ All checks passed! Project setup is complete.")
        return 0
    else:
        print(f"\n✗ {checks_total - checks_passed} checks failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
