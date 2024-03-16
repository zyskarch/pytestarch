from __future__ import annotations

import app.red.red3  # type: ignore  # noqa: F401
from app.red.red import Red  # type: ignore

from ..red.red2 import Red2  # type: ignore

Red()
Red2()
Red3()  # type: ignore # noqa: F821
