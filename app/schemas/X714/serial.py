import asyncio
import serial_asyncio
from .on_receive import OnReceive
import time
from app.core.config import settings
from app.schemas.logger import log_error, log_info
from .rfid import RfidCommands

class Serial(asyncio.Protocol, OnReceive, RfidCommands):
    def __init__(self, port: str, baudrate: int):
        self.transport = None
        self.port = port
        self.baudrate = baudrate
        self.on_con_lost = None
        self.rx_buffer = bytearray()
        self.last_byte_time = None

        self.door = None
        self.card_id = None
        self.is_connected = False
        self.is_reading = False
        self.tags = {}
        
    def connection_made(self, transport):
        self.transport = transport
        self.is_connected = True
        log_info("✅ Conexão serial estabelecida com sucesso.")

    def data_received(self, data):
        self.rx_buffer += data

        while b'\n' in self.rx_buffer:
            idx = self.rx_buffer.index(b'\n') 
            pacote = self.rx_buffer[:idx]
            self.rx_buffer = self.rx_buffer[idx+1:]

            print(f"📦 Pacote recebido (até \\n): {pacote.decode(errors='ignore').strip()}")
            asyncio.create_task(self.on_receive(pacote))

    def connection_lost(self, exc):
        log_error("⚠️ Conexão serial perdida.")
        self.transport = None
        self.is_connected = False

        if self.on_con_lost:
            self.on_con_lost.set()

    def write(self, to_send, verbose = True):
        if self.transport:
            if verbose:
                log_info(f"📤 Enviando: {to_send}")
            if isinstance(to_send, str):
                to_send += '\n' 
                to_send = to_send.encode()  # converte string para bytes
            self.transport.write(to_send)
        else:
            log_error("❌ Tentativa de envio falhou: conexão não estabelecida.")

    async def connect(self):
        """Loop de conexão/reconexão serial"""
        loop = asyncio.get_running_loop()

        while True:
            self.on_con_lost = asyncio.Event()

            try:
                print(f"🔌 Tentando conectar em {self.port} a {self.baudrate} bps...")
                await serial_asyncio.create_serial_connection(
                    loop, lambda: self, self.port, baudrate=self.baudrate
                )
                log_info("🟢 Conectado com sucesso.")
                await self.on_con_lost.wait()
                print("🔄 Conexão perdida. Tentando reconectar...")
            except Exception as e:
                log_error(f"❌ Erro ao conectar: {e}")

            print("⏳ Aguardando 3 segundos antes de tentar novamente...")
            await asyncio.sleep(3)


reader = Serial(port=settings.PORT, baudrate=settings.BAUDRATE)
