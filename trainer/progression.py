"""Gradual practice unlocks, derived from the trainer's saved correct answers."""
from .rules import DUALS

CORRECT_PER_UNLOCK = 10
# Keep this order stable so an update never swaps a learner's unlocked types.
TYPE_ORDER = ("Water", "Fire", "Grass", "Normal", "Electric", "Ice", "Fighting", "Poison",
              "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy")
INITIAL_TYPES = 3
SINGLE_UNLOCKS = len(TYPE_ORDER) - INITIAL_TYPES
DUAL_TYPES = tuple(DUALS.values())
UNLOCKS = tuple((t,) for t in TYPE_ORDER[INITIAL_TYPES:]) + DUAL_TYPES


def progression(trainer):
    correct = trainer.attempt_set.filter(correct=True).count()
    earned = min(correct // CORRECT_PER_UNLOCK, len(UNLOCKS))
    singles = TYPE_ORDER[:INITIAL_TYPES + min(earned, SINGLE_UNLOCKS)]
    duals = DUAL_TYPES[:max(0, earned - SINGLE_UNLOCKS)]
    complete = earned == len(UNLOCKS)
    return {
        "correct": correct,
        "singles": singles,
        "duals": duals,
        "single_count": len(singles),
        "dual_count": len(duals),
        "dual_total": len(DUAL_TYPES),
        "earned": earned,
        "complete": complete,
        "next": " / ".join(UNLOCKS[earned]) if not complete else "",
        "toward_next": correct % CORRECT_PER_UNLOCK if not complete else CORRECT_PER_UNLOCK,
        "remaining": CORRECT_PER_UNLOCK - correct % CORRECT_PER_UNLOCK if not complete else 0,
        "target": CORRECT_PER_UNLOCK,
        "focus": UNLOCKS[earned - 1] if earned else (),
    }
