"""Pruebas prioritarias para la carga del catálogo."""

import json
from pathlib import Path

import pytest

from almacenamiento import ErrorCatalogo, cargar_jugadores


RUTA_CATALOGO = Path(__file__).resolve().parents[1] / "data" / "jugadores.json"


def guardar_catalogo(ruta: Path, jugadores: list[dict[str, str]]) -> None:
    """Crea un catálogo temporal con codificación UTF-8."""
    datos = {"version": 1, "jugadores": jugadores}
    ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")


def test_carga_los_veinte_jugadores_del_catalogo() -> None:
    jugadores = cargar_jugadores(RUTA_CATALOGO)

    assert len(jugadores) == 20
    assert len({jugador["id"] for jugador in jugadores}) == 20
    assert jugadores[3]["nombre"] == "Kylian Mbappé"


def test_rechaza_identificadores_repetidos(tmp_path: Path) -> None:
    ruta = tmp_path / "jugadores.json"
    guardar_catalogo(
        ruta,
        [
            {"id": "j001", "nombre": "Jugador Uno", "pais": "Colombia"},
            {"id": "j001", "nombre": "Jugador Dos", "pais": "Argentina"},
        ],
    )

    with pytest.raises(ErrorCatalogo, match="identificadores repetidos"):
        cargar_jugadores(ruta)


def test_rechaza_json_invalido(tmp_path: Path) -> None:
    ruta = tmp_path / "jugadores.json"
    ruta.write_text("{contenido incompleto", encoding="utf-8")

    with pytest.raises(ErrorCatalogo, match="JSON válido"):
        cargar_jugadores(ruta)


def test_rechaza_catalogo_con_esquema_invalido(tmp_path: Path) -> None:
    ruta = tmp_path / "jugadores.json"
    ruta.write_text('{"version": 2, "jugadores": []}', encoding="utf-8")

    with pytest.raises(ErrorCatalogo, match="estructura esperada"):
        cargar_jugadores(ruta)


def test_informa_si_el_archivo_no_existe(tmp_path: Path) -> None:
    ruta = tmp_path / "inexistente.json"

    with pytest.raises(ErrorCatalogo, match="No se encontró"):
        cargar_jugadores(ruta)
