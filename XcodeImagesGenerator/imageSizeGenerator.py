import json
import os
import sys
import argparse
from PIL import Image

def get_image_size(image_path):
    """Get the size of an image."""
    try:
        img = Image.open(image_path)
        return img.size
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

def generate_missing_sizes(image_path, target_sizes, original_extension, base_filename):
    """Generate missing image sizes."""
    image_dir = os.path.dirname(image_path)
    
    for size_name, target_size in target_sizes.items():
        # Calculate the new size based on the target size ratio
        img = Image.open(image_path)
        current_size = img.size
        new_width = int(current_size[0] * target_size[0])
        new_height = int(current_size[1] * target_size[1])
        
        # Open and resize the image
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)  # Use LANCZOS for better quality
        
        # Save the resized image
        if size_name == '1x':
            new_filename = f"{base_filename}{original_extension}"
        else:
            new_filename = f"{base_filename}@{size_name}{original_extension}"
        new_path = os.path.join(image_dir, new_filename)
        img.save(new_path)
        
        # Display green check marks based on size
        # print(f"Generated: {new_filename} ✅")
        
        return new_filename

def parse_contents_json(json_path, undo_log):
    """Parse Contents.json to determine image sizes."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            
            # Extract scale information from JSON
            scales = {}
            for image in data['images']:
                scale = image.get('scale', '1x')
                filename = image.get('filename', None)
                
                if filename is None:
                    # If filename is not specified, skip for now
                    continue
                
                # Rename the image if necessary
                base_filename, extension = os.path.splitext(filename)
                if '@' not in filename and scale != '1x':
                    new_filename = f"{base_filename.replace('x', '')}@{scale}{extension}"
                    os.rename(os.path.join(os.path.dirname(json_path), filename), os.path.join(os.path.dirname(json_path), new_filename))
                    undo_log.append({
                        'old_path': os.path.join(os.path.dirname(json_path), filename),
                        'new_path': os.path.join(os.path.dirname(json_path), new_filename)
                    })
                    image['filename'] = new_filename  # Update filename in JSON data
                
                # Determine the file extension
                _, extension = os.path.splitext(image['filename'])
                if extension not in ['.png', '.jpg', '.jpeg']:
                    print(f"Skipping unsupported file type: {image['filename']}")
                    continue
                
                if scale not in scales:
                    scales[scale] = image['filename']
            
            return data, scales
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None, None

def update_contents_json(json_path, scales, undo_log):
    """Update Contents.json with new image information."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Create a backup of the original JSON file
        backup_path = f"{json_path}_backup"
        with open(backup_path, 'w') as f_backup:
            json.dump(data, f_backup, indent=2)
        undo_log.append({
            'json_backup_path': backup_path,
            'json_path': json_path
        })
        
        # Remove old images
        data['images'] = []
        
        # Add new image information in correct order
        for size in ['1x', '2x', '3x']:
            if size in scales:
                new_image = {
                    "idiom": "universal",
                    "filename": scales[size],
                    "scale": size
                }
                data['images'].append(new_image)
        
        # Convert data to JSON string
        json_str = json.dumps(data, indent=2)
        
        # Write updated data back to JSON
        with open(json_path, 'w') as f:
            f.write(json_str)
        
    except Exception as e:
        print(f"Error updating JSON: {e}")

