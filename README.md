# DeMark Dashboard Scaffold (No Indicators Yet)

This project is a clean Streamlit scaffold for a DeMark dashboard workflow.

What is included now:
- Streamlit dashboard shell
- Sidebar ticker/watchlist controls
- Sidebar indicator checklist (placeholders only)
- Daily OHLC chart (no indicator overlays)
- Data loading with yfinance + synthetic fallback

What is intentionally not included yet:
- Indicator logic or calculations
- Overlay plotting for any TD studies

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The indicator checkboxes are UI placeholders only for step-by-step implementation later.
- Everything in this scaffold is saved in this folder and ready for GitHub versioning.
