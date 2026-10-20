from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[("candidate", "Candidate"), ("employer", "Employer")],
                default="candidate",
                max_length=12,
            ),
        ),
    ]
