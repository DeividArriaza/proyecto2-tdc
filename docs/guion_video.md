# Guion final — Proyecto 2: PDA y CYK

Universidad del Valle de Guatemala · CC2019 · Sección 30 · Semestre 2, 2026.
David López, 24730: voz 1, es-GT-AndresNeural. Carlos López, 24531: voz 2, es-MX-JorgeNeural.
Narración sintética de las intervenciones de cada integrante. Objetivo de montaje: 8:45.
Las estimaciones se calculan a 150 palabras/minuto; los tiempos definitivos quedan en timeline.json.
Todas las terminales y tablas proceden de ejecuciones reales; los fragmentos omitidos se indican con «…».

## 01. Dos formas de reconocer una frase
Voz: David
Visual: portada; nombres, carnés y curso.
```narracion
Somos David López y Carlos López, de Teoría de la Computación de la Universidad del Valle de Guatemala. Presentamos el proyecto dos: reconocer frases de una gramática libre de contexto mediante un autómata de pila y mediante CYK. Mostraremos ejecuciones reales, una aceptación, un rechazo y la evidencia de cada decisión. Después compararemos los algoritmos contando operaciones y revisaremos las pruebas y la documentación del proyecto.
```

## 02. El problema y la gramática G
Voz: David
Visual: reglas de G; 8 variables, 21 terminales, 5 reglas binarias y 25 léxicas.
```narracion
La gramática del enunciado combina un grupo nominal con un grupo verbal. Permite verbos simples, objetos y complementos con preposición. Ya está en forma normal de Chomsky: cada producción genera dos variables o una palabra. Compartimos una sola definición en grammar punto py. La entrada se separa por espacios; ene cuenta palabras. Conservamos mayúsculas y puntuación, y rechazamos la cadena vacía porque esta gramática no deriva épsilon.
```

## 03. La extensión del proyecto uno
Voz: David
Visual: extracto real de AutomataPila(AFN), procedencia y nuevos campos.
```narracion
Para cumplir la extensión del proyecto uno, AutomataPila hereda de la clase AFN original. Reutiliza estados, alfabeto, estado inicial, aceptación y validaciones. Agrega alfabeto de pila, símbolo de fondo y transiciones que consultan la cima y la reemplazan por una secuencia. El código original está conservado en recognizer, proyecto uno, con su procedencia. Representamos la pila como una tupla cuya cima ocupa la posición cero. Reemplazar la cima por una tupla vacía significa desapilar.
```

## 04. Definición formal del PDA
Voz: David
Visual: tupla formal y cuatro familias de transiciones resaltadas progresivamente.
```narracion
El PDA tiene tres estados: inicialización, simulación y aceptación. Su alfabeto de pila reúne variables, terminales y el fondo zeta cero. Primero coloca el símbolo inicial sobre el fondo. Después puede expandir una variable aplicando cualquier producción de la gramática, sin consumir entrada. Si la cima es un terminal, debe coincidir con la siguiente palabra para consumirla y desapilarla. Finalmente pasa al estado de aceptación cuando queda el fondo. También exige que toda la entrada se haya consumido.
```

## 05. Búsqueda y recursión izquierda
Voz: David
Visual: BFS, configuración completa e inecuación de poda.
```narracion
El simulador ejecuta las transiciones del autómata recibido mediante búsqueda en anchura. Una configuración incluye estado, posición y pila completa. La regla de recursión izquierda puede generar pilas cada vez mayores. Como ninguna variable deriva épsilon, cada símbolo pendiente requiere al menos una palabra. Podamos cuando hay más símbolos sobre el fondo que palabras restantes. Esto limita la pila y garantiza terminación para esta gramática. Un límite opcional de recursos produce un resultado inconcluso; nunca se presenta como rechazo.
```

## 06. PDA: aceptación con traza real
Voz: David
Visual: comando he cooks; ocho descripciones instantáneas aparecen y se resaltan en orden.
```narracion
Ejecutamos he cooks con el método PDA y la opción traza. Estas son las descripciones instantáneas de la ruta aceptante, extraídas de la salida real. Inicializamos, expandimos ese en grupo nominal y grupo verbal, y sustituimos el grupo nominal por he. Consumimos he, expandimos el grupo verbal a cooks y consumimos cooks. La entrada pendiente queda en épsilon y la pila conserva únicamente el fondo. Alcanzamos el estado final: la frase está aceptada.
```

