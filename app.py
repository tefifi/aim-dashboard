"""
AIM Dashboard — Punto de entrada principal.
Ejecutar con: python app.py
"""

import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
import logging
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html


from layouts.pages import layout_home, all_layouts
from callbacks.navegacion import registrar_callbacks

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "AIM Dashboard"

# ── Panel de progreso en el layout raíz ──────────────────────────────────────
# Debe estar aquí (no en page-content) para que los callbacks siempre
# puedan escribir en él sin importar qué página está cargada.
# Se muestra como barra fija en la parte inferior de la pantalla.
panel_progreso = html.Div(
    id="panel-progreso",
    style={"display": "none"},
    children=[
        html.Div(
            style={
                "position": "fixed",
                "bottom": "0", "left": "0", "right": "0",
                "zIndex": "1000",
                "background": "#ffffff",
                "borderTop": "3px solid #1c3160",
                "boxShadow": "0 -4px 24px rgba(28,49,96,0.15)",
                "padding": "18px 36px 20px",
            },
            children=[
                html.Div(
                    style={"maxWidth": "860px", "margin": "0 auto"},
                    children=[
                        html.Div(
                            style={"display": "flex", "alignItems": "center",
                                   "justifyContent": "space-between", "marginBottom": "10px"},
                            children=[
                                html.Span("Analizando perfil AIM", style={
                                    "fontSize": "0.78rem", "fontWeight": "700",
                                    "letterSpacing": "1.2px", "textTransform": "uppercase",
                                    "color": "#1c3160",
                                }),
                                html.Span(id="progreso-pct", style={
                                    "fontSize": "1rem", "fontWeight": "700",
                                    "color": "#b87a2a",
                                }),
                            ],
                        ),
                        html.Div(
                            style={
                                "background": "#e8ecf2",
                                "borderRadius": "999px",
                                "height": "14px",
                                "marginBottom": "14px",
                                "overflow": "hidden",
                                "border": "2px solid #b0bacb",
                                "boxShadow": "inset 0 1px 3px rgba(0,0,0,0.1)",
                            },
                            children=[
                                html.Div(
                                    id="progreso-bar",
                                    style={
                                        "height": "100%", "borderRadius": "999px",
                                        "background": "linear-gradient(90deg, #b87a2a, #d4a843)",
                                        "width": "0%",
                                        "transition": "width 0.8s ease",
                                        "boxShadow": "0 1px 4px rgba(184,122,42,0.4)",
                                    },
                                )
                            ],
                        ),
                        html.Div(id="progreso-container"),
                        html.Div(id="error-msg", children=""),
                    ],
                )
            ],
        )
    ],
)

# ── Layout raíz ───────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    dcc.Store(id="store_name", storage_type="session"),
    dcc.Store(id="store_link", storage_type="session"),
    dcc.Interval(id="interval_progress", interval=600, n_intervals=0, disabled=True),
    html.Div(id="page-content"),
    panel_progreso,
])

# ── Routing ───────────────────────────────────────────────────────────────────
@app.callback(
    dash.Output("page-content", "children"),
    dash.Input("url", "pathname"),
)
def mostrar_pagina(pathname: str):
    rutas = {
        "/profile_1": all_layouts[0],
        "/profile_2": all_layouts[1],
        "/profile_3": all_layouts[2],
        "/profile_4": all_layouts[3],
        "/profile_5": all_layouts[4],
    }
    return rutas.get(pathname, layout_home)

registrar_callbacks(app)

server = app.server  # para Gunicorn: gunicorn app:server

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)