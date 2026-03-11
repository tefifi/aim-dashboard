"""
Definiciones, constantes y datos estáticos de la aplicación AIM Dashboard.
Separado del código lógico para facilitar mantenimiento y localización.
"""

DEFINICION_TRIADA_AIM = """
**La Tríada AIM (Awareness, Infrastructure, Management)** no es un nuevo modelo de madurez
en ciberseguridad, sino una estrategia de priorización diseñada para guiar a las organizaciones.

A través de nuestro servicio obtenemos el perfil correspondiente a su empresa a partir del
link de su sitio web, para dar indicaciones acerca de qué estrategias de ciberseguridad
serían adecuadas para su organización.
"""

DEFINICIONES_PERFILES = [
    # ── Perfil 1 ── Gestión formalizada, visibilidad técnica limitada
    """
**Perfil 1 — El Gestor Formalizado**

Su organización ha construido una base sólida en la dimensión de **Gestión**: cuenta con
políticas documentadas, conciencia sobre obligaciones legales y una estructura básica para
administrar activos y personal de seguridad. Entiende *qué* debe proteger y *quién* es
responsable de hacerlo.

Sin embargo, la brecha crítica está en la **visibilidad técnica**: carece de capacidad para
detectar amenazas en tiempo real, su arquitectura de red no está diseñada pensando en
seguridad y los vectores de ataque técnicos permanecen sin monitoreo activo.

**¿Qué significa esto en la práctica?**
Su empresa sabe que existe el riesgo, tiene los papeles en orden, pero no vería un ataque
en curso hasta que ya causara daño. Es como tener un buen seguro pero ninguna alarma.

**Próximos pasos recomendados:**
Priorizar la implementación de herramientas de monitoreo (SIEM básico o EDR), revisar la
segmentación de red y realizar un primer ejercicio de análisis de vulnerabilidades.
    """,
    # ── Perfil 2 ── Alta madurez técnica y de conciencia, gestión en desarrollo
    """
**Perfil 2 — El Técnico Avanzado**

Su organización demuestra un nivel de madurez **excepcionalmente alto** en las dimensiones
técnicas: tiene tecnología de seguridad bien implementada, arquitectura defensiva estructurada
y una visibilidad del entorno de amenazas muy por encima del promedio para una PyME.

Además posee una cultura de seguridad activa y capacidad de detección y respuesta ante
incidentes. En términos del modelo AIM, cubre prácticamente todo el espectro de
**Awareness** e **Infrastructure**.

La oportunidad de mejora está en la **formalización de la gestión**: los procesos existen
pero dependen de personas clave, la gestión del talento de seguridad no está sistematizada
y el cumplimiento normativo puede estar rezagado frente al nivel técnico alcanzado.

**Próximos pasos recomendados:**
Documentar y transferir el conocimiento tácito a procesos formales, revisar brechas de
cumplimiento regulatorio y estructurar un plan de sucesión para roles críticos de seguridad.
    """,
    # ── Perfil 3 ── Operaciones robustas, estrategia y cultura por desarrollar
    """
**Perfil 3 — El Operador Robusto**

Su organización ha madurado en la ejecución operativa de la seguridad: administra
correctamente sus activos, mantiene su fuerza laboral alineada con las responsabilidades
de seguridad y ha desarrollado capacidades para identificar y mitigar vulnerabilidades técnicas.

Existe un programa de seguridad que funciona en el día a día. La gestión del riesgo tiene
presencia y la gestión del conocimiento es un punto diferenciador positivo.

Las brechas se concentran en la **dirección estratégica y la cultura**: no existe una
política de seguridad que unifique los esfuerzos, la seguridad no está integrada como
valor organizacional y el cumplimiento normativo no ha sido abordado formalmente.

**Próximos pasos recomendados:**
Desarrollar una política de seguridad corporativa aprobada por la dirección, iniciar un
programa de cultura de seguridad para el personal no técnico y mapear los requisitos
regulatorios aplicables al sector.
    """,
    # ── Perfil 4 ── Cultura y conciencia desarrolladas, infraestructura rezagada
    """
**Perfil 4 — El Consciente Estratégico**

Su organización tiene algo valioso y difícil de construir: una **cultura de seguridad genuina**
y capacidad para detectar y responder a incidentes. El personal entiende los riesgos,
existe conciencia situacional y la gestión del conocimiento en seguridad es un activo real.

Esto la ubica por delante de la mayoría de las PyMEs, donde la mayor vulnerabilidad
es precisamente el factor humano.

La brecha está en la **infraestructura técnica**: la arquitectura no refleja el nivel de
madurez cultural alcanzado, los vectores de ataque técnico no están completamente
mitigados y el marco normativo-legal no ha sido formalizado.

**Próximos pasos recomendados:**
Traducir la cultura de seguridad existente en controles técnicos concretos: segmentación
de red, gestión de vulnerabilidades y hardening de sistemas. Aprovechar la conciencia
del equipo para acelerar la adopción de nuevas herramientas.
    """,
    # ── Perfil 5 ── Infraestructura y gestión sólidas, detección y cultura incipientes
    """
**Perfil 5 — El Arquitecto Estructurado**

Su organización ha invertido en construir una **base técnica y de gestión coherente**:
la arquitectura de seguridad está diseñada defensivamente, los activos están bajo control,
existe una estrategia de seguridad formal y se gestiona el riesgo con criterios definidos.

Es una organización que "construyó bien": su infraestructura digital refleja decisiones
de diseño seguro y los procesos de gestión respaldan esas decisiones.

Las áreas de mejora están en la **capacidad de detección activa y el factor humano**:
aún no se ha desarrollado plenamente la capacidad para detectar y responder a incidentes
en tiempo real, y la seguridad como valor cultural todavía no está arraigada en el
comportamiento cotidiano del personal.

**Próximos pasos recomendados:**
Implementar capacidades de detección y respuesta (SOC básico o servicio MDR), desarrollar
un programa de concientización continua para el personal y establecer ejercicios de
simulación de incidentes (tabletop exercises).
    """]

