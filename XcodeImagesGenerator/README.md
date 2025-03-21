# Image Size Generator for Xcode Assets
=====================================

This script is designed to help manage image sizes in Xcode asset catalogs. It iterates through each imageset in a specified `.xcassets` folder, checks the existing image sizes based on the `Contents.json` files, and generates missing sizes by resizing the largest existing image.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Libraries to Install](#libraries-to-install)
- [How to Use](#how-to-use)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Introduction
This script simplifies the process of maintaining consistent image sizes across different devices and screen resolutions in iOS development.

## Features
- **Automated Size Generation**: Automatically generates missing image sizes (1x, 2x, 3x) based on the largest existing image.
- **JSON Parsing**: Parses `Contents.json` files to determine existing image sizes.
- **Flexible Resizing**: Resizes images while maintaining aspect ratio.

## Libraries to Install
To run this script, you need to install the following libraries:

- **Pillow**: For image processing and resizing.
pip install Pillow


## How to Use
1. **Install Required Libraries**:
 Run the installation command for Pillow as shown above.

2. **Run the Script**:
 Open a terminal and navigate to the directory containing the script. You can execute the script by dragging the script file into the terminal, followed by the path to your `.xcassets` folder.

  Example:
    python image_size_generator.py /path/to/your/xcassets/folder


Alternatively, you can drag the script file into the terminal, type a space, and then drag the `.xcassets` folder into the terminal to execute it.

3. **Verify Execution**:
The script will generate missing image sizes and print the names of the generated images.

## Troubleshooting
- **Permission Issues**: Ensure you have write permissions in the target `.xcassets` folder.
- **Image Processing Errors**: Check if images are corrupted or if there are issues with Pillow installation.

## Contributing
Contributions are welcome! Feel free to submit pull requests or report issues on the GitHub page.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
