import pytest
from unittest.mock import patch, MagicMock
from tools import stock_tool, search_tool, sentiment_tool


class TestStockTool:
    """Test cases for stock_tool function."""
    
    @patch('tools.yf.Ticker')
    def test_stock_tool_success(self, mock_ticker):
        """Test stock_tool returns correct dictionary structure."""
        # Mock the yfinance Ticker object
        mock_stock = MagicMock()
        mock_info = {
            'longName': 'Apple Inc.',
            'regularMarketPrice': 150.25,
            'marketCap': 2500000000000,
            'regularMarketDayHigh': 152.0,
            'regularMarketDayLow': 149.0,
            'regularMarketPreviousClose': 151.0
        }
        mock_stock.info = mock_info
        mock_ticker.return_value = mock_stock
        
        # Call the function
        result = stock_tool('AAPL')
        
        # Assertions
        assert isinstance(result, dict)
        assert 'symbol' in result
        assert 'name' in result
        assert 'price' in result
        assert 'market_cap' in result
        assert 'day_high' in result
        assert 'day_low' in result
        assert 'previous_close' in result
        
        # Verify specific values
        assert result['symbol'] == 'AAPL'
        assert result['name'] == 'Apple Inc.'
        assert result['price'] == 150.25
        
    @patch('tools.yf.Ticker')
    def test_stock_tool_invalid_symbol(self, mock_ticker):
        """Test stock_tool handles invalid stock symbol."""
        # Mock ticker to raise an exception
        mock_ticker.side_effect = Exception("Invalid symbol")
        
        # Call the function
        result = stock_tool('INVALID')
        
        # Should return error information
        assert isinstance(result, dict)
        assert 'error' in result or result == {}


class TestSearchTool:
    """Test cases for search_tool function."""
    
    @patch('tools.DDGS')
    def test_search_tool_success(self, mock_ddgs):
        """Test search_tool returns string result."""
        # Mock DuckDuckGo search results
        mock_search_results = [
            {'title': 'Apple Stock News', 'body': 'Apple stock rises today'},
            {'title': 'Market Analysis', 'body': 'Tech stocks performing well'}
        ]
        
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = mock_search_results
        mock_ddgs.return_value = mock_ddgs_instance
        
        # Call the function
        result = search_tool('Apple stock news')
        
        # Assertions
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'Apple' in result or 'stock' in result
        
    @patch('tools.DDGS')
    def test_search_tool_no_results(self, mock_ddgs):
        """Test search_tool handles no search results."""
        # Mock empty search results
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        mock_ddgs.return_value = mock_ddgs_instance
        
        # Call the function
        result = search_tool('nonexistent query')
        
        # Should return string (possibly empty or error message)
        assert isinstance(result, str)
        
    @patch('tools.DDGS')
    def test_search_tool_exception(self, mock_ddgs):
        """Test search_tool handles search exceptions."""
        # Mock search to raise an exception
        mock_ddgs.side_effect = Exception("Search failed")
        
        # Call the function
        result = search_tool('test query')
        
        # Should return string (error message)
        assert isinstance(result, str)


class TestSentimentTool:
    """Test cases for sentiment_tool function."""
    
    @patch('tools.DDGS')
    @patch('tools.SentimentIntensityAnalyzer')
    def test_sentiment_tool_success(self, mock_analyzer, mock_ddgs):
        """Test sentiment_tool returns string result."""
        # Mock search results
        mock_search_results = [
            {'title': 'Apple Positive News', 'body': 'Apple shows great performance'},
            {'title': 'Apple Analysis', 'body': 'Investors are optimistic about Apple'}
        ]
        
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = mock_search_results
        mock_ddgs.return_value = mock_ddgs_instance
        
        # Mock sentiment analyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer_instance.polarity_scores.return_value = {
            'compound': 0.5,
            'pos': 0.7,
            'neu': 0.2,
            'neg': 0.1
        }
        mock_analyzer.return_value = mock_analyzer_instance
        
        # Call the function
        result = sentiment_tool('Apple')
        
        # Assertions
        assert isinstance(result, str)
        assert len(result) > 0
        
    @patch('tools.DDGS')
    def test_sentiment_tool_no_news(self, mock_ddgs):
        """Test sentiment_tool handles no news results."""
        # Mock empty search results
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = []
        mock_ddgs.return_value = mock_ddgs_instance
        
        # Call the function
        result = sentiment_tool('UnknownCompany')
        
        # Should return string
        assert isinstance(result, str)
        
    @patch('tools.DDGS')
    def test_sentiment_tool_exception(self, mock_ddgs):
        """Test sentiment_tool handles exceptions."""
        # Mock search to raise an exception
        mock_ddgs.side_effect = Exception("Search failed")
        
        # Call the function
        result = sentiment_tool('TestCompany')
        
        # Should return string (error message)
        assert isinstance(result, str)


if __name__ == '__main__':
    pytest.main([__file__])
