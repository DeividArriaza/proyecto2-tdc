# Proyecto 2 — Reconocimiento con PDA y CYK

Universidad del Valle de Guatemala · Teoría de la Computación CC2019, sección 30 · Docente: Tomás Gálvez P. · Semestre 2, 2026

| Integrante | Carné | Responsabilidad principal |
| --- | --- | --- |
| David Lopez | 24730 | PDA, extensión del proyecto 1, consola, repositorio |
| Carlos Lopez | 24531 | CYK, integración, experimentos, comparación, informe, video |

- Repositorio (privado): **PENDIENTE** (enlace final tras D10)
- Video (YouTube, no listado, ≤ 10 min): **PENDIENTE** (enlace final tras C10)

> Borrador de C9. Los datos y comandos corresponden al código actual del repositorio.
> Antes de generar el PDF final deben completarse carnés y enlaces y regenerarse los experimentos.

## 1. Objetivo

Reconocer frases del lenguaje de la gramática G del enunciado con dos métodos independientes:
un autómata de pila (PDA) obtenido de G, que extiende el autómata del proyecto 1, y el algoritmo
CYK. Ambos registran los pasos que justifican su respuesta. Además se calcula la tasa de
crecimiento de cada programa mediante conteo de operaciones y se comparan sus desempeños.

## 2. La gramática G

G = (V, Σ, S, P) con V = {S, VP, PP, NP, V, P, N, Det} y Σ = {cooks, drinks, eats, cuts, he, she,
in, with, a, the, cat, dog, beer, cake, juice, meat, soup, fork, knife, oven, spoon}.

```text
S  → NP VP              PP  → P NP              V   → cooks | drinks | eats | cuts
VP → VP PP | V NP       NP  → Det N | he | she  P   → in | with
VP → cooks | drinks | eats | cuts               Det → a | the
N  → cat | dog | beer | cake | juice | meat | soup | fork | knife | oven | spoon
```

8 variables, 21 terminales y 30 alternativas (5 binarias, 25 léxicas). G ya está en CNF.
Está definida una sola vez en `recognizer/grammar.py` y la usan ambos reconocedores; las pruebas
comparan esa definición con el enunciado. **Entrada:** cada palabra separada por espacios en blanco
es un token y n es la cantidad de palabras. No se cambian mayúsculas ni puntuación: `He cooks` y
`he cooks.` se rechazan. La cadena vacía se rechaza porque G no deriva ε.

## 3. PDA a partir de G (aporte de David; detalle en `docs/pda.md`)

### 3.1 Extensión del autómata del proyecto 1

El modelo AFN del proyecto 1 se reutiliza sin cambios en `recognizer/proyecto1/` (commit `750243e`
de `primer-proyecto-tdc`). `AutomataPila` en `recognizer/automata.py` **hereda** de esa clase y
agrega alfabeto de pila Γ, símbolo de fondo Z0 y transiciones `(estado, lectura|ε, cima) →
{(destino, secuencia_a_apilar)}`. La pila es una tupla con la cima en el índice 0; reemplazar la cima
por `()` desapila. EPSILON se toma del proyecto 1.

### 3.2 Definición formal

P = (Q, Σ, Γ, δ, q0, Z0, F) con Q = {q0, q1, q2}, Γ = V ∪ Σ ∪ {Z0}, F = {q2} y:

1. δ(q0, ε, Z0) = {(q1, S Z0)} — inicialización.
2. Para cada A → α en P: (q1, α) ∈ δ(q1, ε, A) — expansión de variables.
3. Para cada a ∈ Σ: δ(q1, a, a) = {(q1, ε)} — coincidencia de terminales.
4. δ(q1, ε, Z0) = {(q2, Z0)} — finalización.

Acepta por estado final con toda la entrada consumida. Invariante: en q1, si se leyó el prefijo u y
la pila contiene β Z0, entonces S ⇒* uβ por una derivación izquierda; por ello L(P) = L(G)
(Hopcroft, Motwani y Ullman, sección 6.3.1; Sipser, sección 2.2).

