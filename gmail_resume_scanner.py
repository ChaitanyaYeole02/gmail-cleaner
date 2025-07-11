import logging
from typing import List, Dict, Tuple

from services import GmailService, ResumeAnalyzer, EmailAnalyzer
from openai_analyzer import OpenAIAnalyzer
from gemini_analyzer import GeminiAnalyzer
from config import *

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class GmailResumeScanner:
    def __init__(self):
        self.gmail_service = GmailService()
        self.resume_analyzer = ResumeAnalyzer()
        self.email_analyzer = EmailAnalyzer()
        
        # Initialize AI analyzers if configured
        self.openai_analyzer = None
        self.gemini_analyzer = None
        
        if USE_OPENAI and OPENAI_API_KEY:
            self.openai_analyzer = OpenAIAnalyzer(OPENAI_API_KEY)
        
        if USE_GEMINI and GEMINI_API_KEY:
            self.gemini_analyzer = GeminiAnalyzer(GEMINI_API_KEY)
    
    def scan_resumes(self, search_criteria: str) -> Tuple[int, int]:
        """Main function to scan resumes and categorize emails"""
        try:
            # Get emails with PDF attachments
            messages = self.gmail_service.search_emails_with_pdf_attachments(PDF_SEARCH_QUERY)
            
            if not messages:
                logger.info("No emails with PDF attachments found")
                return 0, 0
            
            # Limit processing if configured
            if MAX_EMAILS_TO_PROCESS and len(messages) > MAX_EMAILS_TO_PROCESS:
                messages = messages[:MAX_EMAILS_TO_PROCESS]
                logger.info(f"Limited processing to {MAX_EMAILS_TO_PROCESS} emails")
            
            # Create label for unqualified resumes
            label_id = self.gmail_service.create_label_if_not_exists(DELETE_LABEL_NAME)
            if not label_id:
                logger.error("Failed to create label")
                return 0, 0
            
            scanned_count = 0
            labeled_count = 0
            
            for message in messages:
                try:
                    # Check if message has attachments
                    if 'payload' in message and 'parts' in message['payload']:
                        for part in message['payload']['parts']:
                            if part.get('filename', '').lower().endswith('.pdf'):
                                # Get attachment data
                                attachment_id = part['body']['attachmentId']
                                attachment_data = self.gmail_service.get_attachment_data(message['id'], attachment_id)
                                
                                if attachment_data:
                                    # Extract text from PDF
                                    pdf_text = self.resume_analyzer.pdf_processor.extract_pdf_text(attachment_data)
                                    
                                    if pdf_text:
                                        # Check if resume qualifies
                                        qualified = self.resume_analyzer.check_resume_qualification(pdf_text, search_criteria)
                                        
                                        scanned_count += 1
                                        
                                        if not qualified:
                                            # Add to "To Be Deleted" label
                                            self.gmail_service.add_label_to_message(message['id'], label_id)
                                            labeled_count += 1
                                            logger.info(f"Email {message['id']} marked for deletion - Resume does not qualify")
                                        else:
                                            logger.info(f"Email {message['id']} - Resume qualifies")
                                
                                if PROCESS_ONLY_FIRST_PDF:
                                    break  # Only process first PDF attachment
                    
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            return scanned_count, labeled_count
            
        except Exception as e:
            logger.error(f"Error in scan_resumes: {e}")
            return 0, 0
    
    def scan_resumes_with_prompt(self, prompt: str) -> Tuple[int, int, int]:
        """Scan resumes using flexible prompt-based analysis"""
        try:
            # Parse the prompt
            parsed_prompt = self.email_analyzer.parse_prompt(prompt)
            conditions = parsed_prompt['conditions']
            actions = parsed_prompt['actions']
            
            # Get only emails with PDF attachments
            messages = self.gmail_service.search_emails_with_pdf_attachments(PDF_SEARCH_QUERY)
            
            if not messages:
                logger.info("No emails found")
                return 0, 0, 0
            
            # Limit processing if configured
            if MAX_EMAILS_TO_PROCESS and len(messages) > MAX_EMAILS_TO_PROCESS:
                messages = messages[:MAX_EMAILS_TO_PROCESS]
                logger.info(f"Limited processing to {MAX_EMAILS_TO_PROCESS} emails")
            
            # Create labels
            pass_label_id = self.gmail_service.create_label_if_not_exists(actions['pass_label'])
            fail_label_id = self.gmail_service.create_label_if_not_exists(actions['fail_label'])
            
            if not pass_label_id or not fail_label_id:
                logger.error("Failed to create labels")
                return 0, 0, 0
            
            scanned_count = 0
            pass_count = 0
            fail_count = 0
            
            for message in messages:
                try:
                    # Check if email meets all conditions
                    meets_conditions = self.email_analyzer.check_email_conditions(message, conditions)
                    
                    scanned_count += 1
                    
                    # Only process emails that meet the conditions
                    if meets_conditions:
                        # Add the specified label for emails that meet conditions
                        self.gmail_service.add_label_to_message(message['id'], fail_label_id)
                        fail_count += 1
                        logger.info(f"Email {message['id']} - Conditions met, labeled as '{actions['fail_label']}'")
                    # Don't label emails that don't meet conditions - leave them unlabeled
                    
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            return scanned_count, pass_count, fail_count
            
        except Exception as e:
            logger.error(f"Error in scan_resumes_with_prompt: {e}")
            return 0, 0, 0
    
    def scan_resumes_with_openai(self, prompt: str) -> Tuple[int, Dict[str, int]]:
        """Scan resumes using OpenAI-based analysis"""
        try:
            if not self.openai_analyzer:
                logger.error("OpenAI analyzer not configured")
                return 0, {}
            
            # Categorize the prompt into rules
            rules = self.openai_analyzer.categorize_prompt(prompt)
            if not rules:
                logger.error("Failed to categorize prompt")
                return 0, {}
            
            logger.info(f"Categorized prompt into {len(rules)} rules")
            for i, rule in enumerate(rules):
                logger.info(f"Rule {i+1}: {rule}")
            
            # Get emails with PDF attachments
            messages = self.gmail_service.search_emails_with_pdf_attachments(PDF_SEARCH_QUERY)
            
            if not messages:
                logger.info("No emails found")
                return 0, {}
            
            # Limit processing if configured
            if MAX_EMAILS_TO_PROCESS and len(messages) > MAX_EMAILS_TO_PROCESS:
                messages = messages[:MAX_EMAILS_TO_PROCESS]
                logger.info(f"Limited processing to {MAX_EMAILS_TO_PROCESS} emails")
            
            # Track labels and counts
            label_counts = {}
            scanned_count = 0
            
            for message in messages:
                try:
                    # Categorize email using OpenAI
                    label = self.openai_analyzer.categorize_email(message, rules)
                    
                    scanned_count += 1
                    
                    if label:
                        # Create label if it doesn't exist
                        label_id = self.gmail_service.create_label_if_not_exists(label)
                        if label_id:
                            self.gmail_service.add_label_to_message(message['id'], label_id)
                            label_counts[label] = label_counts.get(label, 0) + 1
                            logger.info(f"Email {message['id']} - Categorized as '{label}'")
                        else:
                            logger.error(f"Failed to create label: {label}")
                    else:
                        logger.info(f"Email {message['id']} - No matching rule found")
                    
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            return scanned_count, label_counts
            
        except Exception as e:
            logger.error(f"Error in scan_resumes_with_openai: {e}")
            return 0, {}
    
    def scan_resumes_with_gemini(self, prompt: str) -> Tuple[int, Dict[str, int]]:
        """Scan resumes using Gemini-based analysis"""
        try:
            if not self.gemini_analyzer:
                logger.error("Gemini analyzer not configured")
                return 0, {}
            
            # Categorize the prompt into rules
            rules = self.gemini_analyzer.categorize_prompt(prompt)
            if not rules:
                logger.error("Failed to categorize prompt")
                return 0, {}
            
            logger.info(f"Categorized prompt into {len(rules)} rules")
            for i, rule in enumerate(rules):
                logger.info(f"Rule {i+1}: {rule}")
            
            # Get emails with PDF attachments
            messages = self.gmail_service.search_emails_with_pdf_attachments(PDF_SEARCH_QUERY)
            
            if not messages:
                logger.info("No emails found")
                return 0, {}
            
            # Limit processing if configured
            if MAX_EMAILS_TO_PROCESS and len(messages) > MAX_EMAILS_TO_PROCESS:
                messages = messages[:MAX_EMAILS_TO_PROCESS]
                logger.info(f"Limited processing to {MAX_EMAILS_TO_PROCESS} emails")
            
            # Track labels and counts
            label_counts = {}
            scanned_count = 0
            
            for message in messages:
                try:
                    # Categorize email using Gemini
                    label = self.gemini_analyzer.categorize_email(message, rules)
                    
                    scanned_count += 1
                    
                    if label:
                        # Create label if it doesn't exist
                        label_id = self.gmail_service.create_label_if_not_exists(label)
                        if label_id:
                            self.gmail_service.add_label_to_message(message['id'], label_id)
                            label_counts[label] = label_counts.get(label, 0) + 1
                            logger.info(f"Email {message['id']} - Categorized as '{label}'")
                        else:
                            logger.error(f"Failed to create label: {label}")
                    else:
                        logger.info(f"Email {message['id']} - No matching rule found")
                    
                    # Add delay to respect rate limits (15 requests per minute = 4 seconds between requests)
                    import time
                    time.sleep(4)
                    
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue
            
            return scanned_count, label_counts
            
        except Exception as e:
            logger.error(f"Error in scan_resumes_with_gemini: {e}")
            return 0, {}

