from datetime import timedelta
import random
import uuid

from .models import Review
from .rules import CHART, DUALS, LABELS, STARTERS, exponent, multiplier, result

DECKS = {"starter": "Starter types", "single": "All 18 types", "dual": "Dual types"}
SPRITES = {
    "Water": ("Squirtle", 7), "Fire": ("Charmander", 4), "Grass": ("Tangela", 114),
    "Normal": ("Rattata", 19), "Electric": ("Pikachu", 25), "Ice": ("Glaceon", 471),
    "Fighting": ("Machop", 66), "Poison": ("Ekans", 23), "Ground": ("Sandshrew", 27),
    "Flying": ("Tornadus", 641), "Psychic": ("Abra", 63), "Bug": ("Caterpie", 10),
    "Rock": ("Roggenrola", 524), "Ghost": ("Misdreavus", 200), "Dragon": ("Dratini", 147),
    "Dark": ("Umbreon", 197), "Steel": ("Registeel", 379), "Fairy": ("Clefairy", 35),
}
DUAL_SPRITES = {"Swampert": 260, "Charizard": 6, "Rayquaza": 384, "Magcargo": 219,
                "Venusaur": 3, "Gyarados": 130, "Gengar": 94}


def pairs(deck):
    defenders = DUALS.values() if deck == "dual" else [
        (kind,) for kind in (STARTERS if deck == "starter" else CHART)]
    moves = STARTERS if deck == "starter" else CHART
    return [(move, types) for types in defenders for move in moves]


def key(move, types):
    return move + ":" + "/".join(types)


def next_question(trainer, today):
    pool = pairs(trainer.deck)
    attempts = trainer.attempt_set
    count = attempts.count()
    reviews = {r.matchup: r for r in trainer.review_set.all()}
    recent = set(attempts.order_by("-id").values_list("matchup", flat=True)[:2])
    previous_key = trainer.question.get("key")
    allowed = STARTERS if trainer.deck == "starter" else CHART
    choose_move = count % 4 == 3 or attempts.filter(day=today).count() == 9
    if choose_move:
        pool = [(move, types) for move, types in pool if
                sum(result(other, types) < result(move, types) for other in allowed) >= 2]
    def priority(pair):
        matchup = key(*pair)
        review = reviews.get(matchup)
        if review and review.retry_after is not None and count >= review.retry_after:
            rank = 0
        elif review and review.due <= today:
            rank = 1
        elif not review:
            rank = 2
        else:
            rank = 3
        return (matchup == previous_key, rank, matchup in recent, random.random())

    move, types = min(pool, key=priority) if count or trainer.deck != "starter" else ("Water", ("Fire",))
    power = result(move, types)
    question = {"token": str(uuid.uuid4()), "move": move, "types": list(types), "key": key(move, types),
                "kind": "effect", "correct": str(power)}
    # Vary the cue while tracking the same underlying fact. Distractors must
    # each have a strictly weaker effect than the intended answer.
    distractors = [t for t in allowed if result(t, types) < power]
    if choose_move:
        options = random.sample(distractors, min(3, len(distractors))) + [move]
        random.shuffle(options)
        question.update(kind="incoming" if count // 4 % 2 else "attack", options=options, correct=move)
    else:
        options = [-2, -1, 0, 1] if len(types) == 1 else list(LABELS)
        question["options"] = [str(p) for p in options]
    return question


def record(trainer, question, answer, today):
    correct = answer == question["correct"]
    trainer.attempt_set.create(token=question["token"], matchup=question["key"], day=today, correct=correct)
    review, created = Review.objects.get_or_create(trainer=trainer, matchup=question["key"],
        defaults={"last_day": today, "due": today + timedelta(days=1)})
    if correct:
        if not created and today >= review.due and review.last_day < today:
            review.interval = min(60, review.interval * 3)
            review.recalled_later = True
            review.due = today + timedelta(days=review.interval)
        review.retry_after = None
    else:
        review.interval = 1
        review.recalled_later = False
        review.due = today + timedelta(days=1)
        review.retry_after = trainer.attempt_set.count() + 2
    review.last_day = today
    review.save()
    question["answer"] = answer


def display(question):
    move, types = question["move"], question["types"]
    power = result(move, types)
    options = [{"value": v, "label": LABELS[int(v)] if question["kind"] == "effect" else v,
                "number": multiplier(int(v)) if question["kind"] == "effect" else ""}
               for v in question["options"]]
    named = next((name for name, dual in DUALS.items() if tuple(types) == dual), "")
    defender_name, defender_sprite = SPRITES[types[0]] if len(types) == 1 else (named, DUAL_SPRITES[named])
    return {**question, "options": options, "defender": " / ".join(types), "defender_name": defender_name,
            "defender_sprite": defender_sprite, "move_sprite": SPRITES.get(move, ("", None))[1],
            "feedback": f"{move} against {' / '.join(types)} is {LABELS[power].lower()}.",
            "math": " · ".join(f"{t} ({multiplier(exponent(move, t))})" for t in types) +
                    " → " + multiplier(power), "answered": "answer" in question,
            "right": question.get("answer") == question["correct"]}