### 3.3 Simulación y evidencia

`recognizer/pda.py` ejecuta cualquier `AutomataPila` con búsqueda en anchura (BFS) sobre
configuraciones (estado, posición, pila completa) y un conjunto de visitadas. Como G no tiene reglas
vacías, cada símbolo sobre el fondo debe consumir al menos una palabra; una configuración con más
símbolos pendientes que palabras restantes se poda con seguridad. Esto garantiza terminación a pesar
de la recursión izquierda VP → VP PP. La evidencia contiene todas las configuraciones exploradas
con su padre y transición, el recorrido aceptante validado o la causa del agotamiento.

```text
(q0, he cooks, Z0) ⊢ (q1, he cooks, S Z0) ⊢ (q1, he cooks, NP VP Z0) ⊢ (q1, he cooks, he VP Z0)
⊢ (q1, cooks, VP Z0) ⊢ (q1, cooks, cooks Z0) ⊢ (q1, ε, Z0) ⊢ (q2, ε, Z0)
```

## 4. Algoritmo CYK (aporte de Carlos; detalle en `docs/cyk.md`)

T[i, l] es el conjunto de variables que derivan las l palabras desde la posición i. La base usa las
reglas léxicas; para l = 2..n, cada corte c combina T[i, c] y T[i+c, l−c] con las reglas A → B C.
Se acepta si S ∈ T[0, n]. Cada variable guarda su primer testigo (producción, corte), con lo cual se
reconstruye un árbol y la derivación izquierda. Ejemplo `she drinks a beer`:

```text
l=4 | S
l=3 | ∅       VP
l=2 | S       ∅       NP
l=1 | NP      V,VP    Det     N
      she     drinks  a       beer
```

S ⇒ NP VP ⇒ she VP ⇒ she V NP ⇒ she drinks NP ⇒ she drinks Det N ⇒ she drinks a N ⇒ she drinks a beer.
En un rechazo (`he eats cake`) la tabla completa muestra que S no está en la celda final.

## 5. Ejecución

Python ≥ 3.10, solo biblioteca estándar. Desde la raíz del repositorio:

```powershell
python main.py "she drinks a beer" --traza                 # PDA y CYK, con pasos
python main.py "he eats cake" --metodo cyk --traza         # solo CYK
python main.py "he cooks" --json salidas/resultado.json    # evidencia completa en JSON
python -m unittest discover -s tests -v                    # todas las pruebas
python scripts/benchmark.py                                # regenera docs/operaciones.csv
```

Códigos de salida: 0 aceptada, 1 rechazada, 2 inconclusa, error o discrepancia entre métodos.

## 6. Tasas de crecimiento

### 6.1 CYK: Θ(n³)

Con R_bin = 5 y R_lex = 25 reglas, los bucles recorren todas las celdas, cortes y reglas sin salidas
tempranas:

| Operación | Conteo exacto |
| --- | --- |
| Celdas | n(n+1)/2 |
| Consultas léxicas | 25n |
| Cortes | Σ_{l=2..n} (n−l+1)(l−1) = (n³ − n)/6 |
| Comprobaciones de reglas binarias | 5(n³ − n)/6 |

T(n) = 5(n³ − n)/6 + 25n + n(n+1)/2 ∈ **Θ(n³)**, ajustada y igual para toda entrada de longitud n.
Para gramática variable: Θ(n³·|R_bin| + n·|R_lex|). Memoria: Θ(n²) celdas con testigos.

### 6.2 PDA: cota exponencial en general, polinomial en G

