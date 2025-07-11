#!/usr/bin/env python3
"""
Resume Analyzer Module
Handles resume qualification and analysis logic
"""

import logging
from typing import List

from config import (
    MATCH_THRESHOLD, 
    MIN_KEYWORD_LENGTH, 
    COMMON_WORDS, 
    INDUSTRY_KEYWORDS,
    LOG_LEVEL, 
    LOG_FORMAT
)
from .pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """Class for analyzing resumes and determining qualification"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    def check_resume_qualification(self, pdf_text: str, search_criteria: str) -> bool:
        """Check if resume qualifies based on search criteria"""
        try:
            # Convert search criteria to lowercase for matching
            search_criteria = search_criteria.lower()
            
            # Extract keywords from search criteria
            keywords = search_criteria.split()
            
            # Remove common words and short words
            keywords = [word for word in keywords if word not in COMMON_WORDS and len(word) >= MIN_KEYWORD_LENGTH]
            
            # Expand keywords using industry mappings
            expanded_keywords = self.pdf_processor.expand_keywords_with_industry_mappings(keywords, INDUSTRY_KEYWORDS)
            
            # Calculate match percentage
            match_percentage = self.pdf_processor.calculate_match_percentage(pdf_text, expanded_keywords)
            
            # Consider qualified if threshold is met
            qualified = match_percentage >= MATCH_THRESHOLD
            
            logger.info(f"Resume analysis - Keywords: {expanded_keywords}, Match percentage: {match_percentage:.2%}, Qualified: {qualified}")
            
            return qualified
            
        except Exception as e:
            logger.error(f"Error checking resume qualification: {e}")
            return False
    
    def analyze_resume_content(self, pdf_text: str, search_criteria: str) -> dict:
        """Analyze resume content and return detailed analysis"""
        try:
            search_criteria_lower = search_criteria.lower()
            keywords = search_criteria_lower.split()
            
            # Remove common words and short words
            keywords = [word for word in keywords if word not in COMMON_WORDS and len(word) >= MIN_KEYWORD_LENGTH]
            
            # Expand keywords using industry mappings
            expanded_keywords = self.pdf_processor.expand_keywords_with_industry_mappings(keywords, INDUSTRY_KEYWORDS)
            
            # Find matching keywords
            matching_keywords = []
            for keyword in expanded_keywords:
                if keyword in pdf_text:
                    matching_keywords.append(keyword)
            
            # Calculate match percentage
            match_percentage = len(matching_keywords) / len(expanded_keywords) if expanded_keywords else 0
            qualified = match_percentage >= MATCH_THRESHOLD
            
            return {
                'qualified': qualified,
                'match_percentage': match_percentage,
                'total_keywords': len(expanded_keywords),
                'matching_keywords': matching_keywords,
                'missing_keywords': [kw for kw in expanded_keywords if kw not in matching_keywords],
                'threshold': MATCH_THRESHOLD
            }
            
        except Exception as e:
            logger.error(f"Error analyzing resume content: {e}")
            return {
                'qualified': False,
                'match_percentage': 0.0,
                'total_keywords': 0,
                'matching_keywords': [],
                'missing_keywords': [],
                'threshold': MATCH_THRESHOLD,
                'error': str(e)
            } 