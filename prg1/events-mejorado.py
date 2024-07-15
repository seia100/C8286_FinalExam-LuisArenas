import asyncio
import logging
from queue import PriorityQueue
import threading

# Configuración del registro de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constructor de eventos
class Event:
    def __init__(self, priority, event_type, data):
        self.priority = priority
        self.event_type = event_type
        self.data = data

    def __lt__(self, other):
        return self.priority < other.priority

# Simulación del cuaderno de notebook
class Notebook:
    def __init__(self):
        self.cells = []  # Lista de celdas de código
        self.event_queue = PriorityQueue()  # Cola de eventos con prioridad
        self.state = {}  # Estado compartido para la ejecución de celdas
        self.lock = threading.Lock()  # Bloqueo para asegurar operaciones seguras en concurrencia

    def add_cell(self, cell):
        """
        Agrega una nueva celda de código al notebook.
        """
        with self.lock:
            self.cells.append(cell)
        logging.info(f'Cell added: {cell}')

    def update_state(self, key, value):
        """
        Actualiza el estado compartido con una nueva clave y valor.
        """
        with self.lock:
            self.state[key] = value
        logging.info(f'State updated: {key} = {value}')
        print(f'State updated: {key} = {value}')  # Output para la consola

    async def execute_cell(self, cell):
        """
        Ejecuta una celda de código en el estado compartido.
        """
        try:
            exec(cell, self.state)
            logging.info(f'Executed cell: {cell}')
            print(f'Executed cell: {cell}')  # Output para la consola
        except Exception as e:
            logging.error(f'Error executing cell: {cell}, Error: {e}')
            print(f'Error executing cell: {cell}, Error: {e}')  # Output para la consola

    async def handle_event(self, event):
        """
        Maneja los eventos según su tipo.
        """
        if event.event_type == 'execute_cell':
            await self.execute_cell(event.data)
        elif event.event_type == 'update_state':
            self.update_state(*event.data)
        else:
            logging.warning(f'Unknown event type: {event.event_type}')
            print(f'Unknown event type: {event.event_type}')  # Output para la consola

    async def event_loop(self):
        """
        Bucle principal de eventos que maneja y procesa eventos de la cola.
        """
        while True:
            if not self.event_queue.empty():
                event = self.event_queue.get()
                await self.handle_event(event)
            await asyncio.sleep(0.1)

    def add_event(self, event):
        """
        Agrega un nuevo evento a la cola de eventos.
        """
        self.event_queue.put(event)
        logging.info(f'Event added: {event.event_type} with priority {event.priority}')
        print(f'Event added: {event.event_type} with priority {event.priority}')  # Output para la consola

# Simulación de interacciones de usuario
async def user_interactions(notebook):
    """
    Simula interacciones del usuario con el notebook.
    """
    notebook.add_event(Event(priority=1, event_type='update_state', data=('var1', 10)))
    notebook.add_event(Event(priority=2, event_type='execute_cell', data="print('Hello, world!')"))
    notebook.add_event(Event(priority=1, event_type='execute_cell', data="print(var1)"))

# Ejecución del sistema
async def main():
    """
    Función principal para iniciar el sistema de notebook y las interacciones del usuario.
    """
    notebook = Notebook()
    await asyncio.gather(
        notebook.event_loop(),
        user_interactions(notebook)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Shutting down the event loop.')
        print('Shutting down the event loop.')  # Output para la consola
