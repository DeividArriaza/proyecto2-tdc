# Contratos D1 para revisión de Carlos

Decisiones del brief del coordinador, listas para implementar CYK sin conocer el interior del PDA.
No se presupone que Carlos ya haya realizado la revisión humana.

## Entorno y entrada

- Python >= 3.10; solo biblioteca estándar; `python -m unittest discover -s tests -v`.
- Importaciones desde la raíz: `from recognizer.grammar import G, Gramatica, tokenizar, es_cnf`.
- `tokenizar(cadena)` es exactamente `cadena.split()`. `n` cuenta palabras, no caracteres.
- No se cambian mayúsculas ni puntuación. Vacía o solo espacios: cero tokens; G la rechaza.
- Palabras fuera de Σ: rechazo concluyente; `evidencia.palabras_desconocidas` contiene las distintas,
  ordenadas. No es un error de uso ni un resultado inconcluso.
- `Gramatica` es frozen+slots; alfabetos frozenset; `producciones[A]` es una tupla de alternativas,
  cada alternativa una tupla de símbolos. La regla vacía se representa con `()`.
- `G.inicial == "S"`; 8 variables, 21 terminales, 30 alternativas. `es_cnf` comprueba CNF estricta,
  sin excepción para S → ε. La construcción de PDA sí admite CFG fuera de CNF.

## Resultado y API pública

Cada módulo expone `recognize(tokens: list[str], **opciones) -> Resultado`.
`recognizer.resultado.Resultado` es una dataclass con:

| Campo | Tipo / significado |
| --- | --- |
| metodo | `"pda"` o `"cyk"` |
| estado | `"aceptada"`, `"rechazada"`, `"inconclusa"` |
| tokens | `list[str]`, copia de la entrada |
| n | `int`, cantidad de tokens |
| operaciones | `dict[str, int]`, conteos sin tiempos de reloj |
| evidencia | `dict`, solo valores serializables a JSON |
| motivo | `str`, explicación de la decisión o interrupción |

`to_dict()` devuelve una copia independiente de todos los campos. La consola exporta una **lista**
de esos objetos, incluso si solo hay uno o ninguno (CYK solicitado pero todavía ausente).
Ningún reconocedor invoca al otro. La consola llama `cyk.recognize(tokens)` sin opciones propias del PDA.

## PDA: opciones, pila y evidencia

`recognize(tokens, *, pda=None, poda_longitud=None, limite_configuraciones=None)`.
`pda=None` construye el PDA de G. `None` para poda usa el certificado de la construcción;
`False` desactiva la poda; `True` requiere certificado o lanza `ValueError`.
Un PDA externo tiene certificado falso. El límite es un entero positivo de expansiones; se puede
aceptar una configuración final al frente de la cola sin expandirla, incluso al alcanzar ese límite.
Sin límite, un PDA arbitrario con pilas no acotadas puede no terminar.

La cima está en índice 0. `apilar=("NP", "VP")` deja NP arriba. EPSILON procede del proyecto 1;
reemplazar la cima por `()` significa desapilar. La pila inicial es `(fondo,)`.
Se acepta por estado final con toda la entrada consumida; no se exige pila vacía.

Una configuración JSON es `{"estado": 1, "posicion": 0, "pila": ["S", "Z0"]}`.
Una transición JSON contiene `origen`, `lectura`, `cima`, `destino`, `apilar` (lista).
Los estados del modelo son enteros; al imprimir se antepone `q`.

`evidencia` contiene:

- `configuraciones`: lista en orden BFS de configuraciones únicas admitidas a la cola, con `id`,
  `padre` (id o null), `transicion` (o null en el inicio), `configuracion` y `expandida` (bool).
  Se conservan las pendientes al aceptar/interrumpir; candidatas podadas/repetidas se cuentan aparte.
- `recorrido_aceptante`: lista de pasos `{antes, transicion, despues}` desde el inicio hasta aceptación.
  Vacía en rechazo/interrupción. `validar_recorrido(pda, tokens, recorrido)` devuelve bool.
- `agotamiento`: null si acepta; de lo contrario un objeto con `causa`, `exploradas`, `podadas`,
  `repetidas`, `frontera_pendiente`. Causas: `frontera_agotada`, `limite_alcanzado`,
  `fuera_del_alfabeto`. Esta última es prevalidación, sin explorar configuraciones.
- `palabras_desconocidas`, `poda_longitud` (bool), `limite_configuraciones` (entero o null).

Los nombres y definiciones de los contadores están en [pda.md](pda.md).

## Propuesta de evidencia CYK (Carlos)

Índices desde cero. `tabla` es una lista de celdas `{inicio, longitud, variables}`, con variables
ordenadas; incluir todas las celdas 0 <= inicio < n y 1 <= longitud <= n - inicio, aun vacías.
Para n=0, tabla vacía y rechazo explícito. La celda final es inicio=0, longitud=n.
`testigos` puede ser una lista `{inicio, longitud, variable, produccion, corte}`; corte null para
reglas léxicas y un entero de longitud izquierda para reglas binarias. `arbol` es null al rechazar,
o un nodo `{variable, produccion, hijos}`; cada hoja terminal puede ser `{terminal, posicion}`.
El árbol debe tener exactamente los tokens de entrada como hojas, en orden.
La consola imprime `evidencia.tabla` al pedir `--traza` y exporta toda la evidencia sin transformarla.
Esta propuesta no implementa CYK ni reemplaza la revisión de C1/C3/C6.

## Consola y estados de salida

`python main.py "frase" [--metodo pda|cyk|ambos] [--traza] [--json RUTA] [--limite N]`.
Por defecto `ambos`; importa CYK de forma diferida. Si no existe, ejecuta PDA y avisa; pedir
exclusivamente CYK ausente termina con 2. Las dependencias rotas dentro de CYK no se ocultan como ausencia.
Salida 0: aceptación; 1: rechazo; 2: inconclusión, uso/exportación inválidos, CYK exclusivo ausente,
o decisiones distintas entre métodos. Si ambos discrepan, se conservan y exportan las dos evidencias.
`--limite` solo afecta PDA. `--json` crea carpetas y escribe UTF-8 sin BOM; stdout se reconfigura a UTF-8.
