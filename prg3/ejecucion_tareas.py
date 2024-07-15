import threading
import time
import queue
import random

# Algoritmo de sincronización de relojes: BerkeleyNode
class BerkeleyNode:
    def __init__(self, node_id, time):
        self.node_id = node_id
        self.time = time

    def adjust_time(self, offset):
        """
        Ajusta el tiempo del nodo basado en un desplazamiento dado.
        """
        self.time += offset

class BerkeleyMaster:
    def __init__(self, nodes):
        self.nodes = nodes

    def synchronize_clocks(self):
        """
        Sincroniza los relojes de los nodos usando el algoritmo de Berkeley.
        """
        times = [node.time for node in self.nodes]
        average_time = sum(times) / len(times)
        for node in self.nodes:
            offset = average_time - node.time
            node.adjust_time(offset)
        return [(node.node_id, node.time) for node in self.nodes]

# Recolector de basura usando Cheney
class CheneyCollector:
    def __init__(self, size):
        self.size = size
        self.from_space = [None] * size
        self.to_space = [None] * size
        self.free_ptr = 0

    def allocate(self, obj):
        """
        Asigna espacio para un objeto en el espacio de memoria gestionado.
        """
        if self.free_ptr >= self.size:
            self.collect()
        addr = self.free_ptr
        self.from_space[addr] = obj
        self.free_ptr += 1
        return addr

    def collect(self):
        """
        Ejecuta el proceso de recolección de basura usando el algoritmo de Cheney.
        """
        self.to_space = [None] * self.size
        self.free_ptr = 0
        for obj in self.from_space:
            if obj is not None:
                self.copy(obj)
        self.from_space, self.to_space = self.to_space, self.from_space

    def copy(self, obj):
        """
        Copia un objeto desde el espacio de origen al espacio de destino.
        """
        addr = self.free_ptr
        self.to_space[addr] = obj
        self.free_ptr += 1
        return addr

# Crear una clase Message
class Message:
    def __init__(self, sender, content, timestamp):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp

    def __str__(self):
        return f"Message from {self.sender} at {self.timestamp}: {self.content}"

# Clase Node
class Node:
    def __init__(self, node_id, total_nodes, network):
        self.node_id = node_id
        self.total_nodes = total_nodes
        self.network = network
        self.queue = queue.Queue()
        self.clock = random.randint(0, 10)  # Inicialización aleatoria para demostrar sincronización
        self.lock = threading.Lock()
        self.requesting_cs = False
        self.replies_received = 0
        self.active = True
        self.garbage_collector = CheneyCollector(10)
        self.berkeley_node = BerkeleyNode(node_id, self.clock)

    def send_message(self, recipient, content):
        """
        Envía un mensaje a otro nodo en la red.
        """
        timestamp = self.clock
        message = Message(self.node_id, content, timestamp)
        self.network.send(recipient, message)

    def receive_message(self, message):
        """
        Recibe un mensaje de otro nodo y actualiza el reloj lógico.
        """
        self.clock = max(self.clock, message.timestamp) + 1
        self.queue.put(message)

    def request_cs(self):
        """
        Solicita acceso a la sección crítica (Critical Section).
        """
        self.clock += 1
        self.requesting_cs = True
        self.replies_received = 0
        for node in range(self.total_nodes):
            if node != self.node_id:
                self.send_message(node, 'REQUEST')

    def release_cs(self):
        """
        Libera la sección crítica y notifica a otros nodos.
        """
        self.clock += 1
        self.requesting_cs = False
        for node in range(self.total_nodes):
            if node != self.node_id:
                self.send_message(node, 'RELEASE')

    def handle_request(self, message):
        """
        Maneja una solicitud de acceso a la sección crítica.
        """
        if not self.requesting_cs or (self.requesting_cs and (self.clock, self.node_id) < (message.timestamp, message.sender)):
            self.send_message(message.sender, 'REPLY')
        else:
            self.queue.put(message)

    def handle_release(self, message):
        """
        Maneja la liberación de la sección crítica (actualmente sin implementar).
        """
        pass

    def handle_reply(self):
        """
        Maneja una respuesta a la solicitud de acceso a la sección crítica.
        """
        self.replies_received += 1
        if self.replies_received == self.total_nodes - 1:
            self.enter_cs()

    def enter_cs(self):
        """
        Entra en la sección crítica y simula trabajo.
        """
        print(f"Node {self.node_id} entering critical section at clock {self.clock}.")
        time.sleep(1)  # Simulate work
        print(f"Node {self.node_id} leaving critical section at clock {self.clock}.")
        self.release_cs()

    def perform_garbage_collection(self):
        """
        Realiza la recolección de basura usando el algoritmo de Cheney.
        """
        print(f"Node {self.node_id} performing garbage collection.")
        self.garbage_collector.collect()
        print(f"Node {self.node_id} garbage collection complete.")

    def run(self):
        """
        Ejecuta el bucle principal del nodo, manejando mensajes recibidos.
        """
        while self.active:
            try:
                message = self.queue.get(timeout=1)
                if message.content == 'REQUEST':
                    self.handle_request(message)
                elif message.content == 'RELEASE':
                    self.handle_release(message)
                elif message.content == 'REPLY':
                    self.handle_reply()
            except queue.Empty:
                continue

    def stop(self):
        """
        Detiene la ejecución del nodo.
        """
        self.active = False

# Clase Network
class Network:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.nodes = [Node(node_id, num_nodes, self) for node_id in range(num_nodes)]
        self.threads = []

    def send(self, recipient, message):
        """
        Envía un mensaje a un nodo específico en la red.
        """
        self.nodes[recipient].receive_message(message)

    def start(self):
        """
        Inicia la ejecución de todos los nodos en la red.
        """
        for node in self.nodes:
            thread = threading.Thread(target=node.run)
            thread.start()
            self.threads.append(thread)

    def stop(self):
        """
        Detiene la ejecución de todos los nodos en la red.
        """
        for node in self.nodes:
            node.stop()
        for thread in self.threads:
            thread.join()

# Simulación de tareas científicas
def simulate_scientific_tasks():
    """
    Simula un conjunto de tareas científicas en una red de nodos.
    """
    num_nodes = 5
    network = Network(num_nodes)
    network.start()

    # Sincronización de relojes usando el algoritmo de Berkeley
    berkeley_master = BerkeleyMaster([node.berkeley_node for node in network.nodes])
    new_times = berkeley_master.synchronize_clocks()
    print("Synchronized times:", new_times)
    for node_id, new_time in new_times:
        network.nodes[node_id].clock = new_time

    # Realiza solicitudes de exclusión mutua para acceder a recursos compartidos
    for node in network.nodes:
        node.request_cs()

    # Espera a que todos los nodos completen su trabajo
    time.sleep(10)

    # Realiza la recolección de basura en los nodos
    for node in network.nodes:
        node.perform_garbage_collection()

    # Detiene la red de nodos de manera ordenada
    network.stop()

if __name__ == "__main__":
    simulate_scientific_tasks()
