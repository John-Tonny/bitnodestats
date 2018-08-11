from django.db import models


class Block(models.Model):
    """
    Data model for bitcoin blockchain headers. Saves essential data only.
    """
    hash = models.CharField(max_length=64)
    height = models.IntegerField(primary_key=True)
    version = models.IntegerField()
    time = models.DateTimeField()
    difficulty = models.FloatField()
    previousblockhash = models.CharField(max_length=64)
    nextblockhash = models.CharField(max_length=64)
    chainwork = models.CharField(max_length=64)
    transactions = models.IntegerField(default=0)
    transactions_estimated = models.IntegerField(default=0)
    size = models.IntegerField(default=0)
    coinbase_string = models.CharField(max_length=200, default='0')

    # for admin site
    def __str__(self):
        return str(self.height)


class BlockStatistics(models.Model):
    """
    Data Model which holds average statistics over blockheaders, which is temporaly coarse grained.
    """
    time = models.DateTimeField()
    bin_start = models.IntegerField(primary_key=True)
    segwit_average_2016 = models.FloatField()
    segwit_average_144 = models.FloatField()
    bip91_average_144 = models.FloatField()
    difficulty = models.FloatField()
    size = models.FloatField()
    hashrate = models.FloatField()
    transactions_day = models.IntegerField(default=0)
    transactions_estimated_day = models.IntegerField(default=0)
