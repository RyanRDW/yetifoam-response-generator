#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment
This file imports and runs the Yetifoam Enhanced Response Generator
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import and run the main application
from yetifoam_enhanced_final_streamlit_app import main

if __name__ == "__main__":
    main()