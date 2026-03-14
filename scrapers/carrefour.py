import re
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from .base import Producto

BASE_URL = "https://www.carrefour.es/supermercado?query={query}"

HEADERS = {
      "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
      ),
}


def scrape_carrefour(query: str) -> list[Producto]:
      url = BASE_URL.format(query=query)

    with sync_playwright() as p:
              browser = p.chromium.launch(headless=True)
              page = browser.new_page(extra_http_headers=HEADERS)
              page.goto(url, timeout=30000, wait_until="domcontentloaded")
              try:
                            page.wait_for_selector("article", timeout=10000)
except Exception:
            pass
        time.sleep(2)
        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(" ")
    return _parsear_texto(text, url)


def _parsear_texto(text: str, url: str) -> list[Producto]:
      productos = []
      pattern = re.compile(
          r"(\d+[,\.]\d+)\s*"
          r"\s+(\d+[,\.]\d+)\s*\/([a-z\xe1\xe9\xed\xf3\xfal]+)"
          r"\s+([A-Z\xC1\xC9\xCD\xD3\xDA][^\n]{5,80})",
          re.IGNORECASE,
      )
      vistos = set()
      for m in pattern.finditer(text):
                nombre = m.group(4).strip()
                if nombre in vistos or len(nombre) < 6:
                              continue
                          vistos.add(nombre)
                precio = float(m.group(1).replace(",", "."))
                precio_u = float(m.group(2).replace(",", "."))
                unidad = m.group(3).upper()
                productos.append(Producto(
                    supermercado="Carrefour",
                    nombre=nombre,
                    precio=precio,
                    precio_por_unidad=precio_u,
                    unidad_referencia=unidad,
                    url=url,
                ))
            return productos
