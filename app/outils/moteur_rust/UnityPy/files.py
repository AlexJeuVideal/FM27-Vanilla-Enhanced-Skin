"""BundleFile : classe Python car le skin remplace `BundleFile.save` (installation sans compression)."""
from ._core import Bundle


class _Reader:
    def __init__(self, core, name):
        self._core, self._name = core, name

    @property
    def bytes(self):
        return self._core.node_bytes(self._name)


class _Serialized:
    def __init__(self, core, name):
        self.reader = _Reader(core, name)
        self._af = core.assets_file(name)

    @property
    def ref_types(self):
        """liste vivante des types référencés (elements.types_ref_manquants y ajoute un type recopié)"""
        return self._af.ref_types


class BundleFile:
    def __init__(self, raw):
        self._core = Bundle(raw)
        self.dataflags = self._core.dataflags
        self._block_info_flags = self._core.block_info_flags
        self._objects = None
        self.files = {}
        for name, serialized in self._core.nodes():
            self.files[name] = _Serialized(self._core, name) if serialized else _Reader(self._core, name)

    @property
    def objects(self):
        if self._objects is None:
            self._objects = self._core.objects()
        return self._objects

    def save(self, packer=None):
        if not packer or packer == "none":
            flags = (64, 64)
        elif packer == "original":
            flags = (int(self.dataflags), int(self._block_info_flags))
        elif packer == "lz4":
            flags = (194, 2)
        elif packer == "lz4hc":
            flags = (195, 3)
        elif isinstance(packer, tuple):
            flags = (int(packer[0]), int(packer[1]))
        else:
            raise NotImplementedError("UnityFS - Packer:", packer)
        return self._core.save(*flags)
