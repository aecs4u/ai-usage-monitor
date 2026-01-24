#!/usr/bin/env python3
"""
Generate icon.png for AI Usage Monitor VS Code extension
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_icon(size=128):
    """Create a professional icon for AI Usage Monitor"""

    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors - blue and green theme
    bg_color = (30, 136, 229, 255)      # Blue #1E88E5
    accent_color = (67, 160, 71, 255)   # Green #43A047
    dark_accent = (25, 118, 210, 255)   # Dark blue #1976D2

    # Draw circular background
    padding = 8
    circle_bbox = [padding, padding, size - padding, size - padding]
    draw.ellipse(circle_bbox, fill=bg_color)

    # Draw bars (representing usage graph)
    bar_area_left = size * 0.2
    bar_area_right = size * 0.8
    bar_area_bottom = size * 0.75
    bar_area_top = size * 0.3

    num_bars = 5
    bar_width = (bar_area_right - bar_area_left) / num_bars * 0.6
    bar_spacing = (bar_area_right - bar_area_left) / num_bars

    # Bar heights (creating an ascending pattern)
    heights = [0.4, 0.6, 0.9, 0.7, 0.5]

    for i, height in enumerate(heights):
        x = bar_area_left + (i * bar_spacing) + (bar_spacing - bar_width) / 2
        bar_height = (bar_area_bottom - bar_area_top) * height
        y = bar_area_bottom - bar_height

        # Alternate colors for visual interest
        color = accent_color if i % 2 == 0 else dark_accent

        # Draw rounded rectangle for bar
        bar_bbox = [x, y, x + bar_width, bar_area_bottom]
        draw.rounded_rectangle(bar_bbox, radius=2, fill=color)

    # Draw subtle AI circuit pattern in top right
    circuit_color = (255, 255, 255, 80)  # Semi-transparent white

    # Small circuit nodes
    nodes = [
        (size * 0.7, size * 0.25),
        (size * 0.85, size * 0.2),
        (size * 0.75, size * 0.15)
    ]

    for x, y in nodes:
        draw.ellipse([x-2, y-2, x+2, y+2], fill=circuit_color)

    # Connect nodes with lines
    for i in range(len(nodes) - 1):
        draw.line([nodes[i], nodes[i+1]], fill=circuit_color, width=1)

    return img

def create_icon_variants():
    """Create icon in different sizes"""
    sizes = [128, 256, 512]

    for size in sizes:
        icon = create_icon(size)
        filename = f'icon-{size}.png' if size != 128 else 'icon.png'
        icon.save(filename)
        print(f'✓ Created {filename} ({size}x{size})')

    print('\nIcons created successfully!')
    print('Main icon: icon.png (128x128)')

if __name__ == '__main__':
    try:
        create_icon_variants()
    except ImportError:
        print('Error: Pillow not installed')
        print('Install with: pip install pillow')
        exit(1)
