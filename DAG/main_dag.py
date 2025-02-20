from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.smtp.operators.email import EmailOperator
from datetime import datetime, timedelta

# Define default DAG arguments
default_args = {
    "owner": "Kaushal Choudhary",
    "depends_on_past": False,
    "start_date": datetime(2024, 2, 20),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define DAG
with DAG(
    "sentiment_scraper_dag",
    default_args=default_args,
    schedule_interval="0 8 * * *",  # Runs daily at 8 AM
    catchup=False,
) as dag:

    # Task 1: Run Web Scraping Script
    scrape_task = BashOperator(
        task_id="scrape_data",
        bash_command="python3 scraper/bs4_scraper.py",
    )

    # Task 2: Run Sentiment Analysis Script
    sentiment_task = BashOperator(
        task_id="analyze_sentiment",
        bash_command="python3 sentimalysis/finbert_sentiment.py",
    )

    # Task 3: Run Database Embedding Script
    embed_task = BashOperator(
        task_id="embed_data",
        bash_command="python3 vector_search/main.py",
    )

    # Task 4: Send Email Notification
    email_task = EmailOperator(
        task_id="send_email_notification",
        to="kaushalc64@gmail.com",
        subject="New Sentiment Data Available",
        html_content="<p>The new data has been scraped, analyzed, and embedded in the database. Your Airflow Master.</p>",
        smtp_conn_id="smtp_default",
    )

    # Define Task Dependencies
    scrape_task >> sentiment_task >> embed_task >> email_task
