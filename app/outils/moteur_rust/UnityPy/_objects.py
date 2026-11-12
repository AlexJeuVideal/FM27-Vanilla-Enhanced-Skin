"""`obj.read()` : champs accessibles en attributs, image pour les textures (mêmes règles qu'UnityPy)."""
from . import _core
from .enums import TextureFormat as TF


def _cle(tree, attribut):
    """nom du champ dans l'arbre : les noms Unity peuvent contenir des espaces (« image data »)"""
    if attribut in tree:
        return attribut
    for k in tree:
        if k.replace(" ", "_") == attribut:
            return k
    return attribut


class Fields:
    """dict de l'arbre de types, lu et modifié par attributs"""

    def __init__(self, tree):
        object.__setattr__(self, "_tree", tree)

    def __getattr__(self, key):
        try:
            value = self._tree[_cle(self._tree, key)]
        except KeyError:
            raise AttributeError(key) from None
        return Fields(value) if isinstance(value, dict) else value

    def __setattr__(self, key, value):
        self._tree[_cle(self._tree, key)] = value


class Texture2D(Fields):
    def __init__(self, tree, reader):
        super().__init__(tree)
        object.__setattr__(self, "object_reader", reader)

    def save(self):
        self.object_reader.save_typetree(self._tree)

    def get_image_data(self):
        if self.image_data:
            return self.image_data
        stream = self._tree.get("m_StreamData")
        if stream and stream["path"]:
            base = stream["path"].replace("\\", "/").rsplit("/", 1)[-1]
            raw = self.object_reader.resource(base, stream["offset"], stream["size"])
            if raw is None:
                raise FileNotFoundError(f"Resource file {base} not found")
            return raw
        raise ValueError("No image data found")

    @property
    def image(self):
        from PIL import Image
        fmt = self._tree["m_TextureFormat"]
        w, h = self._tree["m_Width"], self._tree["m_Height"]
        data = self.get_image_data()
        pw, ph = (w + 3) // 4 * 4, (h + 3) // 4 * 4
        if fmt == TF.DXT1:
            img = Image.frombytes("RGBA", (pw, ph), _core.decode_bc1(data, pw, ph), "raw", "BGRA")
        elif fmt == TF.DXT5:
            img = Image.frombytes("RGBA", (pw, ph), _core.decode_bc3(data, pw, ph), "raw", "BGRA")
        elif fmt == TF.RGBA32:
            pw, ph = w, h
            img = Image.frombytes("RGBA", (w, h), data, "raw", "RGBA")
        else:
            raise NotImplementedError(f"format de texture {TF(fmt).name} non géré")
        if (pw, ph) != (w, h):
            img = img.crop((0, 0, w, h))
        return img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def set_image(self, img, target_format=None, mipmap_count=1):
        from PIL import Image
        if mipmap_count != 1:
            raise NotImplementedError("mipmaps non gérés")
        if not isinstance(img, Image.Image):
            img = Image.open(img)
        fmt = target_format or self._tree["m_TextureFormat"]
        flipped = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        if fmt in (TF.DXT1, TF.DXT1Crunched):
            tex_format = TF.DXT1
            pw, ph = (img.width + 3) // 4 * 4, (img.height + 3) // 4 * 4
            data = _core.encode_bc1(_pad(flipped, pw, ph).tobytes("raw", "RGBA"), pw, ph)
        elif fmt == TF.RGBA32:
            tex_format = TF.RGBA32
            data = flipped.tobytes("raw", "RGBA")
        else:
            raise NotImplementedError(f"format de texture {TF(fmt).name} non géré")
        tree = self._tree
        tree["m_Width"], tree["m_Height"] = img.width, img.height
        if "m_MipMap" in tree:
            tree["m_MipMap"] = False
        if "m_MipCount" in tree:
            tree["m_MipCount"] = 1
        self.image_data = data
        tree["m_CompleteImageSize"] = len(data)
        tree["m_TextureFormat"] = int(tex_format)
        if "m_StreamData" in tree:
            tree["m_StreamData"].update(path="", offset=0, size=0)


def _pad(img, pw, ph):
    from PIL import Image
    w, h = img.size
    if (pw, ph) == (w, h):
        return img
    out = Image.new(img.mode, (pw, ph))
    out.paste(img, (0, 0))
    if pw != w:
        out.paste(img.crop((w - 1, 0, w, h)).resize((pw - w, h), Image.Resampling.NEAREST), (w, 0))
    if ph != h:
        out.paste(img.crop((0, h - 1, w, h)).resize((w, ph - h), Image.Resampling.NEAREST), (0, h))
    if pw != w and ph != h:
        out.paste(Image.new(img.mode, (pw - w, ph - h), color=img.getpixel((w - 1, h - 1))), (w, h))
    return out


def wrap(reader):
    tree = reader.read_typetree()
    if reader.type.name == "Texture2D":
        return Texture2D(tree, reader)
    return Fields(tree)
