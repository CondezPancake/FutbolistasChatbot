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

CRITERIOS_SENTIMIENTO = """
Utiliza exactamente una de estas categorías cuando el texto sea pertinente:

- positivo: expresa elogio, admiración, satisfacción o una valoración favorable.
- negativo: expresa crítica, rechazo, decepción o una valoración desfavorable.
- neutro: describe al jugador sin una valoración positiva o negativa relevante.
- mixto: contiene elogios y críticas relevantes dentro de la misma opinión.

No confundas mixto con neutro. La ausencia de elogios no implica una crítica y
la ausencia de críticas no implica una valoración positiva.
""".strip()

MENSAJE_SISTEMA = "\n\n".join([REGLAS_BASE, CRITERIOS_SENTIMIENTO])

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
            ("system", MENSAJE_SISTEMA),
            ("human", MENSAJE_HUMANO),
        ]
    )


PROMPT_ANALISIS = crear_prompt_analisis()
