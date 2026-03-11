"""
Callbacks del dashboard AIM.
- error-msg, progreso-container, progreso-bar, progreso-pct viven en pages.py
  dentro del panel inline bajo el botón.
- El panel se muestra/oculta via Output("panel-progreso", "style").
"""

import logging
import threading
import time

import dash
from dash import ctx, html
from dash.dependencies import Input, Output, State, ALL

from logic.extractor import ExtractorMVD
from logic.modelo import obtener_perfil

logger = logging.getLogger(__name__)

# ── Estado compartido ─────────────────────────────────────────────────────────
_estado: dict = {"paso": 0, "pct": 0, "perfil": None, "error": None}
_lock = threading.Lock()

# Porcentaje base al inicio de cada paso
_PCT_BASE  = {1: 0,  2: 30, 3: 50, 4: 100}
# Porcentaje máximo al que puede llegar solo con el timer (sin avanzar de paso)
_PCT_TECHO = {1: 28, 2: 48, 3: 95,  4: 100}

PASOS_LABELS  = ["Extrayendo", "Procesando", "Clasificando", "Listo"]
PASOS_DETALLE = [
    "Extrayendo contenido del sitio web...",
    "Traduciendo y procesando texto...",
    "Clasificando perfil con el modelo NLP...",
    "¡Análisis completado!",
]

_PANEL_VISIBLE = {"display": "block"}
_PANEL_OCULTO  = {"display": "none"}


# ── Thread principal de análisis ──────────────────────────────────────────────

def _correr_analisis(link: str, nombre: str) -> None:
    global _estado
    try:
        # Paso 1 — Extracción web
        with _lock:
            _estado = {"paso": 1, "pct": 0, "perfil": None, "error": None}

        extractor = ExtractorMVD(url=link, nombre=nombre)
        extractor.navegar_y_extraer()
        texto = extractor.clasificar_inteligente()

        if not texto:
            with _lock:
                _estado["error"] = {
                    "tipo": "extraccion",
                    "titulo": "No se encontró contenido relevante",
                    "detalle": (
                        "El sitio web no contiene texto relacionado con misión, visión "
                        "o descripción organizacional que el modelo pueda analizar."
                    ),
                    "sugerencia": "Prueba con la URL de la página 'Quiénes somos' o 'Acerca de' de la empresa.",
                }
                _estado["paso"] = -1
            return

        # Paso 2 — Traducción
        with _lock:
            _estado["paso"] = 2
            _estado["pct"]  = _PCT_BASE[2]

        # Paso 3 — Clasificación NLP + K-Means
        with _lock:
            _estado["paso"] = 3
            _estado["pct"]  = _PCT_BASE[3]

        perfil = obtener_perfil(texto) + 1  # 0-4 → 1-5

        # Paso 4 — Listo
        with _lock:
            _estado["paso"] = 4
            _estado["pct"]  = 100
            _estado["perfil"] = perfil

        logger.info("Perfil: %d | '%s'", perfil, link)

    except FileNotFoundError as e:
        logger.error("Modelo no encontrado: %s", e)
        with _lock:
            _estado["error"] = {
                "tipo": "modelo",
                "titulo": "Modelo no encontrado",
                "detalle": "El archivo Modelo_Pymes.pkl no está en la carpeta del proyecto.",
                "sugerencia": "Verifica que Modelo_Pymes.pkl esté en la carpeta raíz junto a app.py.",
            }
            _estado["paso"]  = -1
    except Exception as e:
        logger.exception("Error procesando '%s'", link)
        err_str = str(e)
        # Clasificar el error según su contenido
        if "connection" in err_str.lower() or "timeout" in err_str.lower() or "urlopen" in err_str.lower():
            tipo    = "red"
            titulo  = "Error de conexión"
            detalle = f"No se pudo conectar al sitio: {err_str}"
            sugiere = "Verifica que la URL sea correcta y que el sitio esté accesible desde tu red."
        elif "ssl" in err_str.lower() or "certificate" in err_str.lower():
            tipo    = "ssl"
            titulo  = "Error de certificado SSL"
            detalle = "El sitio tiene un certificado de seguridad inválido o expirado."
            sugiere = "Intenta con la versión http:// en lugar de https://, o prueba con otro sitio."
        elif "403" in err_str or "401" in err_str or "forbidden" in err_str.lower():
            tipo    = "acceso"
            titulo  = "Acceso denegado por el sitio"
            detalle = "El servidor rechazó la solicitud (error 403/401)."
            sugiere = "Este sitio bloquea el acceso automatizado. Prueba con otro sitio o con la URL de una subpágina."
        elif "404" in err_str or "not found" in err_str.lower():
            tipo    = "url"
            titulo  = "Página no encontrada"
            detalle = f"La URL ingresada no existe o fue movida: {err_str}"
            sugiere = "Verifica que la URL sea correcta e incluya https://"
        elif "runtime" in err_str.lower() or "tensor" in err_str.lower():
            tipo    = "modelo"
            titulo  = "Error en el modelo NLP"
            detalle = "Ocurrió un error interno al procesar el texto con los modelos de lenguaje."
            sugiere = "Intenta de nuevo. Si el error persiste, el texto extraído puede ser demasiado corto o inusual."
        else:
            tipo    = "desconocido"
            titulo  = "Error inesperado"
            detalle = err_str
            sugiere = "Intenta de nuevo o prueba con un sitio web diferente."

        with _lock:
            _estado["error"] = {
                "tipo": tipo, "titulo": titulo,
                "detalle": detalle, "sugerencia": sugiere,
            }
            _estado["paso"]  = -1


