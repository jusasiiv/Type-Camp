"""Released Pokémon GO dual typings, bundled so practice needs no network.

Source: https://raw.githubusercontent.com/pvpoke/pvpoke/a2dfcacab516ff0826ce7cfa2b4ac1cc10112587/src/data/gamemaster/pokemon.json
Checked 2026-11-25; includes released regional forms and Mega Evolutions.
Each unordered pair appears once. Preserve this order and append new pairs:
unlock positions and the first seven legacy matchup keys must stay stable.
"""

DUALS = {
    'Swampert': ('Water', 'Ground'),
    'Charizard': ('Fire', 'Flying'),
    'Rayquaza': ('Dragon', 'Flying'),
    'Magcargo': ('Fire', 'Rock'),
    'Venusaur': ('Grass', 'Poison'),
    'Gyarados': ('Water', 'Flying'),
    'Gengar': ('Ghost', 'Poison'),
    'Lokix': ('Bug', 'Dark'),  # lokix
    'Joltik': ('Bug', 'Electric'),  # joltik
    'Cutiefly': ('Bug', 'Fairy'),  # cutiefly
    'Heracross': ('Bug', 'Fighting'),  # heracross
    'Larvesta': ('Bug', 'Fire'),  # larvesta
    'Butterfree': ('Bug', 'Flying'),  # butterfree
    'Paras': ('Bug', 'Grass'),  # paras
    'Nincada': ('Bug', 'Ground'),  # nincada
    'Snom': ('Bug', 'Ice'),  # snom
    'Weedle': ('Bug', 'Poison'),  # weedle
    'Dottler': ('Bug', 'Psychic'),  # dottler
    'Shuckle': ('Bug', 'Rock'),  # shuckle
    'Forretress': ('Bug', 'Steel'),  # forretress
    'Surskit': ('Bug', 'Water'),  # surskit
    'Deino': ('Dark', 'Dragon'),  # deino
    'Morpeko (Full Belly)': ('Dark', 'Electric'),  # morpeko_full_belly
    'Impidimp': ('Dark', 'Fairy'),  # impidimp
    'Scraggy': ('Dark', 'Fighting'),  # scraggy
    'Houndour': ('Dark', 'Fire'),  # houndour
    'Moltres (Galarian)': ('Dark', 'Flying'),  # moltres_galarian
    'Sableye': ('Dark', 'Ghost'),  # sableye
    'Nuzleaf': ('Dark', 'Grass'),  # nuzleaf
    'Sandile': ('Dark', 'Ground'),  # sandile
    'Sneasel': ('Dark', 'Ice'),  # sneasel
    'Rattata (Alolan)': ('Dark', 'Normal'),  # rattata_alolan
    'Grimer (Alolan)': ('Dark', 'Poison'),  # grimer_alolan
    'Inkay': ('Dark', 'Psychic'),  # inkay
    'Tyranitar': ('Dark', 'Rock'),  # tyranitar
    'Pawniard': ('Dark', 'Steel'),  # pawniard
    'Carvanha': ('Dark', 'Water'),  # carvanha
    'Zekrom': ('Dragon', 'Electric'),  # zekrom
    'Altaria (Mega)': ('Dragon', 'Fairy'),  # altaria_mega
    'Hakamo-o': ('Dragon', 'Fighting'),  # hakamo_o
    'Reshiram': ('Dragon', 'Fire'),  # reshiram
    'Giratina (Altered)': ('Dragon', 'Ghost'),  # giratina_altered
    'Exeggutor (Alolan)': ('Dragon', 'Grass'),  # exeggutor_alolan
    'Vibrava': ('Dragon', 'Ground'),  # vibrava
    'Kyurem': ('Dragon', 'Ice'),  # kyurem
    'Drampa': ('Dragon', 'Normal'),  # drampa
    'Dragalge': ('Dragon', 'Poison'),  # dragalge
    'Latias': ('Dragon', 'Psychic'),  # latias
    'Tyrunt': ('Dragon', 'Rock'),  # tyrunt
    'Dialga': ('Dragon', 'Steel'),  # dialga
    'Kingdra': ('Dragon', 'Water'),  # kingdra
    'Dedenne': ('Electric', 'Fairy'),  # dedenne
    'Pawmo': ('Electric', 'Fighting'),  # pawmo
    'Rotom (Heat)': ('Electric', 'Fire'),  # rotom_heat
    'Zapdos': ('Electric', 'Flying'),  # zapdos
    'Rotom': ('Electric', 'Ghost'),  # rotom
    'Voltorb (Hisuian)': ('Electric', 'Grass'),  # voltorb_hisuian
    'Stunfisk': ('Electric', 'Ground'),  # stunfisk
    'Rotom (Frost)': ('Electric', 'Ice'),  # rotom_frost
    'Helioptile': ('Electric', 'Normal'),  # helioptile
    'Toxel': ('Electric', 'Poison'),  # toxel
    'Raichu (Alolan)': ('Electric', 'Psychic'),  # raichu_alolan
    'Geodude (Alolan)': ('Electric', 'Rock'),  # geodude_alolan
    'Magnemite': ('Electric', 'Steel'),  # magnemite
    'Chinchou': ('Electric', 'Water'),  # chinchou
    'Togetic': ('Fairy', 'Flying'),  # togetic
    'Mimikyu': ('Fairy', 'Ghost'),  # mimikyu
    'Cottonee': ('Fairy', 'Grass'),  # cottonee
    'Ninetales (Alolan)': ('Fairy', 'Ice'),  # ninetales_alolan
    'Jigglypuff': ('Fairy', 'Normal'),  # jigglypuff
    'Weezing (Galarian)': ('Fairy', 'Poison'),  # weezing_galarian
    'Rapidash (Galarian)': ('Fairy', 'Psychic'),  # rapidash_galarian
    'Carbink': ('Fairy', 'Rock'),  # carbink
    'Mawile': ('Fairy', 'Steel'),  # mawile
    'Marill': ('Fairy', 'Water'),  # marill
    'Tauros (Blaze)': ('Fighting', 'Fire'),  # tauros_blaze
    'Zapdos (Galarian)': ('Fighting', 'Flying'),  # zapdos_galarian
    'Marshadow': ('Fighting', 'Ghost'),  # marshadow
    'Breloom': ('Fighting', 'Grass'),  # breloom
    'Crabominable': ('Fighting', 'Ice'),  # crabominable
    'Stufful': ('Fighting', 'Normal'),  # stufful
    'Sneasel (Hisuian)': ('Fighting', 'Poison'),  # sneasel_hisuian
    'Meditite': ('Fighting', 'Psychic'),  # meditite
    'Terrakion': ('Fighting', 'Rock'),  # terrakion
    'Lucario': ('Fighting', 'Steel'),  # lucario
    'Poliwrath': ('Fighting', 'Water'),  # poliwrath
    'Marowak (Alolan)': ('Fire', 'Ghost'),  # marowak_alolan
    'Numel': ('Fire', 'Ground'),  # numel
    'Litleo': ('Fire', 'Normal'),  # litleo
    'Salandit': ('Fire', 'Poison'),  # salandit
    'Victini': ('Fire', 'Psychic'),  # victini
    'Heatran': ('Fire', 'Steel'),  # heatran
    'Volcanion': ('Fire', 'Water'),  # volcanion
    'Drifloon': ('Flying', 'Ghost'),  # drifloon
    'Hoppip': ('Flying', 'Grass'),  # hoppip
    'Gligar': ('Flying', 'Ground'),  # gligar
    'Articuno': ('Flying', 'Ice'),  # articuno
    'Pidgey': ('Flying', 'Normal'),  # pidgey
    'Zubat': ('Flying', 'Poison'),  # zubat
    'Articuno (Galarian)': ('Flying', 'Psychic'),  # articuno_galarian
    'Aerodactyl': ('Flying', 'Rock'),  # aerodactyl
    'Skarmory': ('Flying', 'Steel'),  # skarmory
    'Phantump': ('Ghost', 'Grass'),  # phantump
    'Yamask (Galarian)': ('Ghost', 'Ground'),  # yamask_galarian
    'Froslass': ('Ghost', 'Ice'),  # froslass
    'Zorua (Hisuian)': ('Ghost', 'Normal'),  # zorua_hisuian
    'Hoopa': ('Ghost', 'Psychic'),  # hoopa
    'Honedge': ('Ghost', 'Steel'),  # honedge
    'Frillish': ('Ghost', 'Water'),  # frillish
    'Torterra': ('Grass', 'Ground'),  # torterra
    'Snover': ('Grass', 'Ice'),  # snover
    'Deerling': ('Grass', 'Normal'),  # deerling
    'Exeggcute': ('Grass', 'Psychic'),  # exeggcute
    'Lileep': ('Grass', 'Rock'),  # lileep
    'Ferroseed': ('Grass', 'Steel'),  # ferroseed
    'Lotad': ('Grass', 'Water'),  # lotad
    'Swinub': ('Ground', 'Ice'),  # swinub
    'Diggersby': ('Ground', 'Normal'),  # diggersby
    'Nidoqueen': ('Ground', 'Poison'),  # nidoqueen
    'Baltoy': ('Ground', 'Psychic'),  # baltoy
    'Geodude': ('Ground', 'Rock'),  # geodude
    'Diglett (Alolan)': ('Ground', 'Steel'),  # diglett_alolan
    'Mr. Mime (Galarian)': ('Ice', 'Psychic'),  # mr_mime_galarian
    'Amaura': ('Ice', 'Rock'),  # amaura
    'Sandshrew (Alolan)': ('Ice', 'Steel'),  # sandshrew_alolan
    'Dewgong': ('Ice', 'Water'),  # dewgong
    'Shroodle': ('Normal', 'Poison'),  # shroodle
    'Girafarig': ('Normal', 'Psychic'),  # girafarig
    'Bibarel': ('Normal', 'Water'),  # bibarel
    'Slowbro (Galarian)': ('Poison', 'Psychic'),  # slowbro_galarian
    'Nihilego': ('Poison', 'Rock'),  # nihilego
    'Varoom': ('Poison', 'Steel'),  # varoom
    'Tentacool': ('Poison', 'Water'),  # tentacool
    'Lunatone': ('Psychic', 'Rock'),  # lunatone
    'Beldum': ('Psychic', 'Steel'),  # beldum
    'Slowpoke': ('Psychic', 'Water'),  # slowpoke
    'Aron': ('Rock', 'Steel'),  # aron
    'Omanyte': ('Rock', 'Water'),  # omanyte
    'Empoleon': ('Steel', 'Water'),  # empoleon
}