## 07. PDA: rechazo con causa
Voz: David
Visual: ejecución he eats cake; decisión y agotamiento real, en fragmentos legibles.
```narracion
Ahora ejecutamos he eats cake. Todas sus palabras pertenecen al alfabeto, pero la frase no pertenece al lenguaje. Cake solo deriva de ene; para formar el objeto nominal hace falta un determinante, como a o the. La búsqueda termina con la frontera agotada: veintinueve configuraciones expandidas, cuatro podas y ninguna pendiente. Por eso el rechazo es concluyente. Se distingue de interrumpir una ejecución al alcanzar un límite, que dejaría trabajo por explorar.
```

## 08. CYK: construir soluciones por segmentos
Voz: Carlos
Visual: definición T[i,l], base, corte y condición de aceptación.
```narracion
Yo soy Carlos y presento CYK. En lugar de explorar pilas, construimos una tabla de segmentos. Cada celda contiene las variables capaces de generar las palabras de ese segmento. Primero llenamos las celdas de una palabra usando reglas léxicas. Luego aumentamos la longitud, probamos cada corte y buscamos producciones binarias que unan las dos partes. La frase se acepta cuando ese aparece en la celda que cubre toda la entrada. Guardamos testigos para reconstruir una derivación.
```

## 09. CYK: ejecución aceptada y tabla progresiva
Voz: Carlos
Visual: comando she drinks a beer; tabla real se llena por longitud de 1 a 4.
```narracion
Ejecutamos she drinks a beer con CYK y traza. La base asigna grupo nominal a she, dos categorías a drinks, determinante a a y nombre a beer. En longitud dos, a beer forma un grupo nominal. En longitud tres, drinks a beer forma un grupo verbal por la producción de verbo más grupo nominal. Finalmente, she y ese grupo verbal producen ese en longitud cuatro. La celda final contiene el símbolo inicial: la ejecución acepta la frase.
```

## 10. Una derivación comprobable
Voz: Carlos
Visual: derivación real reconstruida desde los testigos; resaltado por paso.
```narracion
Los testigos guardan qué producción y qué corte originaron cada variable. Desde la celda final reconstruimos esta derivación izquierda. Expandimos ese a grupo nominal y grupo verbal; elegimos she; expandimos el grupo verbal a verbo y grupo nominal; elegimos drinks y luego determinante más nombre. Las últimas elecciones generan a y beer. Las hojas coinciden exactamente con la frase de entrada. Guardar el primer testigo es suficiente para mostrar una derivación válida, aunque una gramática pudiera ser ambigua.
```

## 11. CYK: la evidencia del rechazo
Voz: Carlos
Visual: comando he eats cake; tabla real por longitud y celda final vacía.
```narracion
Probamos también he eats cake con CYK. La base contiene grupo nominal, verbo y grupo verbal, y nombre. Aunque he eats forma una oración corta en longitud dos, sobra cake. Eats cake no forma un grupo verbal porque falta el determinante del objeto. La celda de longitud tres queda vacía y no contiene ese. Esta tabla completa justifica el rechazo. No basta con que algún segmento sea una oración: el símbolo inicial debe cubrir todas las palabras.
```

## 12. Ambos métodos coinciden
Voz: Carlos
Visual: dos comandos --metodo ambos, aceptación y rechazo, con salidas reales.
```narracion
La consola permite ejecutar los dos métodos sobre los mismos tokens con la opción método ambos. He cooks queda aceptada por los dos; he eats cake queda rechazada por los dos. Comparten la gramática, pero cada algoritmo toma su decisión de manera independiente. Si los estados difieren, o el PDA queda inconcluso, la consola lo señala. Además de leer la respuesta, podemos exportar la evidencia completa a un archivo JSON para revisar configuraciones, tablas, testigos y contadores.
```

## 13. CYK: tasa de crecimiento exacta
Voz: Carlos
Visual: fórmulas de celdas, cortes y comprobaciones; Θ(n³), memoria Θ(n²).
```narracion
La tasa se obtiene contando operaciones. CYK crea ene por ene más uno, dividido entre dos, celdas. Revisa veinticinco reglas léxicas por palabra. El total de cortes es ene al cubo menos ene, dividido entre seis, y en cada corte comprueba cinco reglas binarias. Para la gramática fija, el término cúbico domina: tiempo theta de ene al cubo y memoria theta de ene al cuadrado. Los bucles se ejecutan completos incluso cuando muchas celdas están vacías.
```

## 14. PDA: buscar una ruta tiene un costo
Voz: David
Visual: forma β PP^k Z0; cotas de G y cota general; pasos de una ruta.
```narracion
En nuestro PDA contamos transiciones y símbolos de pila copiados. Para esta gramática, las pilas tienen un prefijo de formas finitas seguido de repeticiones del complemento. La poda limita esas repeticiones: obtenemos O grande de ene cuadrado configuraciones y transiciones. Copiar y registrar pilas completas añade un factor lineal: tiempo y memoria tienen cota superior O grande de ene al cubo. Son cotas superiores. Para otras gramáticas, la búsqueda puede tener una cota exponencial. Una ruta aceptante tiene tres ene más uno pasos; encontrarla requiere explorar alternativas.
```

