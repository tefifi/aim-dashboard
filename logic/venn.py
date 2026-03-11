"""
Módulo de generación del diagrama de Venn para la Tríada AIM.
Genera imágenes base64 a partir de matplotlib + matplotlib_venn.
"""

import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

from data.definitions import (
    COLORES_BASE,
    VENN_SECTIONS,
    VENN_ID_TO_SUBCATEGORIA,
)

VENN_IDS = ["100", "010", "001", "110", "101", "011", "111"]


def generar_venn_base(foco=None, seleccionados_usuario=None) -> str:
    """
    Genera el diagrama de Venn y retorna la imagen codificada en base64.

    Args:
        foco: Modo de visualización. Opciones:
              "Reporte"  → muestra fortalezas/debilidades por perfil.
              "Completo" → muestra todos los dominios con color.
              "Simple"   → solo color, sin texto.
              str        → destaca únicamente la zona con ese nombre (Core, Bridge, ...).
        seleccionados_usuario: Lista de dominios activos (solo relevante en modo "Reporte").

    Returns:
        String base64 PNG de la imagen generada.
    """
    if seleccionados_usuario is None:
        seleccionados_usuario = []

    plt.figure(figsize=(11, 11))
    venn = venn3(
        subsets=(3, 2, 3, 1, 1, 1, 3),
        set_labels=("Concientizacion", "Infraestructura", "Gestion"),
    )

    # Limpiar etiquetas por defecto
    for vid in VENN_IDS:
        label = venn.get_label_by_id(vid)
        if label:
            label.set_text("")

    for vid in VENN_IDS:
        patch = venn.get_patch_by_id(vid)
        if not patch:
            continue

        section_name = VENN_SECTIONS[vid]
        dominios_zona = VENN_ID_TO_SUBCATEGORIA[vid]

        if foco == "Reporte":
            hay_seleccion = any(d in seleccionados_usuario for d in dominios_zona)
            color = COLORES_BASE[section_name] if hay_seleccion else COLORES_BASE["Desactivado"]
            alpha = 0.8 if hay_seleccion else 0.3

            texto_etiqueta = [
                f"✔ {d}" if d in seleccionados_usuario else f"✗ {d}"
                for d in dominios_zona
            ]
            label = venn.get_label_by_id(vid)
            if label:
                label.set_text("\n".join(texto_etiqueta))
                label.set_fontsize(8)

        elif foco == "Completo":
            color = COLORES_BASE[section_name]
            alpha = 0.8
            label = venn.get_label_by_id(vid)
            if label:
                label.set_text("\n".join(dominios_zona))

        elif foco == "Simple":
            color = COLORES_BASE[section_name]
            alpha = 0.8

        else:
            # Foco específico: destaca solo la zona indicada
            es_foco = section_name == foco
            color = COLORES_BASE[section_name] if es_foco else COLORES_BASE["Desactivado"]
            alpha = 0.9 if es_foco else 0.3
            if es_foco:
                label = venn.get_label_by_id(vid)
                if label:
                    label.set_text("\n".join(dominios_zona))

        patch.set_facecolor(color)
        patch.set_edgecolor("black")
        patch.set_linewidth(1.5)
        patch.set_alpha(alpha)

    if foco == "Reporte":
        titulo = "Tríada AIM — Perfil de cobertura"
    elif foco in ("Completo", "Simple"):
        titulo = "Tríada AIM"
    else:
        titulo = f"Zona: {foco.upper()}" if foco else "Tríada AIM"

    plt.title(titulo, fontsize=13, fontweight="bold")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# Pre-renderizado del Venn completo para la pantalla de inicio (se genera una sola vez)
VENN_IMG_COMPLETO = f"data:image/png;base64,{generar_venn_base('Completo')}"
