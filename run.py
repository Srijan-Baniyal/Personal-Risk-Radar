#!/usr/bin/env python3
"""
Personal Risk Radar - Unified Startup Script

This script provides a simple interface to run all components of the system.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from requests import Response


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         🎯 Personal Risk Radar                          ║
║         Local-first risk modeling & tracking            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def run_api(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """Start the FastAPI server."""
    print(f"🚀 Starting API server on {host}:{port}")
    print(f"📚 API docs will be available at: http://localhost:{port}/docs")
    print()
    
    cmd: list[str] = ["uvicorn", "api.main:app", "--host", host, "--port", str(object=port)]
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(args=cmd)
    except KeyboardInterrupt:
        print("\n✋ API server stopped")


def run_streamlit() -> None:
    """Start the Streamlit UI."""
    print("🎨 Starting Streamlit UI")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print()
    
    try:
        subprocess.run(["streamlit", "run", "main.py"])
    except KeyboardInterrupt:
        print("\n✋ Streamlit stopped")


def run_tests():
    """Run API tests."""
    print("🧪 Running API tests...")
    print()
    
    # Check if API is running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result != 0:
        print("⚠️  API server is not running!")
        print("💡 Start the API first: python run.py api")
        sys.exit(1)
    
    subprocess.run([sys.executable, "test_api.py"])


def init_db():
    """Initialize the database."""
    print("🗄️  Initializing database...")
    
    from persistence.database import init_db as db_init
    
    db_init()
    print("✅ Database initialized successfully")
    print(f"📁 Database file: {Path('personal_risk_radar.db').absolute()}")


def load_sample_data() -> None:
    """Load sample data from CSV files."""
    print("📥 Loading sample data...")
    
    import requests
    
    base_url = "http://localhost:8000"
    
    # Check if API is running
    try:
        response: Response = requests.get(url=f"{base_url}/health", timeout=2)
        if response.status_code != 200:
            raise Exception("API not healthy")
    except Exception:
        print("⚠️  API server is not running!")
        print("💡 Start the API first: python run.py api")
        sys.exit()
    
    # Upload sample risks
    risks_file = Path("examples/sample_risks.csv")
    if risks_file.exists():
        with open(risks_file, "rb") as f:
            files = {"file": (risks_file.name, f, "text/csv")}
            response = requests.post(
                f"{base_url}/api/data-input/upload/risks/csv",
                files=files
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Loaded {data['records_created']} risks")
            else:
                print(f"❌ Failed to load risks: {response.text}")
    
    # Upload sample signals (if we have risks)
    signals_file = Path("examples/sample_signals.csv")
    if signals_file.exists():
        # First check if we have risks
        response = requests.get(f"{base_url}/api/risks/")
        if response.status_code == 200 and len(response.json()) > 0:
            with open(signals_file, "rb") as f:
                files = {"file": (signals_file.name, f, "text/csv")}
                response = requests.post(
                    f"{base_url}/api/data-input/upload/signals/csv",
                    files=files
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Loaded {data['records_created']} signals")
                else:
                    print(f"❌ Failed to load signals: {response.text}")
    
    print("\n📊 Sample data loaded successfully!")


def show_status():
    """Show system status."""
    print("📊 System Status")
    print("=" * 60)
    
    # Check database
    db_file = Path("personal_risk_radar.db")
    if db_file.exists():
        size = db_file.stat().st_size
        print(f"✅ Database: {db_file.name} ({size:,} bytes)")
        
        # Count records
        from persistence.database import get_all_risks, get_db
        with get_db() as db:
            risks = get_all_risks(db)
            print(f"   📈 Risks: {len(risks)}")
    else:
        print("❌ Database: Not initialized")
    
    # Check API
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result == 0:
        print("✅ API Server: Running on http://localhost:8000")
        print("   📚 Docs: http://localhost:8000/docs")
    else:
        print("❌ API Server: Not running")
    
    # Check sample files
    print("\n📁 Sample Data Files:")
    for file in ["examples/sample_risks.csv", "examples/sample_signals.csv"]:
        path = Path(file)
        if path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")
    
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Personal Risk Radar - Unified Control Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py api              # Start API server
  python run.py ui               # Start Streamlit UI
  python run.py test             # Run tests
  python run.py init             # Initialize database
  python run.py load             # Load sample data
  python run.py status           # Show system status
        """
    )
    
    parser.add_argument(
        "command",
        choices=["api", "ui", "test", "init", "load", "status"],
        help="Command to run"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API server port (default: 8000)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable auto-reload for API server"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "api":
        run_api(args.host, args.port, not args.no_reload)
    elif args.command == "ui":
        run_streamlit()
    elif args.command == "test":
        run_tests()
    elif args.command == "init":
        init_db()
    elif args.command == "load":
        load_sample_data()
    elif args.command == "status":
        show_status()


if __name__ == "__main__":
    main()
