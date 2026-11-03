"""Python startup customization executed before any module or framework loads.

Ensures 'backend' is in sys.path so 'app.main:app' resolves seamlessly
whether the application is started from the repository root or from backend/.
"""

import os
import sys
from pathlib import Path

# Add backend directory to sys.path
workspace_dir = Path(__file__).resolve().parent
backend_dir = workspace_dir / "backend"

if backend_dir.exists() and str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# OpenBLAS / thread safety configs
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

if sys.platform == "win32":
    import asyncio
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass
