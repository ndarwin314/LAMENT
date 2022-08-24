# local imports
import characters
from characters import data, colors, characterList
from commands import commandList, commandData
import probability
from database import Snail
import components
# discord api imports
import discord
from discord import option
# database related imports
import aiosqlite

# file handling related imports
import os
from dotenv import load_dotenv
# misc
import logging
from typing import Union
from random import choice

# enable logging, create a bot client and declare intents, connect to databases, and load environmental variables
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = discord.Bot(debug_guilds=[954468468894351450, 774889207704715285])

load_dotenv()
me = os.getenv("me")

def helper_command(func):
    async def inner(*args, **kwargs):
        ctx: discord.ApplicationContext = args["ctx"]
        if ctx.guild.id == 954468468894351450 or 971654143116726293 in [role.id for role in ctx.author.roles]:
            func(*args, **kwargs)
        else:
            await ctx.respond("Not helper L", ephemeral=True)

    return inner

# sets funny presence and sends message saying its running
@bot.event
async def on_ready():
    game = discord.Game("abyss in 85 seconds")
    await bot.change_presence(status=discord.Status.idle, activity=game)
    print(f"{bot.user} lets freaking go")

# sets up server specific database related info
@bot.event
async def on_guild_join(guild: discord.Guild):
    # TODO: change this to add column to DB
    server = Snail(snails={str(guild.me.id): 0}, server=guild.id).save()
    print("added document to database")

@bot.slash_command(description="Pull value of characters")
@option("character", description="Choose a character", autocomplete=characters.get_characters)
async def value(
        ctx: discord.ApplicationContext,
        character: str):
    index = characters.characters.index(character)
    embed = discord.Embed(title=f"{character} Summary", color=colors[data["element"][index]])
    processed = character.lower().replace(" ", "") + ".webp"
    embed.set_thumbnail(url=f"https://mathboi.net/static/{processed}")
    embed.add_field(name="Recommended main stats", value=data["mainstats"][index])
    embed.add_field(name="Recommended substats", value=data["substats"][index])
    embed.add_field(name="Recommended artifact sets", value=data["artifacts"][index])
    embed.add_field(name="Talent Priorities", value=data["talents"][index])
    embed.add_field(name="Summary", value=data["summary"][index], inline=False)
    embed.add_field(name="Resources", value=data["resources"][index])
    embed.set_author(name=me)
    await ctx.respond(embed=embed)

@discord.default_permissions(manage_messages=True)
@bot.slash_command(description="Edit pull command response")
@option("character", description="Choose a character", autocomplete=characters.get_characters)
async def edit(
        ctx: discord.ApplicationContext,
        character: str):
    await ctx.respond(ephemeral=True, view=components.Edit(character=character, data=data))

@discord.default_permissions(manage_messages=True)
@bot.slash_command(description="Add new character to DB")
async def add_character(ctx: discord.ApplicationContext):
    view = components.Add(data)
    await ctx.respond(ephemeral=True, view=view)


@discord.default_permissions(manage_messages=True)
@bot.slash_command(description="Remove character from DB")
@option("character", description="Character to remove", autocomplete=characters.get_characters)
async def delete_character(ctx: discord.ApplicationContext,
              character: str):
    await ctx.respond(ephemeral=True, view=components.Delete(data, character))


@bot.slash_command(description="Effective attack calculator")
@option("attack", description="Total attack on stats page", type=float)
@option("crit_rate", description="Crit rate on stats page", type=float)
@option("crit_damage", description="Crit damage on stats page", type=float)
async def eattack(ctx: discord.ApplicationContext,
                  attack: float,
                  crit_rate: float,
                  crit_damage :float):
    await ctx.respond(f"Effective attack for {attack} attack, {crit_rate} CR, and {crit_damage} CD is "
                      f"{round(attack *(1+crit_rate*crit_damage /10000), 2)}")

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if reaction.emoji == "🐌":
        guildid = reaction.message.guild.id
        authorid = author = str(reaction.message.author.id)
        async with aiosqlite.connect("lament.db") as con:
            cursor = await con.cursor()
            query = f"""SELECT `{guildid}` FROM snails WHERE id={authorid}"""
            results = await cursor.execute(query)
            results = await results.fetchone()
            snailCount = 1 if results is None else results[0] + 1
            query = f"""UPDATE snails SET `{guildid}`={snailCount} WHERE id={authorid}"""
            await cursor.execute(query)
            await con.commit()


