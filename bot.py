import discord
from discord.app_commands import CommandTree
import aiohttp
import os
from keep_alive import keep_alive
import urllib.request

try:
    with urllib.request.urlopen('https://api.ipify.org') as response:
        meu_ip_render = response.read().decode().strip()
    print(f"🌐 ATENÇÃO! O IP público deste servidor no Render é: {meu_ip_render}")
except Exception as e:
    print(f"Não foi possível obter o IP: {e}")
    
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SUPERCELL_API_KEY = os.getenv("SUPERCELL_API_KEY")

BASE_LEVELS = {
    "common": 1, "rare": 3, "epic": 6,
    "legendary": 9, "champion": 11
}

# ==========================================
# FUNÇÕES DE REGRA DE NEGÓCIO (Mantidas)
# ==========================================
def calcular_novo_nivel_rei(cartas: list) -> int:
    niveis_absolutos = []
    for carta in cartas:
        raridade = carta.get("rarity", "common")
        nivel = BASE_LEVELS.get(raridade, 1) + carta.get("level", 1) - 1
        niveis_absolutos.append(nivel)
        
    niveis_absolutos.sort(reverse=True)
    
    def tem_cartas(quantidade, nivel_minimo):
        if len(niveis_absolutos) >= quantidade:
            return niveis_absolutos[quantidade - 1] >= nivel_minimo
        return False

    if tem_cartas(14, 15): return 16
    if tem_cartas(13, 14): return 15
    if tem_cartas(12, 13): return 14
    if tem_cartas(11, 12): return 13
    if tem_cartas(11, 11): return 12
    if tem_cartas(10, 10): return 11
    if tem_cartas(10, 9):  return 10
    if tem_cartas(10, 8):  return 9
    if tem_cartas(10, 7):  return 8
    if tem_cartas(10, 6):  return 7
    if tem_cartas(10, 5):  return 6
    if tem_cartas(10, 4):  return 5
    if tem_cartas(10, 3):  return 4
    if tem_cartas(9, 2):   return 3
    if tem_cartas(9, 1):   return 2
    return 1

def calcular_nivel_rei_antigo(exp: int) -> int:
    if exp >= 75: return 16
    if exp >= 54: return 15
    if exp >= 42: return 14
    if exp >= 38: return 13
    if exp >= 34: return 12
    if exp >= 30: return 11
    if exp >= 26: return 10
    if exp >= 22: return 9
    if exp >= 18: return 8
    if exp >= 14: return 7
    if exp >= 10: return 6
    if exp >= 7: return 5
    if exp >= 5: return 4
    if exp >= 3: return 3
    if exp >= 2: return 2
    return 1

def calcular_nivel_colecao(cartas_normais: list, tropas_torre: list) -> int:
    nivel_colecao = 0
    todas_cartas = cartas_normais + tropas_torre
    for carta in todas_cartas:
        raridade = carta.get("rarity", "common")
        nivel_colecao += BASE_LEVELS.get(raridade, 1) + carta.get("level", 1) - 1
        if raridade == "champion": nivel_colecao += 5
        if carta.get("evolutionLevel", 0) > 0: nivel_colecao += 5
    return nivel_colecao

def calcular_recompensas(nivel: int) -> dict:
    if nivel >= 2001: return {"gems": "5.000", "baus": 3, "bandeiras": 6, "pele": 1}
    elif nivel >= 1801: return {"gems": "4.500", "baus": 3, "bandeiras": 6, "pele": 0}
    elif nivel >= 1601: return {"gems": "4.000", "baus": 2, "bandeiras": 5, "pele": 0}
    elif nivel >= 1401: return {"gems": "3.500", "baus": 2, "bandeiras": 4, "pele": 0}
    elif nivel >= 1201: return {"gems": "3.000", "baus": 1, "bandeiras": 3, "pele": 0}
    elif nivel >= 1001: return {"gems": "2.500", "baus": 1, "bandeiras": 2, "pele": 0}
    elif nivel >= 801: return {"gems": "2.000", "baus": 1, "bandeiras": 1, "pele": 0}
    elif nivel >= 601: return {"gems": "1.500", "baus": 0, "bandeiras": 0, "pele": 0}
    elif nivel >= 401: return {"gems": "1.000", "baus": 0, "bandeiras": 0, "pele": 0}
    elif nivel >= 201: return {"gems": "750", "baus": 0, "bandeiras": 0, "pele": 0}
    elif nivel >= 20: return {"gems": "500", "baus": 0, "bandeiras": 0, "pele": 0}
    return {"gems": "0", "baus": 0, "bandeiras": 0, "pele": 0}

# ==========================================
# CONFIGURAÇÃO DO BOT DO DISCORD
# ==========================================
class ClashClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = ClashClient()

@client.event
async def on_ready():
    print(f'✅ Bot conectado como {client.user}!')

# ==========================================
# COMANDO SLASH: /status
# ==========================================
@client.tree.command(name="status", description="Calcula as recompensas e o novo nível do Clash Royale")
async def status_clash(interaction: discord.Interaction, tag: str):
    await interaction.response.defer()

    clean_tag = tag.replace("#", "").upper()
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {SUPERCELL_API_KEY}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                await interaction.followup.send(f"❌ Erro ao buscar jogador. Verifique a Tag: `#{clean_tag}`")
                return
            
            player_data = await response.json()

    cartas = player_data.get("cards", [])
    tropas = player_data.get("supportCards", [])
    
    nivel_colecao = calcular_nivel_colecao(cartas, tropas)
    recompensas = calcular_recompensas(nivel_colecao)
    novo_nivel_rei = calcular_novo_nivel_rei(cartas)
    nivel_atual_rei = calcular_nivel_rei_antigo(player_data.get("expLevel", 1))
    nome_jogador = player_data.get("name", "Desconhecido")

    embed = discord.Embed(
        title=nome_jogador,
        color=discord.Color.blue(),
        description=f"Tag: `#{clean_tag}`\n📰 [Baseado no artigo da atualização](https://supercell.com/en/games/clashroyale/blog/news/new-collection-levels-and-mastery-changes/)"
    )
    
    embed.add_field(name="📈 Nível de Coleção", value=f"**{nivel_colecao}**", inline=False)
    embed.add_field(name="👑 Torre do Rei", value=f"Antigo: Nível **{nivel_atual_rei}**\nNovo: Nível **{novo_nivel_rei}**", inline=False)

    linhas_recompensas = []
    
    if recompensas['gems'] != "0":  
        linhas_recompensas.append(f"💎 Gemas: **{recompensas['gems']}**")
        
    if recompensas['baus'] > 0:
        linhas_recompensas.append(f"📦 Baús Mágicos de 5★: **{recompensas['baus']}**")
        
    if recompensas['bandeiras'] > 0:
        linhas_recompensas.append(f"🚩 Ilustrações de Bandeiras: **{recompensas['bandeiras']}**")
        
    if recompensas['pele'] > 0:
        linhas_recompensas.append(f"🏰 Visual da Torre: **{recompensas['pele']}**")

    if linhas_recompensas:
        recomp_texto = "\n".join(linhas_recompensas)
    else:
        recomp_texto = "Nenhuma recompensa atingida ainda. Continue evoluindo!"

    embed.add_field(name="🏆 Recompensas da Celebração", value=recomp_texto, inline=False)

    embed.set_footer(text="Bot de Consulta Clash Royale")

    await interaction.followup.send(embed=embed)

keep_alive()
client.run(DISCORD_TOKEN)