def main():
    """Main function to run the resume scanner"""
    print("Gmail Resume Scanner")
    print("=" * 50)
    
    # Get prompt from user
    prompt = input("Enter your analysis prompt (e.g., 'Check if subject exists and body contains 'Hi, I am XYZ' then label with 'To be Reviewed' else 'To be Deleted'): ")
    
    if not prompt.strip():
        print("Prompt cannot be empty!")
        return
    
    try:
        # Initialize scanner
        scanner = GmailResumeScanner()
        
        if not scanner.gmail_service.is_service_available():
            print("Failed to setup Gmail API. Please check your credentials.")
            return
        
        # Check if AI is configured
        if USE_GEMINI and scanner.gemini_analyzer:
            print(f"\n🤖 Using Google Gemini for intelligent categorization...")
            
            # Scan resumes with Gemini
            scanned_count, label_counts = scanner.scan_resumes_with_gemini(prompt)
            
            # Display results
            print("\n" + "=" * 50)
            print("SCANNING RESULTS (Gemini)")
            print("=" * 50)
            print(f"Total emails scanned: {scanned_count}")
            
            if label_counts:
                for label, count in label_counts.items():
                    print(f"Emails labeled as '{label}': {count}")
                
                print(f"\n📊 Summary:")
                for label, count in label_counts.items():
                    print(f"   🏷️  {count} emails → '{label}'")
            else:
                print("No emails were categorized")
                
        elif USE_OPENAI and scanner.openai_analyzer:
            print(f"\n🤖 Using OpenAI for intelligent categorization...")
            
            # Scan resumes with OpenAI
            scanned_count, label_counts = scanner.scan_resumes_with_openai(prompt)
            
            # Display results
            print("\n" + "=" * 50)
            print("SCANNING RESULTS (OpenAI)")
            print("=" * 50)
            print(f"Total emails scanned: {scanned_count}")
            
            if label_counts:
                for label, count in label_counts.items():
                    print(f"Emails labeled as '{label}': {count}")
                
                print(f"\n📊 Summary:")
                for label, count in label_counts.items():
                    print(f"   🏷️  {count} emails → '{label}'")
            else:
                print("No emails were categorized")
                
        else:
            # Use traditional prompt parsing
            parsed_prompt = scanner.email_analyzer.parse_prompt(prompt)
            
            print(f"\nParsed prompt:")
            print(f"Conditions: {parsed_prompt['conditions']}")
            print(f"Actions: {parsed_prompt['actions']}")
            
            print(f"\nScanning emails with prompt: '{prompt}'")
            print("This may take a few minutes...")
            
            # Scan resumes with traditional approach
            scanned_count, pass_count, fail_count = scanner.scan_resumes_with_prompt(prompt)
            
            # Display results
            print("\n" + "=" * 50)
            print("SCANNING RESULTS")
            print("=" * 50)
            print(f"Total emails scanned: {scanned_count}")
            print(f"Emails labeled as '{parsed_prompt['actions']['fail_label']}': {fail_count}")
            print(f"Emails left unlabeled: {scanned_count - fail_count}")
            
            if fail_count > 0:
                print(f"\n📊 Summary:")
                print(f"   🏷️  {fail_count} emails met your conditions → '{parsed_prompt['actions']['fail_label']}'")
                print(f"   📧 {scanned_count - fail_count} emails did not meet conditions → left unlabeled")
            else:
                print("\nNo emails met your conditions")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 