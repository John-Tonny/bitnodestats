import pytz
from django.utils import timezone


SEGWIT_START = pytz.utc.localize(timezone.datetime.strptime("2016-11-12", "%Y-%m-%d"))
SEGWIT_END = pytz.utc.localize(timezone.datetime.strptime("2017-11-12", "%Y-%m-%d"))
SEGWIT_BIT = 1
BIP91_BIT = 4


def check_is_segwit_block(blockheader):
    if get_bit_state(blockheader.version, SEGWIT_BIT) and (SEGWIT_START < blockheader.time < SEGWIT_END):
        return True
    else:
        return False


def check_is_bip91_block(blockheader):
    if get_bit_state(blockheader.version, BIP91_BIT):
        return True
    else:
        return False


def get_bit_state(bit_array, bit_number):
    return (bit_array & (1 << bit_number)) != 0
