#!/usr/bin/env python3
"""
Simple runner for the improved PDF extractor
"""

from improved_pdf_extractor import ImprovedPDFExtractor
import os
import sys

def main():
    print("🔍 Improved PDF Data Extractor")
    print("=" * 40)
    
    # Check if PDFs folder exists
    pdf_folder = "PDFs"
    if not os.path.exists(pdf_folder):
        print(f"❌ Error: '{pdf_folder}' folder not found!")
        print("Please create a 'PDFs' folder and place your PDF files there.")
        return
    
    # Count PDF files
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"❌ No PDF files found in '{pdf_folder}' folder!")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"   • {pdf_file}")
    
    print("\n🚀 Starting extraction...")
    
    # Run the extractor
    extractor = ImprovedPDFExtractor(
        pdf_folder=pdf_folder,
        output_file="structured_extracted_data.xlsx"
    )
    
    try:
        extractor.run()
        print("\n✅ Extraction completed successfully!")
        print("📊 Check 'structured_extracted_data.xlsx' for your organized data")
        print("\n📋 The Excel file contains multiple sheets:")
        print("   • All_Data - Complete dataset with all columns")
        print("   • File_Info - File information and metadata")
        print("   • Product_Info - Product names, codes, manufacturers")
        print("   • Safety_Info - Hazard classifications, signal words")
        print("   • Physical_Properties - Physical characteristics")
        print("   • Composition - Chemical composition and CAS numbers")
        print("   • Handling - Storage and handling information")
        print("   • Regulatory - Transport and regulatory data")
        print("   • Summary - Extraction statistics")
        
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()