"""
Módulo de clasificación mediante modelos de NLP y K-Means.
Contiene la lógica de vectorización semántica y predicción de perfil AIM.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import joblib
from sentence_transformers import SentenceTransformer, CrossEncoder, util
from transformers import pipeline
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Ruta del modelo K-Means (relativa al directorio de este archivo)
MODEL_PATH = Path(__file__).parent.parent / "Modelo_Pymes.pkl"

# Pesos del comité de expertos
W_BART   = 0.50
W_MPNET  = 0.30
W_NLI    = 0.20

# Umbrales de corte
SCORE_MINIMO  = 0.15
UMBRAL_CORTE  = 0.08
DOMINIOS_NUCLEO = ["Risk", "Policy and Strategy", "Knowledge and Capabilities"]

# Herencia AIM: qué pilares influyen a cada dominio
HERENCIA_AIM = {
    "Risk":                          ["AWARENESS", "INFRASTRUCTURE", "MANAGEMENT"],
    "Policy and Strategy":           ["AWARENESS", "INFRASTRUCTURE", "MANAGEMENT"],
    "Knowledge and Capabilities":    ["AWARENESS", "INFRASTRUCTURE", "MANAGEMENT"],
    "Incident Detection and Response": ["AWARENESS", "MANAGEMENT"],
    "Program":                       ["MANAGEMENT", "INFRASTRUCTURE"],
    "Standards and Technology":      ["AWARENESS", "INFRASTRUCTURE"],
    "Culture and Society":           ["AWARENESS"],
    "Situational Awareness":         ["AWARENESS"],
    "Architecture":                  ["INFRASTRUCTURE"],
    "Threat and Vulnerability":      ["INFRASTRUCTURE"],
    "Legal and regulatory Framework": ["MANAGEMENT"],
    "Workforce":                     ["MANAGEMENT"],
    "Asset, Change, and Configuration": ["MANAGEMENT"],
}

# ----------------------------------------------------------------------------------
# Definiciones de dominios y pilares (textos largos de referencia para embeddings)
# Extraídos del archivo original sin modificación de contenido.
# ----------------------------------------------------------------------------------

BASE_DOMINIOS_AMPLIADOS = {
    "Culture and Society": """
### DOMAIN: CULTURE AND SOCIETY
This domain encapsulates the collective set of values, beliefs, perceptions, and behavioral norms
that determine how an institution and its stakeholders approach the protection of information assets.
It functions as the organization's informal operating system, governing the unwritten rules of conduct
that dictate whether official security directives are internalized as a shared responsibility or viewed
as bureaucratic impediments. Unlike technical controls that enforce limitations, this dimension focuses
on the willingness of human actors to adhere to safe practices even in the absence of direct supervision.
""",
    "Situational Awareness": """
### DOMAIN: SITUATIONAL AWARENESS
This domain defines the organization's dynamic capacity to perceive, synthesize, and interpret the
status of its security environment in real-time. It bridges the semantic gap between technical anomalies
and business context, aggregating fragmented telemetry from disparate sources to construct a unified
Common Operating Picture. It answers: What is happening now? Who is the adversary? Which critical
functions are implicated?
""",
    "Standards and Technology": """
### DOMAIN: STANDARDS AND TECHNOLOGY
This domain constitutes the technical realization of cybersecurity: the rigorous selection, implementation,
and maintenance of the hardware, software, and configuration frameworks that enforce protection.
Standards refer to externally validated frameworks (NIST CSF, ISO 27001, CIS Benchmarks).
Technology refers to the specific operational tools deployed to execute those standards.
""",
    "Architecture": """
### DOMAIN: ARCHITECTURE
This domain defines the structural design, organization, and interconnection of an institution's digital
ecosystem. It translates abstract security principles such as defense-in-depth, least privilege, and
resilience into concrete, enforceable topologies. The fundamental objective is to limit the blast radius
of a potential compromise through network segmentation, Zero Trust models, and cloud landing zones.
""",
    "Threat and Vulnerability": """
### DOMAIN: THREAT AND VULNERABILITY
This domain encapsulates the organization's dynamic capability to proactively identify, evaluate, and
mitigate security weaknesses before they can be exploited. It governs the operational lifecycle of a flaw:
from detection (scanning/reporting) to assessment (scoring based on exploitability and asset criticality)
and finally to remediation or compensating controls.
""",
    "Program": """
### DOMAIN: PROGRAM
This domain refers to the strategic planning and execution of cybersecurity as a formal organizational
program. It ensures that security initiatives are funded, staffed, sequenced, and tracked as a coherent
portfolio of work aligned with business objectives and risk tolerance.
""",
    "Workforce": """
### DOMAIN: WORKFORCE
This domain encompasses the people dimension of cybersecurity: recruiting, retaining, and developing
security talent; defining roles and responsibilities; and ensuring that all staff have the skills and
authority required to execute their security functions effectively.
""",
    "Asset, Change and Configuration": """
