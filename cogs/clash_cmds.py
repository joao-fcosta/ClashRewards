import discord
from discord.ext import commands
from discord import app_commands
from services.supercell_api import fetch_player_data
from services import calculator

class ClashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ==========================================
    # COMANDO 1: COLEÇÃO
    # ==========================================
    @app_commands.command(name="colecao", description="Calcula as recompensas e o novo nível de coleção do Clash Royale")
    async def status_clash(self, interaction: discord.Interaction, tag: str):
        await interaction.response.defer()

        # 1. Busca os dados usando a camada de Serviço
        player_data, clean_tag = await fetch_player_data(tag)
        
        if not player_data:
            await interaction.followup.send(f"❌ Erro ao buscar jogador. Verifique a Tag: `#{clean_tag}`")
            return

        # 2. Processa usando a camada de Negócio
        cartas = player_data.get("cards", [])
        tropas = player_data.get("supportCards", [])
        
        nivel_colecao = calculator.calcular_nivel_colecao(cartas, tropas)
        recompensas = calculator.calcular_recompensas(nivel_colecao)
        novo_nivel_rei = calculator.calcular_novo_nivel_rei(cartas)
        nivel_atual_rei = calculator.calcular_nivel_rei_antigo(player_data.get("expLevel", 1))
        nome_jogador = player_data.get("name", "Desconhecido")

        # 3. Monta o visual
        embed = discord.Embed(
            title=nome_jogador,
            color=discord.Color.blue(),
            description=f"Tag: `#{clean_tag}`\n📰 [Ler artigo da atualização](https://supercell.com/en/games/clashroyale/blog/news/new-collection-levels-and-mastery-changes/)"
        )
        
        embed.add_field(name="📈 Nível de Coleção", value=f"**{nivel_colecao}**", inline=False)
        embed.add_field(name="👑 Torre do Rei", value=f"Antigo: Nível **{nivel_atual_rei}**\nNovo: Nível **{novo_nivel_rei}**", inline=False)
        
        linhas_recompensas = []
        if recompensas['gems'] != "0": linhas_recompensas.append(f"💎 Gemas: **{recompensas['gems']}**")
        if recompensas['baus'] > 0: linhas_recompensas.append(f"📦 Baús Mágicos de 5★: **{recompensas['baus']}**")
        if recompensas['bandeiras'] > 0: linhas_recompensas.append(f"🚩 Ilustrações de Bandeiras: **{recompensas['bandeiras']}**")
        if recompensas['pele'] > 0: linhas_recompensas.append(f"🏰 Visual da Torre: **{recompensas['pele']}**")

        recomp_texto = "\n".join(linhas_recompensas) if linhas_recompensas else "Nenhuma recompensa atingida ainda. Continue evoluindo!"
        embed.add_field(name="🏆 Recompensas da Celebração", value=recomp_texto, inline=False)
        
        embed.set_footer(text="Bot de Consulta Clash Royale")

        await interaction.followup.send(embed=embed)
        
    # ==========================================
    # COMANDO 2: PRÓXIMO NÍVEL DO REI
    # ==========================================
    # Ajustado: removido o espaço do name (usando underline)
    @app_commands.command(name="proximo_nivel", description="Calcula qual a maneira mais rápida de subir o nível do rei")
    async def proximo_nivel_rei(self, interaction: discord.Interaction, tag: str):
        await interaction.response.defer()

        player_data, clean_tag = await fetch_player_data(tag)
        
        if not player_data:
            await interaction.followup.send(f"❌ Erro ao buscar jogador. Verifique a Tag: `#{clean_tag}`")
            return

        cartas = player_data.get("cards", [])
        nome_jogador = player_data.get("name", "Desconhecido")
        
        progresso = calculator.calcular_progresso_rei(cartas)

        # Ajustado: Criação do objeto embed que estava faltando!
        embed = discord.Embed(
            title=f"👑 Progresso do Rei - {nome_jogador}",
            color=discord.Color.gold(),
            description=f"Tag: `#{clean_tag}`"
        )

        if progresso["maximo"]:
            texto_progresso = "👑 **Nível Máximo Alcançado!** Você já está no topo."
        else:
            texto_progresso = (
                f"Rumo ao Nível **{progresso['proximo_nivel']}**\n"
                f"Falta upar: **{progresso['cartas_faltantes']} cartas** para o nível **{progresso['nivel_exigido']}**\n"
                f"Progresso: `{progresso['progresso_atual']}/{progresso['total_exigido']}`"
            )

        # Adiciona o campo no Embed do Discord
        embed.add_field(name="📊 Resumo", value=texto_progresso, inline=False)
        embed.set_footer(text="Bot de Consulta Clash Royale")

        await interaction.followup.send(embed=embed)

# Função obrigatória para o bot carregar este módulo
async def setup(bot):
    await bot.add_cog(ClashCommands(bot))