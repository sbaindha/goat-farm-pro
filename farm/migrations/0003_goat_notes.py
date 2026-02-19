from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('farm', '0002_fix_bugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='goat',
            name='notes',
            field=models.TextField(blank=True, help_text='Additional notes about this goat / बकरी के बारे में अतिरिक्त नोट्स'),
        ),
    ]
