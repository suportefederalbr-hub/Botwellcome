import discord
from discord.ext import commands
from discord import app_commands
import os
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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot {bot.user} esta online!')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel is None:
        channel = member.guild.system_channel
    embed = build_welcome_embed(member)
    await channel.send(embed=embed)

@app_commands.command(name="test", description="Testa a mensagem de boas-vindas")
async def test_welcome(interaction: discord.Interaction):
    embed = build_welcome_embed(interaction.user)
    await interaction.response.send_message("Preview:", ephemeral=True)
    channel = discord.utils.get(interaction.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel is None:
        channel = interaction.guild.system_channel
    await channel.send(embed=embed)

bot.tree.add_command(test_welcome)
bot.run(BOT_TOKEN)