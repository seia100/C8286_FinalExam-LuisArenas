import asyncio
import logging
from queue import PriorityQueue, Queue
import threading

# Configuración del registro de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# constructor de eventos
class Event:
    def __init__(self, priority, event_type, data):
        self.priority = priority
        self.event_type = event_type
        self.data = data

    def __lt__(self, other):
        return self.priority < other.priority

# simulacion del cuaderno de notebook
# cuya idea inicial es de agregar una celda, actualizaciones de estado
# ejecutar de manera asincrona las celdas, actualizaicones de estado de menara constante
#  y agregar un nuevo evento 
class Notebook:
    def __init__(self):
        self.cells = []
        self.event_queue = PriorityQueue()
        self.state = {}
        self.lock = threading.Lock()

    def add_cell(self, cell):
        with self.lock:
            self.cells.append(cell)
        logging.info(f'Cell added: {cell}')

    def update_state(self, key, value):
        with self.lock:
            self.state[key] = value
        logging.info(f'State updated: {key} = {value}')
        print(f'State updated: {key} = {value}')  # Output para la consola

    async def execute_cell(self, cell):
        try:
            exec(cell, self.state)
            logging.info(f'Executed cell: {cell}')
            print(f'Executed cell: {cell}')  # Output para la consola
        except Exception as e:
            logging.error(f'Error executing cell: {cell}, Error: {e}')
            print(f'Error executing cell: {cell}, Error: {e}')  # Output para la consola

    async def handle_event(self, event):
        if event.event_type == 'execute_cell':
            await self.execute_cell(event.data)
        elif event.event_type == 'update_state':
            self.update_state(*event.data)
        else:
            logging.warning(f'Unknown event type: {event.event_type}')
            print(f'Unknown event type: {event.event_type}')  # Output para la consola

    async def event_loop(self):
        while True:
            if not self.event_queue.empty():
                event = self.event_queue.get()
                await self.handle_event(event)
            await asyncio.sleep(0.1)

    def add_event(self, event):
        self.event_queue.put(event)
        logging.info(f'Event added: {event.event_type} with priority {event.priority}')
        print(f'Event added: {event.event_type} with priority {event.priority}')  # Output para la consola

# Simulación de interacciones de usuario
async def user_interactions(notebook):
    notebook.add_event(Event(priority=1, event_type='update_state', data=('var1', 10)))
    notebook.add_event(Event(priority=2, event_type='execute_cell', data="print('Hello, world!')"))
    notebook.add_event(Event(priority=1, event_type='execute_cell', data="print(var1)"))

# Ejecución del sistema
async def main():
    notebook = Notebook()
    await asyncio.gather(
        notebook.event_loop(),
        user_interactions(notebook)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    # tecla ctrl + C
    except KeyboardInterrupt:
        logging.info('Shutting down the event loop.')
        print('Shutting down the event loop.')  # Output para la consola
