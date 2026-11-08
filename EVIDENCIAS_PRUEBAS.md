# Evidencias de pruebas

## Ejecución del bloque 3

- Fecha: 7 de noviembre de 2026.
- Rama: `develop`.
- Entorno local: Python 3.15.0, Streamlit 1.67.0, LangChain Core 1.7.6,
  LangChain Google GenAI 4.4.3 y Pydantic 2.14.3.
- Comando: `python -m pytest`.
- Resultado: **10 aprobadas, 0 fallidas** en 1.30 segundos.
- Llamadas a Gemini durante las pruebas: **0**.

## Registro automatizado

| N.º | Prueba prioritaria | Resultado observado |
| ---: | --- | --- |
| 1 | Carga de los 20 jugadores y unicidad de identificadores | Aprobada |
| 2 | Rechazo de identificadores de jugador repetidos | Aprobada |
| 3 | Rechazo de JSON inválido en el catálogo | Aprobada |
| 4 | Rechazo de esquema inválido en el catálogo | Aprobada |
| 5 | Error explícito cuando el catálogo no existe | Aprobada |
| 6 | Separación del prompt en roles y aislamiento de la opinión | Aprobada |
| 7 | Presencia de reglas críticas de clasificación | Aprobada |
| 8 | Doce opiniones ficticias, cuatro jugadores y cuatro categorías | Aprobada |
| 9 | Guardado persistente, UTF-8 e idempotencia por UUID | Aprobada |
| 10 | Filtros combinados, recuentos y ausencia de mutación | Aprobada |

## Comprobaciones de interfaz

Las siguientes verificaciones se ejecutaron con `streamlit.testing.v1.AppTest`,
sin navegador externo y sin utilizar la API de Gemini:

| Escenario | Resultado observado |
| --- | --- |
| Consulta sin filtros | 12 resultados; 4 positivos, 2 negativos, 3 neutros y 3 mixtos |
| Lionel Messi + positivo | 1 resultado; tabla y recuentos muestran el mismo registro |
| Kylian Mbappé | 0 resultados; aparece un mensaje informativo y la descarga vacía permanece disponible |
| Descarga | El control JSON está disponible y usa los filtros activos |
| Integridad del archivo | El SHA-256 se mantuvo en `D575BFE458ABD75B7CF866AB917F7FF968F585F50AFAF1BE75EBDEAEF8F8C857` |

## Observaciones

- La suite emitió 13 advertencias de deprecación de LangSmith relacionadas con
  Python 3.15. No produjeron fallos; el proyecto recomienda Python 3.13 y Docker
  utiliza esa versión.
- AppTest informó que se ejecutaba sin `ScriptRunContext`, comportamiento esperado
  en su modo de prueba aislado. La aplicación no presentó excepciones.
- La clasificación real con Gemini no se evaluó en este bloque para no consumir
  cuota ni depender de una clave local. El flujo se comprobó previamente con
  respuestas estructuradas simuladas.
