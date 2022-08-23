import discord
import aiosqlite
from characters import characters

# used for editing database

o = ["Summary", "Mainstats", "Substats", "Talents", "Artifacts", "Resources"]
options = [discord.SelectOption(label=c, value=c) for c in o]

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
        await interaction.response.send_modal(Text(self))


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, row=2)
    async def confirm_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        lowerField = self.field.lower()
        i = characters.index(self.character)
        oldValue = self.data[lowerField][i]
        self.data[lowerField][i] = self.newValue
        async with aiosqlite.connect("lament.db") as con:
            cursor = await con.cursor()
            print(self.field, self.newValue, self.character)
            query = f"""UPDATE character SET {self.field.lower()}='{self.newValue}' where characterName='{self.character}'"""
            print(query)
            await cursor.execute(query)
        await interaction.response.send_message(f"Replaced value {oldValue} in field {self.field} with {self.newValue} for {self.character}", ephemeral=True)
        self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey, row=2)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.stop()

class Text(discord.ui.Modal):

    def __init__(self, parent: Edit):
        inputText = discord.ui.InputText(style=discord.InputTextStyle.long, label="New value of field")
        self.parent = parent
        super().__init__(inputText, title="New value")

    async def callback(self, interaction: discord.Interaction):
        self.parent.newValue = self.children[0].value
        await interaction.response.defer()




