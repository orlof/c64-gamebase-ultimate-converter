# C64 Gamebase to 1541 Ultimate II(+) Converter

This Python script downloads the C64 Gamebase v18 games collection and transforms it into a directory structure that can be easily copied to a USB or SD card for use with the C64's "1541 Ultimate II(+)" device.

## Table of Contents

- [Description](#description)
- [Compatibility](#compatibility)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Description

The main purpose of this script is to simplify the process of preparing C64 Gamebase v18 games for use with the "1541 Ultimate II(+)" device. It downloads the Gamebase v18 ISO image, extracts all the games from it, and organizes them into a subdirectory named "gamebase" with a directory structure that ensures compatibility with the 1541 Ultimate II(+) device.

Each game directory within the "gamebase" subdirectory is named according to the "Name" field in the respective game's .NFO file. This ensures that the game directories have meaningful and recognizable names.

**Note for Windows Users**: If you are using Windows, you might find that [Obliterator's GB64ReorganizerSD](https://www.obliterator918.com/gamebase-64-reorganizer-sd/) offers more sophisticated features and is easier to use.

## Compatibility

This script has been tested with Python 3.9.16 but should work with other compatible Python versions as well.

## Dependencies

This script relies on the following Python packages, which can be easily installed using pip:

- [requests](https://pypi.org/project/requests/): A library for making HTTP requests.
- [rich](https://pypi.org/project/rich/): A library for adding rich text and formatting to terminal output.
- [pycdlib](https://pypi.org/project/pycdlib/): A library for handling ISO9660 filesystems.

## Installation

1. Clone this repository to your local machine or download the ZIP archive.

   ```bash
   git clone https://github.com/your-username/c64-gamebase-ultimate-converter.git
   ```

2. Navigate to the project directory.

   ```bash
   cd c64-gamebase-ultimate-converter
   ```

3. Install the required dependencies using pip and the provided requirements.txt file.

   ```bash
   python -m venv .venv
   source .venv/bin/activate # or .venv\Scripts\activate.bat on Windows
   pip install -r requirements.txt
   ```

## Usage
1. Run the script using Python.

   ```bash
   python convert_gamebase.py
   ```

2. The script will automatically download the C64 Gamebase v18 ISO image, extract the games,
   and organize them into the "gamebase" subdirectory.

3. Once the conversion is complete, you can copy the "gamebase" subdirectory to a USB or SD card and use it with your
   "1541 Ultimate II(+)" device.

## License

This project is licensed under the MIT License.

---

I hope you enjoy your C64 Gamebase v18 collection on your 1541 Ultimate II(+) device!

_Disclaimer: This project is not affiliated with or endorsed by C64, Gamebase, or the creators of the 1541 Ultimate II(+) device._
