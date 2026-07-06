import os
import math
from PIL import Image, ImageDraw, ImageFont

# Hex Colors from specifications
NAVY_HEX = "#092540"
TEAL_HEX = "#00D2FF"   # Bright cyan/teal
BLUE_HEX = "#2563EB"   # Classic brand blue
WHITE_HEX = "#FFFFFF"

# RGB Colors
NAVY_RGB = (9, 37, 64)
TEAL_RGB = (0, 210, 255)
BLUE_RGB = (37, 99, 235)
WHITE_RGB = (255, 255, 255)

FONT_BOLD_PATH = "C:\\Windows\\Fonts\\arialbd.ttf"
FONT_REG_PATH = "C:\\Windows\\Fonts\\arial.ttf"

def draw_tagline(draw, text, cx, y, font, fill_color, letter_spacing=5):
    # Calculate total width of tagline with letter spacing
    widths = [draw.textlength(c, font=font) for c in text]
    total_width = sum(widths) + letter_spacing * (len(text) - 1)
    
    # Draw character-by-character
    curr_x = cx - total_width / 2
    for c in text:
        draw.text((curr_x, y), c, fill=fill_color, font=font)
        curr_x += draw.textlength(c, font=font) + letter_spacing

def create_logo_png(filename, text_color_rgb):
    width = 600
    height = 200
    # Transparent background
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_smriti = ImageFont.truetype(FONT_BOLD_PATH, 80)
        font_tagline = ImageFont.truetype(FONT_REG_PATH, 16)
    except IOError:
        font_smriti = ImageFont.load_default()
        font_tagline = ImageFont.load_default()
        
    # Draw "smriti" in lowercase character-by-character to color the dots on the 'i's
    chars = ["s", "m", "r", "\u0131", "t", "\u0131"]
    widths = [draw.textlength(c, font=font_smriti) for c in chars]
    total_w = sum(widths)
    
    # Starting X to center the text
    start_x = (width - total_w) / 2
    y_pos = 35
    
    curr_x = start_x
    for i, c in enumerate(chars):
        draw.text((curr_x, y_pos), c, fill=text_color_rgb, font=font_smriti)
        
        # Color dots
        char_w = widths[i]
        if i == 3:  # First 'i' has teal dot
            dot_cx = curr_x + char_w / 2
            dot_cy = y_pos + 18
            r = 6.5
            draw.ellipse([(dot_cx - r, dot_cy - r), (dot_cx + r, dot_cy + r)], fill=TEAL_RGB)
        elif i == 5:  # Second 'i' has blue dot
            dot_cx = curr_x + char_w / 2
            dot_cy = y_pos + 18
            r = 6.5
            draw.ellipse([(dot_cx - r, dot_cy - r), (dot_cx + r, dot_cy + r)], fill=BLUE_RGB)
            
        curr_x += char_w
        
    # Draw Tagline: "A COMPLETE RETAIL ENTERPRISE SOLUTION"
    tagline = "A COMPLETE RETAIL ENTERPRISE SOLUTION"
    draw_tagline(draw, tagline, width / 2, 135, font_tagline, text_color_rgb, letter_spacing=3.5)
    
    img.save(filename, "PNG")
    print(f"Created PNG logo: {filename}")

def create_app_icon_png(filename, size, is_dark_bg=True):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded square background
    padding = int(size * 0.05)
    rect_coords = [padding, padding, size - padding, size - padding]
    corner_radius = int(size * 0.22)
    
    bg_color = NAVY_RGB if is_dark_bg else WHITE_RGB
    text_color = WHITE_RGB if is_dark_bg else NAVY_RGB
    
    draw.rounded_rectangle(rect_coords, radius=corner_radius, fill=bg_color)
    
    # Load bold font
    try:
        font_s = ImageFont.truetype(FONT_BOLD_PATH, int(size * 0.52))
    except IOError:
        font_s = ImageFont.load_default()
        
    # Draw lowercase 's'
    char = "s"
    char_w = draw.textlength(char, font=font_s)
    char_h = int(size * 0.38) # Approximate height of lowercase 's'
    char_x = (size - char_w) / 2
    char_y = (size - char_h) / 2 + int(size * 0.04) # push down slightly
    draw.text((char_x, char_y), char, fill=text_color, font=font_s)
    
    # Draw two dots above 's' side-by-side
    dot_radius = int(size * 0.045)
    dot_y = char_y - int(size * 0.05)
    
    # Left dot (Teal)
    left_cx = int(size * 0.42)
    draw.ellipse([(left_cx - dot_radius, dot_y - dot_radius), (left_cx + dot_radius, dot_y + dot_radius)], fill=TEAL_RGB)
    
    # Right dot (Blue)
    right_cx = int(size * 0.58)
    draw.ellipse([(right_cx - dot_radius, dot_y - dot_radius), (right_cx + dot_radius, dot_y + dot_radius)], fill=BLUE_RGB)
    
    img.save(filename, "PNG")
    print(f"Created app icon {size}x{size}: {filename}")

