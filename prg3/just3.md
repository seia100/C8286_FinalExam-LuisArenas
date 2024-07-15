# Pregunta 3 (5 puntos): Implementa un sistema distribuido en Python para la ejecución de tareas científicas en una red de computadoras, utilizando los siguientes algoritmos:

1. Dijkstra-Scholten para la detección de terminación de procesos distribuidos.
2. Ricart-Agrawala para la exclusión mutua en el acceso a recursos compartidos.
3. Sincronización de relojes para asegurar que todos los nodos tengan una vista consistente
del tiempo.
4. Algoritmo de recolección de basura (Cheney) para gestionar la memoria en los nodos de
computación.

## Instrucciones
### Crear una clase Message:
* Esta clase debe tener atributos para el remitente (sender), el contenido (content) y la marca
de tiempo (timestamp).

### Crea una clase Node:
• Cada nodo debe tener un identificador (node_id), el número total de nodos en la red
(total_nodes), y una referencia a la red.
• Implementa métodos para enviar mensajes a otros nodos, manejar solicitudes de exclusión
mutua utilizando el algoritmo de Ricart-Agrawala, y detectar la terminación de procesos
distribuidos con el algoritmo de Dijkstra-Scholten.
• Implementa un método para sincronizar los relojes de los nodos.
• Implementa un método para realizar la recolección de basura utilizando el algoritmo de
Cheney

### Crea una clase Network:
• Esta clase debe manejar la creación y la coordinación de los nodos en la red.
• Implementar métodos para iniciar y detener la red de nodos.

### Simula la ejecución de tareas científicas:
• Sincroniza los relojes de los nodos.
• Realiza solicitudes de exclusión mutua para acceder a recursos compartidos.
• Realiza la recolección de basura en los nodos.
• Detiene la red de nodos de manera ordenada.

## Interpretacion
### output
![task-ejecuted](image.png)

### Análisis Técnico

**Sincronización de Relojes con Berkeley:**    
* Synchronized times: La línea Synchronized times: [(0, 3.8), (1, 3.8), (2, 3.8), (3, 3.8), (4, 3.8)] muestra que todos los nodos han ajustado sus relojes a un tiempo promedio de 3.8. Esto indica que el algoritmo de Berkeley ha funcionado correctamente, sincronizando los relojes de todos los nodos para que estén en el mismo tiempo.

**Recolección de Basura con Cheney:**    
*   Node 0 performing garbage collection. Node 0 garbage collection complete.: Estas líneas se repiten para cada nodo (del 0 al 4), indicando que cada nodo ha realizado la recolección de basura.
*   La recolección de basura se completa correctamente en todos los nodos, lo que sugiere que el algoritmo de Cheney se ha ejecutado sin problemas, limpiando la memoria utilizada por cada nodo.

## Conclusiones

__Sincronizaciocn de relojes__
* Notamos que todos los nodos ajustaron sus timepos a `3.8`, lo qeu garantiza que todos los nodos estan coordinados temporalmente, un paso crucial para mantener la coherencia y el orden en las operaciones.

__Recolección de basura__
* El output `Node n performing garbage collection`, donde n es el numero de nodos por recolectar la basura. Notamos que se completo la tarea en los cuatro nodos. Esto asegura que los nodos puedan liberar memoria no utilizada, previniendo posibles problemas de memoria en operaciones prolongadas.


### Cambios realizados
- Documentacion mas exhaustiva 
- Mejora de la interpretación.
