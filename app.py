"""Punto de entrada de la aplicación Tribuna Global IA."""

from enum import Enum
from html import escape
import json
from pathlib import Path
from typing import Any

import streamlit as st

from almacenamiento import (
    ErrorCatalogo,
    ErrorOpiniones,
    SENTIMIENTOS,
    cargar_jugadores,
    cargar_opiniones,
    consultar_opiniones,
    contar_sentimientos,
    crear_registro,
    guardar_opinion,
)
from analisis import (
    ErrorAnalisis,
    ErrorEntradaAnalisis,
    analizar_opinion,
    responder_pregunta,
)
from configuracion import (
    ErrorConfiguracionIA,
    cargar_configuracion_ia,
    gemini_esta_configurado,
)


DIRECTORIO_PROYECTO = Path(__file__).resolve().parent
RUTA_JUGADORES = DIRECTORIO_PROYECTO / "data" / "jugadores.json"
RUTA_OPINIONES = DIRECTORIO_PROYECTO / "data" / "opiniones.json"
RUTA_ESTILOS = DIRECTORIO_PROYECTO / "styles.css"
LONGITUD_MINIMA_OPINION = 5
LONGITUD_MAXIMA_OPINION = 1000
ETIQUETAS_SENTIMIENTO = {
    "positivo": "Positivo",
    "negativo": "Negativo",
    "neutro": "Neutro",
    "mixto": "Mixto",
}


class Vista(str, Enum):
    """Secciones principales disponibles en la interfaz."""

    EMITIR = "Emitir opinión"
    CONSULTAR = "Consultar opiniones"


class ModoMensaje(str, Enum):
    """Acciones disponibles dentro de la conversación."""

    OPINAR = "Compartir opinión"
    PREGUNTAR = "Hacer pregunta"


