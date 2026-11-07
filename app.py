"""Punto de entrada de la aplicación Tribuna Global IA."""

from enum import Enum
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from almacenamiento import ErrorCatalogo, cargar_jugadores


DIRECTORIO_PROYECTO = Path(__file__).resolve().parent
RUTA_JUGADORES = DIRECTORIO_PROYECTO / "data" / "jugadores.json"
RUTA_ESTILOS = DIRECTORIO_PROYECTO / "styles.css"


class Vista(str, Enum):
    """Secciones principales disponibles en la interfaz."""

    EMITIR = "Emitir opinión"
    CONSULTAR = "Consultar opiniones"


MENSAJE_BIENVENIDA = {
    "role": "assistant",
    "content": (
        "Selecciona un futbolista y comparte tu opinión. "
        "Analizaré únicamente el mensaje que envíes."
    ),
    "tipo": "bienvenida",
    "jugador_id": None,
    "jugador_nombre": None,
}


def crear_historial_inicial() -> list[dict[str, Any]]:
    """Crea un historial nuevo sin compartir referencias mutables."""
    return [MENSAJE_BIENVENIDA.copy()]


def inicializar_estado_interfaz() -> None:
    """Garantiza una vista válida aunque cambie el estado de la sesión."""
    vistas_validas = {vista.value for vista in Vista}
    if st.session_state.get("vista_activa") not in vistas_validas:
        st.session_state.vista_activa = Vista.EMITIR.value
    if not isinstance(st.session_state.get("historial_chat"), list):
        st.session_state.historial_chat = crear_historial_inicial()


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
        st.divider()
        st.radio(
            "Navegación principal",
            options=[vista.value for vista in Vista],
            format_func=lambda opcion: (
                f"💬  {opcion}" if opcion == Vista.EMITIR.value else f"📚  {opcion}"
            ),
            key="vista_activa",
            label_visibility="collapsed",
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


def mostrar_jugador_actual(jugador: dict[str, Any]) -> None:
    """Muestra el contexto activo sin exponer datos sin escapar."""
    nombre_original = str(jugador["nombre"])
    iniciales = "".join(parte[0] for parte in nombre_original.split()[:2]).upper()
    nombre = escape(nombre_original)
    pais = escape(str(jugador["pais"]))
    jugador_id = escape(str(jugador["id"]))

    st.markdown(
        f"""
        <section class="tg-player" aria-label="Futbolista seleccionado">
          <div class="tg-player__avatar" aria-hidden="true">{iniciales}</div>
          <div class="tg-player__body">
            <span class="tg-player__label">Conversación enfocada en</span>
            <strong>{nombre}</strong>
            <span class="tg-player__country">{pais}</span>
          </div>
          <span class="tg-player__id">{jugador_id}</span>
        </section>
        """,
        unsafe_allow_html=True,
    )


def mostrar_vista_emitir(jugador: dict[str, Any]) -> None:
    """Construye la entrada visual de la experiencia conversacional."""
    mostrar_encabezado()
    mostrar_jugador_actual(jugador)
    st.markdown(
        """
        <section class="tg-view-intro">
          <span class="tg-view-intro__eyebrow">Emitir opinión</span>
          <h2>¿Qué lectura tienes de su juego?</h2>
          <p>
            En el siguiente paso podrás escribir una opinión y conversar con
            Tribuna Global IA sin mezclarla con comentarios anteriores.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def mostrar_vista_consultar() -> None:
    """Construye la entrada visual de la consulta persistente."""
    st.markdown(
        """
        <section class="tg-page-heading">
          <span class="tg-kicker">Archivo de la tribuna</span>
          <h1>Consulta lo que piensa la afición.</h1>
          <p>
            Los registros persistidos se explorarán sin realizar nuevas
            llamadas al modelo de inteligencia artificial.
          </p>
        </section>
        <section class="tg-query-preview" aria-label="Funciones de consulta">
          <article>
            <span>01</span>
            <strong>Filtra</strong>
            <p>Acota los resultados por futbolista y sentimiento.</p>
          </article>
          <article>
            <span>02</span>
            <strong>Compara</strong>
            <p>Revisa recuentos construidos con los mismos filtros.</p>
          </article>
          <article>
            <span>03</span>
            <strong>Descarga</strong>
            <p>Exporta únicamente los registros que estás viendo.</p>
          </article>
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
        initial_sidebar_state="expanded",
    )
    cargar_estilos()
    inicializar_estado_interfaz()

    try:
        jugadores = cargar_catalogo_aplicacion()
    except ErrorCatalogo as exc:
        st.error(str(exc))
        st.stop()

    jugador_seleccionado = seleccionar_jugador(jugadores)

    if st.session_state.vista_activa == Vista.EMITIR.value:
        mostrar_vista_emitir(jugador_seleccionado)
    else:
        mostrar_vista_consultar()


if __name__ == "__main__":
    main()
