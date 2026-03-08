import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import urllib.request
import pandas as pd
from PIL import Image

def get_flag(code):
    url = f"https://flagcdn.com/w40/{code}.png"
    urllib.request.urlretrieve(url, f"{code}.png")
    return plt.imread(f"{code}.png")

fig, ax = plt.subplots()
ax.barh(["United States", "France"], [10, 20])

for i, code in enumerate(["us", "fr"]):
    img = get_flag(code)
    imagebox = OffsetImage(img, zoom=0.5)
    # x coordinate is 0 (or slightly negative), y coordinate is i
    ab = AnnotationBbox(imagebox, (0, i), frameon=False, box_alignment=(1.1, 0.5))
    ax.add_artist(ab)

plt.savefig("test_flags.png")
