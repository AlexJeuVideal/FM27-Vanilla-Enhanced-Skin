"""Le skin y pose son correctif des références vides. Le moteur Rust les gère déjà : le correctif reste sans effet."""


def write_value(value, node, writer, config):
    raise NotImplementedError("écriture gérée par le moteur Rust")
