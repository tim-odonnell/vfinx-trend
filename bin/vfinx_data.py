import csv
import datetime
import os
from zoneinfo import ZoneInfo

NY = ZoneInfo('America/New_York')
CLOSE_HOUR = 18


class DataError(Exception):
    pass

def load_yahoo(data, now_ny):
    try:
        close_prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
        adjclose_prices = data['chart']['result'][0]['indicators']['adjclose'][0]['adjclose']
        stamps = data['chart']['result'][0]['timestamp']
    except (KeyError, IndexError, TypeError) as e:
        raise DataError('unexpected data layout') from e

    results = []
    for i in range(len(close_prices)):
        close_price = close_prices[i]
        adjclose_price = adjclose_prices[i]

        if close_price is None or adjclose_price is None or close_price <= 0 or adjclose_price <= 0:
            continue

        timestamp = stamps[i]
        date_obj = datetime.datetime.fromtimestamp(timestamp, NY).date()
        results.append((date_obj, float(close_price), float(adjclose_price)))

    # Remove entry whose date equals now_ny.date() if now_ny.hour < CLOSE_HOUR
    new_results = []
    for date_obj, close_price, adjclose_price in results:
        if now_ny.hour >= CLOSE_HOUR or date_obj != now_ny.date():
            new_results.append((date_obj, close_price, adjclose_price))

    # One row per date (a later item wins), sorted by date
    by_date = {d: (c, a) for d, c, a in new_results}
    return [(d, c, a) for d, (c, a) in sorted(by_date.items())]

def write_csv(path, rows):
    # Fix 3: write_csv with a bare file name
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['date', 'close', 'adjclose'])
        for date, close, adjclose in rows:
            writer.writerow([date.isoformat(), f'{close:.4f}', f'{adjclose:.4f}'])

def read_csv(path):
    if not os.path.exists(path):
        return []

    data = []
    try:
        with open(path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # skip header
            for row in reader:
                if not row:
                    continue
                date_str, close_str, adjclose_str = row
                try:
                    date_obj = datetime.date.fromisoformat(date_str)
                    close_val = float(close_str)
                    adjclose_val = float(adjclose_str)
                    data.append((date_obj, close_val, adjclose_val))
                except ValueError:
                    # Skip malformed lines if necessary, though problem description implies clean data
                    continue
    except Exception:
        return []
    return data

if __name__ == "__main__":
    # Example usage if needed, but for testing we assume functions are the main deliverable
    pass