## 15. Comparación con operaciones.csv
Voz: Carlos
Visual: gráfica y tabla de filas F reales; series separadas para transiciones, copias y comprobaciones.
```narracion
La gráfica usa los datos reales de operaciones punto CSV. La familia aceptada comienza con she eats the cake y agrega complementos with a fork. Con siete palabras, el PDA evalúa ciento noventa y seis transiciones y CYK doscientas ochenta comprobaciones. Con cuarenta y nueve palabras son ocho mil novecientas cuarenta y seis frente a noventa y ocho mil. Pero el PDA copia trescientos quince mil ciento cincuenta y cuatro símbolos. Las unidades son diferentes: estos números no determinan por sí solos cuál programa tarda menos.
```

## 16. Aceptación, rechazo y límites del experimento
Voz: Carlos
Visual: familias R/E/D en n=50, conteos reales y advertencia sobre unidades.
```narracion
El comportamiento también depende del rechazo. Con cincuenta palabras, un complemento incompleto exige nueve mil trescientas diez transiciones del PDA. Una frase que comienza con cooks se rechaza tras siete, y una palabra desconocida se detecta antes de explorar. CYK mantiene ciento cuatro mil ciento veinticinco comprobaciones binarias en esos casos porque llena toda la tabla. Las cuarenta filas registran coincidencia de decisiones. Los experimentos llegan hasta cincuenta palabras: respaldan el análisis, pero las cotas se justifican estudiando los algoritmos.
```

## 17. Pruebas y documentación
Voz: Carlos
Visual: corrida real unittest -v, fragmento inicial y resumen 57 OK; rutas verificadas.
```narracion
Ejecutamos python, módulo unittest, discover, directorio tests, modo detallado. El resumen real confirma cincuenta y siete pruebas y resultado OK. Se verifican gramática, transiciones, trazas, tablas, derivaciones, consola e integración. La validación cruzada incluye nueve mil trescientas treinta y una cadenas cortas sobre un alfabeto reducido. La documentación está en docs: PDA, CYK, informe y operaciones punto CSV. Las implementaciones están en recognizer y las pruebas en tests. El informe completo también está disponible como PDF en la carpeta docs.
```

## 18. Cierre
Voz: David
Visual: conclusiones y nombres; publicación pendiente, sin subir archivos.
```narracion
Hemos mostrado dos reconocedores independientes para la misma gramática, con evidencia verificable de aceptación y rechazo. El PDA extiende el autómata del proyecto uno y controla la recursión izquierda mediante una poda justificada. CYK reutiliza segmentos y ofrece crecimiento cúbico para gramática fija. La comparación se apoya en operaciones reales y distingue sus unidades. El código, las pruebas y los documentos permiten reproducir los resultados. Somos David López y Carlos López. Gracias por acompañarnos en la demostración.
```

## Tiempos por escena

Estimación: 150 palabras/minuto. Montaje: audio medido + 0.4 s, redondeado a cuadros de 30 fps.

| Escena | Estimada | Montaje | Inicio |
| --- | --- | --- | --- |
| 01 | 26.8 s | 23.87 s | 00:00:00,000 |
| 02 | 27.2 s | 25.53 s | 00:00:23,867 |
| 03 | 30.0 s | 28.83 s | 00:00:49,400 |
| 04 | 31.6 s | 28.70 s | 00:01:18,233 |
| 05 | 32.0 s | 29.53 s | 00:01:46,933 |
| 06 | 29.6 s | 26.03 s | 00:02:16,467 |
| 07 | 29.2 s | 25.60 s | 00:02:42,500 |
| 08 | 30.8 s | 29.60 s | 00:03:08,100 |
| 09 | 31.2 s | 27.53 s | 00:03:37,700 |
| 10 | 31.6 s | 29.73 s | 00:04:05,233 |
| 11 | 31.2 s | 28.17 s | 00:04:34,967 |
| 12 | 31.2 s | 28.70 s | 00:05:03,133 |
| 13 | 30.8 s | 28.83 s | 00:05:31,833 |
| 14 | 35.2 s | 32.40 s | 00:06:00,667 |
| 15 | 34.8 s | 30.73 s | 00:06:33,067 |
| 16 | 32.4 s | 33.23 s | 00:07:03,800 |
| 17 | 32.4 s | 37.57 s | 00:07:37,033 |
| 18 | 31.2 s | 30.33 s | 00:08:14,600 |
