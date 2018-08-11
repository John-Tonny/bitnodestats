import pytz

from django.shortcuts import render
from django.http import Http404
from django.utils import timezone

import bitcoin.rpc
import bitcoin.core

from .models import BlockStatistics, Block
from lib.bitcoin_utils.rpc_bitcoinlib import SerialRPC
from lib.calculation import running_mean



def date_string_to_localized_datetime(date_string):
    try:
        datetime = pytz.utc.localize(timezone.datetime.strptime(date_string, "%Y-%m-%d-%H:%M"))
    except ValueError:
        raise Http404("Date specified is not a valid date. Format must be YYYY-MM-DD HH-mm.")

    return datetime


def date_string_days_ago(days):
    datetime_delta = timezone.datetime.now(tz=pytz.utc) - timezone.timedelta(days=days)
    datetime_delta_string = datetime_delta.strftime("%Y-%m-%d-%H:%M")
    return datetime_delta_string


def date_string_now():
    return timezone.datetime.now(tz=pytz.utc).strftime("%Y-%m-%d-%H:%M")


def get_item_date_range(item, date_begin, date_end):
    return Block.objects.filter(time__range=(date_begin, date_end)).values_list(item, flat=True)


def bitcoind_get_info():
    try:
        bitcoind_rpc = SerialRPC()
        getinfo = bitcoind_rpc.proxy.getbestblockhash()
        return getinfo
    except ConnectionRefusedError:
        raise Http404("Connection to bitcoind could not be established.\
        Run it with '$ bitcoind -daemon'.")
    except bitcoin.rpc.InWarmupError:
        raise Http404("Bitcoind is still in the starting phase. It can take some time\
        until it is ready.")


def index(request):
    """
    Main page of bitnodestats.
    """
    context = {}
    return render(request, 'nodestats/base.html', context)


def blockheight(request,
                date_begin=date_string_days_ago(10),
                date_end=date_string_now()):
    """
    Shows a graph of blockheight.
    """
    date_begin = date_string_to_localized_datetime(date_begin)
    date_end = date_string_to_localized_datetime(date_end)

    blockheights = get_item_date_range('height', date_begin, date_end)
    times = get_item_date_range('time', date_begin, date_end)

    context = {
        'times': times,
        'blockheights': blockheights,
    }
    return render(request, 'nodestats/blockheight.html', context)


def segwit(request,
           date_begin=date_string_days_ago(50),
           date_end=date_string_now()):
    """
    Shows a graph of segwit activation.
    """
    date_begin = date_string_to_localized_datetime(date_begin)
    date_end = date_string_to_localized_datetime(date_end)

    time_bins = BlockStatistics.objects.filter(time__range=(date_begin, date_end)).values_list('time', flat=True)
    segwit_average_2016 = BlockStatistics.objects.filter(
        time__range=(date_begin, date_end)).values_list('segwit_average_2016', flat=True)
    segwit_average_144 = BlockStatistics.objects.filter(
        time__range=(date_begin, date_end)).values_list('segwit_average_144', flat=True)
    bip91_average_144 = BlockStatistics.objects.filter(
        time__range=(date_begin, date_end)).values_list('bip91_average_144', flat=True)

    context = {
        'times': time_bins,
        'segwit_average_144': segwit_average_144,
        'segwit_average_2016': segwit_average_2016,
        'bip91_average_144': bip91_average_144,
    }

    return render(request, 'nodestats/segwit.html', context)


def difficulty(request, date_begin=date_string_days_ago(356*1), date_end=date_string_now()):
    """
    Shows a graph of difficulty.
    """
    date_begin = date_string_to_localized_datetime(date_begin)
    date_end = date_string_to_localized_datetime(date_end)

    time_bins = BlockStatistics.objects.filter(time__range=(date_begin, date_end)).values_list('time', flat=True)
    diff = BlockStatistics.objects.filter(time__range=(date_begin, date_end)).values_list('difficulty', flat=True)

    hashrate144 = BlockStatistics.objects.filter(time__range=(date_begin, date_end)).values_list('hashrate', flat=True)
    hashrate1008 = running_mean(hashrate144, 7)
    hashrate2016 = running_mean(hashrate144, 14)

    # for plotting we need to increase the window
    min_hash = min(hashrate144)
    max_hash = max(hashrate144)

    diff_to_hash_per_sec = (2**32 / 600)

    min_diff = min_hash / diff_to_hash_per_sec
    max_diff = max_hash / diff_to_hash_per_sec

    context = {
        'times': time_bins,
        'difficulty': diff,
        'hashrate144': hashrate144,
        'hashrate1008': hashrate1008,
        'hashrate2016': hashrate2016,
        'min_diff': min_diff,
        'max_diff': max_diff,
        'min_hash': min_hash,
        'max_hash': max_hash
    }

    return render(request, 'nodestats/difficulty.html', context)


def blocksize(request, date_begin=date_string_days_ago(356*3), date_end=date_string_now()):
    """
    Shows a graph of difficulty.
    """
    date_begin = date_string_to_localized_datetime(date_begin)
    date_end = date_string_to_localized_datetime(date_end)

    time_bins = BlockStatistics.objects.filter(time__range=(date_begin, date_end)).values_list('time', flat=True)
    size = BlockStatistics.objects.filter(time__range=(date_begin, date_end)).values_list('size', flat=True)

    context = {
        'times': time_bins,
        'blocksize': size,
    }

    return render(request, 'nodestats/blocksize.html', context)
