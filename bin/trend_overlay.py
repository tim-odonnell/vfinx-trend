"""Trend-lines chart: price over the last N years with every trend line drawn faintly behind it (SVG, stdlib only).

Written by a local Gemma E2B (Google official q4_0) in 9 guided steps, checked by Claude: 94 tests pass and the output is
identical to Claude's reference (~/e2b-abilities/tasks/06b-trend-overlay-steps). overlay_svg(prices, trends, last_date,
last_price, next_day, years) - prices = [(date, price)], trends = [{name, start, a, b, r2}] with price = exp(a + b*days since start).
A trend with special=True gets the extra class 'avg' on its line and label (the amber all-history trend; Claude, 2026-11-20)."""
import datetime
import math

W, H, L, R, T, B = 640, 300, 48, 44, 10, 18


def money(v: float) -> str:
    if v >= 1000:
        return f'${v:,.0f}'
    return f'${v:,.2f}'


def trend_price(t: dict, d: datetime.date) -> float:
    return math.exp(t['a'] + t['b'] * (d - t['start']).days)


def visible(prices, last_date, years):
    d1 = last_date - datetime.timedelta(days=round(365.25 * years))
    
    relevant_prices = []
    for d, price in prices:
        if d >= d1:
            relevant_prices.append((d, price))
            
    return d1, relevant_prices


