import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from datetime import datetime, timezone
from flask import Flask
from threading import Thread

# Mantem o host acordado 24h
app = Flask('')

@app.route('/')
def home():
    return "Bot esta vivo"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

BOT_TOKEN = os.getenv('BOT_TOKEN')
WELCOME_CHANNEL_NAME = '┌membros┐'
RULES_CHANNEL_NAME = '┌regras┐'

# ID do teu servidor
SEU_SERVER_ID = 1508984653355159813

def build_welcome_embed(member):
    rules_channel = discord.utils.get(member.guild.text_channels, name=RULES_CHANNEL_NAME)

    embed = discord.Embed(
        title=f"[+] BEM-VINDO A EYE SOCIETY",
        description=(
            f"{member.mention}, voce acabou de entrar na sociedade.\n\n"
            f"[1] -> Leia {rules_channel.mention} para nao tomar ban\n"
            f"[2] -> Se apresente no chat e cole com a galera"
        ),
        color=0x8B00FF
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    if member.guild.icon:
        embed.set_footer(text=f"[SECRETMASTER] Esta de olho | Membro #{member.guild.member_count}",
                         icon_url=member.guild.icon.url)
    else:
        embed.set_footer(text=f"[SECRETMASTER] Esta de olho | Membro #{member.guild.member_count}")

    embed.add_field(name="[CARGO]", value=member.top_role.mention, inline=True)
    embed.add_field(name="[ENTROU]", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)

    return embed

async def send_welcome(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel is None:
        channel = member.guild.system_channel
    if channel:
        embed = build_welcome_embed(member)
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot {bot.user} esta online!')

    guild = bot.get_guild(SEU_SERVER_ID)
    if not guild:
        print("Erro: Server ID incorreto")
        return

    # Pega quem entrou nos ultimos 10 minutos enquanto o bot tava off
    now = datetime.now(timezone.utc)
    async for entry in guild.audit_logs(limit=50, action=discord.AuditLogAction.member_join):
        membro = entry.target
        tempo_desde_entrada = (now - membro.joined_at.replace(tzinfo=timezone.utc)).total_seconds()

        if tempo_desde_entrada < 600:
            await send_welcome(membro)
            await asyncio.sleep(1)

@bot.event
async def on_member_join(member):
    await send_welcome(member)

@app_commands.command(name="test", description="Testa a mensagem de boas-vindas")
async def test_welcome(interaction: discord.Interaction):
    embed = build_welcome_embed(interaction.user)
    await interaction.response.send_message("Preview:", ephemeral=True)
    channel = discord.utils.get(interaction.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel is None:
        channel = interaction.guild.system_channel
    await channel.send(embed=embed)

@app_commands.command(name="welcome", description="Manda boas-vindas manual pra um ID")
@app_commands.describe(user_id="ID do usuario que entrou")
async def welcome_command(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer(ephemeral=True)

    try:
        member = await interaction.guild.fetch_member(int(user_id))
    except:
        await interaction.followup.send("ID invalido ou usuario nao esta no servidor", ephemeral=True)
        return

    await send_welcome(member)
    await interaction.followup.send(f"Boas-vindas enviadas pra {member.mention}", ephemeral=True)

bot.tree.add_command(test_welcome)
bot.tree.add_command(welcome_command)
bot.run(BOT_TOKEN)
