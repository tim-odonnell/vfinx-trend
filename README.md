# vfinx-trend

Daily report: is **VFINX** (Vanguard 500 Index Fund Investor Shares) **above or below its trend** over 1 month,
3 and 6 months, 1, 5, 10, 20, 30 and 40 years, and what NAV the **next trading day** would need to be exactly on each trend.

- Data: Yahoo Finance `VFINX`, the full daily history since 1980-01-02 (the oldest daily data free sources have; the
  fund started in 1976). Each run downloads all of it (~1 MB) and saves it as
  `~/VFINX-Reports/data/vfinx-daily.csv` (`date,close,adjclose`) - ready for other uses, and used by the report
  when a download fails (the report then says so). Today's bar is ignored until 18:00 New York time (NAV not out yet).
- Trend: least-squares line through the **log** of the dividend-adjusted closes in each window (= exponential trend,
  dividends reinvested), shown in today's NAV dollars and extended to the next trading day. R² shows how well prices
  followed the line - near 0 means that window has no real trend.
- Chart: under the dots and bars, the last 5 years of price with every trend line drawn faintly behind it (`bin/trend_overlay.py`,
  written by a local Gemma E2B in 9 guided steps and checked against a reference - see ~/e2b-abilities task 6b). On phones it opens at today; swipe for earlier years.
- Output: `~/VFINX-Reports/<last close date>.html` + `.md`, `latest.html`; desktop pop-up with "Open report".
  Takes ~2 s; no AI model involved (numbers are computed, never written by a model).

| Command / icon | What it does |
|---|---|
| `vfinx-run-now` / **VFINX Report - Run Now** | make the report now |
| `vfinx-mode nightly` / **VFINX Report - Nightly Auto** | run automatically Mon-Fri 06:35 (a missed run is made at next boot) |
| `vfinx-mode manual` / **VFINX Report - Manual Mode** | no automatic runs (the default after install) |
| `vfinx-mode status` | mode, next run, last run, newest report |
| `vfinx-trend --json FILE --now 2026-11-19T07:00 --out DIR` | offline test run |

Install: `./install.sh`. Trend lines are fitted to past prices; they are not a forecast and not financial advice.
Made from gold-trend; the data module `bin/vfinx_data.py` was drafted by a local Gemma E2B and finished by Claude.
