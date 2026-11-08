"""Lectura, escritura y consulta de los archivos JSON del proyecto."""

from collections import Counter
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from analisis import PROMPT_VERSION, AnalisisOpinion


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


def crear_registro(
    jugador: dict[str, Any],
    texto: str,
    analisis: AnalisisOpinion,
    modelo: str,
) -> dict[str, Any]:
    """Crea un registro completo con metadatos generados por la aplicación."""
    if not analisis.es_pertinente or analisis.sentimiento is None:
        raise ErrorOpiniones("Una opinión no pertinente no puede convertirse en registro.")

    try:
        registro = OpinionPersistida.model_validate(
            {
                "id": uuid4(),
                "fecha_utc": datetime.now(timezone.utc),
                "jugador_id": jugador.get("id"),
                "jugador_nombre": jugador.get("nombre"),
                "opinion_original": texto,
                "sentimiento": analisis.sentimiento,
                "razon": analisis.razon,
                "modelo": modelo,
                "version_prompt": PROMPT_VERSION,
            }
        )
    except (AttributeError, ValidationError) as exc:
        raise ErrorOpiniones("No fue posible construir un registro de opinión válido.") from exc

    return registro.model_dump(mode="json")


def guardar_opinion(ruta: str | Path, registro: dict[str, Any]) -> bool:
    """Añade una opinión mediante reemplazo atómico y evita repetir su UUID.

    Devuelve ``True`` cuando escribe un registro nuevo y ``False`` cuando el
    identificador ya estaba persistido, lo que hace seguro repetir el guardado.
    """
    ruta_opiniones = Path(ruta)

    try:
        registro_validado = OpinionPersistida.model_validate(registro)
    except ValidationError as exc:
        raise ErrorOpiniones("La opinión recibida no cumple la estructura esperada.") from exc

    archivo_actual = cargar_opiniones(ruta_opiniones)
    identificador = str(registro_validado.id)
    if any(
        opinion["id"] == identificador for opinion in archivo_actual["opiniones"]
    ):
        return False

    archivo_actual["opiniones"].append(registro_validado.model_dump(mode="json"))
    try:
        archivo_validado = ArchivoOpiniones.model_validate(archivo_actual)
    except ValidationError as exc:
        raise ErrorOpiniones("No fue posible validar el archivo antes de guardarlo.") from exc

    ruta_temporal: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{ruta_opiniones.name}.",
            suffix=".tmp",
            dir=ruta_opiniones.parent,
            delete=False,
        ) as archivo_temporal:
            ruta_temporal = Path(archivo_temporal.name)
            json.dump(
                archivo_validado.model_dump(mode="json"),
                archivo_temporal,
                ensure_ascii=False,
                indent=2,
            )
            archivo_temporal.write("\n")
            archivo_temporal.flush()
            os.fsync(archivo_temporal.fileno())

        os.replace(ruta_temporal, ruta_opiniones)
    except OSError as exc:
        if ruta_temporal is not None:
            try:
                ruta_temporal.unlink(missing_ok=True)
            except OSError:
                pass
        raise ErrorOpiniones(
            "No fue posible guardar la opinión; el archivo original se conservó."
        ) from exc

    return True
