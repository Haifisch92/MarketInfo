

from PIL import Image
import shutil
import os
import time

# Caratteri in stile jp2a
ASCII_CHARS = "   ...',;:clodxkO0KXNWM"

def resize_image(image, new_width):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(aspect_ratio * new_width * 0.55)
    return image.resize((new_width, int(new_height)))

def image_to_ascii_color(image_path, terminal_width):
    image = Image.open(image_path).convert("RGB")
    image = resize_image(image, terminal_width)

    ascii_img = ""
    pixels = list(image.getdata())
    width = image.width

    for i in range(0, len(pixels), width):
        line = ""
        for j in range(width):
            r, g, b = pixels[i + j]
            brightness = int((r + g + b) / 3)
            char = ASCII_CHARS[brightness * len(ASCII_CHARS) // 256]
            # ANSI escape for 24-bit foreground color
            line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        ascii_img += line + "\n"
    
    return ascii_img

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def display_ascii_art_color(image_path):
    terminal_width = shutil.get_terminal_size().columns
    ascii_art = image_to_ascii_color(image_path, terminal_width)
    clear_terminal()
    print(ascii_art)

# LOOP dinamico (aggiorna ogni 0.5s)
image_path = "image/capital2.jpeg"

try:
    while True:
        display_ascii_art_color(image_path)
        time.sleep(0.5)
except KeyboardInterrupt:
    clear_terminal()
    print("Uscita.")