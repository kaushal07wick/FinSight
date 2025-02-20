import pandas as pd
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch.nn.functional as F

# Load FinBERT model and tokenizer
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Function to split long text and aggregate sentiment
def get_finbert_sentiment(text):
    if pd.isna(text) or text.strip() == "":
        return "Neutral"

    # Tokenize and split text into chunks
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunk_size = 512
    sentiment_scores = []

    # Process each chunk separately
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        inputs = torch.tensor([chunk_tokens])

        with torch.no_grad():
            outputs = model(inputs)

        scores = F.softmax(outputs.logits, dim=1)
        sentiment_scores.append(scores.squeeze().tolist())

    # Average sentiment scores across chunks
    avg_scores = torch.tensor(sentiment_scores).mean(dim=0)
    labels = ["Negative", "Neutral", "Positive"]
    sentiment = labels[avg_scores.argmax().item()]

    return sentiment

# Load CSV file
df = pd.read_csv(r"C:/Users/Lenovo/Documents/Experiment/scraping/data/main_jpm_transcripts.csv", index_col=0)

# Clean column names
df.columns = df.columns.str.strip()

# Apply sentiment analysis
df["Sentiment_Label"] = df["Text"].apply(get_finbert_sentiment)

# Save results to CSV
df.to_csv("finbert_sentiment_results.csv", index=True)

# Preview results
print(df.head())
