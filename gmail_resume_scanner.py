import time
import logging

from typing import Dict, Tuple
from services import GmailService, PDFProcessor
from gemini_analyzer import GeminiAnalyzer
from config import LOG_LEVEL, LOG_FORMAT, USE_GEMINI, GEMINI_API_KEY, PDF_SEARCH_QUERY, MAX_EMAILS_TO_PROCESS

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class GmailResumeScanner:
    def __init__(self):
        self.gmail_service = GmailService()
        
        # Initialize AI analyzers if configured
        self.gemini_analyzer = None
        
        if USE_GEMINI and GEMINI_API_KEY:
            self.gemini_analyzer = GeminiAnalyzer(GEMINI_API_KEY)
    
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
            
            # Track labels and counts
            label_counts = {}
            scanned_count = 0
            
            # Process emails in batches for memory efficiency
            for batch in self.gmail_service.search_emails_batch(PDF_SEARCH_QUERY, MAX_EMAILS_TO_PROCESS):
                if not batch:
                    logger.info("No emails found")
                    break
                
                logger.info(f"Processing batch of {len(batch)} emails...")
                
                for message in batch:
                    try:
                        # First check if this is a job application email (if enabled)
                        email_components = self.gemini_analyzer.extract_email_components(message)

                        is_job_app = self.gemini_analyzer.is_job_application(email_components)
                        
                        if not is_job_app:
                            logger.info(f"Email {message['id']} - Not a job application, skipping")
                            continue
                        
                        # Extract PDF content if available
                        pdf_text = None
                        if email_components['has_pdf']:
                            try:
                                # Find PDF attachment
                                if 'payload' in message and 'parts' in message['payload']:
                                    for part in message['payload']['parts']:
                                        if part.get('filename', '').lower().endswith('.pdf'):
                                            attachment_id = part['body']['attachmentId']
                                            attachment_data = self.gmail_service.get_attachment_data(message['id'], attachment_id)

                                            if attachment_data:
                                                pdf_processor = PDFProcessor()
                                                pdf_text = pdf_processor.extract_pdf_text(attachment_data)
                                                break
                            except Exception as e:
                                logger.error(f"Error extracting PDF text: {e}")
                        
                        # Categorize email using Gemini with PDF content
                        label = self.gemini_analyzer.categorize_email(email_components, rules, pdf_text or "")
                        
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
                        time.sleep(4)
                        
                    except Exception as e:
                        logger.error(f"Error processing message {message['id']}: {e}")
                        continue
                
                logger.info(f"Completed batch. Total scanned: {scanned_count}, labels: {label_counts}")
            
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
        else:
            print("Gemini analyzer not configured. Please check your configuration.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 