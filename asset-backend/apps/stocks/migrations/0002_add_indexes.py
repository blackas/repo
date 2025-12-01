# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        # Stock 인덱스
        migrations.AlterField(
            model_name='stock',
            name='name',
            field=models.CharField(max_length=100, verbose_name='종목명', db_index=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='market',
            field=models.CharField(max_length=20, blank=True, null=True, verbose_name='시장', db_index=True),
        ),

        # DailyPrice 복합 인덱스
        migrations.AddIndex(
            model_name='dailyprice',
            index=models.Index(fields=['trade_date', '-change_rate'], name='stocks_daily_trade_date_idx'),
        ),
        migrations.AddIndex(
            model_name='dailyprice',
            index=models.Index(fields=['stock', 'trade_date'], name='stocks_daily_stock_date_idx'),
        ),
    ]
