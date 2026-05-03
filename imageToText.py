from PIL import Image
import pytesseract
from pathlib import Path
import pandas as pd
import re

folder_path = Path("/Users/mashai/Documents/dev/mortenson/Screenshots")
output_file = Path("list_output.txt")

# Your screenshots appear to be 4 columns.
# Most are either 1 or 2 rows. Adjust if needed.
NUM_COLUMNS = 4
NUM_ROWS = 2

def extract_cards_from_image(image_path):
    img = Image.open(image_path)

    data = pytesseract.image_to_data(
        img,
        output_type=pytesseract.Output.DATAFRAME,
        config="--psm 6"
    )

    # Clean OCR output
    data = data.dropna(subset=["text"])
    data = data[data["text"].str.strip() != ""]
    data = data[data["conf"] > 35]

    if data.empty:
        return []

    card_width = img.width / NUM_COLUMNS
    card_height = img.height / NUM_ROWS

    data["col"] = (data["left"] // card_width).astype(int)
    data["row"] = (data["top"] // card_height).astype(int)

    # Avoid weird values outside expected range
    data = data[(data["col"] >= 0) & (data["col"] < NUM_COLUMNS)]
    data = data[(data["row"] >= 0) & (data["row"] < NUM_ROWS)]

    cards = []

    for (row, col), words in data.groupby(["row", "col"]):
        words = words.sort_values(["top", "left"])

        lines = []
        current_line = []
        last_top = None

        for _, word in words.iterrows():
            word_text = str(word["text"]).strip()

            if not word_text:
                continue

            if last_top is None or abs(word["top"] - last_top) < 18:
                current_line.append(word_text)
            else:
                lines.append(" ".join(current_line))
                current_line = [word_text]

            last_top = word["top"]

        if current_line:
            lines.append(" ".join(current_line))

        lines = [line.strip() for line in lines if line.strip()]

        location_line = None
        location_index = None

        for i, line in enumerate(lines):
            # Matches: SEATTLE, WA or Downtown Seattle, WA
            if re.search(r",\s*[A-Z]{2}$", line.strip()):
                location_line = line
                location_index = i
                break

        if location_line is None:
            continue

        project_name = " ".join(lines[location_index + 1:]).strip()

        cards.append({
            "row": row,
            "col": col,
            "location": location_line,
            "project_name": project_name,
            "source": image_path.name
        })

    return sorted(cards, key=lambda x: (x["row"], x["col"]))


all_cards = []

for path in sorted(folder_path.iterdir()):
    if path.suffix.lower() == ".png":
        all_cards.extend(extract_cards_from_image(path))


with open(output_file, "w", encoding="utf-8") as f:
    for card in all_cards:
        f.write(f"{card['location']}\n")
        f.write(f"{card['project_name']}\n")
        # f.write(f"Source: {card['source']}\n") # File source row
        f.write("\n")

print(f"Saved {len(all_cards)} project cards to {output_file}")