def thin(pts, maxn=500):
    if len(pts) > maxn:
        step = max(1, len(pts) // maxn)
        out = pts[::step]
        if out[-1] != pts[-1]:
            out.append(pts[-1])
        return out
    return pts


def place_labels(ys, gap=10):
    if not ys:
        return []

    # 1. Create pairs of (value, original_index) and sort by value (stable sort is default for Python's sort)
    indexed_ys = sorted([(value, i) for i, value in enumerate(ys)])

    new_ys_sorted = []
    last_calculated_value = None

    # 2. Walk through the positions sorted by ys value to calculate new values
    for value, original_index in indexed_ys:
        if last_calculated_value is None:
            # The first value in the sorted walk is simply its original value
            current_calculated_value = value
            new_ys_sorted.append(current_calculated_value)
            last_calculated_value = current_calculated_value
            continue

        # Check the condition: must be at least gap more than the previous calculated value
        required_min = last_calculated_value + gap
        
        if value < required_min:
            current_calculated_value = required_min
        else:
            current_calculated_value = value
        
        new_ys_sorted.append(current_calculated_value)
        last_calculated_value = current_calculated_value
        
    # 3. Map the calculated values back to the original order of ys
    result = [0] * len(ys)
    for i, (value, original_index) in enumerate(indexed_ys):
        # new_ys_sorted[i] holds the new value for the element that was originally at index original_index
        result[original_index] = new_ys_sorted[i]
        
    return result


def trend_ends(trends, d1, d2):
    """
    Calculates the start date, price at d1, and price at d2 for each trend.
    Returns a list of tuples (sd, p1, p2).
    """
    results = []
    for t in trends:
        sd = max(d1, t['start'])
        p1 = trend_price(t, sd)
        p2 = trend_price(t, d2)
        results.append((sd, p1, p2))
    return results


def price_range(pts, ends):
    """
    Calculates the price range based on collected prices and trend ends.
    pts: list of (date, price) pairs, for example [(datetime.date(2026,1,1), 100.0), (datetime.date(2026,1,6), 110.0)].
    ends: the list that trend_ends returns: (sd, p1, p2) tuples.
    Returns (0.97 * min(all), 1.03 * max(all)).
    """
    all_prices = [price for date, price in pts] + [e[1] for e in ends] + [e[2] for e in ends]
    
    if not all_prices:
        # Handle case where pts might be empty, although based on guide logic it shouldn't be.
        return (0.97 * 100.0, 1.03 * 100.0)
        
    min_p = min(all_prices)
    max_p = max(all_prices)
    return (0.97 * min_p, 1.03 * max_p)


def x_of(d, d1, d2):
    """
    Calculates the x-coordinate for a given date d based on d1 and d2.
    x_of(d) = L + (d - d1).days / (d2 - d1).days * (W - L - R)
    """
    return L + (d - d1).days / (d2 - d1).days * (W - L - R)


def y_of(p, lo, hi):
    """
    Calculates the y-coordinate for a given price p based on lo and hi.
    y_of(p) = T + (math.log(hi) - math.log(p)) / (math.log(hi) - math.log(lo)) * (H - T - B)
    """
    # Avoid division by zero if lo == hi, though unlikely if data is varied
    if math.log(hi) == math.log(lo):
        return T # Or handle error, but returning T seems safer if range is zero.
        
    return T + (math.log(hi) - math.log(p)) / (math.log(hi) - math.log(lo)) * (H - T - B)


def axis_parts(lo, hi, d1, d2):
    """
    Generates the SVG axis parts for the chart.
    """
    # 1. Chart frame
    line_part = f'<line x1="{L}" y1="{H - B}" x2="{W - R}" y2="{H - B}" class="ax"/>'
    
    # 2. Hi text
    hi_text_part = f'<text x="{L - 4}" y="{T + 8}" class="tk" text-anchor="end">{money(hi)}</text>'
    
    # 3. Lo text
    lo_text_part = f'<text x="{L - 4}" y="{H - B}" class="tk" text-anchor="end">{money(lo)}</text>'
    
    # 4. d1 text
    d1_text_part = f'<text x="{L}" y="{H - 4}" class="tk">{d1:%b %Y}</text>'
    
    # 5. d2 text
    d2_text_part = f'<text x="{W - R}" y="{H - 4}" class="tk" text-anchor="end">{d2:%b %Y}</text>'
    
    return [line_part, hi_text_part, lo_text_part, d1_text_part, d2_text_part]


def line_parts(trends, ends, last_date, last_price, d1, d2, lo, hi):
    lines = []
    for t in trends:
        sd = max(d1, t['start'])
        p1 = trend_price(t, sd)
        p2 = trend_price(t, d2)
        
        op = max(0.15, t['r2'])
        cls = 'up' if last_price >= trend_price(t, last_date) else 'down'
        
        x1 = x_of(sd, d1, d2)
        y1 = y_of(p1, lo, hi)
        x2 = x_of(d2, d1, d2)
        y2 = y_of(p2, lo, hi)
        
        extra = ' avg' if t.get('special') else ''   # Claude 2026-11-20: the amber all-history line
        line_string = f'<line x1="{x_of(sd, d1, d2):.1f}" y1="{y_of(p1, lo, hi):.1f}" x2="{x_of(d2, d1, d2):.1f}" y2="{y_of(p2, lo, hi):.1f}" class="ghost {cls}{extra}" style="opacity:{op:.2f}"/>'
        lines.append(line_string)
        
    return lines


def label_parts(trends, ends, lo, hi):
    """
    Labels the trend lines on the chart.
    Returns a list of formatted text elements for the trend labels.
    """
    # Calculate the y-positions for the end points (p2) of all trend segments
    y_positions = [y_of(p2, lo, hi) for sd, p1, p2 in ends]
    
    # Place labels using place_labels. This function handles spacing logic.
    placed = place_labels(y_positions)

    labels = []
    for i, t in enumerate(trends):
        # Calculate opacity based on r2, ensuring minimum opacity is 0.15
        op = max(0.15, t['r2'])
        
        # The x position for labels is fixed at W - R + 4 (which is 640 - 44 + 4 = 500)
        # The y position is the placed position for this trend, plus a small offset (3)
        text_y = placed[i] + 3
        
        label_text = f'<text x="{W - R + 4}" y="{text_y:.1f}" class="tk lbl{' avg' if t.get('special') else ''}" style="opacity:{max(op, 0.45):.2f}">{t["name"]}</text>'
        
        labels.append(label_text)
        
    return labels


def price_parts(pts, last_date, last_price, d1, d2, lo, hi):
    path = 'M' + 'L'.join(f'{x_of(d, d1, d2):.1f},{y_of(p, lo, hi):.1f}' for d, p in pts)
    f'<path d="{path}" class="price"/>'
    f'<circle cx="{x_of(last_date, d1, d2):.1f}" cy="{y_of(last_price, lo, hi):.1f}" r="3.5" class="fgfill"/>'
    return [f'<path d="{path}" class="price"/>', f'<circle cx="{x_of(last_date, d1, d2):.1f}" cy="{y_of(last_price, lo, hi):.1f}" r="3.5" class="fgfill"/>']


def overlay_svg(prices, trends, last_date, last_price, next_day, years=5):
    d1, pts = visible(prices, last_date, years); pts = thin(pts); d2 = next_day
    ends = trend_ends(trends, d1, d2); lo, hi = price_range(pts, ends)
    
    parts = ['<svg class="chart wide" viewBox="0 0 640 300" role="img">']
    
    # Handle axis_parts which is expected to return a list based on error
    axis_elements = axis_parts(lo, hi, d1, d2)
    if isinstance(axis_elements, list):
        parts.extend(axis_elements)
    else:
        parts.append(axis_elements)
    
    # Handle line_parts which is expected to return a list based on error
    line_elements = line_parts(trends, ends, last_date, last_price, d1, d2, lo, hi)
    if isinstance(line_elements, list):
        parts.extend(line_elements)
    else:
        parts.append(line_elements)
        
    # Handle label_parts
    label_elements = label_parts(trends, ends, lo, hi)
    if isinstance(label_elements, list):
        parts.extend(label_elements)
    else:
        parts.append(label_elements)
        
    # Handle price_parts
    price_elements = price_parts(pts, last_date, last_price, d1, d2, lo, hi)
    if isinstance(price_elements, list):
        parts.extend(price_elements)
    else:
        parts.append(price_elements)
        
    parts.append('</svg>')
    return '\n'.join(parts)

