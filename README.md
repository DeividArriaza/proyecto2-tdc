# Proyecto 2 — Teoría de la Computación

Plan completo para desarrollar desde cero el proyecto solicitado en [Proyecto 2 2026.pdf](<Proyecto 2 2026.pdf>), trabajando entre **David Lopez y Carlos Lopez**.

**Estado actual:** solo están el enunciado y este plan; las implementaciones, pruebas y entregables están pendientes. Las rutas indicadas son propuestas de archivos por crear. Los comandos se podrán ejecutar cuando existan los módulos correspondientes.

## Objetivo y alcance

Construir dos reconocedores para la gramática G del enunciado: uno que ejecute un autómata de pila (PDA) y otro que utilice CYK. Ambos deben recibir una cadena y mostrar evidencia de los pasos del reconocimiento. Además, deben analizarse sus tasas de crecimiento mediante conteo de operaciones, compararse sus desempeños y entregarse documentación PDF, repositorio privado y video no listado de máximo 10 minutos.

La gramática ya está en CNF según el enunciado. No se necesita implementar un lector de gramáticas, convertirla a CNF, dibujar un diagrama ni construir una interfaz gráfica. Puede representarse G directamente en código. Debe respetarse el requisito de extender el autómata del proyecto 1.

## Distribución entre las dos personas

Se desglosa el trabajo en **20 tareas**, diez por persona. David desarrolla el PDA, la consola y prepara el repositorio. Carlos desarrolla CYK, integra y verifica los métodos y prepara la comparación y documentación. Cada persona analiza y documenta su algoritmo, prepara sus pruebas y explica su parte en el video.

La numeración identifica tareas; el orden de ejecución depende de la columna de dependencias. Las tareas de Carlos pueden avanzar mientras David desarrolla el PDA.

| ID | Responsable | Tarea | Depende de | Estado |
| --- | --- | --- | --- | --- |
| D1 | David Lopez | Preparar estructura y acordar contratos | Acuerdo con Carlos | Hecho (pendiente revisión de Carlos) |
| D2 | David Lopez | Representar y verificar la gramática | D1 | Hecho (pendiente revisión de Carlos) |
| D3 | David Lopez | Recuperar y extender el autómata del proyecto 1 | D1 y código del proyecto 1 | Hecho (pendiente revisión de Carlos) |
| D4 | David Lopez | Definir formalmente el PDA equivalente a G | D2, D3 | Hecho (pendiente revisión de Carlos) |
| D5 | David Lopez | Implementar la simulación del PDA | D4 | Hecho (pendiente revisión de Carlos) |
| D6 | David Lopez | Registrar y presentar evidencia del PDA | D5 | Hecho (pendiente revisión de Carlos) |
| D7 | David Lopez | Probar el modelo y el reconocedor PDA | D2–D6 | Hecho (pendiente revisión de Carlos) |
| D8 | David Lopez | Contar operaciones y analizar el PDA | D5–D7 | Hecho (pendiente revisión de Carlos) |
| D9 | David Lopez | Implementar la consola y exportación de resultados | D1; D6 y C3 para completar | Hecho (pendiente revisión de Carlos) |
| D10 | David Lopez | Preparar el repositorio y verificar la entrega | D1 para preparar; C6–C10 para cerrar | Preparado (faltan repo privado, accesos y enlaces) |
| C1 | Carlos Lopez | Diseñar CYK y sus estructuras | D1, D2 | Pendiente |
| C2 | Carlos Lopez | Implementar la tabla y decisión CYK | C1 | Pendiente |
| C3 | Carlos Lopez | Registrar la tabla y reconstruir una derivación | C2 | Pendiente |
| C4 | Carlos Lopez | Probar CYK y sus derivaciones | C2, C3 | Pendiente |
| C5 | Carlos Lopez | Contar operaciones y analizar CYK | C2–C4 | Pendiente |
| C6 | Carlos Lopez | Integrar, comparar respuestas y probar la consola | D7, D9, C4 | Pendiente |
| C7 | Carlos Lopez | Generar experimentos de operaciones reproducibles | D8, C5, C6 | Pendiente |
| C8 | Carlos Lopez | Redactar la comparación de desempeño | D8, C5, C7 | Pendiente |
| C9 | Carlos Lopez | Integrar y generar el informe PDF | D4, D8, C5–C8 | Pendiente |
| C10 | Carlos Lopez | Preparar, grabar y subir el video | C6, C9 y coordinación con David | Pendiente |

