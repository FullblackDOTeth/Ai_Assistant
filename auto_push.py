import time
import subprocess
import os
from datetime import datetime

def git_push():
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        subprocess.run(['git', 'commit', '-m', f'Auto-commit: {timestamp}'], check=True)
        
        # Push to remote
        subprocess.run(['git', 'push'], check=True)
        print(f'Successfully pushed changes at {timestamp}')
    except subprocess.CalledProcessError as e:
        print(f'Error during git operations: {str(e)}')
    except Exception as e:
        print(f'Unexpected error: {str(e)}')

def main():
    # Change to repository directory
    os.chdir('E:/Head Ai')
    
    # Push interval in seconds (4 minutes = 240 seconds)
    PUSH_INTERVAL = 240
    
    print('Starting auto-push service...')
    print(f'Will push changes every {PUSH_INTERVAL/60} minutes')
    
    while True:
        git_push()
        time.sleep(PUSH_INTERVAL)

if __name__ == '__main__':
    main()
