import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Undervärderade Aktier", layout="wide")
st.title("📊 Hitta undervärderade aktier")

st.markdown("""
Denna app analyserar ett antal aktier och visar vilka som ser billiga ut just nu utifrån:
- **P/E-tal < 15**
- **P/B-tal < 2**
- **Direktavkastning > 3%**
- **EV/EBIT < 15** *(om tillgängligt)*
- **PEG-tal < 1.5** *(om tillgängligt)*
- **ROE > 10%** *(avkastning på eget kapital)*
- **Skuldsättning (D/E) < 1.0**

**Datakälla:** Yahoo Finance via `yfinance`
""")

stocks = st.text_area("Ange ticker-symboler (komma-separerade):", "AAPL,MSFT,TSLA,AZN.ST,INVEB.ST")
tickers = [s.strip() for s in stocks.split(",") if s.strip() != ""]

pe_limit = st.slider("Max P/E", 1, 30, 15)
pb_limit = st.slider("Max P/B", 0.1, 10.0, 2.0)
div_limit = st.slider("Min direktavkastning (%)", 0.0, 10.0, 3.0)
ev_ebit_limit = st.slider("Max EV/EBIT", 1, 40, 15)
peg_limit = st.slider("Max PEG", 0.1, 3.0, 1.5)
roe_limit = st.slider("Min ROE (%)", 0.0, 40.0, 10.0)
debt_equity_limit = st.slider("Max Debt/Equity", 0.0, 3.0, 1.0)

@st.cache_data(show_spinner=False)
def fetch_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            pe = info.get("trailingPE")
            pb = info.get("priceToBook")
            dividend = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
            peg = info.get("pegRatio")
            roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0
            debt_equity = info.get("debtToEquity")
            ebit = info.get("ebit")
            ev = info.get("enterpriseValue")
            ev_ebit = ev / ebit if ev and ebit else None
            name = info.get("shortName", ticker)
            market_cap = info.get("marketCap")
            data.append({
                "Ticker": ticker,
                "Namn": name,
                "P/E": pe,
                "P/B": pb,
                "Direktavkastning (%)": round(dividend, 2),
                "PEG": peg,
                "ROE (%)": round(roe, 1),
                "D/E": round(debt_equity, 2) if debt_equity else None,
                "EV/EBIT": round(ev_ebit, 2) if ev_ebit else None,
                "Marknadsvärde (MUSD)": round(market_cap / 1e6, 1) if market_cap else None
            })
        except Exception as e:
            st.warning(f"Fel vid hämtning av data för {ticker}: {e}")
    return pd.DataFrame(data)

if st.button("Analysera"):
    df = fetch_data(tickers)
    st.subheader("🔍 Resultat")
    filt = df[
        (df["P/E"] < pe_limit) &
        (df["P/B"] < pb_limit) &
        (df["Direktavkastning (%)"] > div_limit) &
        (df["PEG"] < peg_limit) &
        (df["ROE (%)"] > roe_limit) &
        (df["D/E"] < debt_equity_limit) &
        (df["EV/EBIT"] < ev_ebit_limit)
    ]
    st.success(f"{len(filt)} av {len(df)} aktier matchar kriterierna")
    st.dataframe(filt.style.format({
        "P/E": "{:.1f}",
        "P/B": "{:.2f}",
        "Direktavkastning (%)": "{:.1f}",
        "PEG": "{:.2f}",
        "ROE (%)": "{:.1f}",
        "D/E": "{:.2f}",
        "EV/EBIT": "{:.2f}",
        "Marknadsvärde (MUSD)": "{:.0f}"
    }), use_container_width=True)
