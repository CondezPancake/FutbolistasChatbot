"""Lectura, escritura y consulta de los archivos JSON del proyecto."""

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class ErrorCatalogo(ValueError):
    """Indica que el catálogo no se puede utilizar de forma segura."""


class ErrorOpiniones(ValueError):
    """Indica que el archivo de opiniones no se puede utilizar de forma segura."""


class JugadorCatalogo(BaseModel):
    """Representa un futbolista válido dentro del catálogo."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    nombre: str = Field(min_length=1)
    pais: str = Field(min_length=1)


class CatalogoJugadores(BaseModel):
    """Define la estructura esperada del archivo de jugadores."""

    model_config = ConfigDict(extra="forbid")

    version: Literal[1]
    jugadores: list[JugadorCatalogo] = Field(min_length=1)


class OpinionPersistida(BaseModel):
    """Valida un registro completo recuperado del almacenamiento local."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: UUID
    fecha_utc: AwareDatetime
    jugador_id: str = Field(min_length=1)
    jugador_nombre: str = Field(min_length=1)
    opinion_original: str = Field(min_length=5, max_length=1000)
    sentimiento: Literal["positivo", "negativo", "neutro", "mixto"]
    razon: str = Field(min_length=1, max_length=300)
    modelo: str = Field(min_length=1)
    version_prompt: str = Field(min_length=1)

    @field_validator("fecha_utc")
    @classmethod
    def validar_fecha_utc(cls, valor: datetime) -> datetime:
        """Impide aceptar fechas conscientes que pertenezcan a otra zona horaria."""
        if valor.utcoffset() != timedelta(0):
            raise ValueError("La fecha del registro debe estar expresada en UTC.")
        return valor


class ArchivoOpiniones(BaseModel):
    """Define el contrato versionado del archivo persistente."""

    model_config = ConfigDict(extra="forbid")

    version: Literal[1]
    opiniones: list[OpinionPersistida]

    @model_validator(mode="after")
    def validar_identificadores_unicos(self) -> "ArchivoOpiniones":
        """Detecta reintentos duplicados antes de operar con los registros."""
        conteo_ids = Counter(opinion.id for opinion in self.opiniones)
        if any(cantidad > 1 for cantidad in conteo_ids.values()):
            raise ValueError("El archivo contiene identificadores de opinión repetidos.")
        return self


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

    conteo_ids = Counter(jugador.id for jugador in catalogo.jugadores)
    ids_repetidos = sorted(
        jugador_id for jugador_id, cantidad in conteo_ids.items() if cantidad > 1
    )
    if ids_repetidos:
        raise ErrorCatalogo(
            f"El catálogo contiene identificadores repetidos: {', '.join(ids_repetidos)}."
        )

    return [jugador.model_dump() for jugador in catalogo.jugadores]


def cargar_opiniones(ruta: str | Path) -> dict[str, Any]:
    """Lee y valida opiniones sin sobrescribir archivos ausentes o dañados."""
    ruta_opiniones = Path(ruta)

    try:
        contenido = ruta_opiniones.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"version": 1, "opiniones": []}
    except OSError as exc:
        raise ErrorOpiniones(
            f"No fue posible leer el archivo de opiniones: {ruta_opiniones}"
        ) from exc

    try:
        datos = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ErrorOpiniones(
            "El archivo de opiniones contiene JSON inválido y se conservó sin cambios."
        ) from exc

    try:
        archivo = ArchivoOpiniones.model_validate(datos)
    except ValidationError as exc:
        raise ErrorOpiniones(
            "El archivo de opiniones no cumple la estructura esperada y se conservó sin cambios."
        ) from exc

    return archivo.model_dump(mode="json")