Operación dominante elegida por David: símbolos de pila copiados al construir cada sucesor.
Para una CFG fija sin ε con poda, el número de configuraciones está acotado por O(n·g^(n+1)), con
g = |Γ|, de donde se obtiene una cota superior exponencial O(n²·g^(n+1)). Para **G** toda pila
alcanzable tiene la forma β PP^k Z0, con β en un conjunto finito y 0 ≤ k ≤ n; hay O(n) pilas y
O(n²) configuraciones. Cotas superiores para G: **O(n²) transiciones evaluadas** y **O(n³) símbolos
copiados** (y memoria O(n³), porque se guardan las pilas completas como evidencia).
Verificar un recorrido aceptante dado requiere 3n + 1 pasos; el costo está en **buscarlo**.

## 7. Experimentos reproducibles

`scripts/benchmark.py` ejecuta ambos métodos sin límite de búsqueda y escribe `docs/operaciones.csv`
(40 filas, determinista; no mide tiempos). Familias, con F_k = `she eats the cake` + k veces
` with a fork` (n = 3k + 4):

| Familia | Frase | k | Decisión |
| --- | --- | --- | --- |
| F | F_k | 0..15 | aceptada |
| R | F_k + ` with` (PP incompleto) | 0..15 | rechazada |
| E | `cooks ` + F_k (orden inválido desde el inicio) | 0, 5, 10, 15 | rechazada |
| D | F_k + ` dances` (palabra fuera de Σ) | 0, 5, 10, 15 | rechazada |

Columnas: `pda_*` son los contadores de `docs/pda.md`; `cyk_*` los de `docs/cyk.md`;
`pda_causa` indica `frontera_agotada` o `fuera_del_alfabeto`; `pda_limite` vacío significa que no
hubo límite y, por tanto, ningún resultado es inconcluso. `coinciden` es `True` en las 40 filas.

| n | PDA transiciones | PDA copias de pila | CYK comprobaciones | CYK variables agregadas |
| --- | --- | --- | --- | --- |
| 4 (F_0) | 66 | 304 | 50 | 9 |
| 7 (F_1) | 196 | 1 323 | 280 | 16 |
| 19 (F_5) | 1 376 | 20 729 | 5 700 | 44 |
| 34 (F_10) | 4 336 | 109 179 | 32 725 | 79 |
| 49 (F_15) | 8 946 | 315 154 | 98 000 | 114 |
| 50 (R_15) | 9 310 | 334 274 | 104 125 | 115 |
| 50 (E_15) | 7 | 37 | 104 125 | 117 |
| 50 (D_15) | 0 | 0 | 104 125 | 114 |

En las 16 filas de F, los conteos coinciden exactamente con estos polinomios (y análogos en R):

- PDA, transiciones evaluadas: (11/3)n² + 3n − 14/3.
- PDA, símbolos copiados: (22/9)n³ + (71/6)n² − (107/6)n + 266/9.
- CYK, comprobaciones binarias: (5/6)(n³ − n), igual que la fórmula analítica.

## 8. Discusión de desempeños

**Lo que dice el análisis.** CYK es Θ(n³) para cualquier gramática CNF fija y cualquier entrada:
su costo es el de llenar la tabla, no el de la frase. El PDA no determinista simulado por búsqueda
no tiene, en general, una cota polinomial: para una CFG arbitraria la cota superior es exponencial,
y sin visitados ni poda la recursión izquierda lo haría no terminar. En G, la forma restringida de
las pilas reduce el espacio de configuraciones a O(n²); por eso el PDA resulta polinomial aquí.
Esa es una propiedad de G, no del método.

**Lo que muestran los datos.** Medido en «decisiones» (transiciones del PDA frente a comprobaciones
de reglas de CYK), el PDA crece como n² y CYK como n³: el PDA hace más trabajo con n = 4
(66 frente a 50) y menos desde n = 7 (196 frente a 280); con n = 49, 8 946 frente a 98 000.
Medido en el trabajo real de la representación del PDA, cada transición copia y compara una pila de
longitud O(n), y los símbolos copiados crecen como (22/9)n³, unas 2,9 veces las comprobaciones de
CYK para n grande. **Las unidades no son equivalentes**: una comprobación de CYK son dos consultas a
diccionarios; una transición del PDA construye, hashea y registra una tupla. Ninguna de las dos
métricas por sí sola decide cuál programa es «más rápido».