@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if reaction.emoji == "🐌":
        guildid = reaction.message.guild.id
        authorid = str(reaction.message.author.id)
        async with aiosqlite.connect("lament.db") as con:
            cursor = await con.cursor()
            query = f"""SELECT `{guildid}` FROM snails WHERE id={authorid}"""
            results = await cursor.execute(query)
            results = await results.fetchone()
            snailCount = 1 if results is None else results[0]-1
            query = f"""UPDATE snails SET `{guildid}`={snailCount} WHERE id={authorid}"""
            await cursor.execute(query)
            await con.commit()

# helper function thats probably overkill for the snail command
def index_to_place(i: int):
    match i:
        case 0:
            return "🥇"
        case 1:
            return "🥈"
        case 2:
            return "🥉"
        case _:
            return f"**{i+1}**"


@bot.slash_command(description="Snail Counter")
async def snails(ctx: discord.ApplicationContext):
    server = ctx.guild.id
    id = ctx.guild.id
    async with aiosqlite.connect("lament.db") as con:
        cursor = await con.cursor()
        query = f"""SELECT id, `{id}` FROM snails"""
        results = await cursor.execute(query)
        await con.commit()
    results = await results.fetchall()
    snails = sorted(results, key=lambda p: p[1], reverse=True)
    embed = discord.Embed(title="Snail Leaderboard", color=discord.Colour.blurple(), description="Who is the slowest of them all?")
    embed.add_field(name="Snail King", value=f"{index_to_place(0)} {(await bot.fetch_user(snails[0][0])).name}: {snails[0][1]}", inline=False)
    bad = []
    for i in range(1, min(3, len(snails))):
        bad.append(f"{index_to_place(i)} {(await bot.fetch_user(snails[i][0])).name}: {snails[i][1]}\n")
    embed.add_field(name="Snail top 3", value="".join(bad),inline=False)
    bad = []
    for i in range(3, min(10, len(snails))):
        bad.append(f" {index_to_place(i)} {(await bot.fetch_user(snails[i][0])).name}: {snails[i][1]}\n")
    embed.add_field(name="Snail top 10", value="".join(bad), inline=False)
    embed.set_author(name=me)
    await ctx.respond(embed=embed)

# fancy formatting wow
@bot.slash_command(description="Odds of getting 5* from weapon or character banner")
@option("banner", description="Weapon or character banner", choices=["Character", "Weapon"])
@option("pity", description="Current pity on the banner", type=int, min_value=0, max_value=90)
@option("primo", description="Current number of primos", type=int, min_value=0)
@option("fate", description="Current number of fates", type=int, min_value=0)
@option("guarantee", description="Do you have a guarantee", type=bool)
async def wish(ctx: discord.ApplicationContext, banner: str, pity: int, primo: int, fate: int, guarantee: bool):
    wishes = int(primo / 160 + fate)
    embed = discord.Embed(title="Wish Probabilities", color=discord.Color.blurple())
    embed.set_author(name=me)
    func = probability.character if banner=="Character" else probability.weapon
    label = "Constellations" if banner=="Character" else "Refinements"
    if banner=="Weapon":
        pity = max(80, pity)
    results = func(wishes, guarantee, pity)
    bad = ["```\n", "|{:<16}| {:<13}|".format(label, "Probability")]
    for i in range(len(results)):
        embed.add_field(name="", value="")
        bad.append("|{:<16}| {:<13}|".format(i, str(results[i]) + "%"))
    bad.append("```")
    lineSeperator = "\n" + "|" + "-"*16 + "+" + "-"*14 + "|" + "\n"
    response = lineSeperator.join(bad)
    response = response.replace("|", "+", 2)
    response = response[::-1].replace("|", "+", 2)[::-1]
    await ctx.send_response(response, ephemeral=True)

@bot.slash_command(description="add :batchest:")
async def batchest(ctx: discord.ApplicationContext):
    await ctx.respond("🦇🌰")

@bot.slash_command(description="How does Dendro work")
async def dendro(ctx: discord.ApplicationContext):
    embed = discord.Embed(title="How does Dendro work?", description="Its complicated, here is an early guide https://docs.google.com/document/d/e/2PACX-1vRKcjJ7GXzosMQmQbScEsJEmzYIc4fyE3RfU6IiGLJWR6dloCZuuWSUQRlyJlbevoyBdABwfQ51Veks/pub", colour=colors["dendro"])
    embed.add_field(name="Does <x> work?", value="It needs to be tested on the live server.", inline=False)
    embed.add_field(name="Is Tighnari/Collei/DMC good?", value="Give time for testing.", inline=False)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/962218404566138950/1011791022554087504/unknown.png")
    #embed.set_image(url=)
    await ctx.respond(embed=embed)

