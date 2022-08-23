import discord
from discord import AutocompleteContext

elements = ["pyro", "hydro", "electro", "cryo", "geo", "anemo"]
pyroCharacters = ["Amber",
                  "Bennett",
                  "Diluc",
                  "Hu Tao",
                  "Klee",
                  "Thoma",
                  "Xiangling",
                  "Xinyan",
                  "Yanfei",
                  "Yoimiya"]

hydroCharacters = ["Ayato",
                   "Barbara",
                   "Childe",
                   "Kokomi",
                   "Mona",
                   "Xingqiu",
                   "Yelan"]
electroCharacters = ["Beidou",
                     "Fischl",
                     "Keqing",
                     "Kuki",
                     "Lisa",
                     "Raiden",
                     "Razor",
                     "Sara",
                     "Yae"]
cryoCharacters = ["Aloy",
                  "Ayaka",
                  "Chongyun",
                  "Diona",
                  "Eula",
                  "Ganyu",
                  "Kaeya",
                  "Qiqi",
                  "Rosaria",
                  "Shenhe"]
geoCharacters = ["Albedo",
                 "Gorou",
                   "Itto",
                   "Ningguang",
                   "Noelle",
                   "Yun Jin",
                   "Zhongli"]
anemoCharacters = ["Heizou",
                 "Jean",
                 "Kazuha",
                 "Sayu",
                 "Sucrose",
                 "Venti",
                 "Xiao"]
characterDict = {"pyro": pyroCharacters,
                 "hydro": hydroCharacters,
                 "electro": electroCharacters,
                 "cryo": cryoCharacters,
                 "anemo": anemoCharacters,
                 "geo": geoCharacters}
characters = sorted(pyroCharacters + hydroCharacters + electroCharacters + cryoCharacters + anemoCharacters + geoCharacters)
colors = dict()
for c in characters:
    if c in pyroCharacters:
        colors[c] = discord.Color.from_rgb(178, 89, 63)
    elif c in hydroCharacters:
        colors[c] = discord.Color.from_rgb(57, 112, 184)
    elif c in electroCharacters:
        colors[c] = discord.Color.from_rgb(123, 81, 172)
    elif c in cryoCharacters:
        colors[c] = discord.Color.from_rgb(118, 213, 229)
    elif c in geoCharacters:
        colors[c] = discord.Color.from_rgb(189, 152, 71)
    elif c in anemoCharacters:
        colors[c] = discord.Color.from_rgb(56, 170, 171)

# autocomplete helper function for commands that are based on characters
async def get_characters(ctx: AutocompleteContext):
    return [c for c in characters if c.lower().startswith(ctx.value.lower())]

