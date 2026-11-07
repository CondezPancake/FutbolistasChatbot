"""Lectura, escritura y consulta de los archivos JSON del proyecto."""

from pydantic import BaseModel, ConfigDict, Field


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
