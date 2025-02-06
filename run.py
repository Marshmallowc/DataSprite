import streamlit.web.cli as stcli
import sys
from pathlib import Path

if __name__ == "__main__":
    root_dir = Path(__file__).parent
    frontend_dir = root_dir / "frontend"
    sys.path.append(str(root_dir))
    
    sys.argv = [
        "streamlit",
        "run",
        str(frontend_dir / "app.py"),
        "--server.port=8501",
        "--server.address=localhost"
    ]
    
    sys.exit(stcli.main()) 