"""
Migration: Bug fixes
1. Goat.photo_url (CharField) → Goat.photo (ImageField)
2. Expense.payment_method max_length 1 → 2 (CH for Cheque)
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0001_initial'),
    ]

    operations = [
        # FIX #1: photo_url CharField → photo ImageField
        migrations.RenameField(
            model_name='goat',
            old_name='photo_url',
            new_name='photo',
        ),
        migrations.AlterField(
            model_name='goat',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='goats/'),
        ),
        # FIX #2: Expense payment_method max_length 1 → 2
        migrations.AlterField(
            model_name='expense',
            name='payment_method',
            field=models.CharField(
                choices=[('C', 'Cash'), ('B', 'Bank Transfer'), ('CH', 'Cheque'), ('O', 'Online/UPI')],
                default='C',
                max_length=2,
            ),
        ),
    ]