## Forma de trabajo y delegación a agentes

1. Leer ambos el PDF y acordar D1 antes de desarrollar módulos dependientes. David debe conseguir desde el inicio el código del proyecto 1.
2. Para delegar, entregar al agente este README, el PDF y los IDs asignados. Puede recibir una tarea o un conjunto de tareas de la misma persona. No es necesario usar veinte agentes.
3. El agente debe crear o modificar los archivos de su ámbito, conservar el trabajo ajeno y comunicar los cambios de interfaces antes de aplicarlos. Los requisitos de cada tarea están descritos más abajo.
4. Si trabajan simultáneamente, usar copias de trabajo o ramas separadas cuando los usuarios lo indiquen. Cada persona mantiene sus módulos y pruebas; Carlos integra los resultados en C6. No sobrescribir archivos compartidos sin coordinación.
5. No hacer commit, push, compartir el repositorio ni publicar el video sin una instrucción explícita del usuario correspondiente. Son acciones pendientes dentro del plan de entrega.
6. Al cerrar una tarea, entregar: archivos modificados, explicación breve, comandos de comprobación, resultados y pendientes. La persona responsable revisa la evidencia y cambia el estado en la tabla. No marcar una tarea terminada si falta un requisito obligatorio.
7. Ambos revisan el trabajo del otro: Carlos sigue una traza PDA y David una tabla CYK. Cada integrante debe poder explicar el proyecto completo a nivel general.

### Acuerdos que deben quedar escritos al terminar D1

- Lenguaje y versión: se propone Python 3.10 o posterior y biblioteca estándar para ambos reconocedores. Declarar por separado cualquier dependencia para generar el PDF.
- Tokenización: cada palabra es un terminal y `n` es la cantidad de palabras. Acordar tratamiento de espacios, mayúsculas y puntuación. Se propone separar por espacios en blanco sin cambiar el resto de la entrada.
- Gramática: módulo único con producciones y símbolo inicial. Ambos reconocedores deben usar esa misma definición.
- Pila: orientación de la cima, símbolo de fondo, representación de epsilon y orden de los símbolos al reemplazar la cima.
- API: se propone `recognize(tokens, ...)` por módulo, con resultado que incluya método, estado de reconocimiento, palabras y contadores de operaciones.
- Estados: aceptación, rechazo y, si existe un límite de recursos, inconcluso. Agotar un límite nunca implica que la frase no pertenezca al lenguaje.
- Evidencia: PDA devuelve configuraciones y un recorrido aceptante; CYK devuelve tabla y testigos de derivación. Acordar un formato que pueda exportarse, por ejemplo JSON.
- Independencia: PDA ejecuta un autómata dado; CYK calcula su tabla. Ninguno debe llamar al otro para decidir la respuesta.

### Estructura propuesta

```text
README.md
Proyecto 2 2026.pdf
main.py                         # David: consola
recognizer/
    __init__.py
    grammar.py                  # David: gramática compartida
    automata.py                 # David: extensión del proyecto 1 y PDA
    pda.py                      # David: simulación
    cyk.py                      # Carlos: CYK
tests/
    test_grammar_automata.py     # David
    test_pda.py                 # David
    test_cyk.py                 # Carlos
    test_integration.py         # Carlos
    test_cli.py                 # Carlos, coordinado con David
scripts/
    benchmark.py                # Carlos: experimentos
docs/
    acuerdos.md                 # David: contratos acordados con Carlos
    pda.md                      # David: definición y análisis del PDA
    cyk.md                      # Carlos: explicación y análisis CYK
    operaciones.csv             # Carlos: datos reproducibles
    informe.md                  # Carlos integra los aportes de ambos
    informe.pdf
    guion_video.md
```

La estructura puede ajustarse de común acuerdo. No agregar herramientas, interfaz gráfica ni dependencias que no ayuden a cumplir el enunciado.

## Tareas de David Lopez

### D1. Preparación y contratos

**Hacer:** crear la estructura mínima y acordar con Carlos los puntos indicados arriba. Documentar cómo se importarán los módulos, la forma del resultado y los nombres de campos para las trazas y contadores. Preparar `.gitignore` para cachés y salidas temporales.

