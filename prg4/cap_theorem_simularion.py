import asyncio
import random
import time
import logging

# Configuración del registro de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Node:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = nodes  # Diccionario de nodos en la red
        self.data_store = {}  # Almacén de datos del nodo
        self.log = []  # Registro de operaciones del nodo
        self.current_term = 0  # Término actual en el algoritmo de consenso
        self.voted_for = None  # Nodo al que este nodo ha votado en la elección actual
        self.commit_index = 0  # Índice de confirmación de operaciones
        self.lock = asyncio.Lock()  # Para asegurar operaciones seguras en concurrencia
        self.is_available = True  # Indica si el nodo está disponible
        self.version = 0  # Versión de los datos para consistencia eventual

    async def send_message(self, target_node, message):
        """
        Envía un mensaje a otro nodo con simulación de latencia y posibles fallos.
        """
        if not self.is_available or not target_node.is_available:
            logging.info(f'Node {self.node_id} or Node {target_node.node_id} is not available.')
            return
        await asyncio.sleep(random.uniform(0.1, 1.0))  # Simulación de latencia de red
        if random.random() < 0.1:  # Simular fallo en el envío del mensaje
            logging.info(f'Message from Node {self.node_id} to Node {target_node.node_id} lost.')
            return
        await target_node.receive_message(message)

    async def receive_message(self, message):
        """
        Recibe un mensaje y lo maneja.
        """
        if not self.is_available:
            logging.info(f'Node {self.node_id} is not available to receive messages.')
            return
        await self.handle_message(message)

    async def handle_message(self, message):
        """
        Maneja diferentes tipos de mensajes.
        """
        if message['type'] == 'request_vote':
            await self.handle_request_vote(message)
        elif message['type'] == 'append_entries':
            await self.handle_append_entries(message)
        elif message['type'] == 'read_request':
            await self.handle_read_request(message)

    async def handle_request_vote(self, message):
        """
        Maneja las solicitudes de voto de otros nodos.
        """
        async with self.lock:
            if message['term'] > self.current_term:
                self.current_term = message['term']
                self.voted_for = None
            if self.voted_for is None and message['term'] == self.current_term:
                self.voted_for = message['candidate_id']
                response = {
                    'type': 'vote_response',
                    'term': self.current_term,
                    'vote_granted': True,
                    'from_node': self.node_id
                }
                if message['candidate_id'] in self.nodes:
                    await self.send_message(self.nodes[message['candidate_id']], response)

    async def handle_append_entries(self, message):
        """
        Maneja las solicitudes de agregar entradas al log de otros nodos.
        """
        async with self.lock:
            if message['term'] >= self.current_term:
                self.current_term = message['term']
                self.log.extend(message['entries'])
                self.commit_index = message['commit_index']
                for entry in message['entries']:
                    self.data_store[entry['key']] = entry['value']
                    self.version += 1
                response = {
                    'type': 'append_response',
                    'term': self.current_term,
                    'success': True,
                    'from_node': self.node_id
                }
                if message['leader_id'] in self.nodes:
                    await self.send_message(self.nodes[message['leader_id']], response)

    async def handle_read_request(self, message):
        """
        Maneja las solicitudes de lectura de datos.
        """
        async with self.lock:
            response = {
                'type': 'read_response',
                'data': self.data_store.get(message['key'], None),
                'version': self.version,
                'from_node': self.node_id
            }
            if message['requester_id'] in self.nodes:
                await self.send_message(self.nodes[message['requester_id']], response)

    async def request_vote(self):
        """
        Solicita votos de otros nodos para convertirse en el líder.
        """
        async with self.lock:
            self.current_term += 1
            self.voted_for = self.node_id
            votes = 1
            for node in self.nodes.values():
                if node.node_id != self.node_id:
                    message = {
                        'type': 'request_vote',
                        'term': self.current_term,
                        'candidate_id': self.node_id
                    }
                    await self.send_message(node, message)

    async def append_entries(self, entries):
        """
        Solicita a otros nodos que agreguen entradas a sus logs.
        """
        async with self.lock:
            self.log.extend(entries)
            self.commit_index = len(self.log)
            for node in self.nodes.values():
                if node.node_id != self.node_id:
                    message = {
                        'type': 'append_entries',
                        'term': self.current_term,
                        'leader_id': self.node_id,
                        'entries': entries,
                        'commit_index': self.commit_index
                    }
                    await self.send_message(node, message)

    async def read_data(self, key, requester_id):
        """
        Realiza una operación de lectura en el sistema distribuido.
        """
        message = {
            'type': 'read_request',
            'key': key,
            'requester_id': requester_id
        }
        for node in self.nodes.values():
            if node.node_id != self.node_id:
                await self.send_message(node, message)

    async def simulate_network_partition(self, partitioned_nodes):
        """
        Simula una partición de red removiendo nodos de la lista de nodos conocidos.
        """
        for node in partitioned_nodes:
            self.nodes.pop(node.node_id, None)

    async def heal_network_partition(self, healed_nodes):
        """
        Cura una partición de red agregando nodos de nuevo a la lista de nodos conocidos.
        """
        for node in healed_nodes:
            self.nodes[node.node_id] = node

