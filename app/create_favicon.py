#!/usr/bin/env python3
"""
Create favicon files for Athena Realtime Interviewer
Generates orange-themed favicons with "A" letter
"""

import os
from pathlib import Path

def create_svg_favicon():
    """Create the base SVG favicon"""
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
    <!-- Orange background circle -->
    <circle cx="16" cy="16" r="16" fill="#ff4a00"/>
    
    <!-- Letter A in white -->
    <text x="16" y="22" 
          text-anchor="middle" 
          font-family="Arial, sans-serif" 
          font-size="20" 
          font-weight="bold" 
          fill="white">A</text>
    
    <!-- Optional: subtle shadow effect -->
    <circle cx="16" cy="16" r="16" fill="none" stroke="rgba(0,0,0,0.1)" stroke-width="1"/>
</svg>'''
    
    return svg_content

def create_simple_html_favicon():
    """Create a simple HTML-based favicon using data URI"""
    svg_content = create_svg_favicon()
    
    # Create HTML file that shows how to use the favicon
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Favicon Preview</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,{svg_content.replace('"', "'")}">
</head>
<body>
    <h1>Athena Favicon Preview</h1>
    <p>Check the browser tab for the orange "A" favicon!</p>
    <div style="font-size: 64px; color: #ff4a00;">🅰️</div>
</body>
</html>'''
    
    return html_content

def main():
    # Create the SVG favicon
    svg_content = create_svg_favicon()
    
    # Write SVG file
    with open('favicon.svg', 'w') as f:
        f.write(svg_content)
    print("Created favicon.svg")
    
    # Create a simple ICO file content (basic format)
    # For a proper ICO, you'd need a more complex format, but this creates a placeholder
    ico_placeholder = b'\x00\x00\x01\x00\x01\x00\x20\x20\x00\x00\x01\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    # Write basic placeholder files (you can replace these with proper icons later)
    with open('favicon.ico', 'wb') as f:
        f.write(ico_placeholder)
    print("Created favicon.ico (placeholder)")
    
    # Create HTML preview file
    html_preview = create_simple_html_favicon()
    with open('favicon-preview.html', 'w') as f:
        f.write(html_preview)
    print("Created favicon-preview.html")
    
    print("\nFavicon files created!")
    print("For production, convert the SVG to proper ICO and PNG formats using:")
    print("- Online tools like favicon.io")
    print("- ImageMagick: convert favicon.svg favicon.ico")
    print("- Or use the SVG directly in modern browsers")

if __name__ == "__main__":
    main()