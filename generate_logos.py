import os
import math
from PIL import Image, ImageDraw, ImageFont

# Hex Colors
NAVY_HEX = "#092540"
TEAL_HEX = "#00D2FF"  # Bright cyan/teal from the image
WHITE_HEX = "#FFFFFF"

# RGB Colors
NAVY_RGB = (9, 37, 64)
TEAL_RGB = (0, 210, 255)
WHITE_RGB = (255, 255, 255)

FONT_BOLD_PATH = "C:\\Windows\\Fonts\\arialbd.ttf"
FONT_REG_PATH = "C:\\Windows\\Fonts\\arial.ttf"

def draw_gradient_line(draw, x1, y1, x2, y2, color1, color2, width):
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        draw.line([(x1, y1), (x2, y2)], fill=color1, width=width)
        return
        
    for i in range(steps + 1):
        t = i / steps
        r = int(color1[0] + (color2[0] - color1[0]) * t)
        g = int(color1[1] + (color2[1] - color1[1]) * t)
        b = int(color1[2] + (color2[2] - color1[2]) * t)
        
        curr_x = int(x1 + dx * t)
        curr_y = int(y1 + dy * t)
        draw.ellipse([(curr_x - width/2, curr_y - width/2), (curr_x + width/2, curr_y + width/2)], fill=(r, g, b))

def create_logo_png(filename, text_color_rgb, start_dot_rgb, end_dot_rgb, is_white=False):
    # Wordmark logo dimensions
    width = 500
    height = 200
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_smriti = ImageFont.truetype(FONT_BOLD_PATH, 72)
        font_sub = ImageFont.truetype(FONT_REG_PATH, 34)
    except IOError:
        font_smriti = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # Draw SMRITI
    smriti_text = "SMRITI"
    smriti_w = draw.textlength(smriti_text, font=font_smriti)
    smriti_x = (width - smriti_w) / 2
    smriti_y = 20
    draw.text((smriti_x, smriti_y), smriti_text, fill=text_color_rgb, font=font_smriti)
    
    # Draw line
    line_y = 112
    line_left = smriti_x - 5
    line_right = smriti_x + smriti_w + 5
    
    # Draw gradient line
    draw_gradient_line(draw, int(line_left), line_y, int(line_right), line_y, start_dot_rgb, end_dot_rgb, width=4)
    
    # Draw terminal dots
    dot_radius = 6
    draw.ellipse([(line_left - dot_radius, line_y - dot_radius), (line_left + dot_radius, line_y + dot_radius)], fill=start_dot_rgb)
    draw.ellipse([(line_right - dot_radius, line_y - dot_radius), (line_right + dot_radius, line_y + dot_radius)], fill=end_dot_rgb)
    
    # Draw "Distributor OS"
    sub_text = "Distributor OS"
    sub_w = draw.textlength(sub_text, font=font_sub)
    sub_x = (width - sub_w) / 2
    sub_y = 132
    draw.text((sub_x, sub_y), sub_text, fill=text_color_rgb, font=font_sub)
    
    img.save(filename, "PNG")
    print(f"Created PNG logo: {filename}")

def create_app_icon_png(filename, size):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded navy square background
    padding = int(size * 0.05)
    rect_coords = [padding, padding, size - padding, size - padding]
    corner_radius = int(size * 0.2)
    draw.rounded_rectangle(rect_coords, radius=corner_radius, fill=NAVY_RGB)
    
    # Load bold font
    try:
        font_s = ImageFont.truetype(FONT_BOLD_PATH, int(size * 0.55))
    except IOError:
        font_s = ImageFont.load_default()
        
    # Draw stylized 'S' in center
    char = "S"
    char_w = draw.textlength(char, font=font_s)
    char_h = int(size * 0.55) # approximate height
    char_x = (size - char_w) / 2
    char_y = (size - char_h) / 2 - int(size * 0.04)
    draw.text((char_x, char_y), char, fill=WHITE_RGB, font=font_s)
    
    # Draw small gradient underline dot
    line_y = int(size * 0.76)
    line_left = int(size * 0.35)
    line_right = int(size * 0.65)
    draw_gradient_line(draw, line_left, line_y, line_right, line_y, NAVY_RGB, TEAL_RGB, width=int(size * 0.035))
    
    img.save(filename, "PNG")
    print(f"Created app icon {size}x{size}: {filename}")

