from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from .models import Attempt, Review, Trainer
from .practice import display, next_question, pairs, record
from .progression import DUAL_TYPES, TYPE_ORDER, UNLOCKS, progression
from .rules import CHART, DUALS, LABELS, exponent, multiplier, result


class TrainerTests(TestCase):
    def test_go_chart(self):
        self.assertEqual(len(CHART), 18)
        for groups in CHART.values():
            entries = " ".join(groups).split()
            self.assertTrue(set(entries) <= CHART.keys())
            self.assertEqual(len(entries), len(set(entries)))
        examples = [
            ("Water", ("Fire",), "1.6×"), ("Ground", ("Flying",), "0.390625×"),
            ("Ice", DUALS["Rayquaza"], "2.56×"), ("Electric", DUALS["Swampert"], "0.625×"),
            ("Ground", ("Bug", "Flying"), "0.244140625×"), ("Water", ("Fire", "Grass"), "1×"),
        ]
        for move, defenders, expected in examples:
            self.assertEqual(multiplier(result(move, defenders)), expected)
        self.assertEqual(exponent("Normal", "Ghost"), -2)

    def test_daily_goal_continuation_and_retry(self):
        self.client.get("/")
        for number in range(1, 16):
            trainer = Trainer.objects.get()
            q = trainer.question
            payload = {"action": "answer", "choice": q["correct"], "token": q["token"]}
            response = self.client.post("/", payload, HTTP_X_TRAINER_FRAGMENT="1")
            self.assertContains(response, "Correct!")
            self.client.post("/", payload)
            self.assertEqual(Attempt.objects.count(), number)
            self.assertEqual(self.client.get("/").context["q"]["token"], q["token"])
            if number == 10:
                self.assertIn(q["kind"], ("attack", "incoming"))
            self.client.post("/", {"action": "next", "token": q["token"]})
            if number == 10:
                self.assertContains(self.client.get("/"), "Keep practicing")
                self.client.post("/", {"action": "continue"})
        self.assertEqual(self.client.get("/progress/").context["count"], 15)
        self.assertEqual(Client().get("/progress/").context["count"], 0)

    def test_spaced_review(self):
        today = timezone.localdate()
        trainer = Trainer.objects.create(day=today)
        q = next_question(trainer, today)
        record(trainer, q, "?", today)
        from uuid import uuid4
        q["token"] = str(uuid4())
        record(trainer, q, q["correct"], today)
        review = trainer.review_set.get()
        self.assertEqual(review.due, today + timedelta(days=1))
        self.assertFalse(review.recalled_later)
        tomorrow = today + timedelta(days=1)
        q["token"] = str(uuid4())
        record(trainer, q, q["correct"], tomorrow)
        review.refresh_from_db()
        self.assertTrue(review.recalled_later)
        self.assertEqual(review.due, tomorrow + timedelta(days=3))

    def test_decks_invalid_answers_and_new_day(self):
        self.client.get("/")
        for deck in ("single", "dual", "progressive"):
            self.client.post("/", {"action": "deck", "deck": deck})
            q = self.client.get("/").context["q"]
            self.assertEqual(len(q["types"]), 2 if deck == "dual" else 1)
            rejected = self.client.post("/", {"action": "answer", "choice": "invalid", "token": q["token"]})
            self.assertEqual(rejected.status_code, 400)
        self.client.post("/", {"action": "answer", "choice": "?", "token": q["token"]})
        self.client.post("/", {"action": "finish"})
        with patch("trainer.views.timezone.localdate", return_value=timezone.localdate()+timedelta(days=1)):
            page = self.client.get("/")
            self.assertEqual(page.context["count"], 0)
            self.assertFalse(page.context["trainer"].summary)
            self.assertEqual(page.context["q"]["key"], q["key"])
        self.assertContains(self.client.get("/chart/?move=Normal"), "Ghost")


class ProgressionTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.trainer = Trainer.objects.create(day=self.today)

    def add_correct(self, count, day=None):
        Attempt.objects.bulk_create([
            Attempt(trainer=self.trainer, token=uuid4(), matchup="Water:Fire",
                    day=day or self.today, correct=True) for _ in range(count)
        ])

    def test_unlock_boundaries_and_completion(self):
        self.assertEqual(set(TYPE_ORDER), set(CHART))
        previous = 0
        for count, singles, duals in [(0, 3, 0), (9, 3, 0), (10, 4, 0), (149, 17, 0),
                                      (150, 18, 0), (159, 18, 0), (160, 18, 1),
                                      (170, 18, 2), (len(UNLOCKS) * 10, 18, len(DUALS))]:
            self.add_correct(count - previous)
            previous = count
            state = progression(self.trainer)
            self.assertEqual((state["single_count"], state["dual_count"]), (singles, duals))
            self.assertEqual(len(pairs("progressive", state)), singles * (singles + duals))
        self.add_correct(100)
        state = progression(self.trainer)
        self.assertTrue(state["complete"])
        self.assertEqual(state["next"], "")
        self.assertEqual(state["remaining"], 0)
        self.assertEqual(set(pairs("progressive", state)),
                         set(pairs("single", state)) | set(pairs("dual", state)))

    def test_questions_and_choices_stay_inside_unlocks(self):
        previous = 0
        for count in (0, 3, 9, 10, 13, 19, 149, 150, 159, 160, 163, len(UNLOCKS) * 10):
            self.add_correct(count - previous)
            previous = count
            state = progression(self.trainer)
            for _ in range(5):
                question = next_question(self.trainer, self.today)
                self.assertIn(question["move"], state["singles"])
                self.assertIn(tuple(question["types"]),
                              tuple((t,) for t in state["singles"]) + state["duals"])
                if question["kind"] != "effect":
                    self.assertLessEqual(set(question["options"]), set(state["singles"]))
                    powers = [result(move, question["types"]) for move in question["options"]]
                    self.assertEqual(powers.count(max(powers)), 1)
                    self.assertEqual(result(question["correct"], question["types"]), max(powers))

    def test_new_unlock_is_taught_but_due_reviews_keep_priority(self):
        self.add_correct(10)
        q = next_question(self.trainer, self.today)
        self.assertTrue(q["move"] == "Normal" or q["types"] == ["Normal"])
        Review.objects.create(trainer=self.trainer, matchup="Grass:Water", last_day=self.today,
                              due=self.today, retry_after=10)
        self.assertEqual(next_question(self.trainer, self.today)["key"], "Grass:Water")
        self.add_correct(150)
        self.trainer.review_set.all().delete()
        self.assertEqual(tuple(next_question(self.trainer, self.today)["types"]), DUAL_TYPES[0])

    def test_first_and_final_dual_unlock_feedback(self):
        self.trainer.delete()
        self.trainer = self.client.get("/").context["trainer"]
        for milestone, expected in [(160, DUAL_TYPES[0]), (len(UNLOCKS) * 10, DUAL_TYPES[-1])]:
            self.add_correct(milestone - 1 - self.trainer.attempt_set.filter(correct=True).count())
            q = self.client.get("/").context["q"]
            response = self.client.post("/", {"action": "answer", "token": q["token"],
                                              "choice": q["correct"]}, HTTP_X_TRAINER_FRAGMENT="1")
            self.assertContains(response, f"Unlocked: {' / '.join(expected)}!")
            self.assertEqual(response.context["progression"]["dual_count"], 1 if milestone == 160 else len(DUALS))
            self.client.post("/", {"action": "next", "token": q["token"]})
            q = self.client.get("/").context["q"]
            self.assertEqual(tuple(q["types"]), expected)
        self.assertContains(self.client.get("/progress/"), "Everything unlocked!")

    def test_wrong_answers_do_not_unlock_and_duplicate_posts_do_not_count(self):
        # Use a browser-owned trainer for real fragment and form submissions.
        self.trainer.delete()
        page = self.client.get("/")
        self.trainer = page.context["trainer"]
        self.add_correct(9, self.today - timedelta(days=1))
        q = page.context["q"]
        self.client.post("/", {"action": "answer", "choice": "?", "token": q["token"]})
        self.assertEqual(progression(self.trainer)["single_count"], 3)
        self.client.post("/", {"action": "next", "token": q["token"]})
        q = self.client.get("/").context["q"]
        payload = {"action": "answer", "choice": q["correct"], "token": q["token"]}
        answered = self.client.post("/", payload, HTTP_X_TRAINER_FRAGMENT="1")
        self.assertContains(answered, "Unlocked: Normal!")
        self.assertEqual(answered.context["progression"]["single_count"], 4)
        self.client.post("/", payload)
        state = self.client.get("/progress/").context["progression"]
        self.assertEqual((state["correct"], state["toward_next"]), (10, 0))
        with patch("trainer.views.timezone.localdate", return_value=self.today + timedelta(days=1)):
            self.assertEqual(self.client.get("/").context["progression"]["single_count"], 4)

    def test_skip_modes_preserve_and_contribute_to_progress(self):
        self.trainer.delete()
        page = self.client.get("/")
        self.trainer = page.context["trainer"]
        self.add_correct(8)
        self.assertNotContains(page, "Starter types")
        for deck in ("single", "dual"):
            page = self.client.post("/", {"action": "deck", "deck": deck}, follow=True)
            self.assertEqual(page.context["progression"]["single_count"], 3)
            q = page.context["q"]
            self.assertEqual(len(q["types"]), 2 if deck == "dual" else 1)
            self.client.post("/", {"action": "answer", "token": q["token"], "choice": q["correct"]})
        page = self.client.post("/", {"action": "deck", "deck": "progressive"}, follow=True)
        self.assertEqual(page.context["progression"]["single_count"], 4)
        self.assertEqual(page.context["progression"]["dual_count"], 0)
        self.assertIn(page.context["q"]["move"], TYPE_ORDER[:4])
        self.assertEqual(Attempt.objects.count(), 10)
        self.assertEqual(Review.objects.count(), 2)

    def test_complete_dual_catalog_and_display(self):
        self.assertEqual(len(DUALS), 139)
        self.assertEqual(len({frozenset(types) for types in DUALS.values()}), len(DUALS))
        self.assertIn(("Dragon", "Fairy"), DUAL_TYPES)  # Mega Altaria
        self.assertIn(("Dark", "Normal"), DUAL_TYPES)  # Regional forms count too.
        self.assertNotIn(("Normal", "Rock"), DUAL_TYPES)  # No hypothetical pairs.
        self.assertEqual(len(pairs("dual", progression(self.trainer))), 18 * 139)
        for name, types in DUALS.items():
            self.assertEqual(len(set(types)), 2)
            self.assertLessEqual(set(types), CHART.keys())
            for move in CHART:
                self.assertIn(result(move, types), LABELS)
            q = {"move": "Water", "types": list(types), "kind": "effect",
                 "options": [str(p) for p in LABELS], "correct": str(result("Water", types))}
            self.assertEqual(display(q)["defender_name"], name)
            # Older saved questions need not use the catalog's type order.
            q["types"].reverse()
            self.assertEqual(display(q)["defender_name"], name)


