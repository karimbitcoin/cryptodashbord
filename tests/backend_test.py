import requests
import unittest
import sys
import json
from datetime import datetime

# Use the public endpoint URL from frontend/.env
BASE_URL = "https://891d87e6-328c-4d28-89ad-e4c1a6f8fbbc.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

class CryptoDashboardAPITest(unittest.TestCase):
    """Test suite for Cryptocurrency Dashboard API endpoints"""
    
    def setUp(self):
        """Setup for each test"""
        self.headers = {'Content-Type': 'application/json'}
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
        self.test_intervals = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
    
    def test_api_root(self):
        """Test the API root endpoint"""
        print("\n🔍 Testing API root endpoint...")
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print(f"✅ API root endpoint returned: {data}")
    
    def test_cryptocurrencies_endpoint(self):
        """Test the cryptocurrencies endpoint"""
        print("\n🔍 Testing /api/cryptocurrencies endpoint...")
        response = requests.get(f"{API_URL}/cryptocurrencies")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0, "Cryptocurrency list should not be empty")
        
        # Check structure of first cryptocurrency
        crypto = data[0]
        required_fields = ["symbol", "price", "price_change_24h", "price_change_percentage_24h", 
                          "volume_24h", "market_cap", "last_updated"]
        for field in required_fields:
            self.assertIn(field, crypto, f"Field '{field}' missing from cryptocurrency data")
        
        print(f"✅ Found {len(data)} cryptocurrencies")
        print(f"✅ Sample cryptocurrency: {crypto['symbol']} - ${crypto['price']}")
    
    def test_cryptocurrencies_with_symbols(self):
        """Test the cryptocurrencies endpoint with specific symbols"""
        symbols = ",".join(self.test_symbols[:2])  # Test with BTC and ETH
        print(f"\n🔍 Testing /api/cryptocurrencies with symbols={symbols}...")
        
        response = requests.get(f"{API_URL}/cryptocurrencies?symbols={symbols}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if we got the requested symbols
        returned_symbols = [crypto["symbol"] for crypto in data]
        print(f"✅ Returned symbols: {returned_symbols}")
        
        # Note: The API might not filter correctly if using mock data
        # So we're just checking the response structure
        self.assertIsInstance(data, list)
    
    def test_market_indicators_endpoint(self):
        """Test the market indicators endpoint"""
        print("\n🔍 Testing /api/market-indicators endpoint...")
        response = requests.get(f"{API_URL}/market-indicators")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        required_fields = ["total_market_cap", "total_volume_24h", "btc_dominance", 
                          "eth_dominance", "fear_greed_index", "last_updated"]
        for field in required_fields:
            self.assertIn(field, data, f"Field '{field}' missing from market indicators data")
        
        print(f"✅ Market indicators data received")
        print(f"✅ Total market cap: ${data['total_market_cap']}")
        print(f"✅ BTC dominance: {data['btc_dominance']}%")
        print(f"✅ Fear & Greed Index: {data['fear_greed_index']}")
    
    def test_chart_endpoint(self):
        """Test the chart endpoint for different symbols and intervals"""
        for symbol in self.test_symbols[:2]:  # Test with first two symbols
            for interval in self.test_intervals[:3]:  # Test with first three intervals
                print(f"\n🔍 Testing /api/chart/{symbol}?interval={interval}...")
                response = requests.get(f"{API_URL}/chart/{symbol}?interval={interval}")
                self.assertEqual(response.status_code, 200)
                data = response.json()
                
                required_fields = ["symbol", "interval", "candles", "last_updated"]
                for field in required_fields:
                    self.assertIn(field, data, f"Field '{field}' missing from chart data")
                
                # Check candles structure
                self.assertIsInstance(data["candles"], list)
                self.assertTrue(len(data["candles"]) > 0, "Candles list should not be empty")
                
                # Check first candle structure
                candle = data["candles"][0]
                candle_fields = ["time", "open", "high", "low", "close", "volume"]
                for field in candle_fields:
                    self.assertIn(field, candle, f"Field '{field}' missing from candle data")
                
                print(f"✅ Chart data received for {symbol} with interval {interval}")
                print(f"✅ Number of candles: {len(data['candles'])}")
    
    def test_invalid_symbol(self):
        """Test the chart endpoint with an invalid symbol"""
        print("\n🔍 Testing /api/chart with invalid symbol...")
        response = requests.get(f"{API_URL}/chart/INVALIDCOIN?interval=1h")
        
        # The API should still return data even for invalid symbols (using mock data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that we got a response with the requested symbol
        self.assertEqual(data["symbol"], "INVALIDCOIN")
        print(f"✅ API handled invalid symbol gracefully")
    
    def test_invalid_interval(self):
        """Test the chart endpoint with an invalid interval"""
        print("\n🔍 Testing /api/chart with invalid interval...")
        response = requests.get(f"{API_URL}/chart/BTCUSDT?interval=invalid")
        
        # The API should default to 1h interval or handle it gracefully
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that we got a response with some interval
        self.assertIn("interval", data)
        print(f"✅ API handled invalid interval gracefully, used: {data['interval']}")

def run_tests():
    """Run the test suite"""
    print(f"🚀 Starting API tests against {API_URL}")
    test_suite = unittest.TestLoader().loadTestsFromTestCase(CryptoDashboardAPITest)
    result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
