#!/usr/bin/env python3
"""
Validate that the Delegate.ai project is ready for deployment.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and print status."""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists and print status."""
    if os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description} missing: {dir_path}")
        return False

def check_command_exists(command, description):
    """Check if a command is available."""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        print(f"✅ {description} available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {description} not found")
        return False

def validate_json_file(file_path, description):
    """Validate JSON file syntax."""
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print(f"✅ {description} is valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {description} has invalid JSON: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} not found")
        return False

def main():
    """Main validation function."""
    print("🔍 Validating Delegate.ai deployment setup...\n")

    # Get project root
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"

    all_checks_passed = True

    # Check project structure
    print("📁 Checking project structure:")
    checks = [
        (backend_dir, "Backend directory"),
        (frontend_dir, "Frontend directory"),
        (project_root / "ai_system", "AI system directory"),
        (project_root / "DEPLOYMENT_GUIDE.md", "Deployment guide"),
        (project_root / "README.md", "Project README"),
    ]

    for path, desc in checks:
        if not check_directory_exists(path, desc) and not check_file_exists(path, desc):
            all_checks_passed = False

    print()

    # Check backend files
    print("🔧 Checking backend configuration:")
    backend_checks = [
        (backend_dir / "requirements.txt", "Backend requirements"),
        (backend_dir / "Dockerfile", "Docker configuration"),
        (backend_dir / "start.sh", "Startup script"),
        (backend_dir / "Procfile", "Railway Procfile"),
        (backend_dir / "railway.json", "Railway config"),
        (backend_dir / ".env.example", "Environment example"),
        (backend_dir / ".env.production", "Production environment template"),
        (backend_dir / "app" / "main.py", "Main application"),
        (backend_dir / "alembic.ini", "Database migration config"),
    ]

    for path, desc in backend_checks:
        if not check_file_exists(path, desc):
            all_checks_passed = False

    # Validate JSON files
    json_files = [
        (backend_dir / "railway.json", "Railway configuration"),
        (frontend_dir / "package.json", "Frontend package.json"),
        (frontend_dir / "vercel.json", "Vercel configuration"),
    ]

    for path, desc in json_files:
        if not validate_json_file(path, desc):
            all_checks_passed = False

    print()

    # Check frontend files
    print("🌐 Checking frontend configuration:")
    frontend_checks = [
        (frontend_dir / "package.json", "Package configuration"),
        (frontend_dir / "next.config.mjs", "Next.js configuration"),
        (frontend_dir / "vercel.json", "Vercel configuration"),
        (frontend_dir / ".env.local.example", "Environment example"),
        (frontend_dir / ".env.production", "Production environment template"),
        (frontend_dir / "app" / "page.tsx", "Main page component"),
        (frontend_dir / "app" / "layout.tsx", "Root layout"),
    ]

    for path, desc in frontend_checks:
        if not check_file_exists(path, desc):
            all_checks_passed = False

    print()

    # Check deployment tools
    print("🛠️ Checking deployment tools:")
    tool_checks = [
        ("railway", "Railway CLI"),
        ("vercel", "Vercel CLI"),
        ("docker", "Docker"),
        ("python", "Python"),
        ("node", "Node.js"),
        ("npm", "NPM"),
    ]

    for command, desc in tool_checks:
        if not check_command_exists(command, desc):
            all_checks_passed = False

    print()

    # Check deployment scripts
    print("📜 Checking deployment scripts:")
    script_checks = [
        (project_root / "deploy.sh", "Main deployment script"),
        (project_root / "test-deployment.sh", "Deployment testing script"),
        (backend_dir / "start.sh", "Backend startup script"),
    ]

    for path, desc in script_checks:
        if check_file_exists(path, desc):
            # Check if script is executable
            if os.access(path, os.X_OK):
                print(f"✅ {desc} is executable")
            else:
                print(f"⚠️  {desc} is not executable (run: chmod +x {path})")
        else:
            all_checks_passed = False

    print()

    # Summary
    if all_checks_passed:
        print("🎉 All checks passed! Your project is ready for deployment.")
        print("\n🚀 To deploy, run:")
        print("   ./deploy.sh")
        print("\n📖 For detailed instructions, see:")
        print("   ./DEPLOYMENT_GUIDE.md")
    else:
        print("❌ Some checks failed. Please address the issues above before deploying.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())