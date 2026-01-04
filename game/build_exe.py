import subprocess
import sys
import os

# Path to the icon file (use .ico)
ICON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'assets', 'icons', 'icon.ico'))

# Ensure we are in the project root (game directory)
os.chdir(os.path.abspath(os.path.dirname(__file__)))

# PyInstaller command
cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--noconsole',  # Hide terminal window
    f'--icon={ICON_PATH}',
    '--name=XO_Game',
    '--version-file=version.txt',
    '--add-data=assets;assets',  # Include assets folder
    'main.py'
]

print('Building XO_Game.exe (v5.0.0)...')
print('Running:', ' '.join(cmd))
try:
    subprocess.check_call(cmd)
    print("\nSuccess! The executable is located in the 'dist' folder.")
    print("You can now share 'dist/XO_Game.exe' with others.")
except subprocess.CalledProcessError as e:
    print(f"\nError during build: {e}")
    sys.exit(1)
