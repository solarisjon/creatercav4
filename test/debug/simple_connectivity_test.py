#!/usr/bin/env python3
import sys
sys.path.insert(0, './src')

# Simple connectivity test
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from config import config

def test_basic_connectivity():
    jira_config = config.jira_config
    url = jira_config['url']
    
    print(f"Testing basic connectivity to: {url}")
    
    try:
        # Test 1: Simple GET request to see if server is reachable
        response = requests.get(url, timeout=5, verify=False)
        print(f"✅ Server reachable: HTTP {response.status_code}")
        
        # Test 2: Try the REST API endpoint with Bearer token
        api_url = f"{url}/rest/api/2/myself"
        headers = {
            'Authorization': f'Bearer {jira_config["api_token"]}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10, verify=False)
        print(f"API call result: HTTP {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bearer token auth successful! User: {data.get('displayName', 'Unknown')}")
            return True
        else:
            print(f"❌ Bearer token auth failed: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - network or firewall issue")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    return False

if __name__ == "__main__":
    success = test_basic_connectivity()
    sys.exit(0 if success else 1)
