import subprocess
import sys

def install_requirements():
    """Install requirements for mock data generation"""
    requirements = [
        'psycopg2-binary',
        'faker',
        'numpy',
        'jira'
    ]
    
    print("Installing mock data requirements...")
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])
    
    print("Requirements installed successfully!")

if __name__ == "__main__":
    install_requirements()
