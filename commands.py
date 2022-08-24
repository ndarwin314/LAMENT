from discord import AutocompleteContext
import sqlite3
import pandas as pd

con = sqlite3.connect("lament.db")
cursor = con.cursor()
commandData = pd.read_sql("SELECT commandName, title, description, subtitle, response, image FROM commands", con)
commandList = commandData["commandName"]

# autocomplete helper function for commands that are based on characters
async def get_characters(ctx: AutocompleteContext):
    return [c for c in commandList if c.lower().startswith(ctx.value.lower())]