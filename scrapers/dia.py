import re
  import requests
  from bs4 import BeautifulSoup
  from .base import Producto

  HEADERS = {
      "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-ES,es;q=0.9",
}

BASE_URL = "https://www.dia.es/search?q={query}"

  _BASURA = {"anadir", "ver mas", "filtros", "destacados", "mejor valorado",
                        "sin lactosa", "oferta club dia", "nuevo"}


def scrape_dia(query: str) -> list[Producto]:
    url = BASE_URL.format(query=query)
          resp = requests.get(url, headers=HEADERS, timeout=15)
          soup = BeautifulSoup(resp.text, "html.parser")
          text = soup.get_text(" ")
          return _parsear_texto(text, url)


      def _parsear_texto(text: str, url: str) -> list[Producto]:
    productos = []
          pattern = re.compile(
              r"([A-Z\xC1\xC9\xCD\xD3\xDA][^\n]{5,80}?)"
              r"\s+(\d+[,\.]\d+)\s*"
              r"\s*\((\d+[,\.]\d+)\s*\/([A-Z\xC1\xC9\xCD\xD3\xDA]+)\)",
              re.IGNORECASE,
          )
          vistos = set()
          for m in pattern.finditer(text):
              nombre = m.group(1).strip()
              if nombre.lower() in _BASURA or nombre in vistos or len(nombre) < 6:
                  continue
              vistos.add(nombre)
              precio = float(m.group(2).replace(",", "."))
              precio_u = float(m.group(3).replace(",", "."))
              unidad = m.group(4).upper()
              productos.append(Producto(
                            supermercado="Dia",
                            nombre=nombre,
                            precio=precio,
                            precio_por_unidad=precio_u,
                            unidad_referencia=unidad,
                            url=url,
                        ))
          return productos