**Aceptación y rechazo.** CYK hace exactamente el mismo trabajo para todas las frases de igual n
(filas F, R, E y D con n = 50: 104 125 comprobaciones). El PDA depende de la entrada: rechaza
`cooks she eats…` tras 7 transiciones porque ninguna expansión de S puede empezar con `cooks`, y
rechaza palabras fuera de Σ antes de explorar (0 operaciones). En cambio, un rechazo tardío (familia
R) cuesta prácticamente lo mismo que una aceptación de igual longitud: el polinomio de F evaluado en
n = 50 da 9 312 transiciones y R_15 usa 9 310. BFS agota la frontera al rechazar, y al aceptar llega
a la configuración final cuando ya exploró casi todo el espacio alcanzable.

**Recursión izquierda.** VP → VP PP obliga al PDA descendente a usar visitados y poda por longitud
para terminar; CYK, ascendente, no se ve afectado porque cada celda combina segmentos más cortos.

**Reutilización de subproblemas.** CYK calcula cada segmento una sola vez (programación dinámica).
El PDA no reutiliza el análisis de un segmento: el mismo NP puede analizarse de nuevo con distintos
sufijos PP^k en la pila, porque las configuraciones difieren. En los datos `repetidas = 0`: no hay
configuraciones idénticas que aprovechar. A la vez, la tabla de CYK es muy dispersa en G
(7n/3 variables agregadas en total frente a n(n+1)/2 celdas): CYK paga por subproblemas que
casi nunca producen algo.

**Memoria.** CYK: Θ(n²) celdas. PDA: O(n²) configuraciones con pilas de longitud O(n), O(n³)
símbolos guardados como evidencia en G, y exponencial en el peor caso general.

**Límites de esta evidencia.** Los experimentos usan familias concretas con n ≤ 50. Que los
conteos coincidan con polinomios en 16 puntos respalda las cotas, pero no las demuestra: la
demostración es el análisis de las secciones 6.1 y 6.2. Los conteos no miden constantes de Python
ni de la máquina, y no se usaron tiempos de reloj. No puede concluirse que un método sea siempre
mejor: para G y frases largas el PDA hace menos transiciones, pero CYK ofrece una garantía Θ(n³)
para cualquier gramática CNF, que la búsqueda en el PDA no tiene.

## 9. Validación

`python -m unittest discover -s tests -v`: pruebas de gramática, modelo de autómata, PDA, CYK,
consola e integración. CYK se comprueba con tablas calculadas a mano (`he cooks`,
`she drinks a beer`), conteos cerrados, árboles cuyas hojas son exactamente los tokens y cuyas
producciones pertenecen a G, derivaciones izquierdas válidas y una gramática CNF distinta (aⁿbⁿ).
La validación cruzada compara las decisiones del PDA y CYK en todas las cadenas de longitud ≤ 5
sobre {he, cooks, eats, with, the, cat} (9 331 cadenas) y en 60 frases generadas de G con semilla
fija junto con versiones perturbadas. Es evidencia acotada a esas longitudes y alfabeto.

## 10. Referencias

- Hopcroft, J., Motwani, R. y Ullman, J. *Introduction to Automata Theory, Languages, and
  Computation*, 3.ª ed. Secciones 6.3.1 (de CFG a PDA) y 7.4.4 (pertenencia a un CFL, CYK).
- Sipser, M. *Introduction to the Theory of Computation*, 3.ª ed. Sección 2.2 (CFG ⇒ PDA) y
  sección 7.2 (todo CFL está en P mediante programación dinámica).
- [CYK algorithm](https://en.wikipedia.org/wiki/CYK_algorithm), enlazado en el enunciado.
- Documentación del proyecto: `docs/acuerdos.md`, `docs/pda.md`, `docs/cyk.md`, `docs/operaciones.csv`.
