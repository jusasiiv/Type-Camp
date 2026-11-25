from django.db import migrations, models


def use_progression(apps, schema_editor):
    apps.get_model("trainer", "Trainer").objects.using(schema_editor.connection.alias).filter(
        deck="starter"
    ).update(deck="progressive")


def use_starters(apps, schema_editor):
    apps.get_model("trainer", "Trainer").objects.using(schema_editor.connection.alias).filter(
        deck="progressive"
    ).update(deck="starter")


class Migration(migrations.Migration):
    dependencies = [("trainer", "0002_trainer_recovery_hash")]

    operations = [
        migrations.AlterField(
            model_name="trainer", name="deck",
            field=models.CharField(default="progressive", max_length=16),
        ),
        migrations.RunPython(use_progression, use_starters),
    ]
