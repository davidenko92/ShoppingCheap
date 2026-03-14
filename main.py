"""
ShoppingCheap - Comparador de precios de supermercados online

Uso:
  1. Copia .env.example como .env y rellena tu API key
  2. Edita MI_LISTA con los productos que quieres comparar
  3. Ejecuta: python main.py
"""

from comparador import comparar_lista
from matching import LLMMatcher
from report import imprimir_resultado

# -----------------------------------------------
# EDITA AQUI TU LISTA DE LA COMPRA
# -----------------------------------------------
MI_LISTA = [
    "leche entera",
    "huevos",
    "aceite de oliva virgen extra",
    "yogur natural",
    "pan de molde",
    "arroz",
    "pasta espagueti",
    "atun en lata",
    "tomate frito",
    "zumo de naranja",
]

# -----------------------------------------------
# SUPERMERCADOS A COMPARAR
# Opciones: "Alcampo", "Dia", "Hipercor", "Carrefour"
# Elimina "Carrefour" si no tienes Playwright instalado
# -----------------------------------------------
SUPERMERCADOS = ["Alcampo", "Dia", "Hipercor", "Carrefour"]


if __name__ == "__main__":
    print("ShoppingCheap - Comparador de precios")
    print(f"Productos: {len(MI_LISTA)} | Supermercados: {', '.join(SUPERMERCADOS)}")
    print()

    matcher = LLMMatcher(verbose=True)
    resultado = comparar_lista(MI_LISTA, SUPERMERCADOS, matcher)
    imprimir_resultado(resultado, MI_LISTA)
