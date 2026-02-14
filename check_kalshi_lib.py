import subprocess
import sys

# Try to install and use kalshi library if it exists
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kalshi"])
    print("Installed kalshi library")
except:
    print("Could not install kalshi library, trying to import anyway")

try:
    import kalshi
    print("Successfully imported kalshi library")
    print(f"Version: {kalshi.__version__ if hasattr(kalshi, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"Could not import kalshi: {e}")
    
# Try other potential libraries
libraries = ["kalshi-python", "kalshi-api", "kalshi-sdk"]
for lib in libraries:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        print(f"Installed {lib}")
        break
    except:
        print(f"Could not install {lib}")