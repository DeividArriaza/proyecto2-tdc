# PDA de David: modelo, construcción, búsqueda y conteos

## Origen y representación

`recognizer/proyecto1/{models,constants,errors}.py` procede de
`primer-proyecto-tdc/src/automatas/`, commit `750243e`. Solo se agregan dos comentarios de procedencia
y se sustituyen imports `automatas.x` por `.x`. La prueba de vendorizado compara el resto completo
con el original; si ese repositorio no está disponible, omite únicamente esa prueba.
`AutomataPila` **hereda AFN** como dataclass frozen+slots y reutiliza estados, alfabeto, inicial,
aceptación y sus validaciones. Las transiciones AFN deben quedar vacías; toda ejecución usa
`transiciones_pila`. Se añaden alfabeto de pila, fondo, transiciones con pila y validaciones propias.
Alfabetos, destinos y reglas se congelan; los mappings se copian a `MappingProxyType`.

Pila como tupla con cima en índice 0. Una transición reemplaza la cima por `apilar`, en orden:
`nueva_pila = apilar + pila[1:]`. `()` desapila. EPSILON es `"ε"` del proyecto 1, nunca un terminal.

## Definición formal y equivalencia

Para CFG H=(V,Σ,S,R), construir P=(Q,Σ,Γ,δ,q0,Z0,F), donde Q={q0,q1,q2}, F={q2},
Γ=V ∪ Σ ∪ {Z0}. Si Z0 ya es un símbolo de H, se agregan guiones bajos hasta evitar la colisión.
En el código q0=0, q1=1, q2=2. Para G, V y Σ son los de `grammar.py` (8 y 21 símbolos).

1. δ(q0,ε,Z0) = {(q1,S Z0)}.
2. Para toda A → α de R, (q1,α) ∈ δ(q1,ε,A).
3. Para todo a ∈ Σ, δ(q1,a,a) = {(q1,ε)}.
4. δ(q1,ε,Z0) = {(q2,Z0)}.

Aceptación por estado final **y entrada consumida**. En esta construcción solo queda Z0 al llegar a q2;
el fondo se conserva. Quitar el fondo en el último paso daría la variante por pila vacía equivalente.
Un PDA externo puede aceptar por estado final con pila no vacía: el simulador respeta esa definición.

Invariante: en q1, si se consumió el prefijo u y queda β encima de Z0, existe una derivación
izquierda S ⇒* uβ. Inicialización establece S; expandir la variable superior aplica la siguiente
producción izquierda; consumir un terminal lo traslada de β al prefijo u. Una pila que empieza por
terminal solo permite consumir ese terminal. Si P acepta w, β está vacío y S ⇒* w, así L(P) ⊆ L(H).
Recíprocamente, seguir cualquier derivación izquierda de w con expansiones y coincidencias consume
w y deja solo Z0, habilitando q2: L(H) ⊆ L(P). Esto también cubre reglas unitarias y vacías.

