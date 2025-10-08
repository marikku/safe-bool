#!/usr/bin/env python3
"""
Script to extract svg-inline--fa elements from svg_html.html and match them 
with original elements in original.html, then output to CSV.
"""

import re
import csv
from pathlib import Path
from bs4 import BeautifulSoup


def find_svg_elements_with_context(svg_html_path):
    """Find all svg-inline--fa elements in svg_html.html with their line numbers and context."""
    print(f"Reading {svg_html_path}...")
    
    with open(svg_html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    svg_elements = []
    
    for i, line in enumerate(lines, start=1):
        # Search for svg elements with svg-inline--fa class
        if 'svg-inline--fa' in line and '<svg' in line:
            # Extract the full SVG element and the comment that follows
            svg_match = re.search(r'<svg[^>]*class="[^"]*svg-inline--fa[^"]*"[^>]*>.*?</svg>', line)
            if svg_match:
                svg_element = svg_match.group(0)
                
                # Look for the comment that shows the original icon
                comment_match = re.search(r'<!--\s*(<i[^>]*>.*?</i>)[^>]*-->', line)
                original_icon = ""
                if comment_match:
                    original_icon = comment_match.group(1).strip()
                
                # Extract icon classes from SVG
                icon_classes = []
                class_match = re.search(r'data-icon="([^"]+)"', svg_element)
                if class_match:
                    icon_classes.append(class_match.group(1))
                
                svg_elements.append({
                    'line_number': i,
                    'svg_element': svg_element[:200] + '...' if len(svg_element) > 200 else svg_element,
                    'original_icon': original_icon,
                    'icon_name': class_match.group(1) if class_match else '',
                })
    
    print(f"Found {len(svg_elements)} svg-inline--fa elements")
    return svg_elements


def find_original_elements(original_html_path, svg_elements):
    """Find the original elements in original.html that match the SVG elements."""
    print(f"Reading {original_html_path}...")
    
    with open(original_html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    results = []
    
    for svg_elem in svg_elements:
        original_icon = svg_elem['original_icon']
        
        if not original_icon:
            results.append({
                'svg_line': svg_elem['line_number'],
                'svg_element': svg_elem['svg_element'],
                'original_line': 'N/A',
                'original_element': 'Not found in comment',
                'icon_name': svg_elem['icon_name']
            })
            continue
        
        # Search for the original icon in original.html
        found = False
        for i, line in enumerate(lines, start=1):
            # Clean up spaces for comparison
            line_clean = re.sub(r'\s+', ' ', line.strip())
            original_clean = re.sub(r'\s+', ' ', original_icon.strip())
            
            if original_clean in line_clean:
                results.append({
                    'svg_line': svg_elem['line_number'],
                    'svg_element': svg_elem['svg_element'],
                    'original_line': i,
                    'original_element': original_icon,
                    'icon_name': svg_elem['icon_name'],
                    'context': line.strip()[:150] + '...' if len(line.strip()) > 150 else line.strip()
                })
                found = True
                break
        
        if not found:
            results.append({
                'svg_line': svg_elem['line_number'],
                'svg_element': svg_elem['svg_element'],
                'original_line': 'Not found',
                'original_element': original_icon,
                'icon_name': svg_elem['icon_name'],
                'context': ''
            })
    
    return results


def write_to_csv(results, output_path):
    """Write results to CSV file."""
    print(f"Writing results to {output_path}...")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['svg_line', 'original_line', 'icon_name', 'original_element', 'svg_element', 'context']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow(result)
    
    print(f"Successfully wrote {len(results)} rows to {output_path}")


def main():
    # Define paths
    base_dir = Path(__file__).parent / 'src'
    svg_html_path = base_dir / 'svg_html.html'
    original_html_path = base_dir / 'original.html'
    output_csv_path = Path(__file__).parent / 'svg_elements_mapping.csv'
    
    # Check if files exist
    if not svg_html_path.exists():
        print(f"Error: {svg_html_path} not found!")
        return
    
    if not original_html_path.exists():
        print(f"Error: {original_html_path} not found!")
        return
    
    # Process files
    svg_elements = find_svg_elements_with_context(svg_html_path)
    results = find_original_elements(original_html_path, svg_elements)
    write_to_csv(results, output_csv_path)
    
    print("\nSummary:")
    print(f"Total SVG elements found: {len(svg_elements)}")
    print(f"Matched with original: {sum(1 for r in results if r['original_line'] != 'Not found' and r['original_line'] != 'N/A')}")
    print(f"Not matched: {sum(1 for r in results if r['original_line'] == 'Not found')}")
    print(f"\nOutput saved to: {output_csv_path}")


if __name__ == "__main__":
    main()
