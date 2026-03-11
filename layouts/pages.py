"""
Módulo de layouts del dashboard AIM.
"""

from dash import dcc, html

from data.definitions import (
    DEFINICION_TRIADA_AIM,
    DEFINICIONES_PERFILES,
    DOMINIOS_DEFINICIONES,
    CONSEJOS_PERFILES_NEGATIVOS,
    CONSEJOS_PERFILES_POSITIVO,
    FORTALEZAS_PERFIL,
)
from logic.venn import VENN_IMG_COMPLETO, generar_venn_base



# ---------- Pantalla de inicio ------------------------------------------------

def crear_layout_home() -> html.Div:
    return html.Div(
        className="aim-container",
        children=[
            html.Div(className="aim-header", children=[
                html.H1("Tríada AIM"),
                html.P("Perfil de ciberseguridad para PyMEs", className="subtitle"),
            ]),

            html.Div(className="aim-two-col", children=[

                # ---- Columna izquierda ----
                html.Div(className="col-left", children=[
                    html.Div(className="aim-card", children=[
                        html.Div("Ingrese sus datos", className="aim-card-label"),
                        html.Label("Nombre de la organización",
                                   style={"fontWeight": "600", "marginBottom": "4px"}),
                        dcc.Input(
                            id="Nombre_org", type="text",
                            placeholder="Ej: Mi Empresa S.A.",
                            className="aim-input",
                        ),
                        html.Label("Sitio web de la organización",
                                   style={"fontWeight": "600", "marginBottom": "4px"}),
                        dcc.Input(
                            id="Link_org", type="text",
                            placeholder="https://www.miempresa.cl",
                            className="aim-input",
                        ),
                        html.Button(
                            "Analizar perfil →",
                            id={"type": "btn", "index": 0},
                            n_clicks=0,
                            className="aim-btn-primary",
                        ),
                    ]),

                    # Descripción tríada
                    html.Div(className="aim-card", children=[
                        html.Div("¿Qué es la Tríada AIM?", className="aim-card-label"),
                        dcc.Markdown(DEFINICION_TRIADA_AIM, className="aim-definition"),
                    ]),
                ]),

                # ---- Columna derecha ----
                html.Div(className="col-right", children=[
                    html.Div(className="aim-card", children=[
                        html.Div("Modelo de referencia", className="aim-card-label"),
                        html.Img(src=VENN_IMG_COMPLETO, className="venn-img"),
                    ]),
                ]),
            ]),
        ],
    )


# ---------- Pantalla de perfil ------------------------------------------------

def _tarjeta_dominio(nombre: str, tipo: str) -> html.Div:
    """Tarjeta acordeón con descripción completa al expandir."""
    is_strength = tipo == "strength"
    color       = "var(--success)"    if is_strength else "var(--danger)"
    bg_color    = "var(--success-bg)" if is_strength else "var(--danger-bg)"
    border_col  = "var(--success-border)" if is_strength else "var(--danger-border)"
    icono       = "✦" if is_strength else "◈"
    desc        = DOMINIOS_DEFINICIONES.get(nombre, "")

    return html.Details(
        style={
            "background": bg_color,
            "border": f"1.5px solid {border_col}",
            "borderRadius": "8px",
            "marginBottom": "10px",
            "overflow": "hidden",
        },
        children=[
            html.Summary(
                style={
                    "padding": "14px 18px",
                    "cursor": "pointer",
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "fontWeight": "700",
                    "fontSize": "1rem",
                    "color": color,
                    "listStyle": "none",
                    "userSelect": "none",
                },
                children=[
                    html.Span(icono, style={"fontSize": "0.9rem", "flexShrink": "0"}),
                    html.Span(nombre, style={"flex": "1"}),
                    html.Span("▾  ver más", style={
                        "fontSize": "0.78rem",
                        "color": "var(--text-muted)",
                        "fontWeight": "500",
                        "whiteSpace": "nowrap",
                    }),
                ],
            ),
            html.Div(
                style={
                    "padding": "12px 18px 16px",
                    "borderTop": f"1.5px solid {border_col}",
                    "background": "#ffffff",
                },
                children=[
                    html.P(
                        desc,
                        style={
                            "margin": "0",
                            "fontSize": "0.98rem",
                            "color": "var(--text-secondary)",
                            "lineHeight": "1.75",
                        },
                    )
                ],
            ),
        ],
    )


