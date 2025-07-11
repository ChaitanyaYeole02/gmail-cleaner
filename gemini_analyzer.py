#!/usr/bin/env python3
"""
Gemini-based Email Analyzer
Uses Google Gemini API for natural language understanding of prompts and email categorization
"""

import json
import logging
import time
from typing import Dict, List, Optional
import google.generativeai as genai

from config import LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Class for Gemini-based email analysis"""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite-preview-06-17",
            generation_config=genai.GenerationConfig(
                temperature=0,         # 0 → most deterministic
                top_p=1.0,             # optional; shown for completeness
            ),
        )
    
    def categorize_prompt(self, prompt: str) -> List[Dict]:
        """Categorize user prompt into structured rules"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                system_prompt = """
You are an email categorization expert. Given a user's prompt, create ONLY the categorization rules that are explicitly mentioned.

IMPORTANT: 
1. Do NOT create additional "catch-all" or "else" rules unless the user explicitly asks for them.
2. Understand the PATTERN and MEANING of the prompt, not just exact text.
3. If the user says "I am XYZ from ABC city", understand this means "I am [any name] from [any city]" - it's a pattern where XYZ and ABC are placeholders.
4. Convert patterns into intelligent matching rules that understand the meaning.
5. Use EXACT case matching for label names as specified in the prompt.

For each rule, specify:
- Subject: ['Exists', 'Does not Exist', 'Contains <text>', 'Does not contain <text>', 'Starts with <text>', 'Ends with <text>']
- Body: ['Exists', 'Does not Exist', 'Contains <text>', 'Does not contain <text>', 'Starts with <text>', 'Ends with <text>', 'Contains pattern <description>']
- PDF: ['Exists', 'Does not Exist', 'Contains skill <skill>', 'Does not contain skill <skill>']
- Label Action: ['Label name'] - Use EXACT case as specified in the prompt

Examples:
- "Mark emails with body containing 'I am XYZ from ABC city' as To be Deleted" → Understand as "body contains pattern 'I am [name] from [city]'"
- "Label emails with body starting with 'Hello, I am' as To be Reviewed" → Use "Starts with" condition
- "Mark emails with PDF containing Java skills as To be Reviewed" → Use exact skill name

Return a JSON array of rules.
"""

                user_prompt = f"""
Please categorize this prompt into rules: "{prompt}"

IMPORTANT: 
1. Only create rules that are explicitly mentioned in the prompt. Do NOT add "else" or "catch-all" rules unless the user specifically asks for them.
2. Understand the PATTERN and MEANING of the prompt. If the user uses XYZ, ABC, etc., understand these as placeholders for any value.
3. Convert patterns into intelligent matching rules.
4. For complex conditions, create separate rules for each specific case mentioned.
5. If the user mentions "no subject and no body", create a rule with Subject: ["Does not Exist"] and Body: ["Does not Exist"].
6. If the user mentions "professional and project based", understand this means emails that contain:
   - Professional language (Dear, Hiring Manager, experience, skills, etc.)
   - Project mentions (built, created, developed, etc.)
   - Technical skills (Python, Java, React, etc.)
   - Years of experience
   - Achievements or certifications
   This is the OPPOSITE of simple introductions like "I am [name] from [city]"
7. Use EXACT case for label names as specified in the prompt (e.g., "To be Deleted" not "To be deleted")

Return ONLY a valid JSON array with rules like this (no markdown formatting, no extra text):
[
    {{
        "Subject": ["Does not Exist"],
        "Body": ["Does not Exist"],
        "Label Action": ["To be Deleted"]
    }},
    {{
        "Body": ["Contains pattern", "I am [name] from [city]"],
        "Label Action": ["To be Deleted"]
    }},
    {{
        "Body": ["Contains pattern", "professional and project based"],
        "Label Action": ["To be Reviewed"]
    }}
]

If the user says "else" or "otherwise", then create additional rules.