def create_favicon_ico(filename):
    # Favicons sizes: 16x16, 32x32, 48x48
    ico_imgs = []
    for s in [16, 32, 48]:
        img = Image.new("RGBA", (s, s), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        # Background rounded rect
        draw.rounded_rectangle([0, 0, s-1, s-1], radius=max(1, int(s*0.2)), fill=NAVY_RGB)
        # S text
        try:
            f = ImageFont.truetype(FONT_BOLD_PATH, int(s*0.65))
        except IOError:
            f = ImageFont.load_default()
        cw = draw.textlength("S", font=f)
        draw.text(((s-cw)/2, (s-int(s*0.65))/2 - max(1, int(s*0.05))), "S", fill=WHITE_RGB, font=f)
        ico_imgs.append(img)
        
    ico_imgs[0].save(filename, format="ICO", sizes=[(16,16), (32,32), (48,48)], append_images=ico_imgs[1:])
    print(f"Created ICO favicon: {filename}")

def generate_svgs():
    # Full Color Logo SVG
    svg_logo = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 200" width="100%" height="100%" fill="none">
  <defs>
    <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{NAVY_HEX}" />
      <stop offset="100%" stop-color="{TEAL_HEX}" />
    </linearGradient>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800&amp;display=swap');
      .brand-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 72px;
        fill: {NAVY_HEX};
        letter-spacing: 2px;
      }}
      .sub-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 400;
        font-size: 34px;
        fill: {NAVY_HEX};
        letter-spacing: 1px;
      }}
    </style>
  </defs>
  <text x="250" y="85" text-anchor="middle" class="brand-text">SMRITI</text>
  <line x1="110" y1="112" x2="390" y2="112" stroke="url(#line-grad)" stroke-width="4" stroke-linecap="round" />
  <circle cx="110" cy="112" r="6" fill="{NAVY_HEX}" />
  <circle cx="390" cy="112" r="6" fill="{TEAL_HEX}" />
  <text x="250" y="165" text-anchor="middle" class="sub-text">Distributor OS</text>
</svg>
'''

    # White Logo SVG
    svg_logo_white = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 200" width="100%" height="100%" fill="none">
  <defs>
    <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{WHITE_HEX}" />
      <stop offset="100%" stop-color="{TEAL_HEX}" />
    </linearGradient>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800&amp;display=swap');
      .brand-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 72px;
        fill: {WHITE_HEX};
        letter-spacing: 2px;
      }}
      .sub-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 400;
        font-size: 34px;
        fill: {WHITE_HEX};
        letter-spacing: 1px;
      }}
    </style>
  </defs>
  <text x="250" y="85" text-anchor="middle" class="brand-text">SMRITI</text>
  <line x1="110" y1="112" x2="390" y2="112" stroke="url(#line-grad)" stroke-width="4" stroke-linecap="round" />
  <circle cx="110" cy="112" r="6" fill="{WHITE_HEX}" />
  <circle cx="390" cy="112" r="6" fill="{TEAL_HEX}" />
  <text x="250" y="165" text-anchor="middle" class="sub-text">Distributor OS</text>
</svg>
'''

    # App Icon SVG
    svg_icon = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%" fill="none">
  <defs>
    <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{NAVY_HEX}" />
      <stop offset="100%" stop-color="{TEAL_HEX}" />
    </linearGradient>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@800&amp;display=swap');
      .s-text {{
        font-family: 'Outfit', 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 300px;
        fill: {WHITE_HEX};
      }}
    </style>
  </defs>
  <rect x="24" y="24" width="464" height="464" rx="92" fill="{NAVY_HEX}" />
  <text x="256" y="330" text-anchor="middle" dominant-baseline="middle" class="s-text">S</text>
  <line x1="180" y1="390" x2="332" y2="390" stroke="url(#line-grad)" stroke-width="18" stroke-linecap="round" />
</svg>
'''

    return svg_logo, svg_logo_white, svg_icon

def write_and_compile():
    print("Generating assets...")
    
    # Render PNGs locally
    create_logo_png("temp_logo.png", NAVY_RGB, NAVY_RGB, TEAL_RGB)
    create_logo_png("temp_logo_white.png", WHITE_RGB, WHITE_RGB, TEAL_RGB)
    create_app_icon_png("temp_icon_192.png", 192)
    create_app_icon_png("temp_icon_512.png", 512)
    create_app_icon_png("temp_favicon_png.png", 32)
    create_favicon_ico("temp_favicon.ico")
    
    svg_logo, svg_logo_white, svg_icon = generate_svgs()
    
    # Copy generated assets to all target paths
    public_paths = [
        "smriti_retail_os/public",
        "smriti_retail_os/public/images"
    ]
    
    for base in public_paths:
        os.makedirs(base, exist_ok=True)
        
        # 1. SVGs
        with open(os.path.join(base, "logo.svg"), "w", encoding="utf-8") as f:
            f.write(svg_logo)
        with open(os.path.join(base, "logo-blue.svg"), "w", encoding="utf-8") as f:
            f.write(svg_logo)
        with open(os.path.join(base, "smriti_logo.svg"), "w", encoding="utf-8") as f:
            f.write(svg_icon)  # Icon is the main square visual
        with open(os.path.join(base, "logo-wh.svg"), "w", encoding="utf-8") as f:
            f.write(svg_logo_white)
        with open(os.path.join(base, "logo_white.svg"), "w", encoding="utf-8") as f:
            f.write(svg_logo_white)
            
        # 2. PNGs
        import shutil
        shutil.copy2("temp_logo.png", os.path.join(base, "logo.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "logo-blue.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "smriti_logo.png"))
        shutil.copy2("temp_logo.png", os.path.join(base, "smriti-logo.png"))
        
        shutil.copy2("temp_logo_white.png", os.path.join(base, "logo-wh.png"))
        shutil.copy2("temp_logo_white.png", os.path.join(base, "logo_white.png"))
        
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
