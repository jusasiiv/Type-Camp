from django.conf import settings
from django.core import signing
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables

from .models import Trainer
from .practice import DECKS, display, next_question, record
from .rules import CHART, LABELS, exponent, multiplier
from .recovery import fingerprint, new_phrase

DAILY_GOAL = 10
COOKIE = "typecamp_trainer"


def get_trainer(request, today):
    try:
        identity = request.get_signed_cookie(COOKIE, salt="trainer")
        trainer = Trainer.objects.filter(pk=identity).first()
    except (KeyError, signing.BadSignature):
        trainer = None
    if trainer is None:
        trainer = Trainer.objects.create(day=today)
    if trainer.day != today:
        trainer.day = today
        trainer.summary = False
        trainer.question = {}
        trainer.save()
    return trainer


def remember(response, trainer):
    response.set_signed_cookie(COOKIE, str(trainer.pk), salt="trainer", max_age=365 * 86400,
                               secure=not settings.DEBUG, httponly=True, samesite="Lax")
    response["Cache-Control"] = "private, no-store"
    return response


def stats(trainer, today):
    attempts = trainer.attempt_set.filter(day=today)
    count = attempts.count()
    return {"count": count, "goal": DAILY_GOAL, "filled": min(count, DAILY_GOAL),
            "segments": range(DAILY_GOAL), "correct_count": attempts.filter(correct=True).count(),
            "remembered": trainer.review_set.filter(recalled_later=True).count()}


@require_http_methods(["GET", "POST"])
@transaction.atomic
def practice(request):
    today = timezone.localdate()
    trainer = get_trainer(request, today)
    q = trainer.question
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "deck" and request.POST.get("deck") in DECKS:
            trainer.deck = request.POST["deck"]
            trainer.summary = False
            q = {}
        elif action == "continue" and trainer.summary:
            trainer.summary = False
            q = {}
        elif action == "finish":
            trainer.summary = True
        elif request.POST.get("token") == q.get("token") and q:
            if action == "answer" and "answer" not in q:
                answer = request.POST.get("choice")
                if answer not in [*q["options"], "?"]:
                    return HttpResponseBadRequest("Choose an answer shown on the card.")
                record(trainer, q, answer, today)
            elif action == "next" and "answer" in q:
                trainer.summary = trainer.attempt_set.filter(day=today).count() == DAILY_GOAL
                q = {}
    if not q and not trainer.summary:
        q = next_question(trainer, today)
    trainer.question = q
    trainer.save()
    if request.method == "POST" and request.headers.get("X-Trainer-Fragment") != "1":
        return remember(redirect("practice"), trainer)
    data = {**stats(trainer, today), "trainer": trainer, "q": display(q) if q else None,
            "decks": DECKS, "deck_name": DECKS[trainer.deck], "page": "practice"}
    template = "lesson" if request.headers.get("X-Trainer-Fragment") == "1" else "practice"
    return remember(render(request, f"trainer/{template}.html", data), trainer)


def chart(request):
    selected = request.GET.get("move", "Water")
    if selected not in CHART:
        selected = "Water"
    groups = [{"label": LABELS[p], "factor": multiplier(p),
               "types": [t for t in CHART if exponent(selected, t) == p]} for p in (1, 0, -1, -2)]
    return render(request, "trainer/chart.html", {"page": "chart", "types": sorted(CHART),
                  "selected": selected, "groups": groups})


@sensitive_post_parameters("phrase")
@sensitive_variables("phrase", "data")
@require_http_methods(["GET", "POST"])
@transaction.atomic
def progress(request):
    today = timezone.localdate()
    trainer = get_trainer(request, today)
    data = {"page": "progress"}
    if request.method == "POST":
        action = request.POST.get("action")
        if action in ("generate", "replace"):
            # A stale form or a repeated POST must not invalidate a newly issued phrase.
            previous = request.POST.get("previous", "")
            if (action == "generate" and not trainer.recovery_hash) or (
                action == "replace" and trainer.recovery_hash and previous == trainer.recovery_hash
            ):
                phrase = new_phrase()
                digest = fingerprint(phrase)
                while Trainer.objects.filter(recovery_hash=digest).exists():
                    phrase = new_phrase()
                    digest = fingerprint(phrase)
                trainer.recovery_hash = digest
                trainer.save(update_fields=["recovery_hash"])
                data["issued_phrase"] = phrase
            else:
                data["notice"] = "A recovery phrase is already active."
        elif action == "restore":
            phrase = request.POST.get("phrase", "")
            target = None
            if 0 < len(phrase) <= 256:
                target = Trainer.objects.filter(recovery_hash=fingerprint(phrase)).first()
            if target is None:
                data["notice"] = "Phrase not recognized. Check the names and their order."
            elif target.pk == trainer.pk:
                data["notice"] = "This browser already uses that trainer profile."
            elif trainer.attempt_set.exists():
                confirmation = signing.dumps([str(trainer.pk), target.recovery_hash], salt="confirm-restore")
                data.update(confirmation=confirmation, current_total=trainer.attempt_set.count(),
                            restored_total=target.attempt_set.count())
            else:
                return remember(redirect("progress"), target)
        elif action == "confirm":
            try:
                source, digest = signing.loads(request.POST.get("confirmation", ""),
                                               salt="confirm-restore", max_age=600)
            except signing.BadSignature:
                source, digest = None, None
            target = Trainer.objects.filter(recovery_hash=digest).first() if source == str(trainer.pk) else None
            if target is not None:
                return remember(redirect("progress"), target)
            data["notice"] = "Please enter your recovery phrase again to confirm."
        else:
            return HttpResponseBadRequest("Unknown recovery action.")
    data["recovery_hash"] = trainer.recovery_hash
    rows = [{"matchup": r.matchup.replace(":", " → "), "due": r.due, "remembered": r.recalled_later}
            for r in trainer.review_set.order_by("due", "matchup")]
    return remember(render(request, "trainer/progress.html", {
        **data, "rows": rows, **stats(trainer, today)}), trainer)
