# Guion del video (borrador C10)

Duración objetivo: **8:30** (límite: 10:00). Terminal con fuente grande y repositorio abierto.
Ensayar una vez con cronómetro y ajustar antes de grabar. Subir a YouTube como **no listado**.

| Tiempo | Quién | Contenido | En pantalla |
| --- | --- | --- | --- |
| 0:00–0:40 | Carlos | Presentación, objetivo, G en CNF, política de entrada (palabras, sin normalizar) | `docs/informe.md` §1–2 |
| 0:40–1:40 | David | Extensión del AFN del proyecto 1: herencia, pila, fondo, transiciones | `recognizer/automata.py` |
| 1:40–2:40 | David | Definición formal del PDA (4 tipos de transición) y por qué reconoce L(G) | `docs/pda.md` |
| 2:40–3:50 | David | Ejecución aceptada con traza; BFS, visitados y poda por recursión izquierda | Comando 1 |
| 3:50–4:20 | David | Rechazo con agotamiento de frontera | Comando 2 |
| 4:20–5:20 | Carlos | CYK: celdas, cortes, recurrencia, testigos; tabla de `she drinks a beer` | `docs/cyk.md` |
| 5:20–6:10 | Carlos | Ejecución aceptada y rechazada con tabla; árbol y derivación en el JSON | Comandos 3 y 4 |
| 6:10–7:30 | Carlos | Tasas: CYK Θ(n³) exacta; PDA O(n²) transiciones / O(n³) copias en G, exponencial en general; tabla de experimentos | `docs/informe.md` §6–8 |
| 7:30–8:10 | Ambos | Validación cruzada y pruebas | Comando 5 |
| 8:10–8:30 | Carlos | Dónde están documentación, pruebas, CSV y PDF; cierre | Árbol del repositorio |

## Comandos

```powershell
python main.py "she drinks a beer" --metodo pda --traza                       # 1
python main.py "he eats cake" --metodo pda --traza                            # 2
python main.py "she drinks a beer" --metodo cyk --traza --json salidas/demo.json  # 3
python main.py "he cooks with" --metodo cyk --traza                           # 4
python -m unittest discover -s tests                                          # 5
```

## Puntos que no deben faltar

- Una frase aceptada y otra rechazada con **ambos** métodos, mostrando traza o tabla.
- Que la tasa se calcula con conteo de operaciones, no con tiempos.
- Que las operaciones de ambos programas no cuestan lo mismo y que los datos no demuestran cotas.
- Ubicación de `docs/informe.pdf`, `docs/operaciones.csv` y `tests/`.
