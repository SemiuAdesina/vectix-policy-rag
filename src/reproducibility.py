"""Utilities for deterministic local runs."""

import os
import random
from typing import Optional

DEFAULT_SEED = 42


def set_reproducible_seed(seed: Optional[int] = None) -> int:
    """Set the shared seed used by scripts and local runs."""
    resolved_seed = seed if seed is not None else int(os.environ.get("RAG_SEED", DEFAULT_SEED))
    random.seed(resolved_seed)
    try:
        import numpy as np

        np.random.seed(resolved_seed)
    except ImportError:
        pass
    return resolved_seed
