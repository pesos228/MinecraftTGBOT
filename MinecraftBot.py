from javascript import require


class MinecraftBot:
    _instance = None

    def __init__(self, host, username, version):
        self.mineflayer = require('mineflayer')
        self.bot = self.mineflayer.createBot({
            'host': host,
            'username': username,
            'version': version
        })
        MinecraftBot._instance = self

    @classmethod
    def get_instance(cls):
        return cls._instance

    def execute_command(self, command):
        self.bot.chat(command)