MENSAJE_BIENVENIDA = {
    "role": "assistant",
    "content": (
        "Selecciona un futbolista. Puedes compartir una opinión para analizarla "
        "y guardarla, o hacer una pregunta informativa que no se persistirá."
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
    modos_validos = {modo.value for modo in ModoMensaje}
    if st.session_state.get("modo_mensaje") not in modos_validos:
        st.session_state.modo_mensaje = ModoMensaje.OPINAR.value
    if not isinstance(st.session_state.get("historial_chat"), list):
        st.session_state.historial_chat = crear_historial_inicial()
    if not isinstance(st.session_state.get("jugador_conversacion_id"), str):
        st.session_state.jugador_conversacion_id = None


def reiniciar_conversacion() -> None:
    """Limpia el chat y permite seleccionar otro jugador sin borrar archivos."""
    st.session_state.historial_chat = crear_historial_inicial()
    st.session_state.jugador_conversacion_id = None


def cargar_estilos() -> None:
    """Inyecta la hoja de estilos local de la aplicación."""
    estilos = RUTA_ESTILOS.read_text(encoding="utf-8")
    st.markdown(f"<style>{estilos}</style>", unsafe_allow_html=True)


@st.cache_data
def cargar_catalogo_aplicacion() -> list[dict[str, Any]]:
    """Carga el catálogo una vez mientras el archivo no cambie."""
    return cargar_jugadores(RUTA_JUGADORES)


def cargar_opiniones_aplicacion() -> dict[str, Any]:
    """Recupera y valida el archivo persistente sin modificarlo."""
    return cargar_opiniones(RUTA_OPINIONES)


def mostrar_estado_gemini() -> None:
    """Muestra disponibilidad de configuración sin revelar secretos."""
    configurado = gemini_esta_configurado()
    clase = "is-ready" if configurado else "is-pending"
    etiqueta = "Gemini configurado" if configurado else "Gemini pendiente"
    st.markdown(
        f"""
        <div class="tg-provider-status {clase}" aria-label="{etiqueta}">
          <span aria-hidden="true"></span>
          {etiqueta}
        </div>
        """,
        unsafe_allow_html=True,
    )


def seleccionar_jugador(jugadores: list[dict[str, Any]]) -> dict[str, Any]:
    """Selecciona sin escritura y bloquea el jugador durante la conversación."""
    jugadores_por_id = {jugador["id"]: jugador for jugador in jugadores}
    jugador_bloqueado_id = st.session_state.jugador_conversacion_id
    if jugador_bloqueado_id not in jugadores_por_id:
        jugador_bloqueado_id = None
        st.session_state.jugador_conversacion_id = None

    jugador_estado = st.session_state.get("jugador_seleccionado_id")
    if jugador_bloqueado_id is not None:
        st.session_state.jugador_seleccionado_id = jugador_bloqueado_id
    elif jugador_estado not in jugadores_por_id:
        st.session_state.jugador_seleccionado_id = next(iter(jugadores_por_id))

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
        jugador_id = st.radio(
            "Futbolista",
            options=list(jugadores_por_id),
            format_func=lambda identificador: (
                f"{jugadores_por_id[identificador]['nombre']} · "
                f"{jugadores_por_id[identificador]['pais']}"
            ),
            key="jugador_seleccionado_id",
            disabled=jugador_bloqueado_id is not None,
        )
        if jugador_bloqueado_id is not None:
            st.caption(
                "El futbolista está fijado para esta conversación. "
                "Pulsa “Nueva conversación” para cambiarlo."
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
        st.button(
            "＋  Nueva conversación",
            key="nueva_conversacion",
            on_click=reiniciar_conversacion,
            use_container_width=True,
        )
        mostrar_estado_gemini()

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


def mostrar_historial_chat() -> None:
    """Renderiza los mensajes conservando el jugador de cada envío."""
    for mensaje in st.session_state.historial_chat:
        rol = mensaje.get("role")
        contenido = mensaje.get("content")
        if rol not in {"user", "assistant"} or not isinstance(contenido, str):
            continue

        avatar = "⚽" if rol == "assistant" else "👤"
        with st.chat_message(rol, avatar=avatar):
            if rol == "user" and mensaje.get("jugador_nombre"):
                etiqueta = (
                    "Pregunta" if mensaje.get("tipo") == "pregunta" else "Opinión"
                )
                st.caption(f"{etiqueta} sobre {mensaje['jugador_nombre']}")
            st.markdown(contenido)


def procesar_opinion(jugador: dict[str, Any], texto: str) -> str | None:
    """Analiza y persiste un envío, confirmándolo solo después de escribir."""
    opinion = texto.strip()
    if len(opinion) < LONGITUD_MINIMA_OPINION:
        return "La opinión debe contener al menos 5 caracteres útiles."
    if len(opinion) > LONGITUD_MAXIMA_OPINION:
        return "La opinión no puede superar los 1000 caracteres."

    st.session_state.jugador_conversacion_id = jugador["id"]
    mensaje_usuario = {
        "role": "user",
        "content": opinion,
        "tipo": "opinion",
        "jugador_id": jugador["id"],
        "jugador_nombre": jugador["nombre"],
    }
    st.session_state.historial_chat.append(mensaje_usuario)
    registro_id = None

    try:
        with st.spinner("Gemini está analizando únicamente este mensaje..."):
            resultado = analizar_opinion(jugador, opinion)
    except (ErrorAnalisis, ErrorEntradaAnalisis) as exc:
        contenido = (
            "⚠️ **No fue posible analizar la opinión.**\n\n"
            f"{exc}\n\n"
            "_Tu texto permanece en esta conversación y no fue guardado._"
        )
        tipo = "error_analisis"
    else:
        if resultado.es_pertinente:
            sentimiento = str(resultado.sentimiento).capitalize()
            try:
                configuracion = cargar_configuracion_ia()
                registro = crear_registro(
                    jugador,
                    opinion,
                    resultado,
                    configuracion.modelo,
                )
                registro_id = registro["id"]
                mensaje_usuario["registro_id"] = registro_id
                guardado = guardar_opinion(RUTA_OPINIONES, registro)
            except (ErrorOpiniones, ErrorConfiguracionIA) as exc:
                contenido = (
                    f"**Sentimiento: {sentimiento}**\n\n"
                    f"{resultado.razon}\n\n"
                    "⚠️ **El análisis terminó, pero no fue posible guardar la opinión.**\n\n"
                    f"{exc}\n\n"
                    "_Tu texto permanece en esta conversación._"
                )
                tipo = "error_guardado"
            else:
                if guardado:
                    contenido = (
                        f"**Sentimiento: {sentimiento}**\n\n"
                        f"{resultado.razon}\n\n"
                        "✅ **Opinión guardada correctamente.**"
                    )
                    tipo = "opinion_guardada"
                else:
                    contenido = (
                        f"**Sentimiento: {sentimiento}**\n\n"
                        f"{resultado.razon}\n\n"
                        "ℹ️ **Este envío ya estaba guardado; no se creó un duplicado.**"
                    )
                    tipo = "opinion_existente"
        else:
            contenido = (
                "**Mensaje no pertinente**\n\n"
                f"{resultado.razon}\n\n"
                "_No se guardará como una opinión sobre el futbolista._"
            )
            tipo = "no_pertinente"

    st.session_state.historial_chat.append(
        {
            "role": "assistant",
            "content": contenido,
            "tipo": tipo,
            "jugador_id": jugador["id"],
            "jugador_nombre": jugador["nombre"],
            "registro_id": registro_id,
        }
    )
    return None


def procesar_pregunta(jugador: dict[str, Any], texto: str) -> str | None:
    """Responde sobre el jugador sin clasificar ni persistir el mensaje."""
    pregunta = texto.strip()
    if len(pregunta) < LONGITUD_MINIMA_OPINION:
        return "La pregunta debe contener al menos 5 caracteres útiles."
    if len(pregunta) > LONGITUD_MAXIMA_OPINION:
        return "La pregunta no puede superar los 1000 caracteres."

    st.session_state.jugador_conversacion_id = jugador["id"]
    st.session_state.historial_chat.append(
        {
            "role": "user",
            "content": pregunta,
            "tipo": "pregunta",
            "jugador_id": jugador["id"],
            "jugador_nombre": jugador["nombre"],
        }
    )

    try:
        with st.spinner("Gemini está preparando una respuesta breve..."):
            respuesta = responder_pregunta(jugador, pregunta)
    except (ErrorAnalisis, ErrorEntradaAnalisis) as exc:
        contenido = (
            "⚠️ **No fue posible responder la pregunta.**\n\n"
            f"{exc}\n\n"
            "_Tu pregunta permanece en esta conversación y no fue guardada._"
        )
        tipo = "error_pregunta"
    else:
        contenido = f"{respuesta}\n\n_Respuesta informativa; no se guardó como opinión._"
        tipo = "respuesta_pregunta"

    st.session_state.historial_chat.append(
        {
            "role": "assistant",
            "content": contenido,
            "tipo": tipo,
            "jugador_id": jugador["id"],
            "jugador_nombre": jugador["nombre"],
        }
    )
    return None


def mostrar_vista_emitir(jugador: dict[str, Any]) -> None:
    """Construye la entrada visual de la experiencia conversacional."""
    mostrar_encabezado()
    mostrar_jugador_actual(jugador)
    st.markdown(
        """
        <section class="tg-view-intro">
          <span class="tg-view-intro__eyebrow">Emitir opinión</span>
          <h2>Opina o pregunta sobre el futbolista.</h2>
          <p>
            Las opiniones se clasifican y guardan. Las preguntas reciben una
            respuesta informativa, pero nunca se almacenan como opiniones.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    modo = st.radio(
        "¿Qué quieres hacer?",
        options=[modo.value for modo in ModoMensaje],
        key="modo_mensaje",
        horizontal=True,
    )
    mostrar_historial_chat()
    marcador = (
        f"Escribe tu opinión sobre {jugador['nombre']}"
        if modo == ModoMensaje.OPINAR.value
        else f"Pregunta algo sobre {jugador['nombre']}"
    )
    mensaje = st.chat_input(
        marcador,
        max_chars=LONGITUD_MAXIMA_OPINION,
    )
    if mensaje is not None:
        if modo == ModoMensaje.OPINAR.value:
            error = procesar_opinion(jugador, mensaje)
        else:
            error = procesar_pregunta(jugador, mensaje)
        if error:
            st.error(error)
        else:
            st.rerun()


def mostrar_vista_consultar(
    archivo_opiniones: dict[str, Any],
    jugadores: list[dict[str, Any]],
) -> None:
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
        """,
        unsafe_allow_html=True,
    )

    jugadores_por_id = {jugador["id"]: jugador for jugador in jugadores}
    st.markdown(
        "<div class='tg-query-section'><strong>Filtra el archivo</strong>"
        "<span>Los dos filtros se aplican en conjunto.</span></div>",
        unsafe_allow_html=True,
    )
    columna_jugador, columna_sentimiento = st.columns(2)
    with columna_jugador:
        jugador_filtro = st.pills(
            "Jugador",
            options=["todos", *jugadores_por_id],
            default="todos",
            required=True,
            format_func=lambda valor: (
                "Todos los jugadores"
                if valor == "todos"
                else jugadores_por_id[valor]["nombre"]
            ),
            key="filtro_jugador",
            width="stretch",
            wrap=True,
        )
        jugador_id = None if jugador_filtro == "todos" else jugador_filtro
    with columna_sentimiento:
        sentimiento = st.selectbox(
            "Sentimiento",
            options=[None, *SENTIMIENTOS],
            format_func=lambda valor: (
                "Todos los sentimientos"
                if valor is None
                else ETIQUETAS_SENTIMIENTO[valor]
            ),
            key="filtro_sentimiento",
        )

    registros_filtrados = consultar_opiniones(
        archivo_opiniones["opiniones"],
        jugador_id=jugador_id,
        sentimiento=sentimiento,
    )
    conteos = contar_sentimientos(registros_filtrados)

    st.markdown(
        "<div class='tg-query-section'><strong>Resumen filtrado</strong>"
        "<span>Tabla, cifras y descarga comparten el mismo resultado.</span></div>",
        unsafe_allow_html=True,
    )
    columnas_metricas = st.columns(5)
    columnas_metricas[0].metric("Total", len(registros_filtrados))
    for columna, categoria in zip(columnas_metricas[1:], SENTIMIENTOS, strict=True):
        columna.metric(ETIQUETAS_SENTIMIENTO[categoria], conteos[categoria])

    if registros_filtrados:
        filas = [
            {
                "Fecha UTC": registro["fecha_utc"].replace("T", " ").replace(
                    "+00:00", " UTC"
                ),
                "Jugador": registro["jugador_nombre"],
                "Opinión original": registro["opinion_original"],
                "Sentimiento": ETIQUETAS_SENTIMIENTO[registro["sentimiento"]],
                "Razón": registro["razon"],
            }
            for registro in registros_filtrados
        ]
        st.dataframe(filas, hide_index=True, width="stretch")
    else:
        st.info("No hay opiniones que coincidan con los filtros seleccionados.")

    contenido_descarga = json.dumps(
        {"version": 1, "opiniones": registros_filtrados},
        ensure_ascii=False,
        indent=2,
    )
    st.download_button(
        "Descargar resultados en JSON",
        data=f"{contenido_descarga}\n",
        file_name="opiniones_filtradas.json",
        mime="application/json",
        width="stretch",
    )
    st.caption(
        f"Archivo validado: {len(archivo_opiniones['opiniones'])} opiniones disponibles. "
        "La consulta no consume Gemini."
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
        archivo_opiniones = cargar_opiniones_aplicacion()
    except (ErrorCatalogo, ErrorOpiniones) as exc:
        st.error(str(exc))
        st.stop()

    jugador_seleccionado = seleccionar_jugador(jugadores)

    if st.session_state.vista_activa == Vista.EMITIR.value:
        mostrar_vista_emitir(jugador_seleccionado)
    else:
        mostrar_vista_consultar(archivo_opiniones, jugadores)


if __name__ == "__main__":
    main()
