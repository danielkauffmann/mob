import discord
from itertools import cycle

positive_emojis_list = cycle(["👍", "🆗", "🤙", "👌", "👊", "🆒", "✅"]) 
negative_emojis_list = cycle(["🚫", "🛑", "❌", "⛔"])
status_list = cycle(["Estudando...", "Navegando no Moodle", "Descobrindo tarefas", "Dominando o mundo", "Reduzindo as suas faltas", "Calculando as suas médias"])

footer = "Created with 💖 by Mackenzie Students."
defaultcolor = 0x9f000c

# This file is created to style the bot messages
# Styling the check command from moodle.py
def check_command_style(dict, amount, color="", status=None):
    embed=discord.Embed(title=dict["modulename"] + " - " + amount, color= color if color else defaultcolor)
    embed.set_thumbnail(url="https://logodownload.org/wp-content/uploads/2017/09/mackenzie-logo-3.png")
    embed.add_field(name="Matéria", value=dict["fullname"], inline=True)
    embed.add_field(name="Nome da tarefa", value=dict["name"], inline=True)

    if status == 1:
        if dict["hwstatus"] == "Tarefa entregue":
            embed.set_author(name=dict["hwstatus"],icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Checkmark_green.svg/1200px-Checkmark_green.svg.png")
        else:
            embed.set_author(name=dict["hwstatus"],icon_url="https://i1.pngguru.com/preview/326/505/102/red-cross-emoji-discord-logo-line-soviet-union-material-property-symbol-png-clipart.jpg")


    if dict["description"] != "Descrição não disponível":
        embed.add_field(name="Descrição", value=dict["description"], inline=False)
        embed.add_field(name="Tipo de tarefa", value=dict["modulename"], inline=True)
    else:
        embed.add_field(name="Tipo de tarefa", value=dict["modulename"], inline=False)

    embed.add_field(name="Data de entrega", value=dict["deadline"], inline=True)
    embed.add_field(name="Link", value=dict["link"], inline=False)
    embed.add_field(name="Professor", value=dict["author"], inline=False)
    embed.set_footer(text=footer)
    return embed


# Creating a template for messages
def main_messages_style(name="", message="", emote="", color=""):
    message = f"**{message}**" if message != "" else message
    embed=discord.Embed(title=name, description=f"{message} {emote if emote != '' else emote}",
    color= color if color else defaultcolor)
    embed.set_author(name="")
    embed.set_footer(text=footer)
    return embed

