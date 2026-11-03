"""Python startup customization executed before any module or framework loads."""

import os
import sys
from pathlib import Path

# Add backend directory to sys.path automatically
workspace_dir = Path(__file__).resolve().parent
backend_dir = workspace_dir / "backend"
if backend_dir.exists() and str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Also support if running from inside venv
alt_backend = Path("C:/Users/Projects/Routicabot/backend")
if alt_backend.exists() and str(alt_backend) not in sys.path:
    sys.path.insert(0, str(alt_backend))

# Environment configuration to prevent OpenBLAS memory errors and network hangs
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Use SelectorEventLoop on Windows
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())