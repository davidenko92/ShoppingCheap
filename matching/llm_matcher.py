"""
Matching inteligente de productos entre supermercados usando LLM.
Soporta Anthropic (Claude) y OpenAI. Configurable via .env
"""

import os
import re
import json
from dotenv import load_dotenv
from scrapers.base import Producto

load_dotenv()

PROVIDER   = os.getenv("LLM_PROVIDER", "anthropic")
MODEL      = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
CONFIDENCE = float(os.getenv("MATCHING_CONFIDENCE", "0.85"))


def _get_client():
      if PROVIDER == "anthropic":
                import anthropic
                return anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
elif PROVIDER == "openai":
        from openai import OpenAI
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    raise ValueError(f"Proveedor no soportado: {PROVIDER}")


def _llamar_llm(prompt: str) -> str:
      client = _get_client()
      if PROVIDER == "anthropic":
                resp = client.messages.create(
                              model=MODEL,
                              max_tokens=512,
                              messages=[{"role": "user", "content": prompt}],
                )
                return resp.content[0].text
elif PROVIDER == "openai":
        resp = client.chat.completions.create(
                      model=MODEL,
                      messages=[{"role": "user", "content": prompt}],
                      temperature=0,
                      response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content


def _extraer_json(texto: str) -> dict:
      try:
                return json.loads(texto)
except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    if match:
              return json.loads(match.group(1))
          match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
              return json.loads(match.group(0))
          raise ValueError(f"JSON no encontrado en: {texto[:200]}")


def _extraer_atributos(nombre: str) -> dict:
      t = nombre.lower()
      return {
          "entera": "entera" in t,
          "semidesnatada": "semidesnata" in t,
          "desnatada": "desnata" in t and "semidesnata" not in t,
          "sin_lactosa": "sin lactosa" in t,
          "ecologico": any(x in t for x in ["eco", "bio", "ecol"]),
          "fresca": "fresca" in t or "pasteurizada" in t,
      }


def _son_compatibles_rapido(a: str, b: str) -> bool:
      at = _extraer_atributos(a)
      bt = _extraer_atributos(b)
      for tipo in ["entera", "semidesnatada", "desnatada"]:
                if at[tipo] != bt[tipo] and (at[tipo] or bt[tipo]):
                              return False
                      if at["sin_lactosa"] != bt["sin_lactosa"]:
                                return False
                            if at["ecologico"] != bt["ecologico"]:
                                      return False
                                  if at["fresca"] != bt["fresca"]:
                                            return False
                                        return True


class LLMMatcher:
      """
          Agrupa productos equivalentes entre supermercados usando un LLM.

              Flujo de dos pasos para minimizar coste:
                    1. Filtro rapido (reglas, sin LLM) - descarta incompatibles obvios
                          2. LLM - decide en casos ambiguos
                              """

    def __init__(self, verbose: bool = True):
              self.verbose = verbose
              self._cache: dict[tuple, bool] = {}

    def _log(self, msg: str):
              if self.verbose:
                            print(msg)

          def son_equivalentes(self, nombre_a: str, nombre_b: str) -> tuple[bool, str]:
                    key = tuple(sorted([nombre_a, nombre_b]))
                    if key in self._cache:
                                  return self._cache[key], "(cache)"

                    if not _son_compatibles_rapido(nombre_a, nombre_b):
                                  self._cache[key] = False
                                  return False, "Atributos incompatibles (filtro rapido)"

                    prompt = f"""Eres un asistente de compras de supermercado.
            Determina si estos dos productos son equivalentes para una comparacion de precios.

            Producto A: {nombre_a}
            Producto B: {nombre_b}

            Son equivalentes si representan el mismo tipo de producto con formato comparable
            (ejemplo: leche entera UHT 1L de distintas marcas SI son equivalentes;
            leche entera vs semidesnatada NO son equivalentes).

            Responde UNICAMENTE con este JSON, sin texto adicional:
            {{"equivalentes": true, "confianza": 0.95, "razon": "mismo tipo y formato"}}

            El campo confianza debe ser un numero entre 0.0 y 1.0."""

        try:
                      respuesta = _llamar_llm(prompt)
                      resultado = _extraer_json(respuesta)
                      confianza = float(resultado.get("confianza", 1.0))
                      equivalentes = resultado["equivalentes"] and confianza >= CONFIDENCE
                      razon = resultado.get("razon", "")
                      self._cache[key] = equivalentes
                      return equivalentes, f"{razon} (confianza: {confianza:.0%})"
except Exception as e:
              self._log(f"   Error LLM: {e}")
              self._cache[key] = False
              return False, f"Error: {e}"

    def agrupar_equivalentes(self, productos: list[Producto]) -> list[list[Producto]]:
              if not productos:
                            return []

              visitados = set()
              grupos = []
              llamadas = 0

        for i, p_a in enumerate(productos):
                      if i in visitados:
                                        continue
                                    grupo = [p_a]
            visitados.add(i)

            for j, p_b in enumerate(productos):
                              if j <= i or j in visitados:
                                                    continue
                                                if p_a.supermercado == p_b.supermercado:
                                                                      continue
                                                                  equiv, razon = self.son_equivalentes(p_a.nombre, p_b.nombre)
                if equiv:
                                      llamadas += 1
                                      self._log(
                                          f"   OK ({p_a.supermercado} <-> {p_b.supermercado}): {razon}"
                                      )
                                      grupo.append(p_b)
                                      visitados.add(j)

            grupos.append(grupo)

        self._log(f"   Llamadas LLM: {llamadas} | Cache: {len(self._cache)}")
        return grupos

    def mejor_precio_por_grupo(self, grupos: list[list[Producto]]) -> list[dict]:
              resultado = []
        for grupo in grupos:
                      if not grupo:
                                        continue
                                    por_super = {}
            for prod in grupo:
                              s = prod.supermercado
                if s not in por_super or prod.precio < por_super[s].precio:
                                      por_super[s] = prod

            mejor_super = min(por_super, key=lambda s: por_super[s].precio)
            resultado.append({
                              "nombre_representativo": max(grupo, key=lambda p: len(p.nombre)).nombre,
                              "por_supermercado": por_super,
                              "mejor_super": mejor_super,
                              "mejor_precio": por_super[mejor_super].precio,
                              "mejor_precio_unitario": por_super[mejor_super].precio_por_unidad,
                              "unidad": por_super[mejor_super].unidad_referencia,
            })

        return sorted(resultado, key=lambda x: x["mejor_precio"])
