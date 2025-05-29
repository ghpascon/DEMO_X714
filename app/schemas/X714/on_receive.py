import asyncio
from app.schemas.logger import log_error, log_info

class OnReceive:
    async def on_receive(self, data):
        print(f"📥 Dados recebidos (bytes): {data}")
        data = data.decode(errors='ignore')
        log_info(f"📄 Dados como string: {data}")
        data = data.replace("\r","").replace("\n","")
        data = data.lower()

        if data.startswith("#read:"):
            self.is_reading = data.endswith("on")
                    
        elif data == "#tags_cleared":
            self.tags = {}
            log_info("Tags cleared")
                    
        elif data.startswith("#t+@"):
            tag = data[4:]
            epc,tid,ant,rssi = tag.split('|')
            current_tag = {
                "epc":epc,
                "tid":tid,
                "ant":ant,
                "rssi":rssi,
            }
            self.tags[epc] = current_tag