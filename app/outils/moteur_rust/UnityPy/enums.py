"""Formats de texture (valeurs Unity), chargés à la demande pour garder l'import instantané."""
import enum
import os

with open(os.path.join(os.path.dirname(__file__), "_tf.txt"), encoding="ascii") as _f:
    TextureFormat = enum.IntEnum(
        "TextureFormat",
        {k: int(v) for k, v in (p.split("=") for p in _f.read().split(", "))},
    )
