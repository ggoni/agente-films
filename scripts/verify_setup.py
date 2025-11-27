"""Local setup verification script."""

import sys
from pathlib import Path


def check_python_version():
    """Verify Python 3.12+ is installed."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need 3.12+")
        return False


def check_uv_installed():
    """Verify uv package manager is available."""
    import subprocess
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("❌ uv not installed - Run: curl -LsSf https://astral.sh/uv/install.sh | sh")
    return False


def check_venv_exists():
    """Verify virtual environment exists."""
    venv_path = Path(".venv")
    if venv_path.exists():
        print("✅ Virtual environment exists")
        return True
    else:
        print("❌ Virtual environment missing - Run: uv venv")
        return False


def check_dependencies_installed():
    """Verify dependencies are installed."""
    import importlib.util

    required_packages = ["fastapi", "pydantic", "sqlalchemy"]
    missing_packages = [pkg for pkg in required_packages if importlib.util.find_spec(pkg) is None]

    if not missing_packages:
        print("✅ Core dependencies installed")
        return True

    print("❌ Missing dependencies - Run: uv pip install -e .")
    return False


def check_env_file():
    """Verify .env file exists."""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file missing - Copy from .env.example")
        return False


def check_database_url():
    """Verify DATABASE_URL is configured."""
    try:
        from backend.app.config import Settings
        settings = Settings()
        if settings.DATABASE_URL:
            print("✅ DATABASE_URL configured")
            return True
    except Exception as e:
        print(f"❌ DATABASE_URL not configured: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n🔍 Verifying Local Development Setup\n")
    print("=" * 50)

    checks = [
        ("Python Version", check_python_version),
        ("UV Package Manager", check_uv_installed),
        ("Virtual Environment", check_venv_exists),
        ("Dependencies", check_dependencies_installed),
        ("Environment File", check_env_file),
        ("Database Config", check_database_url),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)
        print()

    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Results: {passed}/{total} checks passed")

    if passed == total:
        print("\n✅ Local setup verified! Ready to run the API.")
        print("\n🚀 Next steps:")
        print("   1. Start API: uvicorn backend.app.api.main:app --reload")
        print("   2. Visit docs: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
