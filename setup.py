import subprocess
import pkg_resources
import sys

def install_packages(packages):
    
    for package in packages:
        try:
            # Checks if the package is already installed
            pkg_resources.require(package)
            print(f"{package} is already installed.")
        except pkg_resources.DistributionNotFound:
            # If the package is not installed, try to install it
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except pkg_resources.VersionConflict:
            # If the package is installed but the version conflicts, upgrade it
            print(f"Upgrading {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

# List of required packages and possibly their versions
required_packages = [
    'openmeteo_requests',
    'scikit-learn',
    'sqlalchemy',
    'pandas',
    'numpy',
    'tk',
    'Pillow',
    'datetime',
    'python-dateutil',
    'requests',
    'requests_cache',
    'retry_requests',
    'matplotlib',
    'subprocess.run',
    'pymysql',
    'mysql-connector-python'
]

install_packages(required_packages)