DOMINIOS_DEFINICIONES = {
    "Cultura y Sociedad": (
        "Refleja los valores, creencias y comportamientos del equipo frente a la seguridad. "
        "Una cultura madura convierte a cada persona en un sensor activo de riesgos, donde "
        "reportar incidentes se ve como una responsabilidad compartida y no como una amenaza."
    ),
    "Conciencia Situacional": (
        "Capacidad de detectar, correlacionar y comprender eventos de seguridad en tiempo real. "
        "Incluye monitoreo centralizado (SIEM/XDR), inteligencia de amenazas y dashboards que "
        "traducen datos técnicos en información útil para la toma de decisiones."
    ),
    "Estándares y Tecnología": (
        "Adopción y operación disciplinada de estándares (NIST, ISO 27001, CIS) y herramientas "
        "de seguridad. No basta con comprar tecnología: este dominio mide si está correctamente "
        "configurada, integrada y mantenida."
    ),
    "Arquitectura": (
        "Diseño estructural de la infraestructura digital pensado para minimizar el impacto de "
        "una brecha. Incluye segmentación de red, modelos Zero Trust, zonas desmilitarizadas (DMZ) "
        "y principios de mínimo privilegio aplicados desde el diseño."
    ),
    "Amenazas y Vulnerabilidades": (
        "Ciclo de vida completo de identificación y mitigación de vulnerabilidades: desde "
        "escaneos automáticos y pruebas de penetración hasta la gestión priorizada de parches "
        "según el riesgo real para el negocio."
    ),
    "Programa": (
        "Existencia de un programa formal de ciberseguridad con objetivos, presupuesto, "
        "métricas y hoja de ruta. Asegura que las iniciativas de seguridad sean planificadas "
        "y ejecutadas como un esfuerzo coherente y sostenido."
    ),
    "Capital Humano": (
        "Gestión del talento de seguridad: roles definidos, responsabilidades claras, "
        "capacitación continua y planificación de sucesión. Cubre tanto al equipo técnico "
        "especializado como al personal general con obligaciones de seguridad."
    ),
    "Activos y Configuración": (
        "Inventario actualizado de todos los activos digitales y físicos, con control de "
        "cambios que previene modificaciones no autorizadas o inseguras. Sin saber qué "
        "activos existen, es imposible protegerlos."
    ),
    "Marco Legal y Regulatorio": (
        "Cumplimiento de leyes, regulaciones sectoriales y contratos que imponen obligaciones "
        "de seguridad (ej. Ley 21.663 en Chile, GDPR si hay datos europeos). Implica mapear "
        "los requisitos aplicables y traducirlos en controles operacionales."
    ),
    "Marco Legal y Regulatorio": (
        "Cumplimiento de leyes, regulaciones sectoriales y contratos que imponen obligaciones "
        "de seguridad. Implica mapear los requisitos aplicables y traducirlos en controles "
        "operacionales concretos y auditables."
    ),
    "Detección y Respuesta": (
        "Capacidad de detectar, contener, erradicar y recuperarse de incidentes de seguridad "
        "de forma estructurada. Incluye playbooks de respuesta, equipos con roles definidos "
        "y ejercicios de simulación que validan la preparación real."
    ),
    "Política y Estrategia": (
        "Marco de políticas formales aprobadas por la dirección que definen el comportamiento "
        "esperado, los controles requeridos y la estrategia de seguridad a mediano y largo "
        "plazo. Proporciona el 'norte' que orienta todas las demás decisiones."
    ),
    "Conocimiento y Capacidades": (
        "Base de conocimiento institucional en ciberseguridad: inteligencia de amenazas, "
        "lecciones aprendidas, competencias técnicas especializadas y capacidad de investigación. "
        "Permite anticipar tendencias y no solo reaccionar a ellas."
    ),
    "Riesgo": (
        "Proceso sistemático para identificar, evaluar y priorizar riesgos según su probabilidad "
        "e impacto en el negocio. Un registro de riesgos activo permite tomar decisiones de "
        "inversión en seguridad basadas en evidencia, no en intuición."
    ),
}

