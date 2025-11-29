"""
Simple test script for the quiz solver endpoint
"""
import requests
import json
import sys
from dotenv import load_dotenv
import os

load_dotenv()

def test_endpoint(base_url="http://localhost:8000"):
    """Test the quiz solver endpoint"""
    
    email = os.getenv("EMAIL", "test@example.com")
    secret = os.getenv("SECRET", "test-secret")
    
    # Test payload
    payload = {
        "email": email,
        "secret": secret,
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
    
    print(f"Testing endpoint: {base_url}/solve")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Test 1: Valid request
        print("\n[Test 1] Valid request:")
        response = requests.post(
            f"{base_url}/solve",
            json=payload,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 2: Invalid secret
        print("\n[Test 2] Invalid secret:")
        invalid_payload = payload.copy()
        invalid_payload["secret"] = "wrong-secret"
        response = requests.post(
            f"{base_url}/solve",
            json=invalid_payload,
            timeout=10
        )
        print(f"Status: {response.status_code} (expected: 403)")
        print(f"Response: {response.text}")
        
        # Test 3: Invalid JSON
        print("\n[Test 3] Invalid JSON:")
        response = requests.post(
            f"{base_url}/solve",
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code} (expected: 400)")
        print(f"Response: {response.text}")
        
        # Test 4: Health check
        print("\n[Test 4] Health check:")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {base_url}")
        print("Make sure the server is running: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_endpoint(base_url)