class ProgressionMigrationTests(TransactionTestCase):
    def test_existing_profiles_and_questions_survive(self):
        old_target = [("trainer", "0002_trainer_recovery_hash")]
        new_target = [("trainer", "0003_progressive_practice")]
        self.addCleanup(lambda: MigrationExecutor(connection).migrate(new_target))
        executor = MigrationExecutor(connection)
        executor.migrate(old_target)
        old = executor.loader.project_state(old_target).apps
        old_trainer = old.get_model("trainer", "Trainer")
        question = {"token": str(uuid4()), "move": "Water", "types": ["Fire"], "key": "Water:Fire",
                    "kind": "effect", "correct": "1", "options": ["-2", "-1", "0", "1"]}
        trainer = old_trainer.objects.create(day=timezone.localdate(), question=question)
        for deck in ("single", "dual"):
            old_trainer.objects.create(day=timezone.localdate(), deck=deck)
        old.get_model("trainer", "Attempt").objects.bulk_create([
            old.get_model("trainer", "Attempt")(trainer_id=trainer.pk, token=uuid4(), matchup="Water:Fire",
                                                day=timezone.localdate(), correct=True) for _ in range(10)
        ])
        old.get_model("trainer", "Review").objects.create(
            trainer_id=trainer.pk, matchup="Water:Fire", last_day=timezone.localdate(),
            due=timezone.localdate() + timedelta(days=3), interval=3, recalled_later=True)
        MigrationExecutor(connection).migrate(new_target)
        trainer = Trainer.objects.get(pk=trainer.pk)
        self.assertEqual(trainer.deck, "progressive")
        self.assertEqual(trainer.question, question)
        self.assertEqual(progression(trainer)["single_count"], 4)
        self.assertEqual(trainer.review_set.get().interval, 3)
        self.assertEqual(set(Trainer.objects.values_list("deck", flat=True)), {"progressive", "single", "dual"})
        self.assertEqual(Trainer.objects.create(day=timezone.localdate()).deck, "progressive")


