# NexaKnowledge · Prototipo de gestión del conocimiento

**🔗 Prototipo en línea:** https://nexaknowledge.streamlit.app

**Organización ficticia:** NexaSoft Solutions (desarrollo de software, DevOps, infraestructura, seguridad, analítica y soporte).

Un sistema demostrativo con dos funciones reales en Python:

1. **Clasificación automática supervisada:** vectores TF-IDF del contenido + regresión logística para elegir entre seis tipos documentales.
2. **Búsqueda de información:** representa consulta y documentos como vectores TF-IDF; compara usando similitud del coseno y ordena los resultados. Incluye expansión opcional de sinónimos definidos explícitamente en la ontología.

**Aviso metodológico:** TF-IDF no es un modelo neuronal de embeddings. Por tanto, se trata de recuperación **semántica básica asistida por conceptos**, con limitaciones ante sinónimos no registrados y paráfrasis complejas. Los documentos y las métricas son sintéticos; no se validó el sistema con datos reales.

## Requisitos

Python 3.10 o posterior. Recomendado: entorno virtual.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# En macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Interfaz web

```bash
streamlit run app.py
```

Se abrirá un enlace local (habitualmente `http://localhost:8501`). Las pestañas permiten buscar, clasificar un texto nuevo, añadirlo temporalmente al catálogo, examinar los documentos y visualizar los mapas conceptuales.

**Importante:** los documentos agregados por el usuario solo permanecen en la sesión actual; no se modifican los 60 documentos de demostración.

## Ejecución sin interfaz (CLI)

```bash
python motor.py --consulta "¿Cómo restaurar archivos después de una falla?" --top 5
python motor.py --consulta "control de accesos" --tipo Política
python motor.py --clasificar "Esta política establece obligaciones, responsables y controles de cumplimiento."
python motor.py --evaluar
python motor.py --estadisticas
```

## Pruebas

```bash
python -m pytest -q
```

## Archivos principales

| Ruta | Función |
|---|---|
| `app.py` | Interfaz de demostración con Streamlit |
| `motor.py` | Motor de clasificación, vectorización, similitud y carga de datos |
| `datos/documentos.json` | 60 documentos sintéticos, seis clases (10 por clase) |
| `datos/ontologia.json` | Conceptos, clases, relaciones y términos equivalentes |
| `generar_datos.py` | Recrea el mismo corpus inicial de forma reproducible |
| `recursos/*.png` | Mapas conceptuales y arquitectura |
| `documentacion/Informe_NexaKnowledge.docx` | Informe académico detallado |
| `tests/test_motor.py` | Pruebas de integridad, búsqueda, clasificación y expansión |

## Ejemplos

- Consulta: `Cómo recuperar archivos después de una falla de servidor` → documentos sobre respaldo y recuperación.
- Consulta: `Requisitos para proteger datos personales` → documentos sobre privacidad y seguridad.
- Nuevo texto: `Este procedimiento establece pasos y evidencias para atender tickets e incidentes` → propone una categoría documental.

## Modelo e inferencia

Para cada documento se construye un texto indexado de título, contenido, área y conceptos. `TfidfVectorizer(ngram_range=(1,2))` genera la matriz dispersa de términos. La consulta se transforma usando **el mismo** vectorizador ya ajustado, se compara con `cosine_similarity` y se muestra exclusivamente un puntaje mayor que cero. Las categorías se predicen con otro vectorizador entrenado únicamente con los **contenidos** del corpus etiquetado, seguido de `LogisticRegression`. La clasificación y la búsqueda usan modelos separados.

La ampliación de consulta se basa en equivalencias autorizadas de `ontologia.json`. Es opcional y transparente; no se presenta como comprensión semántica profunda.

La puntuación del coseno indica parecido vectorial, **no** una probabilidad de acierto. La probabilidad de clasificación proviene de `predict_proba`, pero sin calibración en datos reales.

## Evaluación y límites

El clasificador se evalúa con validación cruzada estratificada de cinco pliegues. El corpus se generó con plantillas por tipo documental, por lo que puntajes altos reflejan la facilidad del conjunto de prueba y **no acreditan precisión en documentos reales**. Próximos pasos: corpus real anonimizado, etiquetado humano, prueba externa, métricas macro-F1 y Recall@k, control de permisos, OCR y gestión de versiones documentales.

**No se almacenan archivos confidenciales** ni se envía contenido a servicios externos. El procesamiento es local.

## Despliegue en Streamlit Cloud

El repositorio ya viene listo para publicarse. Configuración usada:

| Campo | Valor |
|---|---|
| Main file path | `app.py` |
| Python version | 3.13 |
| Dependencias | `requirements.txt` (versiones fijas) |

Las versiones de `requirements.txt` están fijadas a las que se usaron para medir Precision@K y Recall@K, de modo que el prototipo publicado reproduce exactamente las cifras del informe.

El archivo `.streamlit/config.toml` define el tema y desactiva la telemetría. No se necesita `packages.txt`: `generar_diagramas.py` requiere el binario de Graphviz, pero ese script no se ejecuta en la aplicación web, solo en local para regenerar las figuras.
