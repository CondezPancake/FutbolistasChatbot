# Tribuna Global IA

**Cada opinión juega su partido.**

Aplicación académica en Streamlit para registrar opiniones sobre futbolistas,
clasificarlas con Gemini mediante LangChain y consultarlas después de reiniciar
la aplicación.

## Estado actual

El repositorio contiene la estructura base, la configuración reproducible, los
datos ficticios requeridos, el selector validado de futbolistas y la identidad
visual responsive. La navegación separa la emisión de opiniones de la consulta
persistente. El chat ya conserva mensajes durante la sesión; la clasificación
cuenta con un prompt versionado y seguro. La conexión con Gemini, la salida
estructurada y el guardado definitivo se implementarán en las siguientes actividades.

## Prompt de clasificación

`analisis.py` define un `ChatPromptTemplate` con mensajes `system` y `human`.
La versión `1.0` establece:

- criterios explícitos para positivo, negativo, neutro y mixto;
- pertinencia evaluada antes del sentimiento;
- sentimiento nulo para mensajes no pertinentes;
- interpretación prudente de negaciones e ironía;
- razón breve, en tercera persona y sin hechos inventados;
- tratamiento de la opinión como datos no confiables.

La opinión se delimita dentro del mensaje humano y nunca se incorpora al mensaje
del sistema. Esta etapa construye el prompt, pero todavía no consume la API.

## Conversación de sesión

La sección **Emitir opinión** permite:

- enviar textos de 5 a 1000 caracteres con `st.chat_input`;
- mostrar mensajes mediante `st.chat_message`;
- capturar el identificador y nombre del futbolista al enviar cada opinión;
- mantener el historial durante las reejecuciones de Streamlit;
- iniciar una conversación nueva sin modificar `data/opiniones.json`.

Las respuestas actuales indican claramente que el análisis y el guardado todavía
no se han ejecutado; no se inventan clasificaciones provisionales.

## Navegación

La barra lateral conserva dos recorridos independientes:

- **Emitir opinión:** mantiene visible el futbolista seleccionado y prepara la
  experiencia conversacional.
- **Consultar opiniones:** presenta el acceso a filtros, recuentos y descarga sin
  realizar llamadas al modelo.

La vista activa se conserva en `st.session_state` durante las reejecuciones de
Streamlit y se restablece de forma segura si contiene un valor desconocido.

## Identidad visual

Tribuna Global IA utiliza una interfaz conversacional oscura inspirada en la
claridad de las herramientas modernas de IA, con una identidad futbolística propia:

- superficies oscuras y jerarquía visual limpia;
- verde cancha como color de acción;
- marca tipográfica `TG` sin recursos externos;
- contexto visible del jugador seleccionado;
- estilos responsive, foco de teclado y reducción de movimiento.

Los tokens y componentes visuales viven en `styles.css`; la configuración base
de Streamlit se mantiene en `.streamlit/config.toml`.

## Catálogo de futbolistas

La aplicación lee `data/jugadores.json` con UTF-8 y comprueba antes de mostrarlo:

- versión de esquema compatible;
- presencia de identificador, nombre y país;
- textos no vacíos;
- ausencia de campos inesperados;
- identificadores internos únicos.

El selector muestra nombre y país, pero utiliza el identificador estable del
jugador como valor interno.

## Requisitos

- Python 3.13 recomendado
- Docker 29 o posterior, opcional
- Docker Compose 5 o posterior, opcional
- Clave de Gemini API para las actividades de análisis

## Configuración local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Completa `GOOGLE_API_KEY` en `.env` cuando la integración con Gemini esté lista.
El archivo `.env` está excluido de Git.

## Ejecución local

```powershell
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`.

## Ejecución con Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

La carpeta `data` se monta en el contenedor para conservar las opiniones entre
reinicios.

## Pruebas

```powershell
pytest
```

La suite tendrá un máximo de diez pruebas prioritarias de funcionamiento.

## Estructura

```text
.
├── app.py
├── analisis.py
├── almacenamiento.py
├── styles.css
├── data/
│   ├── jugadores.json
│   └── opiniones.json
├── tests/
├── .streamlit/config.toml
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── compose.yaml
└── README.md
```

## Seguridad

- No publiques `.env` ni claves reales.
- Usa `.env.example` únicamente como plantilla.
- Los errores de la API no se convierten en opiniones ni sentimientos neutros.
- Los doce registros incluidos son ficticios y están identificados con el
  modelo `registro-ficticio`.
