# LinuxCNC Config Editor
This is a GUI editor of configuration files (INI) for LinuxCNC. It’s not designed for generating your CNC machine’s configuration like Stepconf or PNCconf but rather a tool for helping you edit the configuration file after the fact.

## DISCLAIMER

**THE AUTHORS OF THIS SOFTWARE ACCEPT ABSOLUTELY NO LIABILITY FOR ANY
HARM OR LOSS RESULTING FROM ITS USE.**

**IT IS _EXTREMELY_ UNWISE TO RELY ON SOFTWARE ALONE FOR SAFETY.**

**Any machinery capable of harming persons must have provisions for
completely removing power from all motors, etc, before persons enter
any danger area.**

**All machinery must be designed to comply with local and national
safety codes, and the authors of this software can not, and do not,
take any responsibility for such compliance.**


This software is released under the GPLv2 license.
See the file LICENSE.md for more details.

## Installation
This tool currently only requires PyQt5 to run. For future changes install dependencies by the following:

`pip3 install -r requirements.txt`

## Usage
Simply run the Python script with the following command:

`python3 LinuxCNC_Config_Editor.py`