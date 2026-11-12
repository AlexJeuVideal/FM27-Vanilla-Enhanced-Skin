"""Remplaçant de UnityPy pour les scripts du skin : même API, moteur Rust (`_core`).

N'expose que ce que les scripts utilisent. Tout le reste lève AttributeError plutôt que de deviner.
"""
import gc
import os
import sys

if sys.platform == "darwin":   # Mac (v1.87) : moteur dans _mac/ (universal2) ; le _core.abi3.so d'ici est celui de Linux
    from ._mac import _core
    sys.modules[__name__ + "._core"] = _core

from . import enums, files, helpers

# les arbres de 10 000 objets déclenchent le ramasse-miettes en boucle ; scripts courts, sans cycles qui s'accumulent
gc.set_threshold(200000, 50, 50)
from .files import BundleFile

__version__ = "1.25.4+fm27turbo"


class Environment:
    def __init__(self, *args):
        self.files = {}
        for arg in args:
            if isinstance(arg, (str, os.PathLike)):
                arg = os.fspath(arg)
                if not os.path.isfile(arg):
                    continue
                with open(arg, "rb") as f:
                    raw = f.read()
                name = arg
            elif hasattr(arg, "read"):
                raw = arg.read()
                name = "bytes"
            else:
                raw = bytes(arg)
                name = "bytes"
            self.files[name] = BundleFile(raw)
        if len(self.files) == 1:
            self.file = next(iter(self.files.values()))
        self._objects = None

    @property
    def objects(self):
        if self._objects is None:
            self._objects = [o for f in self.files.values() for o in f.objects]
        return list(self._objects)

    @property
    def container(self):
        out = {}
        by_id = {o.path_id: o for o in self.objects}
        for o in self.objects:
            if o.type.name == "AssetBundle":
                for path, info in o.read_typetree()["m_Container"]:
                    target = by_id.get(info["asset"]["m_PathID"])
                    if target is not None:
                        out[path] = target
        return out


def load(*args):
    return Environment(*args)
