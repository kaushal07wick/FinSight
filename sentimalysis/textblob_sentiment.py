import pandas as pd 
from textblob import TextBlob
import matplotlib.pyplot as plt

df = pd.read_csv(r"C:/Users/Lenovo/Documents/Experiment/scraping/data/main_jpm_transcripts.csv", index_col=0)

print(df.head())

def get_sentiment(text):
    analysis = TextBlob(str(text))
    return analysis.sentiment.polarity

print("Running sentiment analysis on the transcripts")
df['sentiment'] = df['Text'].apply(get_sentiment)

#classify into positive, neutral and negative
df["sentiment_label"] = df["sentiment"].apply(
    lambda x: "Positive" if x > 0.5 else "Negative" if x < -0.5 else "Neutral"
)

print(df)

df.to_csv('sentiment_analysis_jpm.csv')

df["sentiment_label"].value_counts().plot(kind="bar", color=["green", "gray", "red"])
plt.title("Sentiment Analysis Results")
plt.xlabel("Sentiment")
plt.ylabel("Count")
plt.show()