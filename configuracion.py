"""Configuración segura de proveedores y modelos de inteligencia artificial."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic import SecretStr


MODELO_GEMINI_PREDETERMINADO = "gemini-3.5-flash"
MARCADORES_DE_CLAVE = {"", "tu_clave_de_gemini", "clave_configurada_localmente"}


class ErrorConfiguracionIA(RuntimeError):
    """Indica que la configuración necesaria para Gemini no está disponible."""


@dataclass(frozen=True)
class ConfiguracionIA:
    """Conserva la configuración sin revelar la clave en representaciones."""

    api_key: SecretStr
    modelo: str


def cargar_configuracion_ia() -> ConfiguracionIA:
    """Lee la configuración local y rechaza claves vacías o de ejemplo."""
    load_dotenv()
    clave = os.getenv("GOOGLE_API_KEY", "").strip()
    modelo = os.getenv("GEMINI_MODEL", MODELO_GEMINI_PREDETERMINADO).strip()

    if clave in MARCADORES_DE_CLAVE:
        raise ErrorConfiguracionIA(
            "Configura una clave válida de Gemini en GOOGLE_API_KEY dentro de .env."
        )
    if not modelo:
        raise ErrorConfiguracionIA("GEMINI_MODEL no puede estar vacío.")

    return ConfiguracionIA(api_key=SecretStr(clave), modelo=modelo)


def gemini_esta_configurado() -> bool:
    """Informa disponibilidad sin exponer la clave ni crear el cliente."""
    try:
        cargar_configuracion_ia()
    except ErrorConfiguracionIA:
        return False
    return True
