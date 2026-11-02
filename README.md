# Proyecto 2 — Reconocimiento con PDA y CYK

Universidad del Valle de Guatemala · Teoría de la Computación CC2019, sección 30.
Docente: Tomás Gálvez P. · Semestre 2, 2026.

| Integrante | Carné |
| --- | --- |
| David López | 24730 |
| Carlos López | 24531 |

[Informe PDF](docs/informe.pdf) · [Video de demostración](https://youtu.be/9PlEOdXy-zE) ·
[Repositorio](https://github.com/DeividArriaza/proyecto2-tdc)

## Descripción y gramática

Dos métodos independientes reconocen frases de la gramática libre de contexto G:

- **PDA:** autómata de pila construido desde G mediante una extensión del AFN del proyecto 1;
  su simulador explora configuraciones con BFS y reconstruye un recorrido aceptante.
- **CYK:** programación dinámica sobre G en Forma Normal de Chomsky (CNF), con tabla,
  testigos, árbol y derivación izquierda.

G = (V_G, Σ, S, R), con símbolo inicial S. Sus 8 variables son
{S, VP, PP, NP, V, P, N, Det}; sus 21 terminales son las palabras de estas producciones:

```text
S   → NP VP
VP  → VP PP | V NP | cooks | drinks | eats | cuts
PP  → P NP
NP  → Det N | he | she
V   → cooks | drinks | eats | cuts
P   → in | with
N   → cat | dog | beer | cake | juice | meat | soup
N   → fork | knife | oven | spoon
Det → a | the
```

Las 30 alternativas son 5 binarias y 25 léxicas. G ya está en CNF y no deriva ε.

## Requisitos

Python **3.10 o posterior**. Los reconocedores, las pruebas y las gráficas usan únicamente
la biblioteca estándar; no requieren instalar dependencias. Ejecute los comandos desde la raíz.

## Uso

```powershell
python main.py "frase" --metodo ambos --traza --json salidas/resultado.json
python main.py --help
```

| Opción | Comportamiento |
| --- | --- |
| `--metodo pda\|cyk\|ambos` | Selecciona el reconocedor; por defecto, `ambos`. |
| `--traza` | Muestra el recorrido PDA aceptante o su agotamiento, y la tabla CYK completa. |
| `--json RUTA` | Exporta decisiones, contadores y evidencia completa; crea las carpetas necesarias. |
| `--limite N` | Entero positivo: máximo de expansiones PDA; no limita CYK. |

Cada palabra es un token. `split()` separa espacios en blanco, incluidos tabs y saltos de línea.
No se normalizan mayúsculas ni puntuación: `He cooks`, `he cooks.` y palabras desconocidas
se rechazan. La entrada vacía también se rechaza. Sin límite, el PDA de G termina mediante
la poda segura por longitud; alcanzar un límite produce **inconclusa**, nunca rechazo.

| Código de salida | Significado |
| --- | --- |
| `0` | Aceptación de los métodos ejecutados. |
| `1` | Rechazo de los métodos ejecutados. |
| `2` | Inconclusión, discrepancia entre métodos, argumentos inválidos o error de exportación. También se usa si se solicita exclusivamente CYK y su módulo no está disponible. |

Ejemplos ejecutados, con salida abreviada (se omiten contadores y trazas extensas):

```text
> python main.py "he cooks" --metodo ambos --traza
PDA: aceptada. Estado final alcanzado con toda la entrada consumida
CYK: aceptada. S está en la celda final (inicio 0, longitud 2)

> python main.py "he eats cake" --metodo cyk --traza
CYK: rechazada. S no está en la celda final (inicio 0, longitud 3)

> python main.py "he cooks" --metodo pda --limite 1
PDA: inconclusa. Límite de configuraciones alcanzado
```

El JSON incluye las configuraciones y el recorrido PDA, y la tabla, testigos, árbol y
formas de la derivación CYK. Ambos métodos deciden sin consultar al otro.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```

**57 pruebas OK.** Cubren gramática, extensión del AFN, PDA, CYK, evidencia, consola y
validación cruzada: 9 331 cadenas de longitud ≤ 5 sobre un alfabeto reducido, además de
60 frases generadas con semilla fija y sus perturbaciones.

## Experimentos y documentación

El desempeño se estudia mediante conteo de operaciones, sin usar tiempos de reloj.

```powershell
python scripts/conteos_pda.py
python scripts/benchmark.py
python scripts/graficas.py
```

- `conteos_pda.py` imprime ocho casos con contadores PDA en CSV.
- `benchmark.py` regenera `docs/operaciones.csv`: 40 casos de cuatro familias, con ambos métodos;
  `--salida -` imprime el CSV en la consola.
- `graficas.py` genera las figuras SVG lineal y log–log en `docs/figuras/` desde ese CSV.

Para regenerar el informe se requieren Chrome y la dependencia de `requirements-docs.txt`.
En PowerShell, use un entorno separado para documentación:

```powershell
python -m venv .venv-docs
.venv-docs/Scripts/python.exe -m pip install -r requirements-docs.txt
.venv-docs/Scripts/python.exe scripts/generar_pdf.py
```

`generar_pdf.py` convierte `docs/informe.md` en HTML autónomo con SVG embebidos y lo imprime
como `docs/informe.pdf` mediante Chrome headless. Admite `--chrome RUTA` o `CHROME_PATH`
si Chrome no está en su ubicación estándar.

Para G: CYK **Θ(n³)**; PDA, cotas superiores **O(n²) transiciones evaluadas** y **O(n³) símbolos copiados**; véase el [informe](docs/informe.md#6-tasas-de-crecimiento).

## Estructura del repositorio

```text
.
├── .gitignore
├── Proyecto 2 2026.pdf
├── README.md
├── main.py
├── requirements-docs.txt
├── recognizer/
│   ├── __init__.py
│   ├── automata.py
│   ├── cyk.py
│   ├── grammar.py
│   ├── pda.py
│   ├── resultado.py
│   └── proyecto1/
│       ├── __init__.py
│       ├── constants.py
│       ├── errors.py
│       └── models.py
├── scripts/
│   ├── benchmark.py
│   ├── conteos_pda.py
│   ├── generar_pdf.py
│   └── graficas.py
├── tests/
│   ├── test_cli.py
│   ├── test_cyk.py
│   ├── test_grammar_automata.py
│   ├── test_integration.py
│   ├── test_main.py
│   └── test_pda.py
├── docs/
│   ├── acuerdos.md
│   ├── cyk.md
│   ├── guion_video.md
│   ├── informe.html
│   ├── informe.md
│   ├── informe.pdf
│   ├── operaciones.csv
│   ├── pda.md
│   └── figuras/
│       ├── operaciones-lineal.svg
│       └── operaciones-log.svg
└── salidas/
    └── .gitkeep
```

Detalle técnico: [PDA](docs/pda.md), [CYK](docs/cyk.md) y
[contratos de entrada y evidencia](docs/acuerdos.md).