# ── Thread de animación de porcentaje ─────────────────────────────────────────

def _animar_porcentaje() -> None:
    """Incrementa el % gradualmente dentro del techo de cada paso."""
    global _estado
    while True:
        time.sleep(0.8)
        with _lock:
            paso = _estado["paso"]
            if paso <= 0 or paso == 4:
                break
            techo = _PCT_TECHO.get(paso, 95)
            pct   = _estado["pct"]
            if pct < techo:
                # Avance más rápido al principio, más lento cerca del techo
                incremento = max(1, int((techo - pct) * 0.07))
                _estado["pct"] = min(pct + incremento, techo)


# ── Componente visual de pasos ────────────────────────────────────────────────

def _pasos_html(paso: int) -> html.Div:
    items = []
    for i, label in enumerate(PASOS_LABELS, start=1):
        if paso == -1:
            estado = "error" if i == 1 else "pendiente"
        elif i < paso:
            estado = "completado"
        elif i == paso:
            estado = "activo"
        else:
            estado = "pendiente"

        color = {
            "completado": "#1e6b45",   # verde bosque
            "activo":     "#1c3160",   # azul marino
            "pendiente":  "#6b7a96",   # gris medio visible en claro
            "error":      "#8b1c1c",   # rojo ladrillo
        }[estado]
        icono = "✔" if estado == "completado" else ("✖" if estado == "error" else str(i))

        items.append(html.Div(
            style={"display": "flex", "flexDirection": "column",
                   "alignItems": "center", "gap": "5px", "flex": "1"},
            children=[
                html.Div(icono, style={
                    "width": "32px", "height": "32px", "borderRadius": "50%",
                    "border": f"2px solid {color}", "color": color,
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "fontWeight": "700", "fontSize": "0.8rem",
                    "background": "rgba(28,49,96,0.1)" if estado == "activo" else "transparent",
                    "boxShadow": "0 0 0 4px rgba(28,49,96,0.12)" if estado == "activo" else "none",
                }),
                html.Span(label, style={
                    "fontSize": "0.68rem", "color": color, "fontWeight": "600",
                }),
            ],
        ))
        if i < len(PASOS_LABELS):
            items.append(html.Div(style={
                "flex": "2", "height": "2px", "marginTop": "-17px",
                "background": "#1e6b45" if i < paso else "#b0bacb",
                "transition": "background 0.5s",
            }))

    desc_color = "#f87171" if paso == -1 else "#8892a4"
    desc = ("⚠ Error durante el análisis" if paso == -1
            else PASOS_DETALLE[paso - 1] if 1 <= paso <= 4
            else "Iniciando...")

    return html.Div([
        html.Div(items, style={
            "display": "flex", "alignItems": "center",
            "padding": "4px 0 10px", "gap": "2px",
        }),
        html.P(desc, style={
            "color": desc_color, "fontSize": "0.75rem",
            "margin": "0", "textAlign": "center",
        }),
    ])


