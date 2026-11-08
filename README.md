# Tribuna Global IA

**Cada opinión juega su partido.**

Aplicación académica en Streamlit para registrar opiniones sobre futbolistas,
clasificarlas con Gemini mediante LangChain y consultarlas después de reiniciar
la aplicación.

## Estado actual

El repositorio contiene la estructura base, la configuración reproducible, los
datos ficticios requeridos, el selector validado de futbolistas y la identidad
visual responsive. La navegación separa la emisión de opiniones de la consulta
persistente. El chat conserva mensajes durante la sesión e invoca una cadena de
Gemini con salida estructurada. El archivo de opiniones se carga bajo un esquema
validado. Los análisis pertinentes se convierten en registros completos y se
guardan de forma atómica. La consulta permite combinar filtros, revisar recuentos
y descargar exactamente los resultados visibles. El entregable obligatorio está
completo y cuenta con evidencia local, Docker y una llamada real mínima a Gemini.

## Gemini y salida estructurada

La integración utiliza `ChatGoogleGenerativeAI` con el modelo estable configurado
en `GEMINI_MODEL`. El cliente se crea de forma diferida: importar los módulos o
abrir la interfaz no realiza una llamada a la API.

Variables disponibles en `.env`:

```dotenv
GOOGLE_API_KEY=clave_local_rotada
GEMINI_MODEL=gemini-3.5-flash
GEMINI_REASONING_EFFORT=low
```

La clave se conserva como `SecretStr` y nunca se muestra en el indicador visual.
Para Gemini 3.5 no se fuerza `temperature`; el nivel de razonamiento queda en
`low` por defecto para reducir latencia y consumo.

`AnalisisOpinion` limita la respuesta a pertinencia, sentimiento y una razón de
máximo 300 caracteres. La coherencia se valida después del esquema: una opinión
pertinente requiere sentimiento y una no pertinente exige un valor nulo. La
cadena usa `with_structured_output(..., method="json_schema")`.

`analizar_opinion` normaliza y valida la entrada antes de invocar el modelo. Un
fallo de configuración, proveedor o validación produce un mensaje seguro; los
detalles internos y la clave nunca se muestran. La opinión queda visible en el
chat y no se inventa una categoría de respaldo.

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
del sistema. Cada envío pertinente consume una llamada al modelo; las consultas
del archivo no realizan llamadas a Gemini.

## Conversación de sesión

La sección **Emitir opinión** permite:

- enviar textos de 5 a 1000 caracteres con `st.chat_input`;
- alternar entre una opinión persistente y una pregunta informativa;
- mostrar mensajes mediante `st.chat_message`;
- capturar el identificador y nombre del futbolista al enviar cada opinión;
- mantener el historial durante las reejecuciones de Streamlit;
- iniciar una conversación nueva sin modificar `data/opiniones.json`.

Las respuestas distinguen un análisis pertinente, un texto ajeno al futbolista,
un fallo de Gemini y un fallo de escritura. La confirmación de guardado aparece
únicamente después de reemplazar correctamente el archivo persistente.

El futbolista se elige mediante opciones cerradas, sin campo de escritura. Al
enviar el primer mensaje queda fijado durante toda la conversación; para cambiarlo
se debe pulsar **Nueva conversación**. Las preguntas se responden de forma breve
y aislada, pero nunca se clasifican ni se guardan como opiniones.

## Carga de opiniones

`data/opiniones.json` se lee como un diccionario versionado. Cada registro valida
UUID, fecha UTC, jugador, texto original, categoría, razón, modelo y versión del
prompt. También se rechazan campos inesperados e identificadores repetidos.

Si el archivo no existe, la aplicación trabaja con una estructura vacía en
memoria. Si contiene JSON inválido o un esquema desconocido, muestra el error y
conserva el archivo original sin reemplazarlo silenciosamente.

## Persistencia segura