### DOMAIN: ASSET, CHANGE AND CONFIGURATION
This domain refers to the governance and control of the organization's digital and physical assets,
including inventory management, configuration baselines, and change control processes that prevent
unauthorized or insecure modifications to the technology estate.
""",
    "Legal and Regulatory Framework": """
### DOMAIN: LEGAL AND REGULATORY FRAMEWORK
This domain refers to the laws, regulations, contractual obligations, and industry standards that govern
the organization's security posture. It ensures that the organization meets its compliance obligations
while translating external mandates into internal controls and policies.
""",
    "Incident Detection and Response": """
### DOMAIN: INCIDENT DETECTION AND RESPONSE
This domain refers to the organization's capability to detect, analyze, contain, eradicate, and recover
from security incidents in a timely and effective manner. It encompasses the people, processes, and
technology that form the incident lifecycle, from initial alert triage to post-incident review.
""",
    "Policy and Strategy": """
### DOMAIN: POLICY AND STRATEGY
This domain refers to the capacity of an organization to establish formal policies, standards, and a
coherent security strategy that aligns protection investments with business objectives and risk appetite.
It provides the governing framework within which all other security activities operate.
""",
    "Knowledge and Capabilities": """
### DOMAIN: KNOWLEDGE AND CAPABILITIES
This domain refers to the organization's institutional knowledge base and the specialized competencies
required to execute its security strategy. It encompasses threat intelligence, security research, and
the continuous development of skills that keep the organization ahead of the evolving threat landscape.
""",
    "Risk": """
### DOMAIN: RISK
This domain refers to the systematic process of identifying, assessing, prioritizing, and managing
threats to the organization's information assets. It provides the analytical framework for converting
technical vulnerabilities and threat intelligence into business impact language, enabling
defensible resource allocation decisions.
""",
}

BASE_PILARES = {
    "AWARENESS": """
### PILLAR: AWARENESS
Awareness constitutes the cognitive and behavioral layer of the organization's cybersecurity posture.
It represents the internalization of risk management into the daily heuristics of the workforce,
transforming the human element from a potential vulnerability into a sophisticated sensor network.
It includes security champions, phishing simulations, role-based training, and reporting mechanisms.
""",
    "INFRASTRUCTURE": """
### PILLAR: INFRASTRUCTURE
Infrastructure represents the tangible, operative reality of cybersecurity: the collection of hardware,
software, networks, and architectural mechanisms that materially enforce protection. It encompasses
network segmentation, endpoint detection, hardening baselines, encryption, and resilience testing.
It ensures that Defense in Depth is an operational fact rather than a theoretical concept.
""",
    "MANAGEMENT": """
