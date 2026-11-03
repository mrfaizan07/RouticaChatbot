import sys
from pathlib import Path

# When run from root, route 'app' lookups to backend/app
_root = Path(__file__).resolve().parent.parent
_backend = _root / "backend"
_backend_app = _backend / "app"

if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

if str(_backend_app) not in __path__:
    __path__.append(str(_backend_app))
