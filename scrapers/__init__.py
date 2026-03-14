from .base import Producto
from .alcampo import scrape_alcampo
from .dia import scrape_dia
from .hipercor import scrape_hipercor
from .carrefour import scrape_carrefour

SCRAPERS = {
      "Alcampo":   scrape_alcampo,
      "Dia":       scrape_dia,
      "Hipercor":  scrape_hipercor,
      "Carrefour": scrape_carrefour,
}
