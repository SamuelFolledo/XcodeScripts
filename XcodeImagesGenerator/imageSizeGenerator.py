import json
import os
import sys
from PIL import Image

def get_image_size(image_path):
    """Get the size of an image."""
    try:
        img = Image.open(image_path)
        return img.size
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

def generate_missing_sizes(image_path, target_sizes):
    """Generate missing image sizes."""
    image_name = os.path.basename(image_path)
    image_dir = os.path.dirname(image_path)
    
    # Extract base filename without extension
    base_filename = os.path.splitext(image_name)[0]
    
    # Get the current image size
    current_size = get_image_size(image_path)
    
    if current_size is None:
        return
    
    for size_name, target_size in target_sizes.items():
        # Calculate the new size based on the target size ratio
        new_width = int(current_size[0] * target_size[0])
        new_height = int(current_size[1] * target_size[1])
        
        # Open and resize the image
        img = Image.open(image_path)
        img = img.resize((new_width, new_height))
        
        # Save the resized image
        new_filename = f"{base_filename}@{size_name}x.png"
        new_path = os.path.join(image_dir, new_filename)
        img.save(new_path)
        
        print(f"Generated: {new_filename}")

def parse_contents_json(json_path):
    """Parse Contents.json to determine image sizes."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            
            # Extract scale information from JSON
            scales = {}
            for image in data['images']:
                scale = image.get('scale', '1x')
                if scale not in scales:
                    scales[scale] = image['filename']
            
            return scales
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return {}

def main(xcassets_folder):
    """Main function to process the xcassets folder."""
    for root, dirs, files in os.walk(xcassets_folder):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            
            # Check if it's an imageset
            if os.path.exists(os.path.join(dir_path, 'Contents.json')):
                json_path = os.path.join(dir_path, 'Contents.json')
                scales = parse_contents_json(json_path)
                
                # Determine missing sizes based on existing ones
                existing_sizes = list(scales.keys())
                target_sizes = {
                    '1x': (1, 1),
                    '2x': (0.5, 0.5),
                    '3x': (1/3, 1/3)
                }
                
                # Adjust target sizes based on the largest existing size
                max_size = max([int(size.replace('x', '')) for size in existing_sizes])
                for size_name, size_ratio in target_sizes.items():
                    if int(size_name.replace('x', '')) > max_size:
                        target_sizes[size_name] = (1 / max_size, 1 / max_size)
                
                # Generate missing sizes
                for size_name in target_sizes:
                    if size_name not in existing_sizes:
                        # Find the largest existing image to resize
                        largest_image_path = None
                        largest_size = (0, 0)
                        for size, path in scales.items():
                            img_path = os.path.join(dir_path, path)
                            img_size = get_image_size(img_path)
                            if img_size > largest_size:
                                largest_size = img_size
                                largest_image_path = img_path
                        
                        if largest_image_path:
                            generate_missing_sizes(largest_image_path, {size_name: target_sizes[size_name]})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_size_generator.py <xcassets_folder>")
        sys.exit(1)
    
    xcassets_folder = sys.argv[1]
    main(xcassets_folder)
