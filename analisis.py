"""Clasificación de opiniones mediante LangChain y Gemini."""

from langchain_core.prompts import ChatPromptTemplate


PROMPT_VERSION = "1.0"

REGLAS_BASE = """
Eres un sistema de análisis de opiniones de aficionados sobre futbolistas.
Analiza únicamente la opinión actual acerca del jugador seleccionado. Tu tarea
es identificar si el texto es pertinente y, cuando corresponda, clasificar el
sentimiento expresado. No evalúes la calidad objetiva del jugador ni completes
la opinión con conocimientos externos.
""".strip()

MENSAJE_HUMANO = """
Jugador seleccionado:
<jugador>{jugador}</jugador>

Opinión del aficionado:
<opinion>{opinion}</opinion>
""".strip()


def crear_prompt_analisis() -> ChatPromptTemplate:
    """Construye la plantilla versionada con roles separados."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", REGLAS_BASE),
            ("human", MENSAJE_HUMANO),
        ]
    )


PROMPT_ANALISIS = crear_prompt_analisis()