async def simulate_distributed_system():
    """
    Simula el comportamiento de un sistema distribuido bajo diferentes configuraciones del Teorema CAP.
    """
    nodes = {i: Node(i, {}) for i in range(5)}
    for node in nodes.values():
        node.nodes = nodes

    leader_node = nodes[0]

    print("\n--- Escenario 1: Consistencia y Tolerancia a Particiones (CP) ---")
    start_time = time.time()
    
    # Simulación de operaciones en el sistema distribuido
    await leader_node.request_vote()
    await leader_node.append_entries([{'key': 'x', 'value': 1}])

    # Simulación de una partición de red
    partitioned_nodes = [nodes[1], nodes[2]]
    await leader_node.simulate_network_partition(partitioned_nodes)
    
    # Intentar escribir durante la partición
    await leader_node.append_entries([{'key': 'y', 'value': 2}])

    # Curación de la partición de red
    await leader_node.heal_network_partition(partitioned_nodes)

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
    for node in nodes.values():
        print(f'Node {node.node_id} data store: {node.data_store}')

    print("\n--- Escenario 2: Disponibilidad y Tolerancia a Particiones (AP) ---")
    start_time = time.time()

    # Resetear el sistema
    for node in nodes.values():
        node.data_store = {}
        node.log = []
        node.current_term = 0
        node.voted_for = None
        node.commit_index = 0
        node.version = 0

    # Configurar el sistema para priorizar disponibilidad
    for node in nodes.values():
        node.is_available = True

    # Simulación de operaciones en el sistema distribuido
    await leader_node.append_entries([{'key': 'x', 'value': 1}])

    # Simulación de una partición de red
    partitioned_nodes = [nodes[1], nodes[2]]
    await leader_node.simulate_network_partition(partitioned_nodes)

    # Intentar escribir durante la partición
    await leader_node.append_entries([{'key': 'y', 'value': 2}])
    await partitioned_nodes[0].append_entries([{'key': 'z', 'value': 3}])

    # Curación de la partición de red
    await leader_node.heal_network_partition(partitioned_nodes)

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
    for node in nodes.values():
        print(f'Node {node.node_id} data store: {node.data_store}')

    print("\n--- Escenario 3: Consistencia y Disponibilidad (CA) ---")
    start_time = time.time()

    # Resetear el sistema
    for node in nodes.values():
        node.data_store = {}
        node.log = []
        node.current_term = 0
        node.voted_for = None
        node.commit_index = 0
        node.version = 0

    # Configurar el sistema para priorizar consistencia y disponibilidad
    for node in nodes.values():
        node.is_available = True

    # Simulación de operaciones en el sistema distribuido
    await leader_node.append_entries([{'key': 'x', 'value': 1}])

    # Intentar escribir y leer sin particiones
    await leader_node.append_entries([{'key': 'y', 'value': 2}])
    await leader_node.read_data('y', leader_node.node_id)

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
    for node in nodes.values():
        print(f'Node {node.node_id} data store: {node.data_store}')

if __name__ == '__main__':
    asyncio.run(simulate_distributed_system())
