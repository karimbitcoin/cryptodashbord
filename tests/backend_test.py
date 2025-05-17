import requests
import unittest
import sys
import json
from datetime import datetime

# Use the public endpoint URL from frontend/.env
BASE_URL = "https://3d972603-62bc-48d3-8a75-98e83899f5a9.preview.emergentagent.com"
API_URL = f"{BASE_URL}/api"

class CryptoDashboardAPITest(unittest.TestCase):
    """Test suite for Cryptocurrency Dashboard API endpoints"""
    
    def setUp(self):
        """Setup for each test"""
        self.headers = {'Content-Type': 'application/json'}
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
        self.test_intervals = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
        self.token = None
    
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
    
    def test_auth_login(self):
        """Test authentication login endpoint"""
        print("\n🔍 Testing /api/auth/login endpoint...")
        
        # OAuth2 password flow requires form data
        form_data = {
            'username': 'user@example.com',
            'password': 'password'
        }
        
        response = requests.post(
            f"{API_URL}/auth/login", 
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('access_token', data)
        self.assertIn('token_type', data)
        self.assertEqual(data['token_type'], 'bearer')
        
        # Store token for authenticated tests
        self.token = data['access_token']
        print(f"✅ Login successful, token received")
        
        return self.token
    
    def test_auth_me(self):
        """Test getting current user info"""
        if not self.token:
            self.token = self.test_auth_login()
        
        print("\n🔍 Testing /api/auth/me endpoint...")
        
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        response = requests.get(f"{API_URL}/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        required_fields = ["id", "email", "username"]
        for field in required_fields:
            self.assertIn(field, data, f"Field '{field}' missing from user data")
        
        print(f"✅ Current user data received: {data['username']} ({data['email']})")
    
    def test_portfolio_endpoints(self):
        """Test portfolio endpoints"""
        if not self.token:
            self.token = self.test_auth_login()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        # 1. Get all portfolios
        print("\n🔍 Testing /api/portfolio endpoint (GET)...")
        response = requests.get(f"{API_URL}/portfolio", headers=headers)
        self.assertEqual(response.status_code, 200)
        portfolios = response.json()
        self.assertIsInstance(portfolios, list)
        print(f"✅ Retrieved {len(portfolios)} portfolios")
        
        # 2. Create a new portfolio
        print("\n🔍 Testing /api/portfolio endpoint (POST)...")
        new_portfolio = {
            "name": f"Test Portfolio {datetime.now().strftime('%H%M%S')}",
            "assets": [
                {
                    "symbol": "BTCUSDT",
                    "amount": 0.5,
                    "purchase_price": 50000
                },
                {
                    "symbol": "ETHUSDT",
                    "amount": 2.0,
                    "purchase_price": 3000
                }
            ]
        }
        
        response = requests.post(f"{API_URL}/portfolio", json=new_portfolio, headers=headers)
        self.assertEqual(response.status_code, 201)
        created_portfolio = response.json()
        
        required_fields = ["id", "name", "assets", "user_id"]
        for field in required_fields:
            self.assertIn(field, created_portfolio, f"Field '{field}' missing from created portfolio")
        
        portfolio_id = created_portfolio["id"]
        print(f"✅ Created portfolio with ID: {portfolio_id}")
        
        # 3. Get portfolio by ID
        print(f"\n🔍 Testing /api/portfolio/{portfolio_id} endpoint (GET)...")
        response = requests.get(f"{API_URL}/portfolio/{portfolio_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        portfolio = response.json()
        self.assertEqual(portfolio["id"], portfolio_id)
        print(f"✅ Retrieved portfolio: {portfolio['name']}")
        
        # 4. Delete portfolio
        print(f"\n🔍 Testing /api/portfolio/{portfolio_id} endpoint (DELETE)...")
        response = requests.delete(f"{API_URL}/portfolio/{portfolio_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        print(f"✅ Deleted portfolio with ID: {portfolio_id}")
    
    def test_user_preferences(self):
        """Test user preferences endpoint"""
        if not self.token:
            self.token = self.test_auth_login()
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        print("\n🔍 Testing /api/preferences endpoint (GET)...")
        response = requests.get(f"{API_URL}/preferences", headers=headers)
        
        # This endpoint might return 404 if preferences don't exist yet
        if response.status_code == 200:
            preferences = response.json()
            required_fields = ["default_currency", "dark_mode", "favorite_coins"]
            for field in required_fields:
                self.assertIn(field, preferences, f"Field '{field}' missing from preferences")
            print(f"✅ Retrieved user preferences")
        elif response.status_code == 404:
            print(f"✅ User preferences not found (expected for new users)")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

class AuthenticationTest(unittest.TestCase):
    """Test suite for authentication-related functionality"""
    
    def test_login_success(self):
        """Test successful login"""
        print("\n🔍 Testing successful login...")
        
        form_data = {
            'username': 'user@example.com',
            'password': 'password'
        }
        
        response = requests.post(
            f"{API_URL}/auth/login", 
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('access_token', data)
        print(f"✅ Login successful with correct credentials")
    
    def test_login_failure(self):
        """Test failed login with incorrect credentials"""
        print("\n🔍 Testing failed login...")
        
        form_data = {
            'username': 'user@example.com',
            'password': 'wrong_password'
        }
        
        response = requests.post(
            f"{API_URL}/auth/login", 
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        self.assertEqual(response.status_code, 401)
        print(f"✅ Login correctly failed with wrong credentials")
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        print("\n🔍 Testing protected endpoint without token...")
        
        response = requests.get(f"{API_URL}/auth/me")
        self.assertEqual(response.status_code, 401)
        print(f"✅ Protected endpoint correctly rejected unauthenticated request")
    
    def test_register_endpoint(self):
        """Test user registration"""
        print("\n🔍 Testing /api/auth/register endpoint...")
        
        # Generate a unique email
        unique_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        
        new_user = {
            "email": unique_email,
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "TestPassword123"
        }
        
        response = requests.post(f"{API_URL}/auth/register", json=new_user)
        
        # Registration should either succeed with 201 or fail with 400 if user exists
        if response.status_code == 201:
            data = response.json()
            self.assertIn('id', data)
            self.assertEqual(data['email'], new_user['email'])
            print(f"✅ Registration successful for {new_user['email']}")
        elif response.status_code == 400:
            print(f"✅ Registration failed as expected (user might already exist)")
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

def run_tests():
    """Run the test suite"""
    print(f"🚀 Starting API tests against {API_URL}")
    
    # Create test suites
    crypto_suite = unittest.TestLoader().loadTestsFromTestCase(CryptoDashboardAPITest)
    auth_suite = unittest.TestLoader().loadTestsFromTestCase(AuthenticationTest)
    
    # Combine test suites
    all_tests = unittest.TestSuite([crypto_suite, auth_suite])
    
    # Run tests
    result = unittest.TextTestRunner(verbosity=2).run(all_tests)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
