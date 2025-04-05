import discord
from discord.ext import commands
from discord import app_commands
import json
import os

PREFIXO_PATH = "data/prefixos.json"
CANAIS_PATH = "data/canais.json"

def salvar_prefixo(guild_id, novo_prefixo):
    with open(PREFIXO_PATH, "r") as f:
        prefixos = json.load(f)
    prefixos[str(guild_id)] = novo_prefixo
    with open(PREFIXO_PATH, "w") as f:
        json.dump(prefixos, f, indent=4)

def salvar_canais(guild_id, canais_ids):
    with open(CANAIS_PATH, "r") as f:
        canais = json.load(f)
    canais[str(guild_id)] = canais_ids
    with open(CANAIS_PATH, "w") as f:
        json.dump(canais, f, indent=4)

class ConfiguracaoView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=180)
        self.bot = bot
        self.guild = guild

        self.add_item(SelecionarCanais(bot, guild))
        self.add_item(MudarPrefixo())

class SelecionarCanais(discord.ui.Select):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild

        options = [
            discord.SelectOption(
                label=canal.name,
                value=str(canal.id)
            )
            for canal in guild.text_channels
        ]

        super().__init__(
            placeholder="Selecione os canais permitidos...",
            min_values=1,
            max_values=len(options),
            options=options,
            custom_id="select_canais"
        )

    async def callback(self, interaction: discord.Interaction):
        salvar_canais(self.guild.id, self.values)
        canais_mention = ", ".join(f"<#{cid}>" for cid in self.values)
        await interaction.response.send_message(f"✅ Canais permitidos atualizados: {canais_mention}", ephemeral=True)

class MudarPrefixo(discord.ui.Modal, title="Alterar Prefixo"):
    novo_prefixo = discord.ui.TextInput(label="Novo prefixo", placeholder="#", max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        salvar_prefixo(interaction.guild.id, self.novo_prefixo.value)
        await interaction.response.send_message(f"✅ Prefixo alterado para `{self.novo_prefixo.value}`", ephemeral=True)

class Configuracao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="configuracao")
    async def config_texto(self, ctx):
        view = ConfiguracaoView(self.bot, ctx.guild)
        await ctx.send("🔧 Painel de configuração:", view=view)

    @app_commands.command(name="configuracao", description="Abra o painel de configuração do bot")
    async def config_slash(self, interaction: discord.Interaction):
        view = ConfiguracaoView(self.bot, interaction.guild)
        await interaction.response.send_message("🔧 Painel de configuração:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Configuracao(bot))
