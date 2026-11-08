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
- Las pruebas automatizadas no llaman servicios externos. La validación real de
  Gemini se ejecutó una sola vez y se documenta en la sección siguiente.

## Evidencia real de Gemini

Se realizó una única solicitud con `gemini-3.5-flash` y nivel de razonamiento
`low`, sin guardar el resultado:

| Campo | Valor observado |
| --- | --- |
| Jugador | Lionel Messi |
| Opinión | «Qué precisión: falló todos los pases fáciles» |
| `es_pertinente` | `true` |
| `sentimiento` | `negativo` |
| Razón | Identificó que el elogio literal contrasta irónicamente con la crítica por fallar pases sencillos |
| Contrato | Objeto `AnalisisOpinion` validado por Pydantic |
| Solicitudes realizadas | 1 |
| Persistencia | No se guardó; SHA-256 de `opiniones.json` sin cambios |

La respuesta coincide con el caso de aceptación de ironía. La clave se leyó
desde `.env` y no se registró en salidas, documentación ni Git.

## Evidencia de Docker y persistencia

La imagen se construyó desde cero con Python 3.13 y el servicio se dejó activo en
`http://localhost:8501`.

| Comprobación | Resultado observado |
| --- | --- |
| Construcción | Imagen `futbolistaschatbot-tribuna-global` creada correctamente |
| Salud inicial | `HTTP 200` y cuerpo `ok` |
| Registros antes del reinicio | 12 |
| Reinicio | `docker compose restart` completado |
| Salud después del reinicio | `HTTP 200` y cuerpo `ok` |
| Registros después del reinicio | 12 |
| Integridad | SHA-256 sin cambios: `D575BFE458ABD75B7CF866AB917F7FF968F585F50AFAF1BE75EBDEAEF8F8C857` |

El contenedor `tribuna-global-ia` quedó ejecutándose con el puerto `8501`
publicado. El volumen `./data:/app/data` conservó las opiniones tras el reinicio.

## Revalidación del contexto conversacional

Después de utilizar la aplicación y añadir una opinión real, la suite se ajustó
para verificar el mínimo exigido de 12 registros sin asumir que el archivo nunca
crecerá. El resultado continuó en **10 aprobadas, 0 fallidas**.

También se comprobó que cada selector muestra solo el jugador actual y abre las
opciones al hacer clic, sin entrada de texto, tanto en el chat como en consultas.
La selección es única y cambiarla no altera el jugador de mensajes anteriores.