def create_favicon_ico(filename):
    ico_imgs = []
    for s in [16, 32, 48]:
        img = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Rounded background
        draw.rounded_rectangle([0, 0, s-1, s-1], radius=max(1, int(s*0.22)), fill=NAVY_RGB)
        
        # Load font
        try:
            f = ImageFont.truetype(FONT_BOLD_PATH, int(s*0.52))
        except IOError:
            f = ImageFont.load_default()
            
        # Lowercase 's'
        cw = draw.textlength("s", font=f)
        ch = int(s*0.38)
        cx = (s - cw)/2
        cy = (s - ch)/2 + max(1, int(s*0.04))
        draw.text((cx, cy), "s", fill=WHITE_RGB, font=f)
        
        # Two dots
        r = max(1, int(s*0.045))
        dot_y = cy - max(1, int(s*0.05))
        left_cx = int(s * 0.42)
        right_cx = int(s * 0.58)
        
        draw.ellipse([(left_cx - r, dot_y - r), (left_cx + r, dot_y + r)], fill=TEAL_RGB)
        draw.ellipse([(right_cx - r, dot_y - r), (right_cx + r, dot_y + r)], fill=BLUE_RGB)
        
        ico_imgs.append(img)
        
    ico_imgs[0].save(filename, format="ICO", sizes=[(16,16), (32,32), (48,48)], append_images=ico_imgs[1:])
    print(f"Created ICO favicon: {filename}")

def generate_svgs():
    # 1. smriti_wordmark.svg
    svg_wordmark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 200" width="100%" height="100%" fill="none">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800&amp;display=swap');
      .brand-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 80px;
        fill: {NAVY_HEX};
      }}
      .tagline-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 500;
        font-size: 16px;
        fill: {NAVY_HEX};
        letter-spacing: 3.5px;
      }}
    </style>
  </defs>
  <text y="110" class="brand-text">
    <tspan x="195">s</tspan>
    <tspan x="235">m</tspan>
    <tspan x="297">r</tspan>
    <tspan x="327">&#305;</tspan>
    <tspan x="351">t</tspan>
    <tspan x="381">&#305;</tspan>
  </text>
  <circle cx="337" cy="53" r="6.5" fill="{TEAL_HEX}" />
  <circle cx="391" cy="53" r="6.5" fill="{BLUE_HEX}" />
  <text x="300" y="152" text-anchor="middle" class="tagline-text">A COMPLETE RETAIL ENTERPRISE SOLUTION</text>
</svg>
'''

    # White Wordmark SVG (for dark backgrounds)
    svg_wordmark_white = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 200" width="100%" height="100%" fill="none">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800&amp;display=swap');
      .brand-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 80px;
        fill: {WHITE_HEX};
      }}
      .tagline-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 500;
        font-size: 16px;
        fill: {WHITE_HEX};
        letter-spacing: 3.5px;
      }}
    </style>
  </defs>
  <text y="110" class="brand-text">
    <tspan x="195">s</tspan>
    <tspan x="235">m</tspan>
    <tspan x="297">r</tspan>
    <tspan x="327">&#305;</tspan>
    <tspan x="351">t</tspan>
    <tspan x="381">&#305;</tspan>
  </text>
  <circle cx="337" cy="53" r="6.5" fill="{TEAL_HEX}" />
  <circle cx="391" cy="53" r="6.5" fill="{BLUE_HEX}" />
  <text x="300" y="152" text-anchor="middle" class="tagline-text">A COMPLETE RETAIL ENTERPRISE SOLUTION</text>
</svg>
'''

    # 2. smriti_monogram_light.svg (dark navy 's', teal and blue dots)
    svg_monogram_light = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" fill="none">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700&amp;display=swap');
      .s-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 320px;
        fill: {NAVY_HEX};
      }}
    </style>
  </defs>
  <text x="256" y="340" text-anchor="middle" class="s-text">s</text>
  <circle cx="210" cy="135" r="26" fill="{TEAL_HEX}" />
  <circle cx="302" cy="135" r="26" fill="{BLUE_HEX}" />
