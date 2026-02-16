from PIL import Image, ImageDraw, ImageFont
import os

def draw_bubble(draw, text, position, font):
    """Fixed function to draw high-resolution speech bubbles."""
    padding = 20
    # Calculate text size for bubble scaling
    bbox = draw.textbbox(position, text, font=font)

    # Bubble background (Ellipse)
    rect = [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding]
    draw.ellipse(rect, fill="white", outline="black", width=4)

    # Bubble tail (pointing to character)
    tail = [(position[0]+20, rect[3]), (position[0]+10, rect[3]+25), (position[0]+40, rect[3])]
    draw.polygon(tail, fill="white", outline="black")

    # Text
    draw.text(position, text, font=font, fill="black")

def create_comic_page(images, output_path):
    """Combines 6 panels into a high-resolution 2x3 grid."""
    # Using a much larger canvas (3300x5100) for better print-quality resolution
    page = Image.new('RGB', (2600, 3800), 'white')

    for i, img_path in enumerate(images):
        img = Image.open(img_path).resize((1200, 1200)) # Larger resize for clarity
        x = 60 + (i % 2) * 1260
        y = 60 + (i // 2) * 1260
        page.paste(img, (x, y))

    page.save(output_path, quality=95)
    print(f"✅ High-resolution page saved: {output_path}")

def process_comic_panels(model_name, panels_data):
    input_dir = f"output/{model_name.lower().replace('-', '_')}"
    output_dir = f"output/{model_name.lower().replace('-', '_')}_final"
    os.makedirs(output_dir, exist_ok=True)

    # Use a larger font size for higher resolution
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    processed_images = []

    for i, panel in enumerate(panels_data):
        img_path = os.path.join(input_dir, f"panel_{i+1}.png")
        if not os.path.exists(img_path):
            continue

        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Improved placement: stack bubbles slightly differently per panel
        y_offset = 60
        for char, msg in panel['dialogue'].items():
            bubble_text = f"{char}: {msg}"
            # THE FIX: Ensuring the order matches (draw, text, position, font)
            draw_bubble(draw, bubble_text, (60, y_offset), font)
            y_offset += 150

        temp_path = os.path.join(output_dir, f"res_panel_{i+1}.png")
        img.save(temp_path)
        processed_images.append(temp_path)

    if processed_images:
        final_page_path = f"output/{model_name}_HQ_Page.png"
        create_comic_page(processed_images, final_page_path)