**Entregar:** estructura de módulos, `.gitignore` y `docs/acuerdos.md`.

**Cerrar cuando:** Carlos pueda implementar CYK sin depender de detalles internos del PDA y ambos conozcan la misma política de entrada y salida.

### D2. Gramática compartida

**Hacer:** transcribir exactamente las producciones del PDF; identificar variables, terminales y símbolo inicial. Confirmar que las reglas cumplen CNF. Implementar la tokenización acordada y comprobar que no se agregan ni omiten palabras o producciones.

**Entregar:** `recognizer/grammar.py` y pruebas de gramática y tokenización en `tests/test_grammar_automata.py`.

**Cerrar cuando:** ambos métodos puedan consumir la misma G y las pruebas detecten diferencias frente al enunciado. No hace falta programar un lector de gramáticas.

### D3. Extensión del autómata del proyecto 1

**Hacer:** recuperar la clase original, identificar sus campos y extenderla con pila, alfabeto de pila, fondo y transiciones epsilon y de lectura. Representar de forma explícita qué símbolo se desapila y qué secuencia se apila.

**Entregar:** `recognizer/automata.py`, las adaptaciones necesarias del código original y explicación de la extensión en `docs/pda.md`.

**Cerrar cuando:** sea verificable qué definición del proyecto 1 se reutilizó y qué se agregó. Si falta el código original, registrar la dependencia y continuar el trabajo independiente; una clase nueva provisional no completa este requisito.

### D4. Conversión formal de G a PDA

**Hacer:** definir la tupla del PDA, estados, alfabetos, pila inicial, transiciones y condición de aceptación. Incluir inicialización, expansión de variables, coincidencia de terminales y finalización. Implementar la construcción del PDA de G con el modelo de D3. Explicar por qué reconoce el mismo lenguaje.

**Entregar:** definición formal y ejemplo manual en `docs/pda.md`, construcción del autómata y pruebas de sus transiciones.

**Cerrar cuando:** el orden de apilado sea correcto y pueda seguirse manualmente una aceptación de `he cooks`, consumiendo toda la entrada.

### D5. Simulador PDA

**Hacer:** ejecutar las transiciones de un PDA proporcionado, representando estado, posición y pila completa. Explorar sus alternativas con una estrategia explícita. Resolver la recursión izquierda de G y justificar las podas o mecanismos de terminación. Distinguir configuración repetida de configuración con pila diferente.

**Entregar:** `recognizer/pda.py` con aceptación, rechazo y manejo documentado de recursos.

**Cerrar cuando:** el simulador no se limite a reconocer frases por reglas codificadas fuera del autómata y funcione también con un PDA pequeño distinto del de G. Si se limita la búsqueda, informar inconcluso al agotar el límite.

### D6. Evidencia del PDA

**Hacer:** registrar las configuraciones y transiciones exploradas. Reconstruir un recorrido completo cuando se acepta. Conservar evidencia de la exploración y explicar su agotamiento cuando se rechaza. Acordar con D9 la presentación y exportación.

**Entregar:** registros estructurados y ejemplos aceptado y rechazado en `docs/pda.md`.

**Cerrar cuando:** cada paso de una aceptación pueda comprobarse contra una transición real y los registros permitan distinguir rechazo de búsqueda interrumpida.

### D7. Pruebas del PDA

**Hacer:** verificar transiciones, orden de pila, lectura epsilon, consumo completo, cadena vacía, palabras desconocidas, frases con complementos y rechazos. Validar los enlaces del recorrido y un PDA externo. Si existe un límite, comprobar que no produzca falsos rechazos.

**Entregar:** `tests/test_pda.py` y las pruebas del modelo de autómata.

**Cerrar cuando:** las pruebas se ejecuten sin errores y fallen ante un recorrido inválido o una aceptación con entrada pendiente.

### D8. Operaciones y complejidad del PDA

**Hacer:** instrumentar configuraciones, transiciones u otras operaciones dominantes. Analizar la estrategia realmente implementada, las copias de pila, la memoria, las podas y el registro. Separar el costo de un recorrido del costo de buscarlo. Justificar la tasa en notación asintótica e indicar si es una cota superior o ajustada.

