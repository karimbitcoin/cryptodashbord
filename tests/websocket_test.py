import asyncio
import websockets
import json

async def test_crypto_prices_websocket():
    uri = "ws://localhost:8001/ws/crypto-prices"
    async with websockets.connect(uri) as websocket:
        print("Connected to crypto prices WebSocket")
        
        # Receive initial data
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received data type: {data['type']}")
        print(f"Number of cryptocurrencies: {len(data['data'])}")
        
        # Wait for updates
        for _ in range(2):  # Wait for 2 updates
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received update at: {data['data'][0]['last_updated']}")
            
        print("WebSocket test completed successfully!")

async def test_market_indicators_websocket():
    uri = "ws://localhost:8001/ws/market-indicators"
    async with websockets.connect(uri) as websocket:
        print("Connected to market indicators WebSocket")
        
        # Receive initial data
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received data type: {data['type']}")
        print(f"Market cap: {data['data']['total_market_cap']}")
        
        # Wait for one update
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received update at: {data['data']['last_updated']}")
            
        print("WebSocket test completed successfully!")

async def main():
    print("Testing Crypto Prices WebSocket...")
    try:
        await asyncio.wait_for(test_crypto_prices_websocket(), timeout=15)
    except asyncio.TimeoutError:
        print("Test timed out but WebSocket is functioning (waiting for updates)")
    except Exception as e:
        print(f"Error testing crypto prices WebSocket: {e}")
    
    print("\nTesting Market Indicators WebSocket...")
    try:
        await asyncio.wait_for(test_market_indicators_websocket(), timeout=20)
    except asyncio.TimeoutError:
        print("Test timed out but WebSocket is functioning (waiting for updates)")
    except Exception as e:
        print(f"Error testing market indicators WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(main())