### PILLAR: MANAGEMENT
Management constitutes the executive and strategic brain of the cybersecurity ecosystem. It encompasses
governance structures, risk registers, security budgets, policy frameworks, and executive accountability
mechanisms that ensure security is managed as a critical business function aligned with fiduciary duties.
""",
}


# ----------------------------------------------------------------------------------
# Funciones de traducción y vectorización
# ----------------------------------------------------------------------------------

def _traducir_texto_largo(texto: dict) -> str:
    """Traduce el diccionario de texto clasificado al inglés, en chunks si es necesario."""
    translator = GoogleTranslator(source="es", target="en")
    limite = 4_000
    partes_traducidas = []

    for llave, texto_original in texto.items():
        texto_original = str(texto_original)
        if len(texto_original) <= limite:
            try:
                partes_traducidas.append(translator.translate(texto_original))
            except Exception:
                partes_traducidas.append(texto_original)
        else:
            for i in range(0, len(texto_original), limite):
                chunk = texto_original[i : i + limite]
                try:
                    partes_traducidas.append(translator.translate(chunk))
                except Exception:
                    partes_traducidas.append(chunk)

    return " ".join(partes_traducidas).strip()


def _calcular_similitud(
    texto: str,
    nombres: list,
    definiciones: list,
    embeddings_ref,
    model_A,
    model_B,
    model_C,
) -> dict:
    """Calcula similitud fusionada usando MPNet + DeBERTa + BART."""

    # MPNet (semántico)
    emb_texto = model_A.encode(texto, convert_to_tensor=True)
    scores_A = util.cos_sim(emb_texto, embeddings_ref)[0].cpu().numpy()
    if scores_A.max() > scores_A.min():
        scores_A = (scores_A - scores_A.min()) / (scores_A.max() - scores_A.min())

    # DeBERTa (lógico / NLI)
    pares = [[texto, d] for d in definiciones]
    scores_B_logits = model_B.predict(pares)
    scores_B = np.max(scores_B_logits, axis=1) if len(scores_B_logits.shape) > 1 else scores_B_logits
    if scores_B.max() > scores_B.min():
        scores_B = (scores_B - scores_B.min()) / (scores_B.max() - scores_B.min())

    # BART (zero-shot contextual)
    res_C = model_C(texto, nombres, multi_label=True)
    mapa_C = dict(zip(res_C["labels"], res_C["scores"]))
    scores_C = np.array([mapa_C[n] for n in nombres])

    finales = (scores_C * W_BART) + (scores_A * W_MPNET) + (scores_B * W_NLI)

    return {
        nombre: {
            "final": finales[i],
            "bart":  scores_C[i],
            "mpnet": scores_A[i],
            "nli":   scores_B[i],
        }
        for i, nombre in enumerate(nombres)
    }


def _vectorizar(texto: dict) -> pd.DataFrame:
    """
    Vectoriza el texto clasificado y devuelve un DataFrame con scores por dominio.
    Carga los modelos NLP bajo demanda (solo cuando se llama).
    """
    device = 0 if torch.cuda.is_available() else -1

    logger.info("Cargando modelos NLP...")
    model_A = SentenceTransformer("all-mpnet-base-v2")
    model_B = CrossEncoder("cross-encoder/nli-deberta-v3-base")
    model_C = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device)

    nombres_dominios   = list(BASE_DOMINIOS_AMPLIADOS.keys())
    defs_dominios      = list(BASE_DOMINIOS_AMPLIADOS.values())
    emb_dominios       = model_A.encode(defs_dominios, convert_to_tensor=True)

    nombres_pilares    = list(BASE_PILARES.keys())
    defs_pilares       = list(BASE_PILARES.values())
    emb_pilares        = model_A.encode(defs_pilares, convert_to_tensor=True)

    texto_clean = _traducir_texto_largo(texto)

    scores_dominios = _calcular_similitud(
        texto_clean, nombres_dominios, defs_dominios, emb_dominios,
        model_A, model_B, model_C,
    )
    scores_pilares = _calcular_similitud(
        texto_clean, nombres_pilares, defs_pilares, emb_pilares,
        model_A, model_B, model_C,
    )
    scores_pilares_simple = {k: v["final"] for k, v in scores_pilares.items()}

    P_BASE     = 0.60
    P_HERENCIA = 0.40
    datos_tabla = []

    for dominio, detalle in scores_dominios.items():
        padres = HERENCIA_AIM.get(dominio, [])
        score_herencia = (
            sum(scores_pilares_simple[p] for p in padres) / len(padres)
            if padres else 0.0
        )
        bono = 0.10 if len(padres) == 3 else 0.0
        score_final = (detalle["final"] * P_BASE) + (score_herencia * P_HERENCIA) + bono

        datos_tabla.append({
            "Categoría": dominio,
            "Final":     score_final,
            "BART":      detalle["bart"],
            "MPNet":     detalle["mpnet"],
            "NLI":       detalle["nli"],
            "Base":      detalle["final"],
            "Herencia":  score_herencia,
        })

    df = (
        pd.DataFrame(datos_tabla)
        .sort_values(by="Final", ascending=False)
        .reset_index(drop=True)
    )

    # Calcular saltos para el criterio de corte
    df["Salto"] = df["Final"].diff(periods=-1).fillna(0)

    indice_corte = len(df)
    for idx, row in df.iterrows():
        siguiente_dominio = df.iloc[idx + 1]["Categoría"] if idx + 1 < len(df) else ""
        score_siguiente   = df.iloc[idx + 1]["Final"]     if idx + 1 < len(df) else 0

        if row["Final"] < SCORE_MINIMO:
            indice_corte = idx
            break

        if row["Salto"] > UMBRAL_CORTE:
            nucleo_rescatable = (
                siguiente_dominio in DOMINIOS_NUCLEO and score_siguiente >= SCORE_MINIMO
            )
            if not nucleo_rescatable:
                indice_corte = idx + 1
                break

    return df * 100  # Convertir a porcentajes


def obtener_perfil(texto: dict) -> int:
    """
    Clasifica el texto extraído y retorna el índice del perfil (0-4).

    Args:
        texto: Diccionario {nombre_empresa: {MISION: [...], VISION: [...], DESCRIPCION: [...]}}.

    Returns:
        Entero entre 0 y 4 (índice de cluster K-Means).

    Raises:
        FileNotFoundError: Si no se encuentra el archivo del modelo.
        ValueError: Si el texto es None o vacío.
    """
    if not texto:
        raise ValueError("El texto de entrada está vacío o es None.")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo en: {MODEL_PATH}\n"
            "Asegúrate de que 'Modelo_Pymes.pkl' esté en la carpeta raíz del proyecto."
        )

    vector = _vectorizar(texto)
    kmeans = joblib.load(MODEL_PATH)
    perfil = kmeans.predict(vector.iloc[:, 1].values.reshape(1, -1))
    return int(perfil[0])