La construcción corresponde a Hopcroft, Motwani y Ullman, *Introduction to Automata Theory,
Languages, and Computation*, 3.ª ed., sección 6.3.1 (conversión CFG a PDA). Se cita la sección por
tema sin atribuir un número de teorema no comprobado. También Sipser, *Introduction to the Theory
of Computation*, 3.ª ed., sección 2.2, Lema 2.21 (CFG implica PDA). El lema y su construcción pueden
consultarse en estas [notas universitarias de equivalencia](https://www3.cs.stonybrook.edu/~cse350/slides/pda2.pdf).
El [programa universitario CS208](https://www.cse.iitb.ac.in/~supratik/courses/cs208/) ubica la construcción
en HMU 6.3.1. La prueba del invariante anterior es el argumento específico de esta implementación.

## Traza manual completa de `he cooks`

| Paso | Descripción instantánea | Transición desde la fila anterior |
| --- | --- | --- |
| 0 | (q0, he cooks, Z0) | Inicio |
| 1 | (q1, he cooks, S Z0) | (q0, ε, Z0) → (q1, S Z0) |
| 2 | (q1, he cooks, NP VP Z0) | (q1, ε, S) → (q1, NP VP) |
| 3 | (q1, he cooks, he VP Z0) | (q1, ε, NP) → (q1, he) |
| 4 | (q1, cooks, VP Z0) | (q1, he, he) → (q1, ε) |
| 5 | (q1, cooks, cooks Z0) | (q1, ε, VP) → (q1, cooks) |
| 6 | (q1, ε, Z0) | (q1, cooks, cooks) → (q1, ε) |
| 7 | (q2, ε, Z0) | (q1, ε, Z0) → (q2, Z0) |

Cada par consecutivo se relaciona por ⊢. El simulador reconstruye esta ruta mediante padres;
`validar_recorrido` comprueba configuración inicial, continuidad, transición real, lectura,
reemplazo exacto de cima y estado final con consumo total. Una ruta inventada o incompleta falla.

## BFS, seguridad de poda y terminación

BFS usa `deque` y un conjunto de visitados por **(estado, posición, pila completa)**. Destinos se
ordenan para hacer reproducible el recorrido. BFS encuentra un recorrido de mínimo número de pasos;
evita que una rama izquierda infinita impida alcanzar una aceptación de profundidad finita.
Esto consume más memoria que DFS; guardar los padres y todas las configuraciones es parte de la evidencia.
No hay reglas de G en el bucle del simulador; funciona también con un PDA manual para aⁿbⁿ, n ≥ 1.

La construcción certifica la poda solo si no existe producción vacía. En ese caso ninguna variable
puede derivar ε, ni por reglas unitarias: para borrar el último símbolo sería necesaria una regla vacía.
Cada símbolo sobre el fondo necesita consumir al menos un terminal para desaparecer en una aceptación.
Si h=len(pila)-1 > n-pos, no quedan suficientes palabras: esa configuración no puede aceptar.
Descartarla es seguro. Variables improductivas tampoco pueden pertenecer a un recorrido aceptante.
Con h <= n-pos hay longitud de pila a lo sumo n+1, estados y alfabeto finitos y n+1 posiciones;
por ello hay finitas configuraciones admitidas. Visitados y ramificación finita garantizan terminación.

Un PDA externo no lleva certificado; activar explícitamente la poda en él da `ValueError`. La poda
no se transfiere solo porque un PDA tenga la misma forma de campos. Las CFG con producciones vacías
se construyen normalmente y se ejecutan sin esta poda. Sin poda, la búsqueda puede ser infinita:
el límite opcional de expansiones devuelve **inconclusa**, nunca rechazo por agotar recursos.
`poda_longitud=False` permite contrastar ejecuciones cortas aceptantes sin poda.

Para `he eats cake`, la frontera sí se agota: 29 configuraciones expandidas, 4 podas, 0 repetidas,
0 pendientes. La causa registrada es `frontera_agotada`. Con `he cooks --limite 1` hay 1 expansión
y frontera pendiente: `limite_alcanzado`, inconclusa. Palabras desconocidas se rechazan antes del BFS.

## Operaciones y complejidad de la implementación real

| Contador | Operación contada |
| --- | --- |
| configuraciones_generadas | Configuración inicial más cada sucesor, aun podado/repetido |
| configuraciones_expandidas | Configuraciones retiradas de la frontera para buscar sucesores |
| consultas_transiciones | Consultas a δ para ε y, si queda entrada, para el siguiente token |
| transiciones_evaluadas | Cada alternativa devuelta por esas consultas; genera un candidato |
| simbolos_copiados_pila | 1 inicial; por candidato, (len(pila)-1)+len(nueva_pila) |
| podas | Sucesores eliminados por la desigualdad de longitud |
| repetidas | Sucesores no podados ya presentes en visitados |

`simbolos_copiados_pila` cuenta referencias de símbolos copiadas por el corte de la cola y la
concatenación. Es la operación dominante elegida: construir y hashear pilas completas, compararlas
y convertirlas en listas para evidencia cuesta hasta O(n) por sucesor con la poda. El contador no
pretende contar instrucciones de Python ni todas las copias de evidencia; sí mide el crecimiento
del trabajo con la representación real. La aceptación se detecta al frente de la cola sin expandir
esa configuración. Se cumple generadas = 1 + transiciones_evaluadas = admitidas + podas + repetidas.

**CFG fija general sin ε, con poda:** sea g=|Γ| y b el máximo de alternativas de una consulta,
constantes de la gramática. Hay a lo sumo
`C <= |Q| (n+1) sum(h=0..n+1) g^h = O(n g^(n+1))` configuraciones.
Hasta O(bC) sucesores, O(n) trabajo por pila: tiempo superior O(n² g^(n+1)) y memoria superior
O(n² g^(n+1)) incluyendo configuraciones, visitados y evidencia. Son cotas exponenciales superiores,
no afirmaciones ajustadas. Sin visitados, un árbol de búsqueda de profundidad O(n) y ramificación
b>1 puede tener b^O(n) nodos en CNF; no se debe confundir verificar una rama con buscarla.
En CFG arbitrarias con ciclos unitarios/ε sin poda no hay cota finita de terminación para este BFS.
Los costos de construir/indexar la gramática se consideran constantes; cambiarla exige incluirlos.
Se usa el modelo habitual de consultas hash amortizadas; colisiones adversarias no son este análisis.

**G concreta, cota más fina:** la única recursión es VP → VP PP. Después de procesar el sujeto,
toda pila alcanzable tiene la forma `β PP^k Z0`, donde β pertenece a un conjunto **finito constante**:
VP; V NP; verbo NP; verbo; NP; Det N; determinante N; N; sustantivo; P NP; preposición NP; pronombre;
o vacío (incluyendo las etapas internas de un PP). Antes de procesar el sujeto solo existen
las formas de inicialización y un prefijo de NP seguido por VP Z0, también un conjunto constante.
Estas formas se conservan al expandir o leer la cima. Por la poda 0 <= k <= n; entonces solo hay
O(n) pilas distintas y O(n²) configuraciones considerando las posiciones. Cada una tiene O(1)
sucesores: O(n²) transiciones/candidatos, O(n³) tiempo por copias/hash de tuplas y O(n³) memoria por
guardar pilas completas y listas de evidencia. Son cotas **superiores**, no tasas Θ demostradas.
Los conteos de abajo son compatibles con ellas; no prueban cotas asintóticas por sí solos.

**Verificar un recorrido frente a buscarlo:** una derivación CNF de n>0 palabras tiene n reglas
léxicas y n-1 binarias. Este PDA hace 2n-1 expansiones, n lecturas y 2 pasos administrativos:
exactamente 3n+1 pasos, O(n) para gramática fija. Comprobar localmente una transición es constante
en G. Sin embargo, `validar_recorrido` también revisa las pilas explícitas antes/después y copia
tuplas/listas: su costo real es O(suma de longitudes de pila), a lo sumo O(n²), con O(n) memoria
auxiliar, además del recorrido dado. Almacenarlo/exportarlo también puede ocupar O(n²).
Una verificación compacta sin pilas completas podría ser lineal; no se atribuye ese costo al código actual.

## Conteos reproducibles (sin tiempos)

Ejecutar `python scripts/conteos_pda.py`; CSV a stdout, sin límite de búsqueda. Acepta o rechaza
concluyentemente todas las filas. En la tabla Fk significa `she eats the cake` seguido de k veces
` with a fork`; Rk es Fk seguido de ` with`. Las frases completas están en el CSV que imprime el script.

| Frase | n | Estado | Generadas | Expandidas | Transiciones | Copias pila | Podas | Repetidas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| he cooks | 2 | aceptada | 15 | 11 | 14 | 50 | 3 | 0 |
| F0 | 4 | aceptada | 67 | 62 | 66 | 304 | 4 | 0 |
| F1 | 7 | aceptada | 197 | 190 | 196 | 1323 | 6 | 0 |
| R1 | 8 | rechazada | 253 | 246 | 252 | 1893 | 7 | 0 |
| F2 | 10 | aceptada | 393 | 384 | 392 | 3479 | 8 | 0 |
| R2 | 11 | rechazada | 471 | 462 | 470 | 4516 | 9 | 0 |
| F3 | 13 | aceptada | 655 | 644 | 654 | 7168 | 10 | 0 |
| R3 | 14 | rechazada | 755 | 744 | 754 | 8804 | 11 | 0 |

Los CSV incluyen además consultas de transiciones. No se comparan con operaciones CYK todavía;
esa comparación, los experimentos conjuntos y el PDF corresponden a Carlos.

## Validación y límites

Las pruebas cubren las frases del README, varios PP, política de entrada, modelo original,
construcción genérica (incluidas reglas vacías/unitarias), PDA externo y transiciones de evidencia.
Una enumeración independiente de derivaciones izquierdas de longitud <=4 prueba todas las frases
derivadas y contrasta aceptación/rechazo de todos los candidatos de un alfabeto reducido hasta
esa longitud. También contrasta BFS con/sin poda en aceptaciones cortas donde ambos terminan.
Esto respalda la implementación; la seguridad general de la poda depende del argumento anterior.
La revisión humana de Carlos, la comparación real con CYK y los entregables conjuntos siguen pendientes.