**Entregar:** contadores en el simulador y análisis en `docs/pda.md`, con fuentes si se utilizan.

**Cerrar cuando:** Carlos pueda reproducir los contadores en C7 y el análisis no confunda una ejecución truncada con el reconocimiento completo ni use tiempos de reloj como conteo de operaciones.

### D9. Consola y exportación

**Hacer:** recibir como mínimo la frase y permitir ejecutar PDA, CYK o ambos. Mostrar decisión y pasos. Se proponen `--metodo`, `--traza`, `--json` y, si corresponde, `--limite`. Exportar resultados y registros completos. Validar argumentos y explicar la política de entrada.

**Entregar:** `main.py` e instrucciones de uso en este README, coordinadas con Carlos.

**Cerrar cuando:** funcionen ambos módulos mediante los contratos de D1, las trazas se lean correctamente y las entradas inválidas o resultados inconclusos se presenten claramente. Carlos verifica los casos de consola en C6.

### D10. Repositorio y revisión final de entrega

**Hacer:** preparar el repositorio privado y la lista de archivos a entregar. Cuando el usuario lo indique, subir los cambios y compartir acceso con el docente y auxiliar. Al finalizar C9 y C10, verificar los enlaces y que la versión del código coincida con el PDF y el video. Probar instalación y ejecución desde una copia limpia.

**Entregar:** URL del repositorio, acceso verificado, instrucciones reproducibles y lista final de entrega revisada con Carlos.

**Cerrar cuando:** no falten archivos necesarios, los destinatarios tengan acceso y ambos confirmen que la entrega está completa. Un repositorio creado pero sin compartir no satisface el requisito. No se hace commit ni push durante la elaboración de este plan.

## Tareas de Carlos Lopez

### C1. Diseño de CYK

**Hacer:** usar la gramática compartida y definir los índices de la tabla, la base léxica, la recurrencia, los cortes y el criterio de aceptación. Definir cómo almacenar testigos y manejar la entrada vacía. Acordar el resultado con D1.

**Entregar:** diseño y pseudocódigo en `docs/cyk.md`.

**Cerrar cuando:** pueda calcularse a mano la tabla de `he cooks` y explicarse por qué G es apta para CYK sin transformarla.

### C2. Implementación de CYK

**Hacer:** inicializar las categorías de cada palabra y completar segmentos de longitud creciente, examinando los cortes y las reglas binarias. Aceptar si S deriva toda la entrada. Manejar palabras desconocidas y cadena vacía con la misma política de D2.

**Entregar:** `recognizer/cyk.py`, sin depender del simulador PDA.

**Cerrar cuando:** se decida por la tabla completa, sin atajos que alteren G, y se obtengan los resultados esperados en frases positivas y negativas.

### C3. Tabla y derivación CYK

**Hacer:** registrar todas las celdas calculadas, incluidas las vacías, y almacenar testigos para reconstruir al menos una derivación o árbol aceptante. Para un rechazo, mostrar que S no aparece en la celda final; documentar el caso de entrada vacía.

**Entregar:** tabla y derivación serializables y ejemplos en `docs/cyk.md`.

**Cerrar cuando:** las hojas del árbol coincidan exactamente con la frase y todas sus producciones pertenezcan a G. No se exige enumerar todos los árboles de una frase ambigua.

### C4. Pruebas de CYK

**Hacer:** probar la inicialización, combinaciones binarias, segmentos, cadena vacía, palabras desconocidas y frases de distintas longitudes. Verificar las producciones y las hojas de cada árbol aceptante y un rechazo mediante su tabla.

**Entregar:** `tests/test_cyk.py`.

**Cerrar cuando:** las pruebas comprueben resultados y evidencia, no solo que el programa termine. David debe poder revisar al menos una tabla a mano.

### C5. Operaciones y complejidad de CYK

**Hacer:** instrumentar consultas léxicas, cortes y comprobaciones de reglas según los bucles elegidos. Derivar el conteo y la tasa asintótica. Analizar tabla, testigos y registro, distinguiendo gramática fija de gramática variable cuando sea relevante.

**Entregar:** contadores en CYK y desarrollo matemático en `docs/cyk.md`, con fuentes si se utilizan.

**Cerrar cuando:** los conteos de entradas pequeñas puedan verificarse manualmente y la tasa descrita corresponda al código final.

