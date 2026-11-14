from datetime import timedelta
from unittest.mock import patch

from django.test import Client, TestCase
from django.utils import timezone

from .models import Attempt, Trainer
from .practice import next_question, record
from .rules import CHART, DUALS, exponent, multiplier, result


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
        for deck in ("single", "dual", "starter"):
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
