import sys
from pathlib import Path

# Add the scripts directory to sys.path so tests can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
