# CYK de Carlos: diseño, evidencia y conteos

## Por qué G es apta para CYK

CYK decide pertenencia para gramáticas en Forma Normal de Chomsky (CNF): toda regla es A → B C
(dos variables) o A → a (un terminal). `es_cnf(G)` lo comprueba en `recognizer/grammar.py`:
G tiene 5 reglas binarias y 25 léxicas (30 alternativas), sin reglas vacías ni unitarias A → B.
Por eso se usa G tal como está en el enunciado, sin transformarla. Como G no tiene S → ε,
la cadena vacía no pertenece a L(G). `recognize` lanza `ValueError` si recibe una gramática fuera de CNF.

| Binarias (R_bin = 5) | Léxicas (R_lex = 25) |
| --- | --- |
| S → NP VP | VP → cooks \| drinks \| eats \| cuts |
| VP → VP PP | V → cooks \| drinks \| eats \| cuts |
| VP → V NP | NP → he \| she |
| PP → P NP | P → in \| with |
| NP → Det N | Det → a \| the; N → 11 sustantivos |

Una palabra puede tener varias categorías: `cooks` produce {V, VP}. CYK las conserva todas en la celda.

## Diseño (C1)

**Índices.** Tokens `w_0 … w_(n-1)` según `tokenizar` (D2). La celda `T[i, l]` (inicio i,
longitud l, ambos desde 0 y 1) es el conjunto de variables A tales que A ⇒* w_i … w_(i+l-1).
Existen las celdas 0 ≤ i < n y 1 ≤ l ≤ n − i: n(n+1)/2 en total. La celda final es `T[0, n]`.

**Base léxica.** `T[i, 1] = {A | A → w_i ∈ R}`.

**Recurrencia.** Para l ≥ 2, un corte c (1 ≤ c < l) divide el segmento en una parte izquierda de
longitud c y una derecha de longitud l − c:
`T[i, l] = {A | A → B C ∈ R, ∃c: B ∈ T[i, c] y C ∈ T[i+c, l−c]}`.

**Aceptación.** w ∈ L(G) si y solo si n > 0 y S ∈ T[0, n]. Con n = 0 no hay celdas: rechazo explícito.
Las palabras fuera de Σ dejan su celda léxica vacía; la tabla se calcula igual y S no puede
aparecer en ninguna celda que cubra esa palabra. Se informan en `palabras_desconocidas`.

**Testigos.** Cada variable de una celda guarda el *primer* par (producción, corte) que la produjo
(corte `None` en reglas léxicas). Los bucles recorren longitudes, inicios, cortes y reglas en orden
fijo (reglas ordenadas), así que los testigos son reproducibles. Como los hijos de un testigo
binario cubren segmentos estrictamente más cortos, reconstruir el árbol desde `S ∈ T[0, n]` termina.

```text
CYK(w_0..w_(n-1), G):
    T ← diccionario vacío
    para i en 0..n-1:                                   # base léxica
        T[i,1] ← {}
        para cada A → a en R_lex (orden fijo):
            si a = w_i: agregar A a T[i,1] con testigo (a, None)
    para l en 2..n:                                     # longitudes crecientes
        para i en 0..n-l:
            T[i,l] ← {}
            para c en 1..l-1:                           # cortes
                para cada A → B C en R_bin (orden fijo):
                    si B ∈ T[i,c] y C ∈ T[i+c,l-c]:
                        agregar A a T[i,l] con testigo (B C, c) si aún no está
    aceptar ⇔ n > 0 y S ∈ T[0,n]
```

El bucle interno recorre las reglas binarias, como en la presentación clásica del algoritmo; no
usa un índice inverso (B, C) → A. Esa elección hace que el conteo dependa solo de n (ver C5).

## Implementación y API (C2)

`recognizer/cyk.py` expone `recognize(tokens, *, gramatica=G) -> Resultado` (contrato D1) y no
importa el PDA ni el modelo de autómata (lo comprueba `test_no_depende_del_pda`). La consola lo
llama como `cyk.recognize(tokens)`. El parámetro `gramatica` sirve para probar con otra gramática
CNF (aⁿbⁿ en las pruebas) y demostrar que no hay reglas de G codificadas en el algoritmo.

## Evidencia serializable (C3)

`Resultado.evidencia` contiene solo valores JSON:

| Campo | Contenido |
| --- | --- |
| `tabla` | Todas las celdas en orden de cálculo `{inicio, longitud, variables}`, incluidas las vacías |
| `testigos` | `{inicio, longitud, variable, produccion, corte}` por cada variable de cada celda |
| `celda_final` | `{inicio: 0, longitud: n, variables}`; `null` si n = 0 |
| `arbol` | Nodo `{variable, produccion, hijos}`, hojas `{terminal, posicion}`; `null` al rechazar |
| `derivacion` | Formas sentenciales de la derivación izquierda del árbol; `[]` al rechazar |
| `palabras_desconocidas` | Tokens distintos fuera de Σ, ordenados |

`python main.py "frase" --metodo cyk --traza` imprime `tabla`; `--json RUTA` exporta todo.

### Ejemplo aceptado: `he cooks` (n = 2)

| Celda | Cálculo | Variables |
| --- | --- | --- |
| T[0,1] | he: NP → he | {NP} |
| T[1,1] | cooks: V → cooks, VP → cooks | {V, VP} |
| T[0,2] | c=1: NP × {V, VP}; S → NP VP | {S} |

S ∈ T[0,2] ⇒ aceptada. Árbol: S(NP(he), VP(cooks)). Derivación: S ⇒ NP VP ⇒ he VP ⇒ he cooks.

