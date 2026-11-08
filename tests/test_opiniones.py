"""Pruebas prioritarias para persistencia y consulta de opiniones."""

from pathlib import Path

from analisis import AnalisisOpinion
from almacenamiento import (
    SENTIMIENTOS,
    cargar_opiniones,
    consultar_opiniones,
    contar_sentimientos,
    crear_registro,
    guardar_opinion,
)


RUTA_OPINIONES = Path(__file__).resolve().parents[1] / "data" / "opiniones.json"


def test_datos_ficticios_cubren_el_entregable() -> None:
    registros = cargar_opiniones(RUTA_OPINIONES)["opiniones"]

    assert len(registros) >= 12
    assert len({registro["jugador_id"] for registro in registros}) >= 4
    assert {registro["sentimiento"] for registro in registros} >= set(SENTIMIENTOS)


def test_guardado_es_persistente_e_idempotente(tmp_path: Path) -> None:
    ruta = tmp_path / "opiniones.json"
    analisis = AnalisisOpinion(
        es_pertinente=True,
        sentimiento="positivo",
        razon="La opinión expresa admiración por su visión.",
    )
    registro = crear_registro(
        {"id": "j001", "nombre": "Lionel Messi"},
        "Su visión de juego es extraordinaria.",
        analisis,
        "modelo-prueba",
    )

    assert guardar_opinion(ruta, registro) is True
    assert guardar_opinion(ruta, registro) is False
    assert cargar_opiniones(ruta)["opiniones"] == [registro]
    assert "visión" in ruta.read_text(encoding="utf-8")
    assert not list(tmp_path.glob("*.tmp"))


def test_consulta_combina_filtros_y_recuentos_sin_mutar() -> None:
    registros = [
        {
            "jugador_id": "j001",
            "jugador_nombre": "Lionel Messi",
            "sentimiento": "positivo",
        },
        {
            "jugador_id": "j001",
            "jugador_nombre": "Lionel Messi",
            "sentimiento": "neutro",
        },
        {
            "jugador_id": "j013",
            "jugador_nombre": "Luis Díaz",
            "sentimiento": "positivo",
        },
    ]

    filtrados = consultar_opiniones(registros, "j001", "positivo")
    conteos = contar_sentimientos(filtrados)

    assert len(filtrados) == 1
    assert filtrados[0]["jugador_nombre"] == "Lionel Messi"
    assert conteos == {"positivo": 1, "negativo": 0, "neutro": 0, "mixto": 0}
    filtrados[0]["jugador_nombre"] = "Nombre modificado"
    assert registros[0]["jugador_nombre"] == "Lionel Messi"
