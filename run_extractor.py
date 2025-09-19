#!/usr/bin/env python3
"""
Simple launcher script for the PDF Data Extractor
This script provides an easy way to run the application with different modes
"""

import sys
import os
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'PyPDF2', 'pdfplumber', 'pandas', 'openpyxl', 'fitz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages


def install_dependencies():
    """Install required dependencies"""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def create_pdfs_directory():
    """Create pdfs directory if it doesn't exist"""
    pdfs_dir = Path("pdfs")
    if not pdfs_dir.exists():
        pdfs_dir.mkdir()
        print(f"Created directory: {pdfs_dir}")
        print("Please place your PDF files in the 'pdfs' directory")
        return False
    return True


def run_gui():
    """Run the GUI version"""
    try:
        import pdf_extractor_gui
        pdf_extractor_gui.main()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        return False
    return True


def run_cli():
    """Run the command line version"""
    try:
        from pdf_extractor import main
        main()
    except ImportError as e:
        print(f"Error importing CLI module: {e}")
        return False
    return True


def main():
    """Main launcher function"""
    print("=" * 60)
    print("          PDF Data Extractor Launcher")
    print("=" * 60)
    
    # Check dependencies
    print("\n1. Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        response = input("Would you like to install missing dependencies? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if not install_dependencies():
                print("Failed to install dependencies. Exiting.")
                return
        else:
            print("Cannot proceed without required dependencies. Exiting.")
            return
    else:
        print("All dependencies are installed!")
    
    # Check/create pdfs directory
    print("\n2. Checking PDF directory...")
    if not create_pdfs_directory():
        print("PDF directory created. Please add your PDF files and run again.")
        return
    
    # Check if PDFs exist
    pdf_files = list(Path("pdfs").glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in 'pdfs' directory.")
        print("Please add your PDF files to the 'pdfs' directory and run again.")
        return
    else:
        print(f"Found {len(pdf_files)} PDF files ready for processing!")
    
    # Choose mode
    print("\n3. Choose how to run the application:")
    print("   1. GUI Mode (Recommended - User-friendly interface)")
    print("   2. Command Line Mode (Advanced users)")
    print("   3. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            print("\nStarting GUI mode...")
            if not run_gui():
                print("Failed to start GUI mode")
            break
        elif choice == '2':
            print("\nStarting command line mode...")
            if not run_cli():
                print("Failed to start CLI mode")
            break
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()