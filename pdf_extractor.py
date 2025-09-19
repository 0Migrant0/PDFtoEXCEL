#!/usr/bin/env python3
"""
PDF Data Extraction Tool
Extracts core functionality data from PDF documents and exports to Excel
"""

import os
import sys
import re
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    import fitz  # PyMuPDF
except ImportError as e:
    print(f"Error importing PDF libraries: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)


class PDFExtractor:
    """Main class for extracting data from PDF documents"""
    
    def __init__(self, pdf_directory: str = "pdfs", output_file: str = "extracted_data.xlsx"):
        self.pdf_directory = Path(pdf_directory)
        self.output_file = output_file
        self.extracted_data = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for data extraction
        self.patterns = {
            'product_name': [
                r'Product\s*Name[:\s]+([^\n\r]+)',
                r'Product[:\s]+([^\n\r]+)',
                r'Material[:\s]+([^\n\r]+)',
                r'Chemical\s*Name[:\s]+([^\n\r]+)'
            ],
            'cas_number': [
                r'CAS[:\s#]*([0-9-]+)',
                r'CAS\s*Number[:\s]*([0-9-]+)',
                r'(\d{2,7}-\d{2}-\d)'
            ],
            'hazard_classification': [
                r'Hazard\s*Classification[:\s]*([^\n\r]+)',
                r'GHS\s*Classification[:\s]*([^\n\r]+)',
                r'Classification[:\s]*([^\n\r]+)'
            ],
            'safety_precautions': [
                r'Precautionary\s*Statement[s]?[:\s]*([^\n\r]+)',
                r'Safety\s*Precaution[s]?[:\s]*([^\n\r]+)',
                r'First\s*Aid[:\s]*([^\n\r]+)'
            ],
            'physical_properties': [
                r'Physical\s*State[:\s]*([^\n\r]+)',
                r'Appearance[:\s]*([^\n\r]+)',
                r'Color[:\s]*([^\n\r]+)',
                r'Odor[:\s]*([^\n\r]+)'
            ],
            'chemical_composition': [
                r'Composition[:\s]*([^\n\r]+)',
                r'Ingredient[s]?[:\s]*([^\n\r]+)',
                r'Component[s]?[:\s]*([^\n\r]+)'
            ],
            'manufacturer': [
                r'Manufacturer[:\s]*([^\n\r]+)',
                r'Company[:\s]*([^\n\r]+)',
                r'Supplier[:\s]*([^\n\r]+)'
            ],
            'date': [
                r'Date[:\s]*([0-9/\-\.]+)',
                r'Revision\s*Date[:\s]*([0-9/\-\.]+)',
                r'Issue\s*Date[:\s]*([0-9/\-\.]+)'
            ]
        }

    def extract_text_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction failed for {pdf_path}: {e}")
            return ""

    def extract_text_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber (better for tables)"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Extract tables if present
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
            return text
        except Exception as e:
            self.logger.error(f"pdfplumber extraction failed for {pdf_path}: {e}")
            return ""

    def extract_text_pymupdf(self, pdf_path: Path) -> str:
        """Extract text using PyMuPDF (good for complex layouts)"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            self.logger.error(f"PyMuPDF extraction failed for {pdf_path}: {e}")
            return ""

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text using multiple methods for best results"""
        text_methods = [
            ("pdfplumber", self.extract_text_pdfplumber),
            ("PyMuPDF", self.extract_text_pymupdf),
            ("PyPDF2", self.extract_text_pypdf2)
        ]
        
        best_text = ""
        for method_name, method in text_methods:
            try:
                text = method(pdf_path)
                if len(text) > len(best_text):
                    best_text = text
                    self.logger.info(f"Best extraction method for {pdf_path.name}: {method_name}")
            except Exception as e:
                self.logger.warning(f"{method_name} failed for {pdf_path}: {e}")
                continue
        
        return best_text

    def extract_data_from_text(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract structured data from text using regex patterns"""
        data = {
            'filename': filename,
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Clean text for better pattern matching
        clean_text = re.sub(r'\s+', ' ', text)
        
        for field, patterns in self.patterns.items():
            found_value = None
            for pattern in patterns:
                matches = re.findall(pattern, clean_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    # Take the first non-empty match
                    for match in matches:
                        if match and match.strip():
                            found_value = match.strip()
                            break
                    if found_value:
                        break
            
            data[field] = found_value if found_value else "Not Found"
        
        # Extract additional metadata
        data['word_count'] = len(text.split())
        data['character_count'] = len(text)
        
        # Try to identify document type
        doc_type = self.identify_document_type(text, filename)
        data['document_type'] = doc_type
        
        return data

    def identify_document_type(self, text: str, filename: str) -> str:
        """Identify the type of document based on content and filename"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        if 'sds' in filename_lower or 'safety data sheet' in text_lower:
            return 'Safety Data Sheet'
        elif 'msds' in filename_lower or 'material safety data sheet' in text_lower:
            return 'Material Safety Data Sheet'
        elif 'technical' in filename_lower or 'specification' in text_lower:
            return 'Technical Specification'
        elif 'certificate' in filename_lower or 'analysis' in text_lower:
            return 'Certificate of Analysis'
        elif 'product' in filename_lower and 'data' in filename_lower:
            return 'Product Data Sheet'
        else:
            return 'Unknown Document Type'

    def process_single_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Process a single PDF file"""
        self.logger.info(f"Processing: {pdf_path.name}")
        
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text.strip():
                self.logger.warning(f"No text extracted from {pdf_path.name}")
                return {
                    'filename': pdf_path.name,
                    'error': 'No text could be extracted',
                    'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Extract structured data
            data = self.extract_data_from_text(text, pdf_path.name)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error processing {pdf_path.name}: {e}")
            return {
                'filename': pdf_path.name,
                'error': str(e),
                'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """Process all PDF files in the directory"""
        if not self.pdf_directory.exists():
            self.logger.error(f"PDF directory '{self.pdf_directory}' does not exist")
            return []
        
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in '{self.pdf_directory}'")
            return []
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        extracted_data = []
        for pdf_file in pdf_files:
            data = self.process_single_pdf(pdf_file)
            extracted_data.append(data)
        
        return extracted_data

    def export_to_excel(self, data: List[Dict[str, Any]]) -> bool:
        """Export extracted data to Excel file"""
        try:
            if not data:
                self.logger.error("No data to export")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Create Excel writer with multiple sheets
            with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
                # Main data sheet
                df.to_excel(writer, sheet_name='Extracted_Data', index=False)
                
                # Summary sheet
                summary_data = {
                    'Total_Files_Processed': len(data),
                    'Successful_Extractions': len([d for d in data if 'error' not in d]),
                    'Failed_Extractions': len([d for d in data if 'error' in d]),
                    'Document_Types': df['document_type'].value_counts().to_dict() if 'document_type' in df.columns else {},
                    'Export_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                summary_df = pd.DataFrame([summary_data])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Document types breakdown
                if 'document_type' in df.columns:
                    doc_types_df = df['document_type'].value_counts().reset_index()
                    doc_types_df.columns = ['Document_Type', 'Count']
                    doc_types_df.to_excel(writer, sheet_name='Document_Types', index=False)
            
            self.logger.info(f"Data successfully exported to {self.output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            return False

    def run(self) -> bool:
        """Main execution method"""
        self.logger.info("Starting PDF data extraction process")
        
        # Process all PDFs
        self.extracted_data = self.process_all_pdfs()
        
        if not self.extracted_data:
            self.logger.error("No data extracted from any PDF files")
            return False
        
        # Export to Excel
        success = self.export_to_excel(self.extracted_data)
        
        if success:
            self.logger.info(f"Process completed successfully. Output: {self.output_file}")
        else:
            self.logger.error("Process completed with errors")
        
        return success


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract data from PDF documents to Excel')
    parser.add_argument('--pdf-dir', default='pdfs', help='Directory containing PDF files')
    parser.add_argument('--output', default='extracted_data.xlsx', help='Output Excel file name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create extractor and run
    extractor = PDFExtractor(args.pdf_dir, args.output)
    success = extractor.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()