# ── Registro de callbacks ─────────────────────────────────────────────────────

def registrar_callbacks(app: dash.Dash) -> None:

    # 1. Botón Analizar → lanza threads, muestra panel
    @app.callback(
        Output("interval_progress", "disabled"),
        Output("panel-progreso", "style"),
        Output("error-msg", "children"),
        Input({"type": "btn", "index": ALL}, "n_clicks"),
        State("store_name", "data"),
        State("store_link", "data"),
        prevent_initial_call=True,
    )
    def iniciar_analisis(n_clicks, nombre, link):
        global _estado
        if not ctx.triggered_id or not ctx.triggered[0]["value"]:
            return dash.no_update, dash.no_update, ""
        tid = ctx.triggered_id
        if not (isinstance(tid, dict) and tid.get("type") == "btn"):
            return dash.no_update, dash.no_update, ""
        if tid.get("index") != 0:
            return True, _PANEL_OCULTO, ""
        if not link:
            return True, _PANEL_VISIBLE, html.Div(
                "⚠ Por favor ingresa el link del sitio web.",
                style={"color": "#f87171", "fontSize": "0.82rem", "marginTop": "8px"},
            )
        with _lock:
            _estado = {"paso": 0, "pct": 0, "perfil": None, "error": None}

        threading.Thread(target=_correr_analisis,
                         args=(link, nombre or "Organización"), daemon=True).start()
        threading.Thread(target=_animar_porcentaje, daemon=True).start()

        return False, _PANEL_VISIBLE, ""

    # 2. Botones volver al inicio
    @app.callback(
        Output("url", "pathname"),
        Input({"type": "btn", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def volver_inicio(n_clicks):
        if not ctx.triggered_id or not ctx.triggered[0]["value"]:
            return dash.no_update
        tid = ctx.triggered_id
        if isinstance(tid, dict) and tid.get("type") == "btn" and tid.get("index") != 0:
            return "/"
        return dash.no_update

    # 3. Polling → actualiza barra %, pasos, y redirige al terminar
    @app.callback(
        Output("progreso-container", "children"),
        Output("progreso-bar", "style"),
        Output("progreso-pct", "children"),
        Output("url", "pathname", allow_duplicate=True),
        Output("interval_progress", "disabled", allow_duplicate=True),
        Output("panel-progreso", "style", allow_duplicate=True),
        Input("interval_progress", "n_intervals"),
        prevent_initial_call=True,
    )
    def actualizar_progreso(n):
        with _lock:
            e = dict(_estado)

        paso = e["paso"]
        pct  = e.get("pct", 0)

        bar_style = {
            "height": "100%", "borderRadius": "999px",
            "background": "linear-gradient(90deg, #b87a2a, #d4a843)",
            "width": f"{pct}%",
            "transition": "width 0.8s ease",
        }
        pct_txt = f"{pct}%"

        # Error — mostrar panel descriptivo
        if paso == -1:
            err = e.get("error", {})
            if isinstance(err, dict):
                titulo   = err.get("titulo",   "Error durante el análisis")
                detalle  = err.get("detalle",  "Ocurrió un problema inesperado.")
                sugiere  = err.get("sugerencia", "")
                tipo     = err.get("tipo", "desconocido")
            else:
                titulo, detalle, sugiere, tipo = str(err), "", "", "desconocido"

            iconos = {
                "red": "🌐", "ssl": "🔒", "acceso": "🚫",
                "url": "🔗", "modelo": "🤖", "extraccion": "📄",
                "desconocido": "⚠",
            }
            icono = iconos.get(tipo, "⚠")

            panel_error = html.Div(
                style={
                    "marginTop": "12px",
                    "background": "#fdeaea",
                    "border": "1.5px solid #d48585",
                    "borderRadius": "8px",
                    "padding": "14px 16px",
                },
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center",
                               "gap": "8px", "marginBottom": "6px"},
                        children=[
                            html.Span(icono, style={"fontSize": "1.1rem"}),
                            html.Span(titulo, style={
                                "fontWeight": "700", "color": "#8b1c1c",
                                "fontSize": "0.95rem",
                            }),
                        ],
                    ),
                    html.P(detalle, style={
                        "color": "#6b2020", "fontSize": "0.9rem",
                        "margin": "0 0 6px", "lineHeight": "1.5",
                    }),
                    html.P(f"💡 {sugiere}", style={
                        "color": "#3d4a60", "fontSize": "0.88rem",
                        "margin": "0", "fontStyle": "italic",
                    }) if sugiere else None,
                    html.Button(
                        "Intentar de nuevo",
                        style={
                            "marginTop": "12px", "padding": "10px 20px",
                            "background": "#fff", "border": "2px solid #8b1c1c",
                            "borderRadius": "8px", "color": "#8b1c1c",
                            "cursor": "pointer", "fontSize": "0.95rem",
                            "fontWeight": "700", "fontFamily": "inherit",
                        },
                        id={"type": "btn", "index": 0},
                        n_clicks=0,
                    ),
                ],
            )
            return (
                html.Div([_pasos_html(-1), panel_error]),
                {**bar_style, "background": "#8b1c1c", "width": "100%", "boxShadow": "0 1px 4px rgba(139,28,28,0.4)"},
                "Error",
                dash.no_update, True, _PANEL_VISIBLE,
            )

        # Completado
        if paso == 4 and e["perfil"]:
            return (
                _pasos_html(4),
                {**bar_style, "width": "100%"},
                "100%",
                f"/profile_{e['perfil']}", True, _PANEL_OCULTO,
            )

        # En progreso
        return _pasos_html(paso), bar_style, pct_txt, dash.no_update, dash.no_update, dash.no_update

    # 4. Guardar datos en sesión
    @app.callback(
        Output("store_name", "data"),
        Output("store_link", "data"),
        Input("Nombre_org", "value"),
        Input("Link_org", "value"),
        prevent_initial_call=True,
    )
    def guardar_datos(nombre, link):
        return nombre, link

    # 5. Abrir modal Venn al hacer clic en la imagen
    @app.callback(
        Output({"type": "venn-modal", "index": ALL}, "style"),
        Input({"type": "venn-thumb", "index": ALL}, "n_clicks"),
        Input({"type": "venn-close", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_venn_modal(thumb_clicks, close_clicks):
        _ABIERTO = {"display": "flex"}
        _CERRADO = {"display": "none"}

        if not ctx.triggered_id:
            return [_CERRADO] * len(thumb_clicks)

        tid = ctx.triggered_id
        tipo = tid.get("type")
        idx  = tid.get("index")

        # Obtener cuántos perfiles hay
        n = len(thumb_clicks)
        result = [_CERRADO] * n

        if tipo == "venn-thumb":
            # Abrir el modal del perfil clicado (índice = número de perfil 1-5)
            for j in range(n):
                # Los índices son 1..5, la lista es 0..4
                if j + 1 == idx:
                    result[j] = _ABIERTO
        # Si es venn-close, todos quedan cerrados (result ya es todo _CERRADO)

        return result