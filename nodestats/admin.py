from django.contrib import admin

from .models import Block, BlockStatistics


class BlockheaderAdmin(admin.ModelAdmin):
    list_display = ('height', 'hash', 'time')
    model = Block


class BlockheaderStatisticsAdmin(admin.ModelAdmin):
    list_display = ('bin_start', 'time', 'segwit_average_144', 'bip91_average_144', 'difficulty', 'hashrate')
    model = Block


admin.site.register(Block, BlockheaderAdmin)
admin.site.register(BlockStatistics, BlockheaderStatisticsAdmin)
