import discord
from discord import AutocompleteContext, bot, option
import sqlite3
import pandas as pd

def results_to_list(results):
    return [_[0] for _ in results.fetchall()]

con = sqlite3.connect("lament.db")
cursor = con.cursor()
data = pd.read_sql("SELECT characterName, element, summary, mainstats, substats, talents, artifacts, resources, image FROM character", con)
elements = ["pyro", "hydro", "electro", "cryo", "geo", "anemo", "dendro"]

result = cursor.execute("""SELECT characterName from character""")
characters = results_to_list(result)
characterList = characters
colors = {"pyro": discord.Color.from_rgb(178, 89, 63),
          "hydro": discord.Color.from_rgb(57, 112, 184),
          "electro": discord.Color.from_rgb(123, 81, 172),
          "cryo": discord.Color.from_rgb(118, 213, 229),
          "geo": discord.Color.from_rgb(189, 152, 71),
          "anemo": discord.Color.from_rgb(56, 170, 171),
          "dendro": discord.Color.from_rgb(165, 200, 59)} # TODO get actual color

# autocomplete helper function for commands that are based on characters
async def get_characters(ctx: AutocompleteContext):
    return [c for c in characters if c.lower().startswith(ctx.value.lower())]


