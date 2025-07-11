#!/usr/bin/env python3
"""
Email Analyzer Module
Handles flexible prompt-based email analysis
"""

import re
import logging
from typing import Dict, List, Tuple, Optional

from config import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class EmailAnalyzer:
    """Class for analyzing emails based on flexible prompts"""
    
    def __init__(self):
        self.conditions = []
        self.actions = {}
    
    def parse_prompt(self, prompt: str) -> Dict:
        """Parse user prompt to extract conditions and actions"""
        try:
            # Convert to lowercase for easier parsing
            prompt_lower = prompt.lower()
            
            # Initialize result
            result = {
                'conditions': [],
                'actions': {
                    'pass_label': 'To be Reviewed',
                    'fail_label': 'To be Deleted'
                }
            }
            
            # Parse conditions
            self._parse_conditions(prompt_lower, result)
            
            # Parse actions
            self._parse_actions(prompt_lower, result)
            
            logger.info(f"Parsed prompt - Conditions: {result['conditions']}, Actions: {result['actions']}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing prompt: {e}")
            return {'conditions': [], 'actions': {}}
    
    def _parse_conditions(self, prompt: str, result: Dict):
        """Parse conditions from prompt"""
        conditions = []
        
        # Check for subject conditions
        if 'subject' in prompt:
            if 'subject exists' in prompt or 'subject not empty' in prompt:
                conditions.append({'type': 'subject_exists', 'value': True})
            elif 'subject contains' in prompt:
                # Extract text after "subject contains"
                match = re.search(r'subject contains ["\']([^"\']+)["\']', prompt)
                if match:
                    conditions.append({'type': 'subject_contains', 'value': match.group(1)})
        
        # Check for body conditions
        if 'body' in prompt:
            if 'body exists' in prompt or 'body not empty' in prompt:
                conditions.append({'type': 'body_exists', 'value': True})
            elif 'body contains' in prompt:
                # Extract text after "body contains" - handle both quoted and unquoted text
                match = re.search(r'body contains ["\']([^"\']+)["\']', prompt)
                if not match:
                    # Try to extract unquoted text after "body contains"
                    match = re.search(r'body contains ([^,\s]+(?:\s+[^,\s]+)*)', prompt)
                if match:
                    text = match.group(1)
                    # Handle single quotes within the pattern (like 'XYZ' and 'ABC')
                    text = re.sub(r"'([^']+)'", r'[a-zA-Z]+', text)  # Replace 'XYZ' with regex pattern
                    # Make the pattern more flexible by allowing flexible whitespace
                    text = re.sub(r'\s+', r'\\s+', text)
                    # Make common words like "city" optional
                    text = re.sub(r'\\s+city', r'\\s+[a-zA-Z]*', text)
                    conditions.append({'type': 'body_contains', 'value': text})
        
        # Check for PDF attachment conditions
        if 'pdf' in prompt or 'attachment' in prompt:
            if 'pdf exists' in prompt or 'has pdf' in prompt or 'has attachment' in prompt:
                conditions.append({'type': 'pdf_exists', 'value': True})
        
        # Check for resume/skill conditions
        if 'skilled in' in prompt or 'skill' in prompt:
            # Extract skills mentioned
            skill_match = re.search(r'skilled in (\w+)', prompt)
            if skill_match:
                conditions.append({'type': 'resume_skill', 'value': skill_match.group(1)})
        
        result['conditions'] = conditions
    
    def _parse_actions(self, prompt: str, result: Dict):
        """Parse actions from prompt"""
        # Look for custom labels
        if 'label' in prompt and 'with' in prompt:
            # Extract pass label
            pass_match = re.search(r'label.*?with.*?(\w+(?:\s+\w+)*)', prompt)
            if pass_match:
                result['actions']['pass_label'] = pass_match.group(1).strip()
            
            # Extract fail label (usually after "else" or "otherwise")
            fail_match = re.search(r'else.*?(\w+(?:\s+\w+)*)', prompt)
            if fail_match:
                result['actions']['fail_label'] = fail_match.group(1).strip()
        
        # Handle "mark as" or "mark all" patterns
        elif 'mark' in prompt:
            # Extract what to mark as
            mark_match = re.search(r'mark.*?as\s+([^,\s]+(?:\s+[^,\s]+)*)', prompt)
            if mark_match:
                mark_label = mark_match.group(1).strip()
                # If it's "to be deleted", set as fail label
                if 'deleted' in mark_label.lower():
                    result['actions']['fail_label'] = mark_label
                    result['actions']['pass_label'] = 'To be Reviewed'  # Default pass label
                else:
                    result['actions']['pass_label'] = mark_label
                    result['actions']['fail_label'] = 'To be Deleted'  # Default fail label
    
    def check_email_conditions(self, email_data: Dict, conditions: List[Dict]) -> bool:
        """Check if email meets all conditions"""
        try:
            for condition in conditions:
                if not self._check_single_condition(email_data, condition):
                    return False
            return True
            
        except Exception as e:
            logger.error(f"Error checking email conditions: {e}")
            return False
    
    def _check_single_condition(self, email_data: Dict, condition: Dict) -> bool:
        """Check a single condition against email data"""
        condition_type = condition['type']
        value = condition['value']
        
        try:
            if condition_type == 'subject_exists':
                return self._check_subject_exists(email_data)
            
            elif condition_type == 'subject_contains':
                return self._check_subject_contains(email_data, value)
            
            elif condition_type == 'body_exists':
                return self._check_body_exists(email_data)
            
            elif condition_type == 'body_contains':
                return self._check_body_contains(email_data, value)
            
            elif condition_type == 'pdf_exists':
                return self._check_pdf_exists(email_data)
            
            elif condition_type == 'resume_skill':
                return self._check_resume_skill(email_data, value)
            
            else:
                logger.warning(f"Unknown condition type: {condition_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking condition {condition_type}: {e}")
            return False
    
    def _check_subject_exists(self, email_data: Dict) -> bool:
        """Check if email has a subject"""
        headers = email_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name', '').lower() == 'subject':
                subject = header.get('value', '').strip()
                return len(subject) > 0
        return False
    
    def _check_subject_contains(self, email_data: Dict, text: str) -> bool:
        """Check if email subject contains specific text"""
        headers = email_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name', '').lower() == 'subject':
                subject = header.get('value', '').lower()
                return text.lower() in subject
        return False
    
    def _check_body_exists(self, email_data: Dict) -> bool:
        """Check if email has a body"""
        # Check for body in payload
        body = self._extract_email_body(email_data)
        return len(body.strip()) > 0
    
    def _check_body_contains(self, email_data: Dict, text: str) -> bool:
        """Check if email body contains specific text with placeholder support"""
        body = self._extract_email_body(email_data).lower()
        search_text = text.lower()
        
        try:
            # Use regex to match the pattern (text already contains regex patterns from parsing)
            match = re.search(search_text, body)
            logger.info(f"Body check - Pattern: '{search_text}', Body: '{body[:100]}...', Match: {bool(match)}")
            return bool(match)
        except re.error:
            # Fallback to simple string matching if regex fails
            logger.info(f"Body check - Fallback - Search: '{search_text}', Body: '{body[:100]}...', Match: {search_text in body}")
            return search_text in body
    
    def _check_pdf_exists(self, email_data: Dict) -> bool:
        """Check if email has PDF attachments"""
        parts = email_data.get('payload', {}).get('parts', [])
        for part in parts:
            filename = part.get('filename', '').lower()
            if filename.endswith('.pdf'):
                return True
        return False
    
    def _check_resume_skill(self, email_data: Dict, skill: str) -> bool:
        """Check if resume contains specific skill (requires PDF processing)"""
        # This would need to be implemented with PDF text extraction
        # For now, return True as placeholder
        return True
    
    def _extract_email_body(self, email_data: Dict) -> str:
        """Extract email body text"""
        try:
            body = ""
            
            # Check for body in payload
            if 'payload' in email_data:
                payload = email_data['payload']
                
                # Check for body in parts
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part.get('mimeType') == 'text/plain':
                            if 'data' in part.get('body', {}):
                                import base64
                                body_data = part['body']['data']
                                body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        elif part.get('mimeType') == 'text/html':
                            # Also check HTML parts for text content
                            if 'data' in part.get('body', {}):
                                import base64
                                body_data = part['body']['data']
                                html_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                                # Simple HTML tag removal
                                import re
                                html_content = re.sub(r'<[^>]+>', '', html_content)
                                body += html_content
                
                # Check for body directly in payload
                elif 'body' in payload and 'data' in payload['body']:
                    import base64
                    body_data = payload['body']['data']
                    body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            return body.strip()
            
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            return "" 