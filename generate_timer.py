"""
Generate a 2-minute countdown timer GIF.
280x280 pixels, dark navy background, green progress arc.
"""

import math
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_countdown_gif(output_path: str):
    """Create a 2-minute countdown timer as an animated GIF."""
    size = 280
    center = size // 2
    radius = 110
    ring_width = 12
    bg_color = (26, 35, 126)       # #1a237e dark navy
    ring_bg = (55, 55, 65)         # dark gray ring background
    ring_fg = (0, 230, 118)        # #00e676 green
    text_color = (255, 255, 255)   # white

    # Try to load a good font
    font = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 56)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    total_seconds = 120  # 2 minutes
    frames = []

    for elapsed in range(total_seconds + 1):
        remaining = total_seconds - elapsed
        minutes = remaining // 60
        seconds = remaining % 60
        time_str = f"{minutes}:{seconds:02d}"

        # Progress fraction (1.0 = full, 0.0 = empty)
        progress = remaining / total_seconds

        img = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw background ring
        bbox = [
            center - radius, center - radius,
            center + radius, center + radius
        ]
        draw.arc(bbox, 0, 360, fill=ring_bg, width=ring_width)

        # Draw progress arc (clockwise from top)
        if progress > 0:
            start_angle = -90
            end_angle = start_angle + (360 * progress)
            draw.arc(bbox, start_angle, end_angle, fill=ring_fg, width=ring_width)

        # Draw time text centered
        text_bbox = draw.textbbox((0, 0), time_str, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        text_x = center - text_w // 2
        text_y = center - text_h // 2 - 5
        draw.text((text_x, text_y), time_str, fill=text_color, font=font)

        # Convert to palette mode for GIF optimization
        img_p = img.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
        frames.append(img_p)

    # Save as GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 1 second per frame
        loop=1          # Play once
    )
    print(f"  Created: {output_path} ({len(frames)} frames)")


if __name__ == "__main__":
    # Generate for all sessions
    for session in range(1, 6):
        output_dir = Path(f"session{session}/exam-strategy")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "countdown_2min.gif"
        create_countdown_gif(str(output_path))
