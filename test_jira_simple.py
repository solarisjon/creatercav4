#!/usr/bin/env python3
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_jira_simple():
    try:
        from jira import JIRA
        from config import config
        
        print("Loading Jira configuration...")
        jira_config = config.jira_config
        print(f"URL: {jira_config['url']}")
        print(f"Username: {jira_config['username']}")
        print(f"Has password: {bool(jira_config.get('password'))}")
        print(f"Has API token: {bool(jira_config.get('api_token'))}")
        
        # Test Method 1: username + password
        if jira_config.get('password'):
            print("\nTesting username/password authentication...")
            try:
                jira = JIRA(
                    server=jira_config['url'],
                    basic_auth=(jira_config['username'], jira_config['password'])
                )
                # Test connection with a simple query
                myself = jira.myself()
                print(f"✅ Username/password auth successful! Logged in as: {myself['displayName']}")
                return True
            except Exception as e:
                print(f"❌ Username/password auth failed: {e}")
        
        # Test Method 2: username + api_token
        print("\nTesting username/API token authentication...")
        try:
            jira = JIRA(
                server=jira_config['url'],
                basic_auth=(jira_config['username'], jira_config['api_token'])
            )
            # Test connection with a simple query
            myself = jira.myself()
            print(f"✅ Username/API token auth successful! Logged in as: {myself['displayName']}")
            return True
        except Exception as e:
            print(f"❌ Username/API token auth failed: {e}")
            
        return False
            
    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False
        
if __name__ == "__main__":
    success = test_jira_simple()
    sys.exit(0 if success else 1)