### C6. Integración y validación cruzada

**Hacer:** integrar con David la consola y los resultados. Comparar PDA y CYK en las mismas entradas; ante una diferencia, revisar G y el recorrido o tabla antes de modificar la respuesta. Comparar además un conjunto reproducible de cadenas cortas sobre un alfabeto reducido, indicando los límites de esa evidencia.

**Entregar:** `tests/test_integration.py`, `tests/test_cli.py` y registro de los comandos de validación.

**Cerrar cuando:** coincidan los resultados concluyentes, funcionen selección de método, trazas y exportación, y todas las pruebas de ambos integrantes pasen. Un resultado PDA inconcluso no cuenta como rechazo ni como prueba de desacuerdo.

### C7. Experimentos reproducibles

**Hacer:** crear familias de frases aceptadas y rechazadas con distintas longitudes; ejecutar los contadores de D8 y C5 y exportar datos. Registrar entrada, n, decisión, operaciones y cualquier límite alcanzado. Explicar qué operación representa cada columna.

**Entregar:** `scripts/benchmark.py` y `docs/operaciones.csv`.

**Cerrar cuando:** regenerar los datos sea reproducible, las decisiones sean coherentes y ningún tiempo de ejecución sustituya el conteo exigido. Los límites de recursos deben quedar visibles.

### C8. Comparación de desempeño

**Hacer:** comparar tasas analíticas, operaciones observadas, consumo de memoria, comportamiento en aceptación y rechazo, recursión izquierda y reutilización de subproblemas. Explicar que las operaciones de los dos programas no necesariamente cuestan lo mismo. Diferenciar evidencia experimental de demostración asintótica.

**Entregar:** sección de discusión en `docs/informe.md`, revisada por David junto con su análisis PDA.

**Cerrar cuando:** las conclusiones se apoyen en D8, C5 y C7 y se indiquen sus límites. No afirmar que un método siempre es más rápido basándose solo en frases cortas.

### C9. Documento e instrucciones finales

**Hacer:** integrar los aportes de ambos en un informe que contenga objetivo, G, definición formal del PDA, extensión del proyecto 1, explicación de algoritmos, ejemplos de sus pasos, análisis asintótico, comparación, validación y referencias. Completar nombres, carnés e instrucciones reales de instalación y ejecución.

**Entregar:** fuente editable `docs/informe.md`, `docs/informe.pdf` y README de uso actualizado. Si se automatiza el PDF, incluir el script y las dependencias necesarias. Incorporar los enlaces finales del repositorio y video al terminar D10 y C10.

**Cerrar cuando:** el PDF se lea completo, los datos coincidan con el código y experimentos, las instrucciones funcionen y los enlaces finales estén incluidos. Puede prepararse un borrador antes del video; la versión de entrega debe actualizarse después.

### C10. Video y coordinación de la entrega

**Hacer:** escribir un guion, ensayar y grabar una demostración de máximo 10 minutos. David presenta el PDA y Carlos CYK; ambos muestran evidencia y explican el análisis. Incluir ejecución real con una frase aceptada y otra rechazada, tabla o traza de ambos métodos y ubicación de documentación y pruebas.

**Entregar:** `docs/guion_video.md`, grabación final y enlace de YouTube no listado cuando el usuario indique subirlo.

**Cerrar cuando:** se vean los comandos y resultados, el audio sea comprensible, la duración cumpla el límite y el video pueda abrirse con su enlace. Comunicar el enlace a C9 y D10 para completar el PDF y la entrega.

## Orden práctico de ejecución

1. **Preparación:** ambos acuerdan D1; David realiza D2 y recupera el proyecto 1 para D3. Carlos inicia C1 tan pronto esté disponible la gramática.
2. **Desarrollo en paralelo:** David realiza D3–D7 y Carlos C1–C4. Cada uno instrumenta y analiza su algoritmo en D8 y C5. David prepara D9 usando los contratos acordados.
3. **Integración:** completar D9, ejecutar C6 y corregir cada problema en el módulo de su responsable. Repetir las pruebas afectadas después de corregir.
4. **Análisis y documentación:** Carlos realiza C7–C9 con el aporte de David. David prepara el repositorio de D10.
5. **Entrega:** ejecutar una validación desde una copia limpia, grabar C10, incluir los enlaces en C9 y completar D10. Ambos revisan la lista final.