### Ejemplo aceptado: `she drinks a beer` (n = 4)

```text
l=4 | S
l=3 | ∅       VP
l=2 | S       ∅       NP
l=1 | NP      V,VP    Det     N
      she     drinks  a       beer
```

T[1,3] obtiene VP con c=1: V ∈ T[1,1] y NP ∈ T[2,2] (VP → V NP). T[0,4] obtiene S con c=1:
NP ∈ T[0,1] y VP ∈ T[1,3]. Los cortes c=2 (S × NP) y c=3 (∅ × N) no aportan nada.
Derivación: S ⇒ NP VP ⇒ she VP ⇒ she V NP ⇒ she drinks NP ⇒ she drinks Det N ⇒ she drinks a N ⇒ she drinks a beer.

Una derivación de n palabras en CNF usa n − 1 reglas binarias y n léxicas: 2n − 1 pasos y 2n formas.

### Ejemplo rechazado: `he eats cake` (n = 3)

```text
l=3 | ∅
l=2 | S       ∅
l=1 | NP      V,VP    N
      he      eats    cake
```

`cake` solo es N; VP → V NP necesita NP y NP → Det N exige determinante. T[0,3] = ∅, así que S no
aparece en la celda final: rechazada, `arbol = null`, `derivacion = []`. La tabla completa es la
evidencia del rechazo: cada celda vacía puede verificarse revisando sus cortes.

**Entrada vacía.** `tabla = []`, `celda_final = null`, todos los contadores en 0, rechazada.
**Palabra desconocida** (`he dances`): T[1,1] = ∅, motivo con «fuera del alfabeto: dances».

## Operaciones y complejidad (C5)

| Contador | Operación contada | Valor exacto para G |
| --- | --- | --- |
| `celdas` | Celdas creadas | n(n+1)/2 |
| `consultas_lexicas` | Comparaciones token vs regla léxica | R_lex · n = 25n |
| `cortes` | Pares (celda, corte) examinados | (n³ − n)/6 |
| `comprobaciones_binarias` | Reglas A → B C comprobadas en un corte (dominante) | R_bin · (n³ − n)/6 = 5(n³ − n)/6 |
| `reglas_satisfechas` | Comprobaciones léxicas o binarias que se cumplen | depende de la frase |
| `variables_agregadas` | Variables nuevas en alguna celda (= testigos) | depende de la frase |

**Cortes.** Para longitud l hay n − l + 1 inicios y l − 1 cortes. Con j = l − 1:

`Σ_{l=2..n} (n−l+1)(l−1) = Σ_{j=0..n−1} (n−j)·j = n·n(n−1)/2 − (n−1)n(2n−1)/6 = n(n−1)(n+1)/6 = (n³−n)/6`.

**Total.** `T(n) = 5(n³ − n)/6 + 25n + n(n+1)/2`, es decir, **T(n) ∈ Θ(n³)**. La cota es ajustada:
los bucles no tienen salidas tempranas ni dependen del contenido de las celdas, por lo que el mejor,
el peor y el caso promedio coinciden para cada n. Cada comprobación hace dos pruebas de pertenencia
en diccionarios (O(1) esperado) y, si se cumple, una inserción O(1).

Verificación manual: `he cooks` (n=2): 3 celdas, 50 consultas léxicas, 1 corte, 5 comprobaciones.
`she drinks a beer` (n=4): 10 celdas, 100 léxicas, 10 cortes, 50 comprobaciones. Lo comprueban
`test_tabla_manual_he_cooks` y `test_conteos_cerrados_y_tabla_completa` para varias longitudes.

**Gramática variable.** Con esta estructura de bucles el costo es Θ(n³·|R_bin| + n·|R_lex|).
La alternativa de recorrer pares B ∈ T[i,c], C ∈ T[i+c,l−c] con un índice inverso cuesta
O(n³·|V|²) en el peor caso, pero en tablas dispersas como las de G haría menos comprobaciones.
Para G, |R|, |V| son constantes y ambas versiones son Θ(n³) en el peor caso.

**Memoria.** La tabla tiene exactamente n(n+1)/2 celdas, cada una con a lo sumo |V| = 8 variables
y sus testigos: Θ(n²). El árbol tiene 2n − 1 nodos internos y n hojas: Θ(n). La derivación tiene
2n formas de longitud ≤ n: O(n²) símbolos. Exportar la evidencia es, por tanto, O(n²).
Reconstruir árbol y derivación no se suma a los contadores: son Θ(n) y O(n²) operaciones,
dominadas por el llenado Θ(n³).

**Observación sobre G.** En las frases de `docs/operaciones.csv`, `variables_agregadas` crece
linealmente (7k + 9 en la familia F): la tabla es muy dispersa porque G es casi determinista.
Aun así CYK examina todas las celdas y cortes; esa es la razón del Θ(n³) aunque haya pocos hechos útiles.

**Fuentes.** Hopcroft, Motwani y Ullman, *Introduction to Automata Theory, Languages, and
Computation*, 3.ª ed., sección 7.4.4 (prueba de pertenencia a un CFL, algoritmo CYK, O(n³)).
Sipser, *Introduction to the Theory of Computation*, 3.ª ed., sección 7.2: demostración, por
programación dinámica, de que todo lenguaje libre de contexto está en P. Artículo enlazado en el
enunciado: [CYK algorithm](https://en.wikipedia.org/wiki/CYK_algorithm). Se citan por tema;
el conteo exacto anterior corresponde a esta implementación.
