import argparse
import asyncio
import logging
from datetime import date, datetime

from .main import main


HELPS = '''
Parse and save listed stocks information and the daily top3 stocks of each industry.
'''


def parse_date(date_str: str) -> datetime:
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except TypeError:
        logging.debug('invalid date format, use today')
        target_date = date.today()
    finally:
        return target_date


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=HELPS
)
parser.add_argument(
    '-v',
    '--verbose',
    action='store_true',
    help='increase output verbosity'
)
parser.add_argument(
    '-d',
    '--date',
    type=str,
    help='parse specific date, the valid format is yyyy-mm-dd, set as today if not specify'
)

args = parser.parse_args()
log_level = logging.DEBUG if args.verbose else logging.INFO
logging.basicConfig(level=log_level)

target_date = parse_date(args.date)

logging.info(f'{datetime.now()} start')
asyncio.run(main(target_date))
logging.info(f'{datetime.now()} complete')
