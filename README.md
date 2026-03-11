# AIM Dashboard

**Herramienta de clasificación de perfil de ciberseguridad para PyMEs** basada en la
Tríada AIM (Awareness, Infrastructure, Management).

---

## Cómo verlo en localhost

### Opción A — Python directo (más rápido para probar)

**1. Descomprime el proyecto y entra a la carpeta**
```bash
cd aim_dashboard
```

**2. Crea un entorno virtual**
```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

**3. Instala las dependencias**
```bash
pip install -r requirements.txt
```
La primera vez tarda varios minutos porque descarga modelos de ~1.5 GB (PyTorch, BART, DeBERTa, MPNet).

**4. Verifica que el modelo esté en la carpeta raíz**
```
aim_dashboard/
├── app.py
├── Modelo_Pymes.pkl   ← debe estar aquí
└── ...
```

**5. Ejecuta**
```bash
python app.py
```

**6. Abre en el navegador:**
```
http://localhost:8050
```

---

### Opción B — Docker (recomendado para producción)

Requisitos: Docker Desktop instalado.

```bash
cd aim_dashboard
docker-compose up --build
```
La primera vez tarda ~5-10 minutos. Luego abre `http://localhost:8050`.

Para detener: `docker-compose down`

---

### Opción C — Gunicorn (producción sin Docker)

```bash
pip install gunicorn
gunicorn --workers 2 --timeout 300 --bind 0.0.0.0:8050 app:server
```

---

## Estructura del proyecto

```
aim_dashboard/
│
├── app.py                   <- Punto de entrada principal
├── Dockerfile               <- Imagen Docker
├── docker-compose.yml       <- Orquestación
├── requirements.txt
├── Modelo_Pymes.pkl         <- Modelo K-Means (NO subir a repositorios públicos)
│
├── assets/
│   └── style.css            <- Estilos (Dash los carga automáticamente)
│
├── data/
│   └── definitions.py       <- Constantes y textos estáticos
│
├── layouts/
│   └── pages.py             <- Pantallas de home y perfiles
│
├── callbacks/
│   └── navegacion.py        <- Análisis en background, barra de progreso, routing
│
└── logic/
    ├── extractor.py         <- Scraping y clasificación semántica
    ├── modelo.py            <- Vectorización NLP + predicción K-Means
    └── venn.py              <- Diagrama de Venn
```

---

## Flujo de la aplicación

```
URL ingresada
    -> ExtractorMVD: scraping de páginas relevantes           (Paso 1)
    -> clasificar_inteligente: clasifica en MISION/VISION/DESCRIPCION
    -> traducción ES->EN                                       (Paso 2)
    -> vectorización NLP: MPNet + DeBERTa + BART zero-shot    (Paso 3)
    -> KMeans.predict: cluster 0-4 -> Perfil 1-5
    -> Layout del perfil con fortalezas, debilidades y Venn
```

---

## Problemas comunes

| Problema | Solución |
|---|---|
| `FileNotFoundError: Modelo_Pymes.pkl` | Pon el `.pkl` junto a `app.py` |
| La app tarda en arrancar | Normal: los modelos NLP se cargan al primer análisis |
| Error de red al analizar sitio | Verifica que la URL incluya `https://` |
| `Port 8050 already in use` | Cambia el puerto en `app.py` o mata el proceso: `lsof -ti:8050 \| xargs kill` |
| Docker con poca memoria | Asigna al menos 4 GB de RAM en Docker Desktop > Settings > Resources |

---

## Notas para producción

- El análisis NLP corre en un **thread separado** para no bloquear la UI. Con múltiples
  usuarios simultáneos considera usar **Celery + Redis** para una cola de trabajos.
- Los modelos de HuggingFace se cachean en `~/.cache/huggingface/`. En Docker se
  descargan al construir la imagen.
- Para exponer con dominio real, descomenta el servicio `nginx` en `docker-compose.yml`
  y configura tu dominio.