class RecoveryTests(TestCase):
    def setUp(self):
        self.phone = self.client
        self.laptop = Client()
        q = self.phone.get("/").context["q"]
        self.phone.post("/", {"action": "answer", "token": q["token"], "choice": q["correct"]})
        self.phrase = self.phone.post("/progress/", {"action": "generate"}).context["issued_phrase"]

    def test_two_devices_share_answers_and_reviews(self):
        self.assertEqual(len(self.phrase.split()), 9)
        formatted = "  " + "-".join(self.phrase.upper().split()) + "  "
        restored = self.laptop.post("/progress/", {"action": "restore", "phrase": formatted}, follow=True)
        self.assertEqual(restored.context["count"], 1)
        self.assertEqual(len(restored.context["rows"]), 1)
        q = self.laptop.get("/").context["q"]
        self.laptop.post("/", {"action": "next", "token": q["token"]})
        q = self.laptop.get("/").context["q"]
        self.laptop.post("/", {"action": "answer", "token": q["token"], "choice": q["correct"]})
        self.assertEqual(self.phone.get("/progress/").context["count"], 2)
        self.assertEqual(self.phone.get("/progress/").context["progression"],
                         self.laptop.get("/progress/").context["progression"])
        self.assertNotContains(self.phone.get("/progress/"), self.phrase)

    def test_restore_with_history_needs_confirmation(self):
        q = self.laptop.get("/").context["q"]
        self.laptop.post("/", {"action": "answer", "token": q["token"], "choice": "?"})
        preview = self.laptop.post("/progress/", {"action": "restore", "phrase": self.phrase})
        self.assertEqual((preview.context["current_total"], preview.context["restored_total"]), (1, 1))
        self.assertNotContains(preview, self.phrase)
        self.assertEqual(self.laptop.get("/progress/").context["correct_count"], 0)
        token = preview.context["confirmation"]
        self.laptop.post("/progress/", {"action": "confirm", "confirmation": token + "x"})
        self.assertEqual(self.laptop.get("/progress/").context["correct_count"], 0)
        page = self.laptop.post("/progress/", {"action": "confirm", "confirmation": token}, follow=True)
        self.assertEqual(page.context["correct_count"], 1)
        self.assertEqual(Attempt.objects.count(), 2)

    def test_rotation_and_invalid_phrase(self):
        active = self.phone.post("/progress/", {"action": "generate"})
        self.assertNotIn("issued_phrase", active.context)
        payload = {"action": "replace", "previous": active.context["recovery_hash"]}
        replacement = self.phone.post("/progress/", payload).context["issued_phrase"]
        self.assertNotIn("issued_phrase", self.phone.post("/progress/", payload).context)
        invalid = self.laptop.post("/progress/", {"action": "restore", "phrase": self.phrase})
        self.assertContains(invalid, "Phrase not recognized")
        self.assertEqual(invalid.context["count"], 0)
        restored = self.laptop.post("/progress/", {"action": "restore", "phrase": replacement}, follow=True)
        self.assertEqual(restored.context["count"], 1)
