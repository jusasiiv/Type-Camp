import hashlib
import secrets

# Short, single-word Pokémon names without punctuation or accents.
NAMES = """
Abra Absol Aipom Arbok Aron Axew Azelf Bagon Baltoy Banette Bayleef Bellsprout
Bidoof Bonsly Breloom Buizel Bulbasaur Buneary Butterfree Cacnea Camerupt
Chansey Charmander Chikorita Chimecho Chinchou Clefairy Combee Corphish Crobat
Cubone Cyndaquil Delibird Dewgong Diglett Doduo Donphan Dragonite Dratini
Drifloon Drowzee Ducklett Eevee Ekans Electrode Elekid Emolga Espurr Exeggcute
Farigiraf Fearow Feebas Finizen Flaaffy Flareon Flygon Froakie Furret Gastly
Gengar Geodude Gible Glaceon Gligar Gloom Golbat Golem Goomy Growlithe Gulpin
Haunter Heracross Hoothoot Hoppip Horsea Houndour Hypno Inkay Ivysaur Jigglypuff
Jirachi Jolteon Joltik Kabuto Kakuna Kecleon Kingler Koffing Krabby Lapras
Larvitar Leafeon Ledyba Litten Lotad Lugia Luxio Machop Magikarp Magnemite
Makuhita Mankey Mantine Mareep Marill Mawile Meowth Mew Mudkip Munna Natu
Nickit Oddish Onix Oshawott Pachirisu Pichu Pidgey Pikachu Pinsir Poliwag
Ponyta Psyduck Raichu Ralts Rattata Remoraid Riolu Rockruff Sandshrew
Scyther Seel Sentret Shinx Skitty Slowpoke Snorlax Spearow Spheal Squirtle
Staryu Swablu Tangela Togepi Torchic Totodile Treecko Umbreon Vulpix Wooper
Zorua Zubat
""".split()


def new_phrase():
    return " ".join(secrets.choice(NAMES) for _ in range(9))


def fingerprint(phrase):
    normalized = " ".join(phrase.casefold().replace("-", " ").split())
    return hashlib.sha256(normalized.encode()).hexdigest()
