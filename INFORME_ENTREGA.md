# Informe de cumplimiento del taller

## Resultado general

Tribuna Global IA implementa el alcance obligatorio del taller: catálogo,
interfaz conversacional, prompt con roles, salida estructurada, persistencia JSON,
consulta filtrada, manejo de errores y pruebas prioritarias. Los desafíos de
ampliación del documento no forman parte del entregable base.

La integración se comprobó además con una llamada real y mínima a Gemini sobre
un caso irónico. El resultado negativo fue pertinente, estructurado y coherente
con el criterio esperado, sin alterar el archivo persistente.

## Actividades de implementación

| Actividad | Evidencia | Estado |
| --- | --- | --- |
| Catálogo inicial | 20 jugadores validados por identificador | Cumplida |
| Adaptación de interfaz | Selector, dos vistas, chat e historial de sesión | Cumplida |
| Construcción del prompt | Roles `system` y `human`, categorías, pertinencia e ironía | Cumplida |
| Salida estructurada | Pydantic y `with_structured_output` con JSON Schema | Cumplida |
| Almacenamiento | UUID, UTC, escritura atómica e idempotencia | Cumplida |
| Consulta | Filtros combinados, tabla, recuentos y descarga JSON | Cumplida |
| Errores y confirmación | Entrada, API y escritura diferenciadas | Cumplida |

## Entregables obligatorios

| Entregable | Ubicación o evidencia | Estado |
| --- | --- | --- |
| Código ejecutable con Streamlit | `app.py` | Cumplido |
| Catálogo de 20 futbolistas | `data/jugadores.json` | Cumplido |
| 12 opiniones, 4 jugadores y 4 categorías | `data/opiniones.json` | Cumplido |
| Instalación, configuración, versiones y ejecución | `README.md` | Cumplido |
| Persistencia y consulta filtrada | `EVIDENCIAS_PRUEBAS.md` | Cumplido |
| Registro de pruebas | 10 pruebas prioritarias | Cumplido |
| Reflexión sobre dos ambigüedades | Sección siguiente | Cumplido |

## Reflexión sobre ambigüedades de clasificación

### 1. Ironía con vocabulario aparentemente positivo

En «Qué precisión: falló todos los pases fáciles», la palabra «precisión» podría
sesgar una lectura superficial hacia positivo. La segunda parte contradice ese
sentido y revela ironía; por eso el resultado esperado es negativo. El prompt
ordena interpretar el sentido global y exige señales textuales antes de asumir
ironía.

### 2. Diferencia entre mixto y neutro

«Tiene gran técnica, pero su actitud me decepciona» contiene un elogio y una
crítica relevantes, por lo que corresponde a mixto. Neutro se reserva para una
descripción sin valoración, como «Es un jugador de fútbol». La ausencia de una
polaridad no debe inventar la contraria.

## Alcance no obligatorio

Quedan fuera del entregable base los desafíos propuestos por el taller:
comparación entre modelos, corrección manual de etiquetas, gráficas, soporte
multilingüe y migración a una base de datos multiusuario. No reducen el
cumplimiento de la rúbrica principal.
