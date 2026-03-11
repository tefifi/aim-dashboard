"""
Módulo de extracción y clasificación de texto desde sitios web.
Clase ExtractorMVD: navega el sitio, extrae contenido relevante y
clasifica oraciones en categorías MISIÓN, VISIÓN y DESCRIPCIÓN.
"""

import re
import logging

import requests
from bs4 import BeautifulSoup
import trafilatura
import nltk
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# Descarga de recursos NLTK solo si no están disponibles
def _asegurar_nltk():
    for recurso in ("punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{recurso}")
        except LookupError:
            nltk.download(recurso, quiet=True)

_asegurar_nltk()


class ExtractorMVD:
    """
    Extrae y clasifica el contenido de texto de un sitio web corporativo.

    Uso:
        extractor = ExtractorMVD(url="https://empresa.cl", nombre="Empresa S.A.")
        extractor.navegar_y_extraer()
        resultado = extractor.clasificar_inteligente()
    """

    # Rutas de fallback cuando no se encuentran links de navegación
    RUTAS_FALLBACK = [
        "/nosotros", "/pages/nosotros", "/quienes-somos", "/somos",
        "/about", "/mision", "/conocenos", "/about-us",
        "/empresa.htm", "/nosotros-2", "/nuestra-empresa",
    ]

    def __init__(self, url: str, nombre: str):
        self.url_base = url
        self.nombre = nombre
        self.paginas_candidatas: list[str] = []
        self.datos_crudos: list[dict] = []

        # Keywords para detectar páginas "Acerca de" en la navegación
        self._nav_keywords = [
            "desarrollo", "ubicada", "nosotros", "nosotras", "quienes",
            "misión", "vision", "historia", "origen", "equipo", "about",
            "propósito", "manifiesto", "impacto", "sobre",
            "we", "us", "who", "mission", "vision", "history", "origin",
            "team", "purpose", "manifesto", "impact",
        ]

        # Patrones de clasificación semántica
        self._patrones = {
            "MISION": {
                "fuerte": [
                    r"nos enfocamos", r"buscamos hacer", r"nuestra misión",
                    r"nuestro propósito", r"nuestro objetivo", r"la misión es",
                    r"razón de ser", r"por qué existimos", r"nos dedicamos a",
                    r"nuestro compromiso es", r"our mision", r"our purpose",
                    r"our objective", r"mision is", r"we exist",
                    r"we are dedicated to", r"our commitment is",
                ],
                "debil": [
                    r"trabajamos para", r"buscamos", r"ayudar a", r"solucionar",
                    r"dar una alternativa", r"reemplazar", r"permitir", r"entregar",
                    r"proveer", r"facilitar", r"impulsar", r"fomentar", r"promover",
                    r"asegurar", r"garantizar", r"contribuir", r"aportar",
                    r"generar valor", r"we work for", r"we search", r"help",
                    r"solve", r"give an alternative", r"replace", r"allow",
                    r"deliver", r"provide", r"facilitate", r"encourage",
                    r"assure", r"guarantee", r"contribute", r"create value",
                ],
            },
            "VISION": {
                "fuerte": [
                    r"nuestra visión", r"queremos ser", r"seremos", r"proyectamos",
                    r"hacia el futuro", r"nuestro sueño", r"soñamos con",
                    r"aspiramos a", r"horizonte", r"queremos llevar",
                    r"our vision", r"we want to be", r"we will be", r"we project",
                    r"into the future", r"our dream", r"we dream of",
                    r"we aspire to", r"horizon", r"we want to take",
                ],
                "debil": [
                    r"convertirnos en", r"liderar", r"referente", r"mundo",
                    r"global", r"internacional", r"latinoamérica", r"impacto real",
                    r"cambio es necesario", r"otra forma de vida", r"revolucionar",
                    r"transformar", r"redefinir", r"innovación constante",
                    r"vanguardia", r"consolidarnos", r"reconocidos por",
                    r"largo plazo", r"transform", r"become", r"lead", r"world",
                    r"international", r"latin america", r"real impact",
                    r"necessary change", r"another way of life", r"revolutionize",
                    r"redefine", r"constant innovation", r"vanguard",
                    r"consolidate", r"recognized by", r"long term",
                ],
            },
            "DESCRIPCION": {
                "fuerte": [
                    r"somos", r"fundada en", r"experiencia", r"historia comienza",
                    r"nació en", r"comenzó como", r"trayectoria", r"nuestros inicios",
                    r"quienes somos", r"equipo de",
                    r"as in our name", r"we are", r"founded in", r"experience",
                    r"history start", r"born in", r"started as", r"trajectory",
                    r"our begginings", r"who we are", r"team of",
                ],
                "debil": [
                    r"empresa", r"compañía", r"consultora", r"organización",
                    r"startup", r"agencia", r"firma", r"ofrecemos", r"servicios",
                    r"productos", r"plataforma", r"soluciones", r"herramientas",
                    r"ubicados en", r"especialistas en", r"expertos en",
                    r"más de \d+ años", r"experiencia en", r"presencia en",
                    r"company", r"consultant", r"organization", r"agency",
                    r"sign", r"we offer", r"services", r"products", r"platform",
                    r"solutions", r"tools", r"located in", r"specialists in",
                    r"experts in", r"more than \d+ years", r"experience in",
                    r"presence in",
                ],
            },
        }

        self._blacklisted_words = [
            "leer más", "read more", "ver más", "cookies", "derechos reservados",
            "copyright", "iniciar sesión", "carrito", "despachos", "envíos",
            "vacaciones", "feriado", "horario de atención", "subscribe", "boletín",
            "plastic free july", "sumate", "síguenos", "formulario", "censura",
            "see more", "all rights reserved", "fifa", "concurso", "incumplimiento",
            "teléfono", "link", "horario", "log in", "shopping cart", "shipping",
            "deliveries", "holidays", "opening hours", "newsletter", "join us",
            "follow us", "cookie",
        ]

    # ------------------------------------------------------------------
    # Navegación y extracción
    # ------------------------------------------------------------------

    def navegar_y_extraer(self) -> None:
        """Recorre el sitio web y almacena el texto extraído de cada página."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(self.url_base, headers=headers, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            self._encontrar_paginas_candidatas(soup)
        except requests.RequestException as e:
            logger.warning("Error al acceder a %s: %s", self.url_base, e)

        # Siempre incluir la página raíz
        if self.url_base not in self.paginas_candidatas:
            self.paginas_candidatas.append(self.url_base)

        self._extraer_textos()

    def _encontrar_paginas_candidatas(self, soup: BeautifulSoup) -> None:
        found_links: set[str] = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            texto_link = link.get_text().lower()
            es_relevante = any(kw in texto_link for kw in self._nav_keywords) or \
                           any(kw in href.lower() for kw in self._nav_keywords)
            if es_relevante:
                full_url = urljoin(self.url_base, href)
                if self.url_base in full_url and full_url not in found_links:
                    found_links.add(full_url)
                    self.paginas_candidatas.append(full_url)

        if not self.paginas_candidatas:
            for ruta in self.RUTAS_FALLBACK:
                self.paginas_candidatas.append(urljoin(self.url_base, ruta))

    def _extraer_textos(self) -> None:
        for url in self.paginas_candidatas:
            try:
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    texto = trafilatura.extract(
                        downloaded,
                        include_comments=False,
                        include_tables=False,
                        include_links=False,
                        favor_precision=True,
                    )
                    if texto:
                        self.datos_crudos.append({"url": url, "texto": texto})
            except Exception as e:
                logger.debug("No se pudo extraer texto de %s: %s", url, e)

    # ------------------------------------------------------------------
    # Limpieza y validación
    # ------------------------------------------------------------------

    def _limpiar_texto(self, oracion: str) -> str:
        oracion = re.sub(r"(?i)(leer\s+m[áa]s|read\s+more|ver\s+m[áa]s|ver\s+detalle)\.*", "", oracion)
        oracion = re.sub(r"\.{2,}", "", oracion)
        return oracion.strip()

    def _validar_integridad(self, oracion: str) -> bool:
        if not re.search(r'[.!?"]$', oracion):
            return False
        letras = [c for c in oracion if c.isalpha()]
        if len(letras) > 10:
            mayusculas = [c for c in letras if c.isupper()]
            if len(mayusculas) / len(letras) > 0.6:
                return False
        return True

    # ------------------------------------------------------------------
    # Clasificación semántica
    # ------------------------------------------------------------------

    def clasificar_inteligente(self) -> dict | None:
        """
        Clasifica el texto extraído en categorías MISIÓN, VISIÓN y DESCRIPCIÓN.

        Returns:
            Dict {nombre_empresa: {"MISION": [...], "VISION": [...], "DESCRIPCION": [...]}}
            o None si no hay datos.
        """
        if not self.datos_crudos:
            logger.warning("No se encontraron datos para clasificar en %s", self.url_base)
            return None

        resultados: dict[str, list] = {"MISION": [], "VISION": [], "DESCRIPCION": []}
        oraciones_procesadas: set[str] = set()

        for fuente in self.datos_crudos:
            texto_raw = fuente["texto"]
            texto_limpio = re.sub(r"\s+", " ", texto_raw)

            oraciones = nltk.sent_tokenize(texto_limpio)

            for oracion in oraciones:
                oracion = self._limpiar_texto(oracion)
                if len(oracion) < 25 or oracion in oraciones_procesadas:
                    continue

                oracion_lower = oracion.lower()
                if any(bad in oracion_lower for bad in self._blacklisted_words):
                    continue
                if not self._validar_integridad(oracion):
                    continue

                mejor_cat = None
                max_puntaje = 0

                for categoria, tipos in self._patrones.items():
                    puntaje = sum(
                        10 for p in tipos["fuerte"] if re.search(p, oracion_lower)
                    ) + sum(
                        3 for p in tipos["debil"] if re.search(p, oracion_lower)
                    )
                    if puntaje > max_puntaje:
                        max_puntaje = puntaje
                        mejor_cat = categoria

                if mejor_cat and max_puntaje >= 3:
                    resultados[mejor_cat].append(oracion)
                    oraciones_procesadas.add(oracion)

        return {self.nombre: resultados}
