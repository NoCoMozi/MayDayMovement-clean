import os
import sys

def check_config():
    required_vars = ['TELEGRAM_TOKEN', 'GITHUB_TOKEN']
    missing_vars = []
    
    print("Checking bot configuration...")
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ {var} is not set")
        else:
            print(f"✓ {var} is set")
    
    if missing_vars:
        print("\n⚠️ Missing required environment variables!")
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return False
    
    print("\n✅ All required environment variables are set!")
    return True

if __name__ == "__main__":
    check_config()
