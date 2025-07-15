
# Triggering a new Vercel deployment on July 15
# tools.py
import os, json, yfinance as yf, spacy, finnhub, alpaca_trade_api as tradeapi
from serpapi import GoogleSearch
from newsapi import NewsApiClient
from transformers import pipeline

# Initialize heavy models once to be efficient
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline('sentiment-analysis', model="nlptown/bert-base-multilingual-uncased-sentiment")
nlp_ner = spacy.load("en_core_web_sm")

def google_search(query: str) -> str:
    try:
        results = GoogleSearch({"q": query, "api_key": os.environ['SERPAPI_API_KEY']}).get_dict()
        return json.dumps(results.get("organic_results", "No results found."))
    except Exception as e: return f"Error: {e}"

def get_latest_news(query: str) -> str:
    try:
        newsapi = NewsApiClient(api_key=os.environ['NEWSAPI_API_KEY'])
        headlines = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=5)
        return json.dumps(headlines['articles'])
    except Exception as e: return f"Error: {e}"

def get_stock_financials(ticker: str) -> str:
    try: return json.dumps(yf.Ticker(ticker).info)
    except Exception as e: return f"Error: {e}"

def analyze_sentiment(text: str) -> str:
    try: return json.dumps(sentiment_analyzer(text[:512]))
    except Exception as e: return f"Error: {e}"

def summarize_text(long_text: str) -> str:
    try: return summarizer(long_text, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
    except Exception as e: return f"Error: {e}"

def extract_entities(text: str) -> str:
    try:
        doc = nlp_ner(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return json.dumps(entities) if entities else "No entities found."
    except Exception as e: return f"Error: {e}"

def get_insider_trades(ticker: str) -> str:
    try:
        finnhub_client = finnhub.Client(api_key=os.environ['FINNHUB_API_KEY'])
        return json.dumps(finnhub_client.stock_insider_transactions(ticker)[:10])
    except Exception as e: return f"Error: {e}"

def execute_trade(symbol: str, qty: str, side: str) -> str:
    api = tradeapi.REST(os.environ['APCA_API_KEY_ID'], os.environ['APCA_API_SECRET_KEY'], base_url="https://paper-api.alpaca.markets", api_version='v2')
    if side not in ['buy', 'sell']: return "Error: Side must be 'buy' or 'sell'."
    try:
        order = api.submit_order(symbol=symbol, qty=qty, side=side, type='market', time_in_force='gtc')
        return f"SUCCESS: Paper trading order for {side} {qty} shares of {symbol} submitted. Order ID: {order.id}"
    except Exception as e: return f"ERROR: Failed to execute trade. Alpaca response: {e}"

    
