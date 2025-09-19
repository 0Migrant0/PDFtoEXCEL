#!/usr/bin/env python3
"""
Demo script for PDF Data Extractor
Creates sample data to demonstrate the functionality
"""

import pandas as pd
from datetime import datetime
import os

def create_demo_data():
    """Create sample extracted data to demonstrate Excel output format"""
    
    # Sample data that would be extracted from PDFs
    sample_data = [
        {
            'filename': '10 ppm Gas Oil - SDS 1.pdf',
            'document_type': 'Safety Data Sheet',
            'product_name': '10 ppm Gas Oil',
            'cas_number': '68334-30-5',
            'hazard_classification': 'Flammable Liquid Category 3',
            'safety_precautions': 'Keep away from heat, sparks, open flames',
            'physical_properties': 'Liquid, Clear to pale yellow',
            'chemical_composition': 'Hydrocarbon mixture',
            'manufacturer': 'Industrial Chemical Company',
            'date': '2023-01-15',
            'word_count': 2500,
            'character_count': 15000,
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'filename': 'ABF SDS 1.pdf',
            'document_type': 'Safety Data Sheet',
            'product_name': 'ABF Chemical Solution',
            'cas_number': '7732-18-5',
            'hazard_classification': 'Not classified as hazardous',
            'safety_precautions': 'Use appropriate personal protective equipment',
            'physical_properties': 'Clear liquid, odorless',
            'chemical_composition': 'Water-based solution',
            'manufacturer': 'ABF Industries Ltd.',
            'date': '2023-03-22',
            'word_count': 1800,
            'character_count': 11000,
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'filename': 'Cement Class G US-LA_ENGLISH_PP_100021 1.pdf',
            'document_type': 'Technical Specification',
            'product_name': 'Cement Class G',
            'cas_number': '65997-15-1',
            'hazard_classification': 'Eye irritation Category 2A',
            'safety_precautions': 'Avoid contact with eyes and skin',
            'physical_properties': 'Gray powder',
            'chemical_composition': 'Portland cement, silicates',
            'manufacturer': 'Construction Materials Corp',
            'date': '2023-02-10',
            'word_count': 3200,
            'character_count': 19000,
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'filename': 'MB DipSlide - SDS 1.pdf',
            'document_type': 'Safety Data Sheet',
            'product_name': 'MB DipSlide Test Kit',
            'cas_number': 'Not Found',
            'hazard_classification': 'Not classified',
            'safety_precautions': 'Handle with care, wash hands after use',
            'physical_properties': 'Solid test strips',
            'chemical_composition': 'Proprietary test reagents',
            'manufacturer': 'Microbiology Testing Inc.',
            'date': '2023-04-05',
            'word_count': 1200,
            'character_count': 7500,
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Create Excel file with multiple sheets
    output_file = 'demo_extracted_data.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Extracted_Data', index=False)
        
        # Summary sheet
        summary_data = {
            'Total_Files_Processed': len(sample_data),
            'Successful_Extractions': len(sample_data),
            'Failed_Extractions': 0,
            'Document_Types': df['document_type'].value_counts().to_dict(),
            'Export_Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        summary_df = pd.DataFrame([summary_data])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Document types breakdown
        doc_types_df = df['document_type'].value_counts().reset_index()
        doc_types_df.columns = ['Document_Type', 'Count']
        doc_types_df.to_excel(writer, sheet_name='Document_Types', index=False)
    
    print(f"Demo data created successfully!")
    print(f"Output file: {output_file}")
    print(f"Processed {len(sample_data)} sample documents")
    print("\nSample data overview:")
    print(df[['filename', 'document_type', 'product_name']].to_string(index=False))
    
    return output_file

if __name__ == "__main__":
    create_demo_data()