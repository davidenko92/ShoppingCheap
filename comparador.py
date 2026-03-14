"""
Motor principal de comparacion.
Orquesta scrapers + matching LLM.
"""

from collections import defaultdict
from scrapers import SCRAPERS, Producto
from matching import LLMMatcher


def buscar_en_todos(query: str, supermercados: list[str] = None) -> dict[str, list[Producto]]:
      if supermercados is None:
                supermercados = list(SCRAPERS.keys())

      resultados = {}
      for nombre in supermercados:
                print(f"  Buscando en {nombre}...", end=" ", flush=True)
                try:
                              productos = SCRAPERS[nombre](query)
                              resultados[nombre] = productos
                              print(f"OK {len(productos)} productos")
except Exception as e:
            print(f"ERROR: {e}")
            resultados[nombre] = []

    return resultados


def comparar_lista(
      lista_compra: list[str],
      supermercados: list[str] = None,
      matcher: LLMMatcher = None,
) -> dict:
      if supermercados is None:
                supermercados = list(SCRAPERS.keys())
            if matcher is None:
                      matcher = LLMMatcher()

    informe_productos = {}
    totales = defaultdict(float)
    compra_optima = []

    for item in lista_compra:
              print(f"\n Buscando: '{item}'")
              resultados = buscar_en_todos(item, supermercados)
              todos = [p for prods in resultados.values() for p in prods]

        if not todos:
                      print("   Sin resultados")
                      informe_productos[item] = []
                      continue

        print(f"   Agrupando {len(todos)} productos con LLM...")
        grupos = matcher.agrupar_equivalentes(todos)
        grupos_info = matcher.mejor_precio_por_grupo(grupos)

        informe_productos[item] = grupos_info

        if grupos_info:
                      top = grupos_info[0]
                      mejor_super = top["mejor_super"]
                      mejor_prod = top["por_supermercado"][mejor_super]
                      compra_optima.append((item, mejor_super, mejor_prod))
                      for super_name, prod in top["por_supermercado"].items():
                                        totales[super_name] += prod.precio

              return {
                        "informe": informe_productos,
                        "totales": dict(totales),
                        "compra_optima": compra_optima,
              }
