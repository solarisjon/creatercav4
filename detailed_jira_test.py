#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, './src')

def main():
    from jira import JIRA
    from config import config

    jira_config = config.jira_config
    print('Testing direct connection...')
    print(f'URL: {jira_config["url"]}')
    print(f'Username: {jira_config["username"]}')

    # Test 1: Password authentication
    print('\n=== Testing Password Authentication ===')
    try:
        jira = JIRA(
            server=jira_config['url'],
            basic_auth=(jira_config['username'], jira_config['password'])
        )
        print('✅ Password auth: Connection established')
        myself = jira.myself()
        print(f'✅ Logged in as: {myself["displayName"]}')
        print(f'✅ User key: {myself["key"]}')
        return True
    except Exception as e:
        print(f'❌ Password auth failed: {str(e)}')
        
    # Test 2: API Token authentication
    print('\n=== Testing API Token Authentication ===')
    try:
        jira = JIRA(
            server=jira_config['url'],
            basic_auth=(jira_config['username'], jira_config['api_token'])
        )
        print('✅ API token auth: Connection established')
        myself = jira.myself()
        print(f'✅ Logged in as: {myself["displayName"]}')
        print(f'✅ User key: {myself["key"]}')
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