La aplicación, no Gemini, genera el UUID, la fecha UTC, la identidad del jugador,
el modelo y la versión del prompt. Solo los análisis pertinentes se convierten
en registros.

Antes de guardar se vuelve a validar el registro y el archivo completo. El nuevo
contenido se escribe en un temporal dentro de `data`, se sincroniza y finalmente
reemplaza `opiniones.json`. Si el proceso falla, el original se conserva. Repetir
el guardado del mismo UUID no crea otro registro; dos envíos independientes con
el mismo texto sí pueden conservarse como opiniones distintas.

## Navegación

La barra lateral conserva dos recorridos independientes:

- **Emitir opinión:** mantiene visible el futbolista seleccionado y prepara la
  experiencia conversacional.
- **Consultar opiniones:** presenta el acceso a filtros, recuentos y descarga sin
  realizar llamadas al modelo.

La vista activa se conserva en `st.session_state` durante las reejecuciones de
Streamlit y se restablece de forma segura si contiene un valor desconocido.

## Consulta de opiniones

La sección **Consultar opiniones** permite seleccionar todos los jugadores o uno
específico y combinarlo con todos los sentimientos o una categoría. La tabla
muestra fecha UTC, jugador, opinión original, sentimiento y razón. El total y los
cuatro recuentos se calculan sobre el mismo resultado filtrado.

La descarga genera `opiniones_filtradas.json` con únicamente los registros que
aparecen en pantalla. Cambiar filtros no invoca Gemini ni modifica el archivo.

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

## Versiones utilizadas

| Componente | Versión |
| --- | --- |
| Python local | 3.15.0 |
| Python en Docker | 3.13 |
| Streamlit | 1.67.0 |
| LangChain Core | 1.7.6 |
| LangChain Google GenAI | 4.4.3 |
| Pydantic | 2.14.3 |
| Docker | 29.8.2 |
| Docker Compose | 5.6.0 |

## Configuración local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Completa `GOOGLE_API_KEY` en `.env` cuando la integración con Gemini esté lista.
Usa una clave nueva y rotada. El archivo `.env` está excluido de Git.

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
Actualmente contiene exactamente diez. El resultado observado y las
comprobaciones de interfaz se documentan en
[EVIDENCIAS_PRUEBAS.md](EVIDENCIAS_PRUEBAS.md).

El cumplimiento punto por punto y la reflexión sobre ambigüedades están en
[INFORME_ENTREGA.md](INFORME_ENTREGA.md).

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

## Paso a paso para ejecutar y demostrar el proyecto

1. Abre PowerShell en la raíz del repositorio y confirma que estás en
   `develop` con `git branch --show-current`.
2. Crea el entorno con `python -m venv .venv`.
3. Actívalo con `.\.venv\Scripts\Activate.ps1`.
4. Instala las dependencias mediante
   `python -m pip install -r requirements-dev.txt`.
5. Copia la plantilla con `Copy-Item .env.example .env` y configura dentro de
   `.env` una clave nueva en `GOOGLE_API_KEY`; nunca la publiques ni la pegues
   en capturas o commits.
6. Ejecuta `pytest` y confirma que las 10 pruebas terminan aprobadas.
7. Inicia localmente con `streamlit run app.py` y abre
   `http://localhost:8501`.
8. En **Emitir opinión**, selecciona un jugador, envía un texto y comprueba que
   la confirmación aparece solamente después del guardado. Cambia a **Hacer
   pregunta** para consultar información sin crear un registro.
9. En **Consultar opiniones**, combina los filtros, compara tabla y recuentos y
   descarga `opiniones_filtradas.json`.
10. Para la demostración con Docker ejecuta `docker compose up --build -d`,
    consulta `http://localhost:8501`, revisa el estado con `docker compose ps`
    y los logs con `docker compose logs --tail 50`.
11. Reinicia con `docker compose restart`, vuelve a consultar las opiniones y
    verifica que `data/opiniones.json` conserva los registros.
12. Cuando termines la demostración, detén el servicio con
    `docker compose down`.
