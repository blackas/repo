# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        # DailyReport 인덱스
        migrations.AddIndex(
            model_name='dailyreport',
            index=models.Index(fields=['user', '-report_date'], name='reports_user_date_idx'),
        ),
        migrations.AddIndex(
            model_name='dailyreport',
            index=models.Index(fields=['-created_at'], name='reports_created_idx'),
        ),
    ]