def _columna_dominios(titulo: str, icono: str, color: str,
                      dominios: list, tipo: str) -> html.Div:
    return html.Div([
        html.Div(
            className="aim-domain-col-header",
            style={"color": color, "borderBottomColor": color, "fontSize": "0.82rem"},
            children=[
                html.Span(icono, style={"fontSize": "1rem"}),
                html.Span(titulo),
            ],
        ),
        *[_tarjeta_dominio(d, tipo) for d in dominios],
    ])


def crear_layout_perfil(i: int) -> html.Div:
    idx         = i - 1
    venn_img    = f"data:image/png;base64,{generar_venn_base('Reporte', FORTALEZAS_PERFIL[idx])}"
    fortalezas  = CONSEJOS_PERFILES_POSITIVO[idx]
    debilidades = CONSEJOS_PERFILES_NEGATIVOS[idx]

    return html.Div(
        className="aim-container",
        children=[
            # Botón volver
            html.Div(className="aim-nav-home", children=[
                html.Button(
                    "← Inicio",
                    id={"type": "btn", "index": i},
                    n_clicks=0,
                    className="aim-btn-secondary",
                    style={"width": "auto", "padding": "8px 18px"},
                )
            ]),

            # Header
            html.Div(className="aim-header", children=[
                html.H1(f"Perfil {i}"),
                html.P("Resultado del análisis de ciberseguridad AIM", className="subtitle"),
            ]),

            # Descripción del perfil (ancho completo)
            html.Div(className="aim-card", style={"marginBottom": "20px"}, children=[
                html.Div(f"Perfil {i} — Descripción", className="aim-card-label"),
                dcc.Markdown(DEFINICIONES_PERFILES[idx], className="aim-definition"),
            ]),

            # Grid: fortalezas | debilidades | Venn (Venn más ancho)
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr 1.4fr",
                    "gap": "20px",
                    "alignItems": "start",
                },
                children=[
                    # Fortalezas
                    html.Div(className="aim-card", children=[
                        _columna_dominios(
                            "Fortalezas identificadas", "✦", "#34d399",
                            fortalezas, "strength",
                        ),
                    ]),
                    # Áreas de mejora
                    html.Div(className="aim-card", children=[
                        _columna_dominios(
                            "Áreas de mejora", "◈", "#f87171",
                            debilidades, "weakness",
                        ),
                    ]),
                    # Diagrama Venn con zoom modal
                    html.Div(className="aim-card", style={"textAlign": "center"}, children=[
                        html.Div("Cobertura AIM", className="aim-card-label"),
                        # Imagen clickeable
                        html.Div(
                            style={"position": "relative", "cursor": "zoom-in"},
                            children=[
                                html.Img(
                                    src=venn_img,
                                    className="venn-img venn-clickable",
                                    id={"type": "venn-thumb", "index": i},
                                    n_clicks=0,
                                ),
                                html.Div(
                                    "🔍 Clic para ampliar",
                                    style={
                                        "position": "absolute", "bottom": "10px",
                                        "right": "10px", "background": "rgba(28,49,96,0.75)",
                                        "color": "#fff", "fontSize": "0.75rem",
                                        "padding": "4px 10px", "borderRadius": "999px",
                                        "fontWeight": "600", "pointerEvents": "none",
                                    }
                                ),
                            ],
                        ),
                        html.P(
                            "✔ Dominios cubiertos   ✗ Por desarrollar",
                            style={"color": "var(--text-muted)", "fontSize": "0.92rem",
                                   "marginTop": "12px", "fontWeight": "500"},
                        ),
                        # Modal overlay
                        html.Div(
                            id={"type": "venn-modal", "index": i},
                            style={"display": "none"},
                            className="venn-modal-overlay",
                            children=[
                                html.Div(className="venn-modal-box", children=[
                                    html.Button(
                                        "✕ Cerrar",
                                        id={"type": "venn-close", "index": i},
                                        className="venn-modal-close",
                                        n_clicks=0,
                                    ),
                                    html.Img(src=venn_img, className="venn-modal-img"),
                                ]),
                            ],
                        ),
                    ]),
                ],
            ),
        ],
    )


layout_home = crear_layout_home()
all_layouts = [crear_layout_perfil(i) for i in range(1, 6)]