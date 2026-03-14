from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
      supermercado: str
      nombre: str
      precio: float
      precio_por_unidad: Optional[float] = None
      unidad_referencia: Optional[str] = None   # "LITRO", "KILO", "UNIDAD"
    url: Optional[str] = None

    def __repr__(self):
              pu = (f" [{self.precio_por_unidad:.2f}euros/{self.unidad_referencia}]"
                                  if self.precio_por_unidad else "")
              return f"{self.supermercado} | {self.precio:.2f}euros{pu} | {self.nombre[:50]}"
