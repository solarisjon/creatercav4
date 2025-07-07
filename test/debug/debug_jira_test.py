#!/usr/bin/env python3
import sys
import urllib3
import platform
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, './src')

def main():
    from jira import JIRA
    from config import config

        # Set the path for the PEM file used for SSL certificate verification
    platformtype = platform.system()

    if platformtype == "Linux":
        os.environ['REQUESTS_CA_BUNDLE'] = "/etc/ssl/certs/ca-certificates.crt"
        os.environ['SSL_CERT_FILE']      = "/etc/ssl/certs/ca-certificates.crt"
    elif platformtype == "Darwin":
        pem_path = "/usr/local/etc/openssl@3/certs/../cert.pem"
        os.environ['REQUESTS_CA_BUNDLE'] = pem_path
        os.environ['SSL_CERT_FILE'] = pem_path
    else:
        print("Unsupported platform. Please set the SSL_CERT_FILE environment variable manually.")


    jira_config = config.jira_config
    print('Testing Jira connection with various options...')
    print(f'URL: {jira_config["url"]}')
    print(f'Username: {jira_config["username"]}')

    # Test with SSL verification disabled first
    print('\n=== Testing with verify=False (SSL disabled) ===')
    
    # Test 1: Bearer token authentication (like escalation_metrics)
    print('\n--- Testing Bearer Token Authentication (escalation_metrics style) ---')
    try:
        headers = {
            'Authorization': f'Bearer {jira_config["api_token"]}'
        }
        jira = JIRA(
            server=jira_config['url'],
            options={'headers': headers, 'verify': False, 'timeout': 10}
        )
        print('✅ Bearer token auth: Connection established')
        myself = jira.myself()
        print(f'✅ Logged in as: {myself["displayName"]}')
        return True
    except Exception as e:
        print(f'❌ Bearer token auth failed: {str(e)}')
    
    # Test 2: Password authentication with SSL disabled
    print('\n--- Testing Password Authentication (no SSL verification) ---')
    try:
        jira = JIRA(
            server=jira_config['url'],
            basic_auth=(jira_config['username'], jira_config['password']),
            options={'verify': False, 'timeout': 10}
        )
        print('✅ Password auth: Connection established')
        myself = jira.myself()
        print(f'✅ Logged in as: {myself["displayName"]}')
        return True
    except Exception as e:
        print(f'❌ Password auth failed: {str(e)}')
        
    # Test 3: API Token authentication with SSL disabled
    print('\n--- Testing API Token Authentication (no SSL verification) ---')
    try:
        jira = JIRA(
            server=jira_config['url'],
            basic_auth=(jira_config['username'], jira_config['api_token']),
            options={'verify': False, 'timeout': 10}
        )
        print('✅ API token auth: Connection established')
        myself = jira.myself()
        print(f'✅ Logged in as: {myself["displayName"]}')
        return True
    except Exception as e:
        print(f'❌ API token auth failed: {str(e)}')
        
    print('\n❌ All authentication methods failed')
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'❌ Script failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
