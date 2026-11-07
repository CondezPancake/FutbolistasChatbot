"""Lectura, escritura y consulta de los archivos JSON del proyecto."""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ErrorCatalogo(ValueError):
    """Indica que el catálogo no se puede utilizar de forma segura."""


class JugadorCatalogo(BaseModel):
    """Representa un futbolista válido dentro del catálogo."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    pais: str = Field(min_length=1)


class CatalogoJugadores(BaseModel):
    """Define la estructura esperada del archivo de jugadores."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(ge=1)
    jugadores: list[JugadorCatalogo] = Field(min_length=1)


def cargar_jugadores(ruta: str | Path) -> list[dict[str, Any]]:
    """Lee y valida el catálogo sin modificar el archivo original."""
    ruta_catalogo = Path(ruta)

    try:
        contenido = ruta_catalogo.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ErrorCatalogo(f"No se encontró el catálogo: {ruta_catalogo}") from exc
    except OSError as exc:
        raise ErrorCatalogo(f"No fue posible leer el catálogo: {ruta_catalogo}") from exc

    try:
        datos = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ErrorCatalogo("El catálogo no contiene un JSON válido.") from exc

    try:
        catalogo = CatalogoJugadores.model_validate(datos)
    except ValidationError as exc:
        raise ErrorCatalogo("El catálogo no cumple la estructura esperada.") from exc

    return [jugador.model_dump() for jugador in catalogo.jugadores]
