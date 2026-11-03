"""Pieza falsa para ConsultaAmistades.

Proporciona datos de amistades simulados para las pruebas unitarias."""

from social_una.dominio.contratos import ConsultaAmistades


class ConsultaAmistadesFalsa(ConsultaAmistades):
    """Implementación falsa de ConsultaAmistades para pruebas."""

    def __init__(self, amistades: dict[int, set[int]] | None = None):
        if amistades is None:
            amistades = {1: {2}, 2: {1}, 3: set()}
        # Guardar una copia donde cada valor es un set nuevo
        self._amistades = {k: set(v) for k, v in amistades.items()}

    def obtener_ids_amigos(self, id_usuario: int) -> set[int]:
        """Devuelve una copia (set nuevo) de los amigos de ese id."""
        return set(self._amistades.get(id_usuario, set()))

    def son_amigos(self, id_a: int, id_b: int) -> bool:
        """True si id_b está en obtener_ids_amigos(id_a)."""
        return id_b in self.obtener_ids_amigos(id_a)
