#!/usr/bin/env python3
"""
PDF Processor Module
Handles PDF text extraction and analysis
"""

import base64
import logging
import io
from typing import List

import PyPDF2

from config import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Class for processing PDF files and extracting text"""
    
    @staticmethod
    def extract_pdf_text(attachment_data: str) -> str:
        """Extract text from PDF attachment"""
        try:
            # Decode base64 attachment
            pdf_data = base64.urlsafe_b64decode(attachment_data)
            pdf_file = io.BytesIO(pdf_data)
            
            # Read PDF
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.lower()  # Convert to lowercase for easier matching
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    @staticmethod
    def extract_keywords_from_text(text: str, common_words: set, min_length: int = 3) -> List[str]:
        """Extract keywords from text, filtering out common words and short words"""
        words = text.lower().split()
        keywords = [word for word in words if word not in common_words and len(word) >= min_length]
        return list(set(keywords))  # Remove duplicates
    
    @staticmethod
    def expand_keywords_with_industry_mappings(keywords: List[str], industry_keywords: dict) -> List[str]:
        """Expand keywords using industry-specific mappings"""
        expanded_keywords = []
        
        for keyword in keywords:
            expanded_keywords.append(keyword)
            # Add related keywords from industry mappings
            for industry, related_keywords in industry_keywords.items():
                if keyword in related_keywords:
                    expanded_keywords.extend(related_keywords)
        
        # Remove duplicates
        return list(set(expanded_keywords))
    
    @staticmethod
    def calculate_match_percentage(pdf_text: str, keywords: List[str]) -> float:
        """Calculate the percentage of keywords that match in the PDF text"""
        if not keywords:
            return 0.0
        
        matches = 0
        for keyword in keywords:
            if keyword in pdf_text:
                matches += 1
        
        return matches / len(keywords) 