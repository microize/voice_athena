#!/usr/bin/env python3
"""
Simple runner script for Athena application.

This script provides easy ways to run the application:
- Modular structure: python run_athena.py (default)
- Legacy backup: python run_athena.py --legacy
"""

import sys
import subprocess
from pathlib import Path

def run_modular():
    """Run the modular Athena application"""
    print("🚀 Starting Athena with modular architecture...")
    subprocess.run([sys.executable, "-m", "athena.main"])

def run_legacy():
    """Run the legacy server.py backup"""
    legacy_file = Path("server.py.backup")
    if not legacy_file.exists():
        print("❌ Legacy server.py.backup not found!")
        print("   The original monolithic server has been replaced with the new modular architecture.")
        print("   Use: python run_athena.py")
        sys.exit(1)
    
    print("⚠️  Starting Athena with legacy backup (server.py.backup)...")
    print("   Consider migrating to the new modular structure: python run_athena.py")
    subprocess.run([sys.executable, "server.py.backup"])

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--legacy":
        run_legacy()
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("📋 Athena Application Runner")
        print()
        print("Usage:")
        print("  python run_athena.py           # Run modular architecture (recommended)")
        print("  python run_athena.py --legacy  # Run legacy backup (deprecated)")
        print("  python run_athena.py --help    # Show this help")
        print()
        print("🏗️  The application has been modularized for better maintainability!")
    else:
        print("🏗️  Using new modular architecture (recommended)...")
        run_modular()

if __name__ == "__main__":
    main()