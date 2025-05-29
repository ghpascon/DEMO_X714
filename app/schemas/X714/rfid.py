from app.schemas.logger import log_error, log_info

class RfidCommands:
    async def start_inventory(self):
        self.write("#READ:ON")

    async def stop_inventory(self):
        self.write("#READ:OFF")

    async def clear_tags(self):
        self.write("#CLEAR")
    
    async def config_reader(self, power=None, session=None):
        set_cmd = "#set_cmd:"

        if power is not None:
            set_cmd += f"read_power:{power}|"
        
        if session is not None:
            set_cmd += f"session:{session}|"        
        
        self.write(set_cmd)