from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

DATA_PATH = Path(__file__).parents[1] / "task_1_web_scraping" / "data" / "books_scraped.csv"
df = pd.read_csv(DATA_PATH)

st.set_page_config(page_title="CodeAlpha Books Dashboard", layout="wide")
st.title("Books to Scrape Analytics Dashboard")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Books", f"{len(df):,}")
c2.metric("Average Price", f"£{df['price_gbp'].mean():.2f}")
c3.metric("Median Price", f"£{df['price_gbp'].median():.2f}")
c4.metric("Average Rating", f"{df['rating_numeric'].mean():.2f}/5")

selected = st.multiselect(
    "Filter star ratings",
    options=sorted(df["rating_numeric"].dropna().unique()),
    default=sorted(df["rating_numeric"].dropna().unique()),
)
filtered = df[df["rating_numeric"].isin(selected)]

col1, col2 = st.columns(2)

with col1:
    fig = plt.figure(figsize=(7, 4))
    plt.hist(filtered["price_gbp"], bins=20, edgecolor="black")
    plt.xlabel("Price (GBP)")
    plt.ylabel("Books")
    plt.title("Price Distribution")
    st.pyplot(fig)

with col2:
    counts = filtered["rating_numeric"].value_counts().sort_index()
    fig = plt.figure(figsize=(7, 4))
    plt.bar(counts.index.astype(str), counts.values)
    plt.xlabel("Star Rating")
    plt.ylabel("Books")
    plt.title("Rating Distribution")
    st.pyplot(fig)

st.subheader("Most Expensive Books")
st.dataframe(
    filtered.nlargest(15, "price_gbp")[
        ["title", "price_gbp", "rating_numeric", "in_stock"]
    ],
    use_container_width=True,
)
