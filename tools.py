from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool
from pydantic import BaseModel, Field
import yfinance as yf
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import re
import os
import requests
from typing import Optional
import pandas as pd

# Ensure NLTK data is downloaded
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading NLTK vader_lexicon...")
    nltk.download('vader_lexicon')


# --- Pydantic Models for Tool Inputs/Outputs ---

class StockData(BaseModel):
    """Data container for holding detailed stock information."""
    stock_name: str = Field(description="The full name of the company.")
    stock_symbol: str = Field(description="The stock ticker symbol.")
    current_price: float = Field(description="The current market price of the stock.")
    previous_close: float = Field(description="The closing price from the previous trading day.")
    day_high: float = Field(description="The highest price the stock reached during the current day.")
    day_low: float = Field(description="The lowest price the stock reached during the current day.")
    market_cap: int = Field(description="The total market capitalization of the company.")

# --- Individual Tools ---

@tool
def stock_tool(symbol: str) -> dict:
    """
    Fetches detailed stock information for a given stock symbol (e.g., 'AAPL', 'MSFT').
    Returns a dictionary containing the stock's name, symbol, current price, and more.
    """
    if not symbol or not isinstance(symbol, str) or not re.match(r'^[A-Z0-9.-]+$', symbol.upper()):
        return {"error": f"Invalid stock symbol format: '{symbol}'. Please use a valid ticker."}

    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        if not info or info.get('trailingPE') is None:
            return {"error": f"No data found for symbol: '{symbol}'. It may be an invalid ticker."}

        market_cap = info.get('marketCap')
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))

        data = StockData(
            stock_name=info.get('longName', 'N/A'),
            stock_symbol=info.get('symbol', symbol.upper()),
            current_price=float(current_price) if current_price is not None else 0.0,
            previous_close=float(info.get('previousClose', 0.0)),
            day_high=float(info.get('dayHigh', 0.0)),
            day_low=float(info.get('dayLow', 0.0)),
            market_cap=int(market_cap) if market_cap is not None else 0,
        )
        print(f"[INFO] Fetched stock data for {symbol.upper()}")
        return data.model_dump()
    except Exception as e:
        print(f"[ERROR] yfinance exception for {symbol.upper()}: {e}")
        return {"error": f"Could not retrieve stock data for '{symbol}'. An external error occurred."}


search_runner = DuckDuckGoSearchRun()
@tool
def search_tool(query: str) -> str:
    """Search the web for information on a given topic."""
    return search_runner.run(query)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=5000)
wiki_runner = WikipediaQueryRun(api_wrapper=api_wrapper)
@tool
def wiki_tool(query: str) -> str:
    """Look up information on Wikipedia."""
    return wiki_runner.run(query)


@tool
def sentiment_tool(company_name: str) -> dict:
    """
    Analyzes the sentiment of recent news headlines for a given company from multiple international regions.
    Returns average sentiment scores and an overall sentiment.
    """
    try:
        print(f"[INFO] Fetching news for sentiment analysis of {company_name} from multiple regions.")
        regions = {'us-en': 'USA', 'in-en': 'India', 'cn-zh': 'China', 'jp-ja': 'Japan'}
        all_headlines = []
        
        for region_code, region_name in regions.items():
            print(f"[INFO] Searching news in {region_name}...")
            query = f"recent news headlines for {company_name} stock"
            regional_search = DuckDuckGoSearchRun(region=region_code)
            headlines_blob = regional_search.run(query)
            headlines = [line.strip() for line in headlines_blob.split('\n') if line.strip() and len(line) > 20]
            all_headlines.extend(headlines)

        if not all_headlines:
            return {"error": "No valid headlines found from any region for sentiment analysis."}
        
        unique_headlines = list(set(all_headlines))
        print(f"[INFO] Found {len(unique_headlines)} unique headlines across all regions.")

        sia = SentimentIntensityAnalyzer()
        sentiment_scores = [sia.polarity_scores(line) for line in unique_headlines]

        if not sentiment_scores:
             return {"error": "Could not calculate sentiment scores."}

        avg_sentiment = {
            "neg": sum(s["neg"] for s in sentiment_scores) / len(sentiment_scores),
            "neu": sum(s["neu"] for s in sentiment_scores) / len(sentiment_scores),
            "pos": sum(s["pos"] for s in sentiment_scores) / len(sentiment_scores),
            "compound": sum(s["compound"] for s in sentiment_scores) / len(sentiment_scores),
        }

        compound = avg_sentiment["compound"]
        if compound >= 0.05: overall = "Positive"
        elif compound <= -0.05: overall = "Negative"
        else: overall = "Neutral"

        print(f"[INFO] Completed sentiment analysis for {company_name}")
        return {
            "company": company_name,
            "headline_count": len(unique_headlines),
            "average_sentiment": avg_sentiment,
            "overall_sentiment": overall,
        }
    except Exception as e:
        print(f"[ERROR] Sentiment analysis failed: {e}")
        return {"error": f"An error occurred during sentiment analysis: {str(e)}"}

# --- CORRECTED AND IMPROVED TOOL FOR LIVE MARKET DATA ---

@tool
def get_live_market_movers_tool(industry: Optional[str] = None) -> dict:
    """
    Fetches the top 5 real-time market movers (gainers and losers) for the current trading day.
    - If an industry is provided (e.g., 'Technology', 'Healthcare'), it will filter for that specific industry.
    - If no industry is provided, it returns the overall top 5 market movers.
    - If an exact industry match isn't found, it will perform a keyword search for relevant stocks.
    """
    try:
        print(f"[INFO] Fetching live market movers...")
        
        tickers = []
        if industry:
            print(f"[INFO] Filtering for industry: {industry}...")
            query = f"top {industry} stocks tickers"
            search_results = search_tool.run(query)
            tickers = list(set(re.findall(r'\b[A-Z]{2,5}\b', search_results)))
            if not tickers:
                return {"error": f"Could not find any stock tickers for the industry: {industry}"}
        else:
            # As a fallback for general movers, we can use a list of popular index ETFs
            tickers = ["SPY", "QQQ", "DIA", "IWM"]

        # Fetch the latest data for the tickers
        data = yf.download(tickers=tickers, period="2d")
        if data.empty:
            return {"error": "Could not download any data for the identified tickers."}

        # Calculate percentage change from previous close
        pct_change = data['Close'].pct_change().iloc[-1]
        
        # Drop any rows with missing data and sort
        pct_change = pct_change.dropna()
        
        gainers = pct_change.nlargest(5)
        losers = pct_change.nsmallest(5)

        # Format the output
        top_5_gainers = [{"ticker": ticker, "percent_change": f"{change:.2%}"} for ticker, change in gainers.items()]
        top_5_losers = [{"ticker": ticker, "percent_change": f"{change:.2%}"} for ticker, change in losers.items()]

        return {
            "industry_searched": industry if industry else "Overall Market",
            "top_gainers": top_5_gainers,
            "top_losers": top_5_losers
        }

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in get_live_market_movers_tool: {e}")
        return {"error": f"An unexpected error occurred while fetching market movers: {str(e)}"}
