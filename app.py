"""Punto de entrada de la aplicación Tribuna Global IA."""

from pathlib import Path
from typing import Any

import streamlit as st

from almacenamiento import ErrorCatalogo, cargar_jugadores


DIRECTORIO_PROYECTO = Path(__file__).resolve().parent
RUTA_JUGADORES = DIRECTORIO_PROYECTO / "data" / "jugadores.json"


@st.cache_data
def cargar_catalogo_aplicacion() -> list[dict[str, Any]]:
    """Carga el catálogo una vez mientras el archivo no cambie."""
    return cargar_jugadores(RUTA_JUGADORES)


def seleccionar_jugador(jugadores: list[dict[str, Any]]) -> dict[str, Any]:
    """Muestra el catálogo y conserva el identificador como valor interno."""
    jugadores_por_id = {jugador["id"]: jugador for jugador in jugadores}

    with st.sidebar:
        st.header("⚽ Tribuna Global IA")
        st.caption("Cada opinión juega su partido.")
        jugador_id = st.selectbox(
            "Futbolista",
            options=list(jugadores_por_id),
            format_func=lambda identificador: (
                f"{jugadores_por_id[identificador]['nombre']} · "
                f"{jugadores_por_id[identificador]['pais']}"
            ),
        )

    return jugadores_por_id[jugador_id]


def main() -> None:
    """Configura la página inicial de la aplicación."""
    st.set_page_config(
        page_title="Tribuna Global IA",
        page_icon="⚽",
        layout="wide",
    )

    try:
        jugadores = cargar_catalogo_aplicacion()
    except ErrorCatalogo as exc:
        st.error(str(exc))
        st.stop()

    jugador_seleccionado = seleccionar_jugador(jugadores)

    st.title("Tribuna Global IA")
    st.caption("Cada opinión juega su partido.")
    st.info(
        "Futbolista seleccionado: "
        f"**{jugador_seleccionado['nombre']}** · {jugador_seleccionado['pais']}"
    )
    st.caption(f"Identificador interno: `{jugador_seleccionado['id']}`")


if __name__ == "__main__":
    main()
