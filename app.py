import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import WordCloud
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from sklearn.manifold import TSNE
import plotly.graph_objects as go

# Initialize Qdrant client
client = QdrantClient("localhost", port=6333)
embedder = TextEmbedding()

# Load the stored CSV with scraped data and sentiment analysis
@st.cache_data
def load_data():
    return pd.read_csv("./data/main_jpm_transcripts.csv")

df = load_data()

@st.cache_data
def load_sentiment_data():
    return pd.read_csv('./data/sentiment_analysis_jpm.csv')

sent_df = load_sentiment_data()

# Streamlit App UI
st.title("AI-Powered Financial Data Dashboard")

# Sidebar Navigation
option = st.sidebar.radio(
    "Select Analysis",
    ["Vector Search", "Sentiment Analysis", "Data Overview", "Word Cloud", "Embeddings Explorer"]
)

# ---- VECTOR SEARCH ----
if option == "Vector Search":
    st.subheader("Ask a financial question")
    query_text = st.text_input("Enter your query:")

    if st.button("Search"):
        if query_text:
            query_embedding = list(embedder.embed([query_text]))[0]
            search_result = client.search(
                collection_name="JPM_Transcripts",
                query_vector=query_embedding,
                limit=5
            )
            st.subheader("Top Matching Results")
            for i, result in enumerate(search_result):
                st.write(f"**Result {i+1} (Score: {result.score:.2f})**")
                st.write(result.payload)  # Assuming metadata is stored


# ---- SENTIMENT ANALYSIS ----
elif option == "Sentiment Analysis":
    st.subheader("Sentiment Score Variation by Quarter")

    if "Title" in sent_df.columns and "sentiment" in sent_df.columns and not sent_df.empty:
        import re

        # Extract Quarter and Year from the Title column
        def extract_quarter_year(title):
            match = re.search(r"(Q[1-4])\s(\d{4})", title)
            return match.group(0) if match else None

        # Apply extraction
        sent_df["Quarter_Label"] = sent_df["Title"].apply(extract_quarter_year)

        # Remove rows where quarter-year couldn't be extracted
        sent_df = sent_df.dropna(subset=["Quarter_Label"])

        # Extract Year and Quarter separately
        sent_df["Year"] = sent_df["Quarter_Label"].str.extract(r"(\d{4})").astype(int)
        sent_df["Quarter"] = sent_df["Quarter_Label"].str.extract(r"(Q[1-4])")

        # Sort data by Year and Quarter
        sent_df = sent_df.sort_values(["Year", "Quarter"])

        # --- First Chart: Line Plot for Sentiment Trends Per Quarter ---
        fig1, ax1 = plt.subplots(figsize=(12, 6))

        for title in sent_df["Title"].unique():
            subset = sent_df[sent_df["Title"] == title]
            ax1.plot(subset["Quarter_Label"], subset["sentiment"], marker="o", linestyle="-", label=title)

        ax1.set_xlabel("Quarter")
        ax1.set_ylabel("Sentiment Score")
        ax1.set_title("Sentiment Score Trends by Quarter")
        ax1.tick_params(axis="x", rotation=45)
        ax1.legend(title="Title", loc="upper left", bbox_to_anchor=(1, 1))  # Legend outside

        st.pyplot(fig1)

        # --- Second Chart: Bar Chart for Aggregated Sentiment Score Per Year ---
        st.subheader("Aggregated Sentiment Score Per Year")

        # Compute the mean sentiment score per year
        yearly_sentiment = sent_df.groupby("Year")["sentiment"].mean().reset_index()

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(x="Year", y="sentiment", data=yearly_sentiment, ax=ax2, palette="Blues")

        ax2.set_xlabel("Year")
        ax2.set_ylabel("Average Sentiment Score")
        ax2.set_title("Yearly Aggregated Sentiment Score")

        st.pyplot(fig2)

    else:
        st.warning("Sentiment analysis data not available.")

   

    # Extract Quarter from Title
    def extract_quarter(title):
        match = re.search(r"(Q[1-4])\s(\d{4})", title)
        return match.group(0) if match else None

    sent_df["quarter"] = sent_df["Title"].apply(extract_quarter)
    sent_df = sent_df.dropna(subset=["quarter"])  # Ensure valid data

    # Dropdown to select a quarter
    selected_quarter = st.selectbox("Select a Quarter", sent_df["quarter"].unique())

    # Filter data
    filtered_df = sent_df[sent_df["quarter"] == selected_quarter]

    if not filtered_df.empty:
        # Convert categorical sentiment to numerical values if necessary
        sentiment_map = {"POSITIVE": 1, "NEUTRAL": 0, "NEGATIVE": -1}
        filtered_df["sentiment_num"] = filtered_df["sentiment"].map(sentiment_map)

        # Calculate sentiment percentages
        pos_perc = (filtered_df[filtered_df["sentiment"] == "POSITIVE"].shape[0] * 100) / filtered_df.shape[0]
        neg_perc = (filtered_df[filtered_df["sentiment"] == "NEGATIVE"].shape[0] * 100) / filtered_df.shape[0]

        # Normalize sentiment score
        sentiment_score = 50 + (pos_perc - neg_perc)  # Centered at 50 for better gauge movement
    else:
        sentiment_score = 50  # Default neutral value

    # Gauge Chart for Sentiment Score
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sentiment_score,
        title={'text': f"Sentiment Score - {selected_quarter}"},
        delta={'reference': 50},  # Changes are reflected against the neutral baseline
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 40], 'color': "firebrick"},
                {'range': [40, 60], 'color': "navajowhite"},
                {'range': [60, 100], 'color': "darkgreen"}
            ]
        }
    ))

    st.plotly_chart(fig_gauge)


# ---- DATA OVERVIEW ----
elif option == "Data Overview":
    st.subheader("Scraped Data Overview")
    st.dataframe(df)

    # Download Button
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv_data, file_name="scraped_data.csv", mime="text/csv")

# ---- WORD CLOUD ----
elif option == "Word Cloud":
    st.subheader("Word Cloud of Most Frequent Words")

    text_data = " ".join(df["Text"].dropna().tolist())
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_data)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# ---- EMBEDDINGS EXPLORER ----
elif option == "Embeddings Explorer":
    st.subheader("2D Visualization of Embeddings")

    # Convert text to embeddings
    embeddings = list(embedder.embed(df["Text"].dropna().tolist()))
    n_samples = len(embeddings)

    if n_samples < 2:
        st.warning("Not enough data for visualization.")
    else:
        # Adjust perplexity based on available data
        perplexity = min(30, max(1, n_samples - 1)) 

        # Reduce dimensionality using t-SNE
        tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
        reduced_embeddings = tsne.fit_transform(np.array(embeddings))

        df_plot = pd.DataFrame(reduced_embeddings, columns=["x", "y"])

        # Plot embeddings
        fig, ax = plt.subplots()
        sns.scatterplot(x=df_plot["x"], y=df_plot["y"], ax=ax)
        ax.set_title("Embedding Similarities (t-SNE)")
        st.pyplot(fig)

