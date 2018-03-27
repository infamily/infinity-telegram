# coding: utf-8
import os
import sys

CONFIG_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), os.pardir,
    )
)

# Add src to the sys.path if necessary
SRC_DIR = os.path.join(CONFIG_DIR, 'src')
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)