# Dominios débiles (áreas a mejorar) por perfil (índice 0 = Perfil 1)
CONSEJOS_PERFILES_NEGATIVOS = [
    ["Conciencia Situacional", "Arquitectura", "Amenazas y Vulnerabilidades"],
    ["Marco Legal y Regulatorio", "Capital Humano", "Activos y Configuración"],
    ["Política y Estrategia", "Cultura y Sociedad", "Marco Legal y Regulatorio"],
    ["Arquitectura", "Amenazas y Vulnerabilidades", "Marco Legal y Regulatorio"],
    ["Detección y Respuesta", "Cultura y Sociedad", "Conciencia Situacional"],
]

# Dominios fuertes (fortalezas) por perfil
CONSEJOS_PERFILES_POSITIVO = [
    ["Marco Legal y Regulatorio", "Capital Humano", "Activos y Configuración"],
    ["Estándares y Tecnología", "Conciencia Situacional", "Arquitectura"],
    ["Programa", "Amenazas y Vulnerabilidades", "Capital Humano"],
    ["Detección y Respuesta", "Cultura y Sociedad", "Conciencia Situacional"],
    ["Arquitectura", "Amenazas y Vulnerabilidades", "Activos y Configuración"],
]

# Fortalezas completas por perfil (para el diagrama Venn)
FORTALEZAS_PERFIL = [
    ["Política y Estrategia", "Riesgo", "Programa", "Detección y Respuesta",
     "Marco Legal y Regulatorio", "Activos y Configuración", "Capital Humano"],
    ["Política y Estrategia", "Conocimiento y Capacidades", "Detección y Respuesta",
     "Estándares y Tecnología", "Arquitectura", "Amenazas y Vulnerabilidades",
     "Cultura y Sociedad", "Conciencia Situacional"],
    ["Conocimiento y Capacidades", "Riesgo", "Programa", "Activos y Configuración",
     "Capital Humano", "Amenazas y Vulnerabilidades"],
    ["Conocimiento y Capacidades", "Riesgo", "Detección y Respuesta",
     "Cultura y Sociedad", "Conciencia Situacional"],
    ["Política y Estrategia", "Riesgo", "Programa", "Marco Legal y Regulatorio",
     "Activos y Configuración", "Arquitectura", "Amenazas y Vulnerabilidades"],
]

# --- Diagrama Venn ---
COLORES_BASE = {
    "Concientizacion":  "#e06060",
    "Infraestructura":  "#4a8c5c",
    "Gestion":          "#3a6ab0",
    "Bridge":           "#c87e30",
    "Core":             "#8a6d3b",
    "Desactivado":      "#c8d0df",
}

VENN_SECTIONS = {
    "100": "Concientizacion",
    "010": "Infraestructura",
    "001": "Gestion",
    "110": "Bridge",
    "101": "Bridge",
    "011": "Bridge",
    "111": "Core",
}

SUBCATEGORIAS = {
    "A":     ["Cultura y Sociedad", "Conciencia Situacional"],
    "I":     ["Arquitectura", "Amenazas y Vulnerabilidades"],
    "M":     ["Marco Legal y Regulatorio", "Activos y Configuración", "Capital Humano"],
    "A-I":   ["Estándares y Tecnología"],
    "A-M":   ["Detección y Respuesta"],
    "I-M":   ["Programa"],
    "A-I-M": ["Política y Estrategia", "Conocimiento y Capacidades", "Riesgo"],
}

DOMINIOS_POR_ETAPA = {
    "Core":           SUBCATEGORIAS["A-I-M"],
    "Bridge":         SUBCATEGORIAS["A-I"] + SUBCATEGORIAS["A-M"] + SUBCATEGORIAS["I-M"],
    "Concientización": SUBCATEGORIAS["A"],
    "Infraestructura": SUBCATEGORIAS["I"],
    "Gestión":        SUBCATEGORIAS["M"],
}

# Mapeo de zonas Venn a subcategorías
VENN_ID_TO_SUBCATEGORIA = {
    "100": SUBCATEGORIAS["A"],
    "010": SUBCATEGORIAS["I"],
    "001": SUBCATEGORIAS["M"],
    "110": SUBCATEGORIAS["A-I"],
    "101": SUBCATEGORIAS["A-M"],
    "011": SUBCATEGORIAS["I-M"],
    "111": SUBCATEGORIAS["A-I-M"],
}
