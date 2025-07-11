#!/usr/bin/env python3
"""
OpenAI-based Email Analyzer
Uses OpenAI API for natural language understanding of prompts and email categorization
"""

import json
import logging
from typing import Dict, List, Optional
import openai

from config import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class OpenAIAnalyzer:
    """Class for OpenAI-based email analysis"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def categorize_prompt(self, prompt: str) -> List[Dict]:
        """Categorize user prompt into structured rules"""
        try:
            system_prompt = """
You are an email categorization expert. Given a user's prompt, create a list of categorization rules.

For each rule, specify:
- Subject: ['Exists', 'Does not Exist', 'Contains <text>', 'Does not contain <text>']
- Body: ['Exists', 'Does not Exist', 'Contains <text>', 'Does not contain <text>']
- PDF: ['Exists', 'Does not Exist', 'Contains skill <skill>', 'Does not contain skill <skill>']
- Label Action: ['Label name']

Examples:
- "Mark emails with body containing 'I am XYZ from ABC city' as To be deleted"
- "Label all emails with PDF containing Java skills as To be reviewed"
- "Mark emails without subject as To be deleted, else To be reviewed"

Return a JSON array of rules.
"""

            user_prompt = f"""
Please categorize this prompt into rules: "{prompt}"

Return only valid JSON array with rules like:
[
    {{
        "Subject": ["Exists"],
        "Body": ["Contains", "I am XYZ from ABC city"],
        "PDF": ["Exists"],
        "Label Action": ["To be deleted"]
    }},
    {{
        "Subject": ["Exists"],
        "Body": ["Does not contain", "I am XYZ from ABC city"],
        "PDF": ["Exists"],
        "Label Action": ["To be reviewed"]
    }}
]
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                rules = json.loads(result)
                logger.info(f"Successfully categorized prompt into {len(rules)} rules")
                return rules
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                logger.error(f"Response: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error categorizing prompt with OpenAI: {e}")
            return []
    
    def categorize_email(self, email_data: Dict, rules: List[Dict]) -> Optional[str]:
        """Categorize an email based on the rules"""
        try:
            # Extract email components
            subject = self._extract_subject(email_data)
            body = self._extract_body(email_data)
            has_pdf = self._has_pdf_attachment(email_data)
            
            system_prompt = """
You are an email categorization expert. Given an email's subject, body, and PDF status, determine which rule it matches.

For each rule, check:
- Subject conditions (Exists, Does not Exist, Contains, Does not contain)
- Body conditions (Exists, Does not Exist, Contains, Does not contain)
- PDF conditions (Exists, Does not Exist, Contains skill, Does not contain skill)

Return the label action for the matching rule, or "NO_MATCH" if no rules match.
"""

            user_prompt = f"""
Email to categorize:
Subject: "{subject}"
Body: "{body}"
Has PDF: {has_pdf}

Rules to match against:
{json.dumps(rules, indent=2)}

Return only the label action (e.g., "To be reviewed", "To be deleted") or "NO_MATCH".
"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            if result == "NO_MATCH":
                return None
            else:
                logger.info(f"Email categorized as: {result}")
                return result
                
        except Exception as e:
            logger.error(f"Error categorizing email with OpenAI: {e}")
            return None
    
    def _extract_subject(self, email_data: Dict) -> str:
        """Extract email subject"""
        headers = email_data.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name', '').lower() == 'subject':
                return header.get('value', '').strip()
        return ""
    
    def _extract_body(self, email_data: Dict) -> str:
        """Extract email body text"""
        try:
            body = ""
            
            if 'payload' in email_data:
                payload = email_data['payload']
                
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part.get('mimeType') == 'text/plain':
                            if 'data' in part.get('body', {}):
                                import base64
                                body_data = part['body']['data']
                                body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        elif part.get('mimeType') == 'text/html':
                            if 'data' in part.get('body', {}):
                                import base64
                                body_data = part['body']['data']
                                html_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                                import re
                                html_content = re.sub(r'<[^>]+>', '', html_content)
                                body += html_content
                
                elif 'body' in payload and 'data' in payload['body']:
                    import base64
                    body_data = payload['body']['data']
                    body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            return body.strip()
            
        except Exception as e:
            logger.error(f"Error extracting email body: {e}")
            return ""
    
    def _has_pdf_attachment(self, email_data: Dict) -> bool:
        """Check if email has PDF attachments"""
        parts = email_data.get('payload', {}).get('parts', [])
        for part in parts:
            filename = part.get('filename', '').lower()
            if filename.endswith('.pdf'):
                return True
        return False 