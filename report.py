"""Presentacion de resultados en consola."""

from collections import defaultdict


def imprimir_resultado(resultado: dict, lista_compra: list[str]):
      informe    = resultado["informe"]
      totales    = resultado["totales"]
      compra_opt = resultado["compra_optima"]

    # 1. Detalle por producto
      print("\n" + "=" * 65)
      print("  DETALLE POR PRODUCTO")
      print("=" * 65)

    for item in lista_compra:
              grupos = informe.get(item, [])
              print(f"\n  {item.upper()}")
              if not grupos:
                            print("  Sin resultados")
                            continue
                        for grupo in grupos[:3]:
                                      nombre = grupo["nombre_representativo"][:60]
                                      print(f"\n  Producto: {nombre}")
                                      for super_name, prod in sorted(
                                                        grupo["por_supermercado"].items(),
                                                        key=lambda x: x[1].precio
                                      ):
                                                        pu = (f" [{prod.precio_por_unidad:.2f}/{prod.unidad_referencia}]"
                                                                                    if prod.precio_por_unidad else "")
                                                        marca = ">>> MEJOR PRECIO" if super_name == grupo["mejor_super"] else ""
                                                        print(f"    {super_name:<14} {prod.precio:.2f} euros{pu}  {marca}")

                              # 2. Ranking total
                              print("\n\n" + "=" * 65)
    print("  TOTAL SI COMPRAS TODO EN UN SOLO SUPERMERCADO")
    print("=" * 65)

    ranking = sorted(totales.items(), key=lambda x: x[1])
    minimo  = ranking[0][1] if ranking else 0
    medallas = ["[1]", "[2]", "[3]", "[4]", "[5]"]

    for i, (super_name, total) in enumerate(ranking):
              extra = "  <- MAS BARATO" if total == minimo else f"  (+{total - minimo:.2f} euros mas)"
        print(f"  {medallas[min(i,4)]} {super_name:<14} {total:.2f} euros{extra}")

    # 3. Compra combinada optima
    print("\n\n" + "=" * 65)
    print("  COMPRA INTELIGENTE (mejor precio por producto)")
    print("=" * 65)

    por_super = defaultdict(list)
    total_combinado = 0.0

    for item, super_name, prod in compra_opt:
              por_super[super_name].append((item, prod))
        total_combinado += prod.precio

    for super_name, items in por_super.items():
              print(f"\n  Ir a: {super_name}")
        for item, prod in items:
                      pu = (f"[{prod.precio_por_unidad:.2f}/{prod.unidad_referencia}]"
                                              if prod.precio_por_unidad else "")
                      print(f"    - {item:<28} {prod.precio:.2f} euros  {pu}")

    print(f"\n  Total compra combinada: {total_combinado:.2f} euros")
    if ranking:
              ahorro = ranking[-1][1] - total_combinado
        print(f"  Ahorro vs supermercado mas caro: {ahorro:.2f} euros")

    # 4. Mejor calidad-precio
    print("\n\n" + "=" * 65)
    print("  MEJOR CALIDAD-PRECIO (precio por litro/kg mas bajo)")
    print("=" * 65)

    for item in lista_compra:
              grupos = informe.get(item, [])
        candidatos = []
        for grupo in grupos:
                      for super_name, prod in grupo["por_supermercado"].items():
                                        if prod.precio_por_unidad:
                                                              candidatos.append((prod.precio_por_unidad, super_name, prod))
                                                  if candidatos:
                                                                _, best_super, best_prod = min(candidatos)
                                                                print(
                                                                    f"  {item:<28} -> {best_super} "
                                                                    f"a {best_prod.precio_por_unidad:.2f}/{best_prod.unidad_referencia}"
                                                                )

                            print()
