import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Undervärderade Aktier", layout="wide")
st.title("📊 Hitta undervärderade aktier")

st.markdown("""
Denna app analyserar ett antal aktier och visar vilka som ser billiga ut just nu utifrån:
- **P/E-tal < 15**
- **P/B-tal < 2**
- **Direktavkastning > 3%** (om tillgänglig)

**Datakälla:** Yahoo Finance via `yfinance`
""")

# Exempellista med aktier att analysera
stocks = st.text_area("Ange ticker-symboler (komma-separerade):", "AAPL,MSFT,TSLA,AZN.ST,INVEB.ST")
tickers = [s.strip() for s in stocks.split(",") if s.strip() != ""]

pe_limit = st.slider("Max P/E", 1, 30, 15)
pb_limit = st.slider("Max P/B", 0.1, 10.0, 2.0)
div_limit = st.slider("Min direktavkastning (%)", 0.0, 10.0, 3.0)

@st.cache_data(show_spinner=False)
def fetch_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            pe = info.get("trailingPE", None)
            pb = info.get("priceToBook", None)
            dividend = info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0
            name = info.get("shortName", ticker)
            market_cap = info.get("marketCap", None)
            data.append({
                "Ticker": ticker,
                "Namn": name,
                "P/E": pe,
                "P/B": pb,
                "Direktavkastning (%)": round(dividend, 2),
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
        (df["Direktavkastning (%)"] > div_limit)
    ]
    st.success(f"{len(filt)} av {len(df)} aktier matchar kriterierna")
    st.dataframe(filt.style.format({
        "P/E": "{:.1f}",
        "P/B": "{:.2f}",
        "Direktavkastning (%)": "{:.1f}",
        "Marknadsvärde (MUSD)": "{:.0f}"
    }), use_container_width=True)
