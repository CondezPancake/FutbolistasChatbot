"""Punto de entrada de la aplicación Tribuna Global IA."""

from pathlib import Path
from typing import Any

import streamlit as st

from almacenamiento import ErrorCatalogo, cargar_jugadores


DIRECTORIO_PROYECTO = Path(__file__).resolve().parent
RUTA_JUGADORES = DIRECTORIO_PROYECTO / "data" / "jugadores.json"
RUTA_ESTILOS = DIRECTORIO_PROYECTO / "styles.css"


def cargar_estilos() -> None:
    """Inyecta la hoja de estilos local de la aplicación."""
    estilos = RUTA_ESTILOS.read_text(encoding="utf-8")
    st.markdown(f"<style>{estilos}</style>", unsafe_allow_html=True)


@st.cache_data
def cargar_catalogo_aplicacion() -> list[dict[str, Any]]:
    """Carga el catálogo una vez mientras el archivo no cambie."""
    return cargar_jugadores(RUTA_JUGADORES)


def seleccionar_jugador(jugadores: list[dict[str, Any]]) -> dict[str, Any]:
    """Muestra el catálogo y conserva el identificador como valor interno."""
    jugadores_por_id = {jugador["id"]: jugador for jugador in jugadores}

    with st.sidebar:
        st.markdown(
            """
            <div class="tg-brand">
              <div class="tg-brand__mark" aria-hidden="true">TG</div>
              <div>
                <div class="tg-brand__name">Tribuna Global</div>
                <div class="tg-brand__tag">Inteligencia futbolera</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        jugador_id = st.selectbox(
            "Futbolista",
            options=list(jugadores_por_id),
            format_func=lambda identificador: (
                f"{jugadores_por_id[identificador]['nombre']} · "
                f"{jugadores_por_id[identificador]['pais']}"
            ),
        )

    return jugadores_por_id[jugador_id]


def mostrar_encabezado() -> None:
    """Presenta la identidad principal del producto."""
    st.markdown(
        """
        <section class="tg-hero">
          <span class="tg-kicker">Análisis de percepción futbolística</span>
          <h1>La conversación también se juega.</h1>
          <p>
            Comparte tu lectura sobre las figuras del fútbol mundial y obtén
            una clasificación clara, breve y centrada en tus palabras.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Configura la página inicial de la aplicación."""
    st.set_page_config(
        page_title="Tribuna Global IA",
        page_icon="⚽",
        layout="wide",
    )
    cargar_estilos()

    try:
        jugadores = cargar_catalogo_aplicacion()
    except ErrorCatalogo as exc:
        st.error(str(exc))
        st.stop()

    jugador_seleccionado = seleccionar_jugador(jugadores)

    mostrar_encabezado()
    st.info(
        "Futbolista seleccionado: "
        f"**{jugador_seleccionado['nombre']}** · {jugador_seleccionado['pais']}"
    )
    st.caption(f"Identificador interno: `{jugador_seleccionado['id']}`")


if __name__ == "__main__":
    main()
