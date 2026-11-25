import uuid
from django.db import models


class Trainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deck = models.CharField(max_length=16, default="progressive")
    question = models.JSONField(default=dict)
    summary = models.BooleanField(default=False)
    day = models.DateField()
    recovery_hash = models.CharField(max_length=64, unique=True, null=True, editable=False)


class Attempt(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    token = models.UUIDField(unique=True)
    matchup = models.CharField(max_length=64)
    day = models.DateField()
    correct = models.BooleanField()

    class Meta:
        indexes = [models.Index(fields=["trainer", "day"])]


class Review(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    matchup = models.CharField(max_length=64)
    last_day = models.DateField()
    due = models.DateField()
    interval = models.PositiveIntegerField(default=1)
    recalled_later = models.BooleanField(default=False)
    retry_after = models.PositiveIntegerField(null=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["trainer", "matchup"], name="one_review_per_matchup")]