No hay que esperar al video para escribir el informe ni esperar al informe final para preparar el repositorio. Los enlaces y la revisión final se completan al cierre.

## Casos mínimos de validación

Con la política propuesta de conservar mayúsculas y puntuación:

| Entrada | Resultado esperado | Qué comprueba |
| --- | --- | --- |
| `he cooks` | Aceptar | Sujeto pronominal y verbo intransitivo |
| `she drinks a beer` | Aceptar | Verbo con objeto NP |
| `the cat eats the meat with a fork in the oven` | Aceptar | Determinantes y varios complementos PP |
| `a dog cuts she` | Aceptar | Se reconoce G, aunque la frase resulte extraña en inglés |
| Cadena vacía | Rechazar | G no deriva epsilon |
| `he` | Rechazar | Falta VP |
| `cooks he` | Rechazar | Orden inválido |
| `he eats cake` | Rechazar | NP nominal requiere determinante |
| `he cooks with` | Rechazar | PP incompleto |
| `he dances` | Rechazar | Palabra fuera del alfabeto |
| `He cooks` / `he cooks.` | Rechazar | Política de entrada acordada |

También verificar espacios repetidos, exportación de registros y, si hay límite de búsqueda, un resultado inconcluso. Agregar pruebas que validen la evidencia y comparen múltiples cadenas; esta tabla no reemplaza las pruebas de cada módulo.

**Comandos propuestos, pendientes de implementar y verificar:**

```powershell
python main.py "he cooks" --metodo ambos --traza
python main.py "he eats cake" --traza --json salidas/rechazo.json
python -m unittest discover -s tests -v
python scripts/benchmark.py
```

## Cobertura de todos los requisitos del enunciado

| Requisito del PDF | Tareas que lo completan | Evidencia final |
| --- | --- | --- |
| Convertir G a PDA | D2–D4 | Definición formal y construcción del autómata |
| Extender el autómata del proyecto 1 | D3 | Código original extendido y explicación |
| Ejecutar un PDA dado | D5, D7 | Simulador y prueba con otro PDA |
| Reconocer frases de G con PDA | D5–D7, C6 | Ejemplos y pruebas |
| Implementar CYK y reconocer frases de G | C1–C4, C6 | Tabla, decisión y pruebas |
| Registrar pasos de ambos métodos | D6, C3, D9 | Configuraciones y tabla o derivación exportables |
| Recibir como mínimo la cadena | D9, C6 | Consola funcional |
| Tasas de crecimiento por operaciones y notación asintótica | D8, C5, C7, C9 | Cálculos, contadores y PDF |
| Discutir diferencias de desempeño | C8, C9 | Discusión apoyada por análisis y datos |
| Documentación PDF | C9 | PDF final con datos y enlaces |
| Repositorio privado compartido | D10 | URL y acceso del docente y auxiliar |
| Video de YouTube no listado de máximo 10 minutos | C10 | URL, visibilidad y duración verificadas |

La rúbrica asigna 5 puntos al documento: 1 a la definición del PDA, 2 a crecimiento y 2 a comparación. Asigna otros 5 al PDA funcional y 5 a CYK funcional, para un total de 15. Deben completarse los tres bloques.

## Lista de cierre conjunta

- [ ] Las veinte tareas tienen evidencia de cierre y responsable que la revisó.
- [ ] La gramática coincide con el enunciado.
- [ ] Se integró la extensión real del autómata del proyecto 1.
- [ ] Ambos reconocedores funcionan y registran sus pasos.
- [ ] Ambos integrantes revisaron una ejecución del método del otro.
- [ ] Todas las pruebas pasan y se comprobaron las instrucciones desde una copia limpia.
- [ ] Los conteos y tasas corresponden a la implementación final.
- [ ] La comparación está documentada y sus conclusiones están justificadas.
- [ ] El PDF tiene nombres, carnés y enlaces finales y fue revisado visualmente.
- [ ] El repositorio es privado y el docente y auxiliar tienen acceso.
- [ ] El video está en YouTube como no listado, dura máximo 10 minutos y su enlace funciona.
- [ ] Código, PDF, experimentos y video corresponden a la misma versión final.

