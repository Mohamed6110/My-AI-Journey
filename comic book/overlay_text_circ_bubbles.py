from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

def wrap_text(text, width=2):
    """Split text"""
    words = text.split()
    lines = [' '.join(words[i:i+width]) for i in range(0, len(words), width)]
    return '\n'.join(lines)

def draw_bubble(draw, text, position, font):
    """Draw Circle"""
    
    wrapped_text = wrap_text(text, width=3)

    
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=4)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    
    diameter = max(text_w, text_h) + 25

    center_x = position[0] + text_w / 2
    center_y = position[1] + text_h / 2
    radius = diameter / 2

    rect = [
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius
    ]

    
    draw.ellipse(rect, fill="white", outline="black", width=3)

    
    tail_tip_y = rect[3] + 15
    tail = [
        (center_x - 10, rect[3] - 2),
        (center_x, tail_tip_y),
        (center_x + 10, rect[3] - 2)
    ]
    draw.polygon(tail, fill="white", outline="black")

    
    text_pos = (center_x - text_w / 2, center_y - text_h / 2)
    draw.multiline_text(text_pos, wrapped_text, font=font, fill="black", align="center", spacing=4)

def process_comic_panels(model_name, panels_data):
    input_dir = f"/content/drive/MyDrive/cyper/{model_name.lower().replace('-', '_')}"
    output_dir = f"/content/drive/MyDrive/cyper/{model_name.lower().replace('-', '_')}_final"
    os.makedirs(output_dir, exist_ok=True)

    try:
        
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 22)
    except:
        font = ImageFont.load_default()

    processed_images = []

    for i, panel in enumerate(panels_data):
        img_path = os.path.join(input_dir, f"panel_{i+1}.png")
        if not os.path.exists(img_path): continue

        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        top_y = 150
        lower_y = 380 

        for idx, (char, msg) in enumerate(panel['dialogue'].items()):
            bubble_text = f"{char}: {msg}"

            
            if idx < 4:
                current_x = 60 + (idx * 550)
                current_y = top_y
            elif idx == 4:
                current_x = 850
                current_y = top_y
            else:
                current_x = 100
                current_y = lower_y

            draw_bubble(draw, bubble_text, (current_x, current_y), font)

        temp_path = os.path.join(output_dir, f"res_panel_{i+1}.png")
        img.save(temp_path)
        processed_images.append(temp_path)

    if processed_images:
        final_page_path = f"/content/drive/MyDrive/cyper/{model_name}_Final_Grid.png"