@bot.slash_command(description="Extra commands, check it out!")
@option("name", description="Name of command", choices=commandList)
async def command(ctx: discord.ApplicationContext, name: str):
    index = characterList.index(name)
    embed = discord.Embed(
        title=commandData["title"][index],
        description=commandData["description"][index],
        color=discord.Color.blurple())
    """embed.add_field(
        name=commandData["subtitle"][index],
        value=commandData["response"][index]
    )"""
    embed.set_author(name=me)
    url = commandData["image"][index]
    if url:
        embed.set_image(url=url)
    await ctx.respond(embed=embed)

@discord.default_permissions(manage_messages=True)
@bot.slash_command(description="add embed commands")
async def add_command(ctx: discord.ApplicationContext):
    await ctx.send_response(view=components.AddCommand(commandData))

@bot.slash_command(description="Four stars you should build.")
async def four_star(ctx: discord.ApplicationContext):
    # TODO: make this an embed
    await ctx.respond("https://docs.google.com/document/d/10lnOwQFIUDGcFdo9KIJ73BeeefmVvtISRA8KEnpjP2U/edit")

@bot.slash_command(description="Xiao")
async def xiao(ctx: discord.ApplicationContext):
    await ctx.respond("https://www.youtube.com/watch?v=0vci3o7mf2A")

@bot.slash_command(description="zy0x")
async def socks(ctx: discord.ApplicationContext):
    await ctx.respond("is shorter than xiao")

# TODO: move these to separate file or database
internationalList = ["https://www.youtube.com/watch?v=-YTMfF1sEcU",
                     "https://www.youtube.com/watch?v=XCyRLrCw_eA",
                     "https://www.youtube.com/watch?v=Mx0CWjD3QO8",
                     "https://www.youtube.com/watch?v=Mx0CWjD3QO8",
                     "https://www.youtube.com/watch?v=ktpyoDBJH00",
                     "https://www.youtube.com/watch?v=hjirqmI5aQ8",
                     "https://www.youtube.com/watch?v=yGhbiombxi8",
                     "https://www.youtube.com/watch?v=83idEzmcTTw",
                     "https://www.youtube.com/watch?v=p3YQZ6lMor4",
                     "https://www.youtube.com/watch?v=AZ8ZNRn-vGI",
                     "https://www.youtube.com/watch?v=OZNiYbYHe1s",
                     "https://www.youtube.com/watch?v=v-p0Zc0AK14",
                     "https://www.youtube.com/watch?v=mLcKkohdDp8",
                     "https://www.youtube.com/watch?v=VOSwrhbDMP0",
                     "https://www.youtube.com/watch?v=ooB8yGU5kig",
                     "https://www.youtube.com/watch?v=oaDu4oQo9JY",
                     "https://www.youtube.com/watch?v=6awXgKJExXE",
                     "https://www.youtube.com/watch?v=o-XgTA7v8Ro"]
@bot.slash_command(description="The best team")
async def international(ctx: discord.ApplicationContext):
    await ctx.respond(choice(internationalList))

creativeList = ["https://cdn.discordapp.com/attachments/895601055742693376/940231755179364352/Raiden_National.png",
"https://cdn.discordapp.com/attachments/895601055742693376/940233047276654602/International.png",
"https://cdn.discordapp.com/attachments/895601055742693376/940225756842315816/unknown_1.png",
"https://cdn.discordapp.com/attachments/895601055742693376/940237125830467654/Skill_issue.png",
"https://cdn.discordapp.com/attachments/954468468894351453/960392520137846814/unknown.png",
"https://cdn.discordapp.com/attachments/954468468894351453/960739414030549042/unknown-26.png"]
@bot.slash_command(description="Genshin players are creative")
async def creative(ctx: discord.ApplicationContext):
    await ctx.respond(choice(creativeList))

kamisatoList = ["https://cdn.discordapp.com/attachments/954468468894351453/1011060862456438825/unknown-110.png",
                "https://cdn.discordapp.com/attachments/962218404566138950/1011061306486423612/kamisatobus.png"]

@bot.slash_command(description="Kamisato siblings")
async def kamisato(ctx: discord.ApplicationContext):
    await ctx.respond(choice(kamisatoList))

nationalList = ["https://media.discordapp.net/attachments/970520412981186600/1005513761148387498/zajefnational.png"]
@bot.slash_command(description="National batchest")
async def national(ctx: discord.ApplicationContext):
    await ctx.respond(choice(nationalList))



bot.run(os.getenv("TOKEN"))

