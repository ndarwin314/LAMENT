import discord
import aiosqlite
from characters import characterList, elements
from typing import Union

# used for editing database

o = ["Summary", "Mainstats", "Substats", "Talents", "Artifacts", "Resources"]
options = [discord.SelectOption(label=c, value=c) for c in o]
elementOptions = [discord.SelectOption(label=c.capitalize(), value=c) for c in elements]

class Edit(discord.ui.View):
    def __init__(self, character: str, data):
        super().__init__()
        self.character = character
        self.data = data
        self.newValue = None
        self.field = None

    @discord.ui.select(placeholder="Choose a Field", options=options, row=0)
    async def choose_field(self, select: discord.ui.Select, interaction: discord.Interaction):
        # we dont want to do anything right now
        self.field = select.values[0]
        await interaction.response.send_modal(EditBox(self, self.field))


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, row=2)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.newValue is None:
            await interaction.response.send_message(
                f"Type a character loser",
                ephemeral=True, delete_after=5)
        else:
            lowerField = self.field.lower()
            i = characterList.index(self.character)
            oldValue = self.data[lowerField][i]
            self.data[lowerField][i] = self.newValue
            async with aiosqlite.connect("lament.db") as con:
                cursor = await con.cursor()
                query = f"""UPDATE character SET {self.field.lower()}='{self.newValue}' where characterName='{self.character}'"""
                await cursor.execute(query)
                await con.commit()
            await interaction.response.send_message(
                f"Replaced value {oldValue} in field {self.field} with {self.newValue} for {self.character}",
                ephemeral=True, delete_after=5)
            #await interaction.message.delete(delay=5)
            self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        #TODO: this doesn't delete because bot can't see ephemeral messages or something, could leave it or make messages normal
        await interaction.response.send_message("Cancelling", ephemeral=True, delete_after=5)
        #await interaction.message.delete(delay=5)
        self.stop()

class EditBox(discord.ui.Modal):

    def __init__(self, parent: Edit, field: str):
        inputText = discord.ui.InputText(
            style=discord.InputTextStyle.long,
            label="New value of field",
            value=parent.data[field.lower()][characterList.index(parent.character)])
        self.parent = parent
        super().__init__(inputText, title="New value")

    async def callback(self, interaction: discord.Interaction):
        self.parent.newValue = self.children[0].value
        await interaction.response.defer()

class Add(discord.ui.View):
    def __init__(self, data):
        self.character = None
        self.element = None
        self.data = data
        super().__init__()


    @discord.ui.select(placeholder="Character element", options=elementOptions, row=1)
    async def choose_field(self, select: discord.ui.Select, interaction: discord.Interaction):
        # we dont want to do anything right now
        self.element = select.values[0]
        await interaction.response.send_modal(Character(self))


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, row=2)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        character = self.character
        if character is None:
            await interaction.response.send_message(
                f"Type a character loser",
                ephemeral=True, delete_after=5)
        elif character in characterList:
            await interaction.response.send_response(f"{character} already present, dumbass", ephemeral=True)
            self.stop()
        else:
            element = self.element
            characterList.append(self.character)
            # TODO: switch to concat since apparently append is deprecated, also this is kind of awful in general
            self.data.append({"characterName": character, "element": element}, ignore_index=True)
            async with aiosqlite.connect("lament.db") as con:
                cursor = await con.cursor()
                await cursor.execute("""INSERT INTO character VALUES (?,"","","","","","", "", ?) """, (character, element))
                await con.commit()
            await interaction.response.send_message(
                f"Added character, {self.character}, with element {self.element} to DB",
                ephemeral=True, delete_after=5)
            #await interaction.message.delete(delay=5)
            self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True, delete_after=5)
        #await interaction.message.delete(delay=5)
        self.stop()

class Character(discord.ui.Modal):
    def __init__(self, parent):
        inputText = discord.ui.InputText(
            style=discord.InputTextStyle.short,
            label="Name of character to add")
        self.parent = parent
        super().__init__(inputText, title="New character")

    async def callback(self, interaction: discord.Interaction):
        self.parent.character = self.children[0].value
        await interaction.response.defer()

class Delete(discord.ui.View):
    def __init__(self, data, character: str):
        self.character = character
        self.data = data
        super().__init__()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, row=2)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        characterList.remove(self.character)
        async with aiosqlite.connect("lament.db") as con:
            cursor = await con.cursor()
            await cursor.execute("""DELETE from character WHERE (characterName=?)""", (self.character,))
            await con.commit()
        await interaction.response.send_response(f"Successfully removed character, {self.character}, from database", ephemeral=True)
        #await interaction.message.delete(delay=5)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True, delete_after=5)
        #await interaction.message.delete(delay=5)
        self.stop()







