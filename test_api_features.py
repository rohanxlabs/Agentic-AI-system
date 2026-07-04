"""Test script to verify all API features work correctly: session persistence, streaming, auth, rate limiting."""
import asyncio
import aiohttp
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000"
TEST_API_KEY = "test-secret-key-123"


async def test_streaming_endpoint():
    """Test the /run/stream endpoint with SSE events."""
    print("\n=== Testing Streaming Endpoint ===")
    session_id = str(uuid.uuid4())
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/run/stream",
            json={
                "goal": "Calculate 25 * 4 + 10",
                "session_id": session_id,
                "enable_tools": True
            }
        ) as response:
            print(f"Response status: {response.status}")
            print("Receiving SSE events:")
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        print(f"  {line_str}")


async def test_session_persistence():
    """Test that STM persists across multiple requests with the same session_id."""
    print("\n=== Testing Session Persistence ===")
    session_id = str(uuid.uuid4())
    print(f"Using persistent session ID: {session_id}")
    
    # First request
    print("\nFirst request - creating session:")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/run",
            json={
                "goal": "What is 10 + 5?",
                "session_id": session_id,
                "enable_tools": True
            }
        ) as response:
            print(f"First request status: {response.status}")
            data = await response.json()
            print(f"First request response: {data}")
    
    # Second request with same session_id
    print("\nSecond request - reusing session:")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/run",
            json={
                "goal": "Multiply that result by 2",
                "session_id": session_id,
                "enable_tools": True
            }
        ) as response:
            print(f"Second request status: {response.status}")
            data = await response.json()
            print(f"Second request response: {data}")
    
    print("\nCheck server logs to verify STM content was preserved between requests!")


async def test_auth_middleware():
    """Test that API key auth works correctly when enabled."""
    print("\n=== Testing API Key Authentication ===")
    
    # Test without API key (should work in default dev mode where auth is disabled)
    print("\nTesting without X-API-Key header (should succeed in dev mode):")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/run",
            json={
                "goal": "Test auth",
                "enable_tools": False
            }
        ) as response:
            print(f"Status: {response.status}")
            print(f"Response: {await response.json()}")
    
    # If API_AUTH_KEY were set in .env, this would fail without the header
    print("\nIf API_AUTH_KEY were set in .env, requests without X-API-Key would return 401 Unauthorized")


async def test_rate_limiting():
    """Test rate limiting by sending more than 10 requests quickly."""
    print("\n=== Testing Rate Limiting ===")
    print(f"Sending 11 rapid requests to trigger rate limit (configured for 10/minute):")
    
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(11):
            task = session.post(
                f"{BASE_URL}/run",
                json={
                    "goal": f"Rate limit test {i}",
                    "enable_tools": False
                }
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count rate limited responses
        rate_limited = 0
        for i, resp in enumerate(responses):
            if isinstance(resp, aiohttp.ClientResponse):
                if resp.status == 429:
                    rate_limited += 1
                    print(f"  Request {i+1}: Rate limited (429) - Correct!")
                else:
                    print(f"  Request {i+1}: Status {resp.status}")
            else:
                print(f"  Request {i+1}: Error - {resp}")
        
        print(f"\nTotal rate limited requests: {rate_limited}")
        if rate_limited > 0:
            print("✅ Rate limiting is working correctly!")


if __name__ == "__main__":
    print("Agentic AI System API Feature Tests")
    print("=" * 50)
    print("First start the server with: uvicorn api:app --reload")
    print("\nThen run this test script to verify all features.")
    
    # To run the tests, uncomment the following:
    # asyncio.run(asyncio.gather(
    #     test_streaming_endpoint(),
    #     test_session_persistence(),
    #     test_auth_middleware(),
    #     test_rate_limiting()
    # ))