IMPORTANT: Return ONLY the JSON array, no other text or formatting. Understand patterns and placeholders intelligently. Use EXACT case for label names.
"""

                response = self.model.generate_content([system_prompt, user_prompt])
                result = response.text.strip()
                
                # Parse JSON response
                try:
                    # Clean up the response - remove any markdown formatting
                    cleaned_result = result.strip()
                    if cleaned_result.startswith('```json'):
                        cleaned_result = cleaned_result[7:]
                    if cleaned_result.endswith('```'):
                        cleaned_result = cleaned_result[:-3]
                    cleaned_result = cleaned_result.strip()
                    
                    logger.info(f"Cleaned response: {cleaned_result}")
                    
                    rules = json.loads(cleaned_result)
                    logger.info(f"Successfully categorized prompt into {len(rules)} rules")
                    return rules
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Gemini response as JSON: {e}")
                    logger.error(f"Original response: {result}")
                    logger.error(f"Cleaned response: {cleaned_result}")
                    
                    # Try to extract JSON from the response if it's wrapped in text
                    try:
                        import re
                        json_match = re.search(r'\[.*\]', result, re.DOTALL)
                        if json_match:
                            extracted_json = json_match.group(0)
                            logger.info(f"Extracted JSON: {extracted_json}")
                            rules = json.loads(extracted_json)
                            logger.info(f"Successfully parsed extracted JSON into {len(rules)} rules")
                            return rules
                    except Exception as extract_error:
                        logger.error(f"Failed to extract JSON: {extract_error}")
                    
                    return []
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries} retries. Please wait a few minutes and try again.")
                        return []
                else:
                    logger.error(f"Error categorizing prompt with Gemini: {e}")
                    return []
        
        return []
    
    def categorize_email(self, email_data: Dict, rules: List[Dict]) -> Optional[str]:
        """Categorize an email based on the rules"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # print("email_data", email_data)
                # Extract email components
                subject = self._extract_subject(email_data)
                body = self._extract_body(email_data)
                has_pdf = self._has_pdf_attachment(email_data)
                
                system_prompt = """
You are an email categorization expert. Given an email's subject, body, and PDF status, determine which rule it matches.

For each rule, check:
- Subject conditions (Exists, Does not Exist, Contains, Does not contain, Starts with, Ends with)
- Body conditions (Exists, Does not Exist, Contains, Does not contain, Starts with, Ends with, Contains pattern)
- PDF conditions (Exists, Does not Exist, Contains skill, Does not contain skill)

IMPORTANT: 
1. Only return a label if the email matches one of the rules. If no rules match, return "NO_MATCH".
2. For "Contains" conditions, check if the email text contains the specified text (case-insensitive).
3. For "Contains pattern" conditions, understand the pattern meaning:
   - "I am [name] from [city]" means the email contains "I am" followed by any name and "from" followed by any city
   - "professional and project based" means the email contains:
     * Professional language (Dear, Hiring Manager, experience, skills, etc.)
     * Project mentions (built, created, developed, etc.)
     * Technical skills (Python, Java, React, etc.)
     * Years of experience
     * Achievements or certifications
     This is the OPPOSITE of simple introductions like "I am [name] from [city]"
   - "Starts with" checks if the text begins with the specified pattern
   - "Ends with" checks if the text ends with the specified pattern
4. Use intelligent pattern matching, not just exact text comparison.
5. Check rules in order - first matching rule wins.
6. Use EXACT case matching for label names.

Return the label action for the matching rule, or "NO_MATCH" if no rules match.
"""

                user_prompt = f"""
Email to categorize:
Subject: "{subject}"
Body: "{body}"
Has PDF: {has_pdf}

Rules to match against:
{json.dumps(rules, indent=2)}

IMPORTANT: For "Contains pattern" rules, check if the email body matches the pattern:
- Pattern "I am [name] from [city]" means the email should contain "I am" followed by any text, then "from" followed by any text
- The email body "{body}" should be checked against this pattern

Return only the label action (e.g., "To be reviewed", "To be deleted") or "NO_MATCH".
"""

                response = self.model.generate_content([system_prompt, user_prompt])
                result = response.text.strip()
                
                logger.debug(f"Gemini categorization result: {result}")
                
                if result == "NO_MATCH":
                    logger.debug("Email categorized as NO_MATCH")
                    return None
                else:
                    logger.info(f"Email categorized as: {result}")
                    return result
                    
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries} retries. Please wait a few minutes and try again.")
                        return None
                else:
                    logger.error(f"Error categorizing email with Gemini: {e}")
                    return None
        
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
                
                # Handle nested parts structure (like multipart/alternative)
                def extract_from_parts(parts):
                    nonlocal body
                    for part in parts:
                        if part.get('mimeType') == 'text/plain':
                            if 'data' in part.get('body', {}):
                                import base64
                                body_data = part['body']['data']
                                logger.debug(f"Decoding text/plain data: {body_data[:50]}...")
                                body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        elif part.get('mimeType') == 'text/html':
                            if 'data' in part.get('body', {}):
                                import base64
                                body_data = part['body']['data']
                                html_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                                import re
                                html_content = re.sub(r'<[^>]+>', '', html_content)
                                body += html_content
                        elif part.get('mimeType') == 'multipart/alternative':
                            # Handle nested multipart structure
                            if 'parts' in part:
                                extract_from_parts(part['parts'])
                
                if 'parts' in payload:
                    extract_from_parts(payload['parts'])
                elif 'body' in payload and 'data' in payload['body']:
                    import base64
                    body_data = payload['body']['data']
                    body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
            
            logger.debug(f"Extracted body: {body[:100]}...")
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