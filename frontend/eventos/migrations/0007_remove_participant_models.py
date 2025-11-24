# Generated manually to remove participant models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0006_personaexterna_alter_participanteevento_options_and_more'),
    ]

    operations = [
        # Fix observaciones field formatting
        migrations.AlterField(
            model_name='evento',
            name='observaciones',
            field=models.TextField(blank=True, help_text='Observaciones y comentarios sobre el evento'),
        ),
    ]