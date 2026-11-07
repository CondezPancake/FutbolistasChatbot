# Tribuna Global IA

**Cada opinión juega su partido.**

Aplicación académica en Streamlit para registrar opiniones sobre futbolistas,
clasificarlas con Gemini mediante LangChain y consultarlas después de reiniciar
la aplicación.

## Estado actual

El repositorio contiene la estructura base, la configuración reproducible y los
datos ficticios requeridos. La interfaz conversacional y la clasificación se
implementarán en las siguientes actividades.

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
