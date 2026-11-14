"""Pokémon GO effectiveness in powers of 1.6, indexed by attacking move type."""
from decimal import Decimal

# Weak, resistant, strongly resistant defenders, respectively.
CHART = {
    "Fire": ("Grass Ice Bug Steel", "Fire Water Rock Dragon", ""),
    "Water": ("Fire Ground Rock", "Water Grass Dragon", ""),
    "Grass": ("Water Ground Rock", "Fire Grass Poison Flying Bug Dragon Steel", ""),
    "Normal": ("", "Rock Steel", "Ghost"),
    "Electric": ("Water Flying", "Electric Grass Dragon", "Ground"),
    "Ice": ("Grass Ground Flying Dragon", "Fire Water Ice Steel", ""),
    "Fighting": ("Normal Ice Rock Dark Steel", "Poison Flying Psychic Bug Fairy", "Ghost"),
    "Poison": ("Grass Fairy", "Poison Ground Rock Ghost", "Steel"),
    "Ground": ("Fire Electric Poison Rock Steel", "Grass Bug", "Flying"),
    "Flying": ("Grass Fighting Bug", "Electric Rock Steel", ""),
    "Psychic": ("Fighting Poison", "Psychic Steel", "Dark"),
    "Bug": ("Grass Psychic Dark", "Fire Fighting Poison Flying Ghost Steel Fairy", ""),
    "Rock": ("Fire Ice Flying Bug", "Fighting Ground Steel", ""),
    "Ghost": ("Psychic Ghost", "Dark", "Normal"),
    "Dragon": ("Dragon", "Steel", "Fairy"),
    "Dark": ("Psychic Ghost", "Fighting Dark Fairy", ""),
    "Steel": ("Ice Rock Fairy", "Fire Water Electric Steel", ""),
    "Fairy": ("Fighting Dragon Dark", "Fire Poison Steel", ""),
}
LABELS = {-3: "Triply resisted", -2: "Doubly resisted", -1: "Resisted",
          0: "Neutral", 1: "Super effective", 2: "Doubly super effective"}
STARTERS = ("Water", "Fire", "Grass")
DUALS = {"Swampert": ("Water", "Ground"), "Charizard": ("Fire", "Flying"),
         "Rayquaza": ("Dragon", "Flying"), "Magcargo": ("Fire", "Rock"),
         "Venusaur": ("Grass", "Poison"), "Gyarados": ("Water", "Flying"),
         "Gengar": ("Ghost", "Poison")}


def exponent(move, defender):
    for power, names in zip((1, -1, -2), CHART[move]):
        if defender in names.split():
            return power
    return 0


def multiplier(power):
    return format((Decimal("1.6") ** power).normalize(), "f") + "×"


def result(move, defenders):
    return sum(exponent(move, defender) for defender in defenders)