</svg>
'''

    # 3. smriti_monogram_dark.svg (white 's', teal and blue dots)
    svg_monogram_dark = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" fill="none">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700&amp;display=swap');
      .s-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 320px;
        fill: {WHITE_HEX};
      }}
    </style>
  </defs>
  <text x="256" y="340" text-anchor="middle" class="s-text">s</text>
  <circle cx="210" cy="135" r="26" fill="{TEAL_HEX}" />
  <circle cx="302" cy="135" r="26" fill="{BLUE_HEX}" />
</svg>
'''

    # 4. smriti_monogram_simple.svg (just the two dots: left teal, right blue)
    svg_monogram_simple = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" fill="none">
  <circle cx="210" cy="256" r="40" fill="{TEAL_HEX}" />
  <circle cx="302" cy="256" r="40" fill="{BLUE_HEX}" />
</svg>
'''

    # Rounded App Icon wrapper (full colored square box)
    svg_app_icon = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" fill="none">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700&amp;display=swap');
      .s-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 266px;
        fill: {WHITE_HEX};
      }}
    </style>
  </defs>
  <rect x="24" y="24" width="464" height="464" rx="112" fill="{NAVY_HEX}" />
  <text x="256" y="326" text-anchor="middle" class="s-text">s</text>
  <circle cx="215" cy="155" r="23" fill="{TEAL_HEX}" />
  <circle cx="297" cy="155" r="23" fill="{BLUE_HEX}" />
</svg>
'''

    return svg_wordmark, svg_wordmark_white, svg_monogram_light, svg_monogram_dark, svg_monogram_simple, svg_app_icon

def write_and_compile():
    print("Generating assets...")
    
    # Render PNGs locally
    create_logo_png("temp_logo.png", NAVY_RGB)
    create_logo_png("temp_logo_white.png", WHITE_RGB)
    create_app_icon_png("temp_icon_192.png", 192, is_dark_bg=True)
    create_app_icon_png("temp_icon_512.png", 512, is_dark_bg=True)
    create_app_icon_png("temp_favicon_png.png", 32)
    create_favicon_ico("temp_favicon.ico")
    
    svg_wordmark, svg_wordmark_white, svg_monogram_light, svg_monogram_dark, svg_monogram_simple, svg_app_icon = generate_svgs()
    
    # Copy generated assets to all target paths
    public_paths = [
        "smriti_retail_os/public",
        "smriti_retail_os/public/images"
    ]
    
    for base in public_paths:
        os.makedirs(base, exist_ok=True)
        
        # 1. Official Named SVG Vector Deliverables
        with open(os.path.join(base, "smriti_wordmark.svg"), "w", encoding="utf-8") as f:
            f.write(svg_wordmark)
        with open(os.path.join(base, "smriti_monogram_light.svg"), "w", encoding="utf-8") as f:
            f.write(svg_monogram_light)
        with open(os.path.join(base, "smriti_monogram_dark.svg"), "w", encoding="utf-8") as f:
            f.write(svg_monogram_dark)
        with open(os.path.join(base, "smriti_monogram_simple.svg"), "w", encoding="utf-8") as f:
            f.write(svg_monogram_simple)
            
        # 2. Legacy/Compatibility SVGs
        with open(os.path.join(base, "logo.svg"), "w", encoding="utf-8") as f:
            f.write(svg_wordmark)
        with open(os.path.join(base, "logo-blue.svg"), "w", encoding="utf-8") as f:
            f.write(svg_wordmark)
        with open(os.path.join(base, "smriti_logo.svg"), "w", encoding="utf-8") as f:
            f.write(svg_app_icon)
        with open(os.path.join(base, "logo-wh.svg"), "w", encoding="utf-8") as f:
            f.write(svg_wordmark_white)
        with open(os.path.join(base, "logo_white.svg"), "w", encoding="utf-8") as f:
            f.write(svg_wordmark_white)
            
        # 3. PNGs & ICOs
        import shutil
        shutil.copy2("temp_logo.png", os.path.join(base, "logo.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "logo-blue.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "smriti_logo.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "smriti-logo.png"))
        
        shutil.copy2("temp_logo_white.png", os.path.join(base, "logo-wh.png"))
        shutil.copy2("temp_logo_white.png", os.path.join(base, "logo_white.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "smriti_wordmark_logo.png"))
        
        shutil.copy2("temp_icon_192.png", os.path.join(base, "icon-192.png"))
        shutil.copy2("temp_icon_512.png", os.path.join(base, "icon-512.png"))
        shutil.copy2("temp_favicon_png.png", os.path.join(base, "favicon.png"))
        
        if "images" in base:
            shutil.copy2("temp_favicon.ico", os.path.join(base, "smriti_favicon.ico"))
            
    # Clean up temp files
    for temp in ["temp_logo.png", "temp_logo_white.png", "temp_icon_192.png", "temp_icon_512.png", "temp_favicon_png.png", "temp_favicon.ico"]:
        if os.path.exists(temp):
            os.remove(temp)
            
    print("Done generating all SVG and PNG assets!")

if __name__ == "__main__":
    write_and_compile()