def process_imageset(dir_path, undo_log):
    """Process an imageset directory."""
    if dir_path.endswith('.imageset') and os.path.exists(os.path.join(dir_path, 'Contents.json')):
        json_path = os.path.join(dir_path, 'Contents.json')
        data, scales = parse_contents_json(json_path, undo_log)
        
        if not scales:
            print(f"No images found in {dir_path}. Skipping.")
            return
        
        existing_sizes = list(scales.keys())
        
        # Check if all necessary sizes exist
        if '1x' in existing_sizes and '2x' in existing_sizes and '3x' in existing_sizes:
            print(f"⏭️ Skipping {os.path.basename(dir_path)}: All necessary sizes exist.")
            return
        
        target_sizes = {
            '1x': (1, 1),
            '2x': (0.5, 0.5),
            '3x': (1/3, 1/3)
        }
        
        # Adjust target sizes based on the largest existing size
        if existing_sizes:
            max_size = max([int(size.replace('x', '')) for size in existing_sizes], default=1)
            for size_name, size_ratio in target_sizes.items():
                if int(size_name.replace('x', '')) > max_size:
                    target_sizes[size_name] = (1 / max_size, 1 / max_size)
        
        # Generate missing sizes
        generated_sizes = []
        for size_name in target_sizes:
            if size_name not in existing_sizes:
                # Find the largest existing image to resize
                largest_image_path = None
                largest_size = (0, 0)
                for size, path in scales.items():
                    img_path = os.path.join(dir_path, path)
                    if os.path.exists(img_path):  # Check if the file exists
                        img_size = get_image_size(img_path)
                        if img_size > largest_size:
                            largest_size = img_size
                            largest_image_path = img_path
                
                if largest_image_path:
                    # Determine the file extension of the largest image
                    _, extension = os.path.splitext(largest_image_path)
                    base_filename = os.path.splitext(os.path.basename(largest_image_path))[0].replace('@3x', '').replace('@2x', '').replace('@1x', '').replace('x', '')
                    
                    generate_missing_sizes(largest_image_path, {size_name: target_sizes[size_name]}, extension, base_filename)
                    if size_name == '1x':
                        undo_log.append({
                            'generated_path': os.path.join(dir_path, f"{base_filename}{extension}")
                        })
                    else:
                        undo_log.append({
                            'generated_path': os.path.join(dir_path, f"{base_filename}@{size_name}{extension}")
                        })
                    generated_sizes.append(size_name)
        
        # Update Contents.json
        if '1x' in scales:
            scales['1x'] = scales['1x'].replace('@1x', '')
        else:
            scales['1x'] = f"{base_filename}{extension}"
        scales['2x'] = f"{base_filename}@2x{extension}"
        scales['3x'] = f"{base_filename}@3x{extension}"
        update_contents_json(json_path, scales, undo_log)
        
        # Report generated sizes for this imageset
        report_line = f"Done generating images for {os.path.basename(dir_path)} for sizes: "
        for size in ['1x', '2x', '3x']:
            if size in generated_sizes or size in existing_sizes:
                report_line += f"{'✅' * int(size.replace('x', ''))}, "
        print(report_line.strip(', '))
        
        return generated_sizes

def undo_changes(undo_log):
    """Undo all changes made by the script."""
    for change in reversed(undo_log):
        if 'old_path' in change:
            # Undo file rename
            os.rename(change['new_path'], change['old_path'])
            # print(f"Undone: Renamed {change['new_path']} back to {change['old_path']}")
        elif 'json_backup_path' in change:
            # Undo JSON update by restoring from backup
            os.replace(change['json_backup_path'], change['json_path'])
            # print(f"Undone: Restored {change['json_path']} from backup")
        elif 'generated_path' in change:
            # Delete generated images
            if os.path.exists(change['generated_path']):
                os.remove(change['generated_path'])
                # print(f"Undone: Deleted {change['generated_path']}")
            else:
                print(f"Warning: {change['generated_path']} does not exist.")
    print("Finished Undoing all changes")

def main(xcassets_folder):
    """Main function to process the xcassets folder."""
    total_populated = 0
    total_skipped = 0
    report_lines = []
    undo_log = []  # Log for undoing changes
    
    for root, dirs, files in os.walk(xcassets_folder):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            generated_sizes = process_imageset(dir_path, undo_log)
            
            if generated_sizes:
                total_populated += 1
            else:
                total_skipped += 1
    
    # Generate summary report
    print("\nSummary Report:")
    print(f"Total Imagesets Populated: {total_populated}")
    print(f"Total Imagesets Skipped: {total_skipped}")
    
    # Ask user if they want to undo changes
    undo_choice = input("Do you want to undo all changes? (y/n): ")
    
    if undo_choice.lower() == 'y':
        undo_changes(undo_log)
    else:
        # Delete backup JSON files if undo is not selected
        for change in undo_log:
            if 'json_backup_path' in change:
                if os.path.exists(change['json_backup_path']):
                    os.remove(change['json_backup_path'])
                    print(f"Deleted backup: {change['json_backup_path']}")
        print("Changes will be kept.")
        
        # Warning for unexpected changes
        print("\nWarning: If unexpected changes were made, you may need to reset your repository. Run the following commands with caution:")
        print("git reset --hard")
        print("git clean -fd")
        print("These commands will discard all changes and remove untracked files. Use them only if necessary.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate missing image sizes in Xcode asset catalogs.')
    parser.add_argument('xcassets_folder', help='Path to the .xcassets folder.')
    args = parser.parse_args()
    
    xcassets_folder = args.xcassets_folder
    main(xcassets_folder)