Este README distribuye todo el trabajo; no declara completada ninguna implementación, publicación ni prueba.

## Uso

Actualización de implementación D1–D9: el plan anterior se conserva como referencia. El PDA y la
consola están implementados; CYK y la revisión conjunta siguen pendientes de Carlos. Los contratos
están en [docs/acuerdos.md](docs/acuerdos.md) y la definición, evidencia, fuentes y análisis del PDA
en [docs/pda.md](docs/pda.md). Los estados D* indican el alcance local del brief, pendiente de revisión;
la integración con una implementación real de CYK corresponde a C6.

Requiere Python >= 3.10, solo biblioteca estándar. No hay paquetes que instalar. Desde la raíz:

```powershell
python -m unittest discover -s tests -v
python main.py "he cooks" --metodo pda --traza
python main.py "he eats cake" --traza --json salidas/rechazo.json
python main.py "he cooks" --metodo ambos --traza
python main.py "he cooks" --metodo pda --limite 1
python scripts/conteos_pda.py
python main.py --help
```

Cada palabra es un token. Los espacios repetidos, tabs y saltos se colapsan con `split()`;
no se normalizan mayúsculas ni puntuación. `He cooks`, `he cooks.` y las palabras desconocidas
se rechazan, identificando cuáles quedan fuera del alfabeto. Vacía o solo espacios también se rechaza.
`--limite N` exige un entero positivo y limita las expansiones del PDA, produciendo inconclusión
si quedan configuraciones sin examinar. Sin límite, el PDA de G termina gracias a la poda segura.

`--metodo` admite `pda`, `cyk`, `ambos` (predeterminado). Hasta que Carlos agregue `recognizer/cyk.py`,
`ambos` ejecuta PDA y muestra «CYK no disponible todavía (tarea C2 de Carlos)»; `cyk` exclusivo
devuelve código 2. `--traza` muestra descripciones instantáneas del PDA o la tabla CYK cuando exista.
`--json RUTA` crea las carpetas necesarias y exporta una lista de resultados completos en UTF-8,
incluidos evidencia y contadores. La consola configura stdout en UTF-8 para imprimir ε y ⊢.

Códigos de salida: **0** aceptación, **1** rechazo, **2** inconclusión/error de uso o exportación,
CYK exclusivo ausente o discrepancia entre métodos. Un límite alcanzado nunca significa rechazo.
`scripts/conteos_pda.py` imprime ocho frases con conteos en CSV; no utiliza tiempos de reloj.

## Lista de entrega

- [x] Gramática compartida y contratos: `recognizer/__init__.py`, `recognizer/resultado.py`,
  `recognizer/grammar.py`, `docs/acuerdos.md`.
- [x] Extensión y simulación: `recognizer/automata.py`, `recognizer/pda.py`,
  `recognizer/proyecto1/{__init__,models,constants,errors}.py`.
- [x] Definición, prueba de equivalencia, ejemplos y análisis: `docs/pda.md`.
- [x] Consola, pruebas y conteos: `main.py`, `tests/test_grammar_automata.py`, `tests/test_pda.py`,
  `tests/test_main.py`, `scripts/conteos_pda.py`.
- [x] Preparación: `.gitignore`, `salidas/.gitkeep`, README y enunciado `Proyecto 2 2026.pdf`.
- [ ] Carlos: CYK, pruebas propias e integración real, benchmark y comparación, informe PDF y video.
- [ ] Revisar entre ambos los contratos y la evidencia de cada método.
- [ ] Convertir `DeividArriaza/proyecto2-tdc` a **privado** (el brief informa que hoy es público).
- [ ] Compartir el repositorio con docente y auxiliar y verificar sus accesos.
- [ ] Agregar enlaces finales al repositorio privado, PDF y video no listado (máximo diez minutos).
- [ ] Completar nombres/carnés, revisión visual y coincidencia entre código, PDF y video.

La comprobación local se realiza desde una copia sin `.git` ni cachés en
`C:/Universidad/TDC/_coord-proyecto2/copia-limpia`, con las pruebas y dos comandos de consola.
El reporte externo `C:/Universidad/TDC/_coord-proyecto2/reporte-david.md` registra resultados reales.
No se hicieron commit, push ni cambios de visibilidad o acceso; siguen a cargo del coordinador.
