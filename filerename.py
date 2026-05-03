import pytesseract
from pathlib import Path
from PIL import Image
import os

index = 1
folder_path = Path('/Users/mashai/Documents/dev/mortenson/Screenshots')
images = [f.name for f in folder_path.iterdir() if f.is_file()]
textData = []

for filename in os.listdir(folder_path):
    old_path = os.path.join(folder_path, filename)
    new_path = os.path.join(folder_path, str(index)+".png")
    os.rename(old_path, new_path)
    index += 1