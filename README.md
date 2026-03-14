# ShoppingCheap

Comparador automatico de precios de supermercados online espanoles con matching inteligente usando LLM (Claude o GPT).

Le pasas una lista de la compra y te dice:
- En que supermercado te sale mas barato comprar todo
- Como distribuir la compra entre supermercados para pagar lo minimo (compra combinada)
- Que opcion tiene mejor calidad-precio (precio por litro/kg)

## Supermercados soportados

| Supermercado | URL | Metodo scraping |
|---|---|---|
| Alcampo | compraonline.alcampo.es | HTML estatico |
| Dia | dia.es | HTML estatico |
| Hipercor | hipercor.es | HTML estatico |
| Carrefour | carrefour.es | JavaScript (Playwright) |

## Requisitos

- Python 3.10+
- API key de Anthropic (Claude) o OpenAI

## Instalacion

```bash
git clone https://github.com/davidenko92/ShoppingCheap
cd ShoppingCheap
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

## Uso

Edita main.py con tu lista de la compra y ejecuta:

```bash
python main.py
```

## Configuracion (.env)

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...
LLM_MODEL=claude-3-5-haiku-20241022
MATCHING_CONFIDENCE=0.85
```

## Estructura del proyecto

```
ShoppingCheap/
├── .env.example
├── requirements.txt
├── main.py               - Punto de entrada, edita tu lista aqui
├── comparador.py         - Orquesta scrapers y matching
├── report.py             - Imprime los resultados
├── scrapers/
│   ├── base.py
│   ├── alcampo.py
│   ├── dia.py
│   ├── hipercor.py
│   └── carrefour.py
└── matching/
    └── llm_matcher.py    - Matching con Claude o OpenAI
```

## Como funciona el matching con LLM

Cada supermercado nombra los productos de forma diferente. Por ejemplo para leche entera 1L:

- Alcampo: AUCHAN Leche entera de vaca 1 l.
- Dia: Leche entera Dia Lactea 1 L
- Hipercor: ASTURIANA leche entera brik 1 l
- Carrefour: Leche entera Carrefour brik 1 l.

El matcher usa dos pasos para minimizar el coste en API:

1. Filtro rapido (gratis): descarta incompatibles obvios por reglas (entera vs semidesnatada, sin lactosa, ecologico, etc.)
2. LLM para casos ambiguos: pregunta a Claude o GPT si dos productos son equivalentes, con puntuacion de confianza

Esto reduce las llamadas a la API en aproximadamente un 80%.

## Notas

- Carrefour requiere Playwright. Si no lo instalas, excluye Carrefour de SUPERMERCADOS en main.py.
- Los precios son en tiempo real, obtenidos en el momento de ejecutar el script.
- El archivo .env esta en .gitignore para proteger tus API keys.
