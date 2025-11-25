# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # User 인덱스
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=20, blank=True, null=True, verbose_name='전화번호', db_index=True),
        ),

        # WatchList 인덱스
        migrations.AddIndex(
            model_name='watchlist',
            index=models.Index(fields=['user', '-created_at'], name='accounts_watchlist_user_idx'),
        ),
    ]
