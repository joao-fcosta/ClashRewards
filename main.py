import discord
from discord.ext import commands
import os
import requests

from core.config import DISCORD_TOKEN
from keep_alive import keep_alive

class MainBot(commands.Bot):
    def __init__(self):
        # Usamos commands.Bot que dá muito mais controle sobre a arquitetura
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        # Aqui você registra todas as suas rotas futuras
        await self.load_extension("cogs.clash_cmds")
        
        # Sincroniza os comandos Slash
        await self.tree.sync()

    async def on_ready(self):
        print(f'✅ Bot conectado como {self.user}!')
        
        # Imprime o IP do Render (se estiver na nuvem)
        try:
            meu_ip = requests.get('https://api.ipify.org').text
            print(f"🌐 IP do Servidor: {meu_ip}")
        except:
            pass

if __name__ == "__main__":
    keep_alive()  # Inicia o servidor Flask em segundo plano
    
    bot = MainBot()
    bot.run(DISCORD_TOKEN)