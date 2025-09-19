#!/usr/bin/env python3
"""
Improved PDF Data Extractor with Structured Column Organization
Extracts data from PDFs and organizes it into separate columns for better readability
"""

import os
import re
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import PyPDF2
from datetime import datetime

class ImprovedPDFExtractor:
    def __init__(self, pdf_folder: str = "PDFs", output_file: str = "structured_extracted_data.xlsx"):
        self.pdf_folder = pdf_folder
        self.output_file = output_file
        self.setup_logging()
        
        # Define structured columns for different data categories
        self.columns = {
            'file_info': ['File_Name', 'Extraction_Date', 'Total_Pages'],
            'product_info': ['Product_Name', 'Product_Code', 'Manufacturer', 'Version', 'Revision_Date'],
            'safety_info': ['Hazard_Classification', 'Signal_Word', 'Precautionary_Statements', 'Emergency_Contact'],
            'physical_properties': ['Physical_State', 'Color', 'Odor', 'pH', 'Melting_Point', 'Boiling_Point', 'Density', 'Solubility'],
            'composition': ['Chemical_Name', 'CAS_Number', 'Concentration', 'Formula'],
            'handling': ['Storage_Conditions', 'Handling_Precautions', 'Personal_Protection'],
            'regulatory': ['Regulatory_Information', 'Transport_Classification', 'UN_Number'],
            'other_data': ['Additional_Information']
        }
        
        # All columns flattened
        self.all_columns = []
        for category in self.columns.values():
            self.all_columns.extend(category)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pdf_extraction_improved.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""

    def parse_structured_data(self, text: str, filename: str) -> Dict[str, Any]:
        """Parse text and extract structured data into appropriate categories"""
        data = {col: "" for col in self.all_columns}
        
        # File information
        data['File_Name'] = filename
        data['Extraction_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Count pages (estimate from text length)
        estimated_pages = max(1, len(text) // 3000)  # Rough estimate
        data['Total_Pages'] = str(estimated_pages)
        
        # Product information extraction
        self._extract_product_info(text, data)
        
        # Safety information extraction
        self._extract_safety_info(text, data)
        
        # Physical properties extraction
        self._extract_physical_properties(text, data)
        
        # Composition extraction
        self._extract_composition(text, data)
        
        # Handling information extraction
        self._extract_handling_info(text, data)
        
        # Regulatory information extraction
        self._extract_regulatory_info(text, data)
        
        # Additional information
        self._extract_additional_info(text, data)
        
        return data

    def _extract_product_info(self, text: str, data: Dict[str, Any]):
        """Extract product information"""
        # Product name patterns
        product_patterns = [
            r'Product\s*[Nn]ame\s*:?\s*([^\n\r]+)',
            r'Trade\s*[Nn]ame\s*:?\s*([^\n\r]+)',
            r'Commercial\s*[Nn]ame\s*:?\s*([^\n\r]+)',
            r'Product\s*[Ii]dentifier\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in product_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Product_Name']:
                data['Product_Name'] = match.group(1).strip()
                break
        
        # Product code patterns
        code_patterns = [
            r'Product\s*[Cc]ode\s*:?\s*([^\n\r]+)',
            r'Item\s*[Nn]umber\s*:?\s*([^\n\r]+)',
            r'Part\s*[Nn]umber\s*:?\s*([^\n\r]+)',
            r'SKU\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Product_Code']:
                data['Product_Code'] = match.group(1).strip()
                break
        
        # Manufacturer patterns
        manufacturer_patterns = [
            r'Manufacturer\s*:?\s*([^\n\r]+)',
            r'Company\s*[Nn]ame\s*:?\s*([^\n\r]+)',
            r'Supplier\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in manufacturer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Manufacturer']:
                data['Manufacturer'] = match.group(1).strip()
                break
        
        # Version and revision date
        version_match = re.search(r'Version\s*:?\s*([^\n\r]+)', text, re.IGNORECASE)
        if version_match:
            data['Version'] = version_match.group(1).strip()
        
        revision_patterns = [
            r'Revision\s*[Dd]ate\s*:?\s*([^\n\r]+)',
            r'Date\s*of\s*[Rr]evision\s*:?\s*([^\n\r]+)',
            r'Last\s*[Uu]pdated\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in revision_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Revision_Date']:
                data['Revision_Date'] = match.group(1).strip()
                break

    def _extract_safety_info(self, text: str, data: Dict[str, Any]):
        """Extract safety information"""
        # Hazard classification
        hazard_patterns = [
            r'Hazard\s*[Cc]lassification\s*:?\s*([^\n\r]+)',
            r'GHS\s*[Cc]lassification\s*:?\s*([^\n\r]+)',
            r'Classification\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in hazard_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Hazard_Classification']:
                data['Hazard_Classification'] = match.group(1).strip()
                break
        
        # Signal word
        signal_patterns = [
            r'Signal\s*[Ww]ord\s*:?\s*([^\n\r]+)',
            r'GHS\s*Signal\s*[Ww]ord\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in signal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Signal_Word']:
                data['Signal_Word'] = match.group(1).strip()
                break
        
        # Precautionary statements
        precautionary_patterns = [
            r'Precautionary\s*[Ss]tatements?\s*:?\s*([^\n\r]+)',
            r'P-[Ss]tatements?\s*:?\s*([^\n\r]+)',
            r'Prevention\s*:?\s*([^\n\r]+)'
        ]
        
        precautionary_statements = []
        for pattern in precautionary_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                precautionary_statements.append(match.group(1).strip())
        
        if precautionary_statements:
            data['Precautionary_Statements'] = " | ".join(precautionary_statements)
        
        # Emergency contact
        emergency_patterns = [
            r'Emergency\s*[Cc]ontact\s*:?\s*([^\n\r]+)',
            r'Emergency\s*[Nn]umber\s*:?\s*([^\n\r]+)',
            r'24\s*[Hh]our\s*[Cc]ontact\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in emergency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Emergency_Contact']:
                data['Emergency_Contact'] = match.group(1).strip()
                break

    def _extract_physical_properties(self, text: str, data: Dict[str, Any]):
        """Extract physical properties"""
        # Physical state
        state_patterns = [
            r'Physical\s*[Ss]tate\s*:?\s*([^\n\r]+)',
            r'Form\s*:?\s*([^\n\r]+)',
            r'Appearance\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in state_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Physical_State']:
                data['Physical_State'] = match.group(1).strip()
                break
        
        # Color
        color_patterns = [
            r'Colo[u]?r\s*:?\s*([^\n\r]+)',
            r'Color\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in color_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Color']:
                data['Color'] = match.group(1).strip()
                break
        
        # Odor
        odor_match = re.search(r'Odo[u]?r\s*:?\s*([^\n\r]+)', text, re.IGNORECASE)
        if odor_match:
            data['Odor'] = odor_match.group(1).strip()
        
        # pH
        ph_patterns = [
            r'pH\s*:?\s*([^\n\r]+)',
            r'pH\s*[Vv]alue\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in ph_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['pH']:
                data['pH'] = match.group(1).strip()
                break
        
        # Melting point
        melting_patterns = [
            r'Melting\s*[Pp]oint\s*:?\s*([^\n\r]+)',
            r'M\.?P\.?\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in melting_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Melting_Point']:
                data['Melting_Point'] = match.group(1).strip()
                break
        
        # Boiling point
        boiling_patterns = [
            r'Boiling\s*[Pp]oint\s*:?\s*([^\n\r]+)',
            r'B\.?P\.?\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in boiling_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Boiling_Point']:
                data['Boiling_Point'] = match.group(1).strip()
                break
        
        # Density
        density_patterns = [
            r'Density\s*:?\s*([^\n\r]+)',
            r'Specific\s*[Gg]ravity\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in density_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Density']:
                data['Density'] = match.group(1).strip()
                break
        
        # Solubility
        solubility_patterns = [
            r'Solubility\s*:?\s*([^\n\r]+)',
            r'Water\s*[Ss]olubility\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in solubility_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Solubility']:
                data['Solubility'] = match.group(1).strip()
                break

    def _extract_composition(self, text: str, data: Dict[str, Any]):
        """Extract composition information"""
        # Chemical names and CAS numbers
        chemical_info = []
        
        # Look for CAS number patterns
        cas_patterns = [
            r'CAS\s*[Nn]umber?\s*:?\s*(\d{1,7}-\d{2}-\d)',
            r'CAS\s*:?\s*(\d{1,7}-\d{2}-\d)',
            r'(\d{1,7}-\d{2}-\d)'
        ]
        
        cas_numbers = []
        for pattern in cas_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                cas_numbers.append(match.group(1))
        
        if cas_numbers:
            data['CAS_Number'] = " | ".join(set(cas_numbers))  # Remove duplicates
        
        # Look for concentration information
        concentration_patterns = [
            r'Concentration\s*:?\s*([^\n\r]+)',
            r'Content\s*:?\s*([^\n\r]+)',
            r'(\d+(?:\.\d+)?\s*%)',
            r'(\d+(?:\.\d+)?\s*wt\.?\s*%)'
        ]
        
        concentrations = []
        for pattern in concentration_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                concentrations.append(match.group(1).strip())
        
        if concentrations:
            data['Concentration'] = " | ".join(concentrations[:5])  # Limit to first 5
        
        # Chemical formula patterns
        formula_patterns = [
            r'Formula\s*:?\s*([^\n\r]+)',
            r'Molecular\s*[Ff]ormula\s*:?\s*([^\n\r]+)',
            r'Chemical\s*[Ff]ormula\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in formula_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Formula']:
                data['Formula'] = match.group(1).strip()
                break

    def _extract_handling_info(self, text: str, data: Dict[str, Any]):
        """Extract handling and storage information"""
        # Storage conditions
        storage_patterns = [
            r'Storage\s*[Cc]onditions?\s*:?\s*([^\n\r]+)',
            r'Storage\s*:?\s*([^\n\r]+)',
            r'Store\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in storage_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Storage_Conditions']:
                data['Storage_Conditions'] = match.group(1).strip()
                break
        
        # Handling precautions
        handling_patterns = [
            r'Handling\s*[Pp]recautions?\s*:?\s*([^\n\r]+)',
            r'Safe\s*[Hh]andling\s*:?\s*([^\n\r]+)',
            r'Handling\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in handling_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Handling_Precautions']:
                data['Handling_Precautions'] = match.group(1).strip()
                break
        
        # Personal protection
        protection_patterns = [
            r'Personal\s*[Pp]rotection\s*:?\s*([^\n\r]+)',
            r'PPE\s*:?\s*([^\n\r]+)',
            r'Protective\s*[Ee]quipment\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in protection_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Personal_Protection']:
                data['Personal_Protection'] = match.group(1).strip()
                break

    def _extract_regulatory_info(self, text: str, data: Dict[str, Any]):
        """Extract regulatory information"""
        # UN number
        un_patterns = [
            r'UN\s*[Nn]umber\s*:?\s*([^\n\r]+)',
            r'UN\s*:?\s*(\d+)',
            r'United\s*Nations\s*[Nn]umber\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in un_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['UN_Number']:
                data['UN_Number'] = match.group(1).strip()
                break
        
        # Transport classification
        transport_patterns = [
            r'Transport\s*[Cc]lassification\s*:?\s*([^\n\r]+)',
            r'Shipping\s*[Cc]lassification\s*:?\s*([^\n\r]+)',
            r'DOT\s*[Cc]lassification\s*:?\s*([^\n\r]+)'
        ]
        
        for pattern in transport_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data['Transport_Classification']:
                data['Transport_Classification'] = match.group(1).strip()
                break

    def _extract_additional_info(self, text: str, data: Dict[str, Any]):
        """Extract any additional relevant information"""
        # Look for other important information that doesn't fit in specific categories
        additional_patterns = [
            r'Additional\s*[Ii]nformation\s*:?\s*([^\n\r]+)',
            r'Notes?\s*:?\s*([^\n\r]+)',
            r'Remarks?\s*:?\s*([^\n\r]+)',
            r'Other\s*[Ii]nformation\s*:?\s*([^\n\r]+)'
        ]
        
        additional_info = []
        for pattern in additional_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                additional_info.append(match.group(1).strip())
        
        if additional_info:
            data['Additional_Information'] = " | ".join(additional_info)

    def process_pdfs(self) -> pd.DataFrame:
        """Process all PDFs and return structured DataFrame"""
        if not os.path.exists(self.pdf_folder):
            self.logger.error(f"PDF folder '{self.pdf_folder}' not found!")
            return pd.DataFrame()
        
        all_data = []
        pdf_files = [f for f in os.listdir(self.pdf_folder) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in '{self.pdf_folder}'")
            return pd.DataFrame()
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            self.logger.info(f"Processing: {pdf_file}")
            pdf_path = os.path.join(self.pdf_folder, pdf_file)
            
            try:
                # Extract text
                text = self.extract_text_from_pdf(pdf_path)
                if not text.strip():
                    self.logger.warning(f"No text extracted from {pdf_file}")
                    continue
                
                # Parse structured data
                structured_data = self.parse_structured_data(text, pdf_file)
                all_data.append(structured_data)
                
                self.logger.info(f"Successfully processed: {pdf_file}")
                
            except Exception as e:
                self.logger.error(f"Error processing {pdf_file}: {str(e)}")
                continue
        
        if not all_data:
            self.logger.error("No data extracted from any PDF files")
            return pd.DataFrame()
        
        # Create DataFrame with structured columns
        df = pd.DataFrame(all_data)
        
        # Reorder columns for better organization
        column_order = self.all_columns
        df = df.reindex(columns=column_order)
        
        return df

    def save_to_excel(self, df: pd.DataFrame):
        """Save DataFrame to Excel with multiple sheets for different categories"""
        if df.empty:
            self.logger.error("No data to save")
            return
        
        try:
            with pd.ExcelWriter(self.output_file, engine='openpyxl') as writer:
                # Main sheet with all data
                df.to_excel(writer, sheet_name='All_Data', index=False)
                
                # Create separate sheets for each category
                for category_name, columns in self.columns.items():
                    category_data = df[['File_Name'] + [col for col in columns if col in df.columns]]
                    # Only include rows that have some data in this category
                    category_data_filtered = category_data.dropna(how='all', subset=[col for col in columns if col in df.columns])
                    if not category_data_filtered.empty:
                        category_data_filtered.to_excel(writer, sheet_name=category_name.title(), index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Files Processed', 'Files with Product Info', 'Files with Safety Info', 
                              'Files with Physical Properties', 'Files with Composition', 'Files with Handling Info'],
                    'Count': [
                        len(df),
                        len(df[df['Product_Name'].notna() & (df['Product_Name'] != '')]),
                        len(df[df['Hazard_Classification'].notna() & (df['Hazard_Classification'] != '')]),
                        len(df[df['Physical_State'].notna() & (df['Physical_State'] != '')]),
                        len(df[df['CAS_Number'].notna() & (df['CAS_Number'] != '')]),
                        len(df[df['Storage_Conditions'].notna() & (df['Storage_Conditions'] != '')])
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            self.logger.info(f"Data successfully saved to {self.output_file}")
            self.logger.info(f"Total records: {len(df)}")
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {str(e)}")

    def run(self):
        """Main execution method"""
        self.logger.info("Starting improved PDF data extraction...")
        
        # Process PDFs
        df = self.process_pdfs()
        
        if df.empty:
            self.logger.error("No data extracted. Exiting.")
            return
        
        # Save to Excel
        self.save_to_excel(df)
        
        self.logger.info("Extraction completed successfully!")
        
        # Print summary
        print(f"\n{'='*50}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*50}")
        print(f"Files processed: {len(df)}")
        print(f"Output file: {self.output_file}")
        print(f"Columns created: {len(self.all_columns)}")
        print("\nColumn categories:")
        for category, columns in self.columns.items():
            print(f"  - {category.replace('_', ' ').title()}: {len(columns)} columns")
        print(f"{'='*50}\n")


def main():
    """Main function"""
    extractor = ImprovedPDFExtractor()
    extractor.run()


if __name__ == "__main__":
    main()