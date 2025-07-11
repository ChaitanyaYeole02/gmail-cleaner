#!/usr/bin/env python3
"""
Generate Test Emails Script
Sends 200 test emails with various combinations for testing the Gmail Resume Scanner
"""

import os
import sys
import random
import time
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import GMAIL_SCOPES, LOG_LEVEL, LOG_FORMAT
import logging

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class TestEmailGenerator:
    """Generate test emails with various combinations"""
    
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        # Sample data for generating varied emails
        self.names = [
            "Chaitanya", "John", "Sarah", "Michael", "Emily", "David", "Lisa", "Robert",
            "Jennifer", "William", "Jessica", "James", "Ashley", "Christopher", "Amanda",
            "Daniel", "Nicole", "Matthew", "Stephanie", "Andrew", "Laura", "Joshua",
            "Melissa", "Ryan", "Michelle", "Kevin", "Kimberly", "Brian", "Rebecca",
            "Jason", "Amber", "Eric", "Rachel", "Steven", "Heather", "Timothy", "Nicole"
        ]
        
        self.cities = [
            "SF", "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
            "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
            "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
            "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville",
            "Detroit", "Oklahoma City", "Portland", "Las Vegas", "Memphis", "Louisville"
        ]
        
        self.skills = [
            "Python", "JavaScript", "Java", "React", "Node.js", "AWS", "Docker", "Kubernetes",
            "Machine Learning", "Data Science", "DevOps", "Full Stack", "Frontend", "Backend",
            "Mobile Development", "Cloud Computing", "AI", "Blockchain", "Cybersecurity",
            "Database Design", "API Development", "UI/UX Design", "Agile", "Scrum"
        ]
        
        self.projects = [
            "Voice Agent", "E-commerce Platform", "Social Media App", "AI Chatbot",
            "Data Analytics Dashboard", "Mobile Game", "Web Scraper", "Task Manager",
            "Weather App", "Recipe Finder", "Fitness Tracker", "Budget Manager",
            "Learning Platform", "Event Scheduler", "Inventory System", "CRM System"
        ]
        
        self.body_templates = [
            # Template 1: Simple introduction
            "Hello,\n\nI am {name} and I am from {city}. I want to apply for this position.\n\nBest regards,\n{name}",
            
            # Template 2: Professional with skills
            "Dear Hiring Manager,\n\nHere is me, I have done {skill1} and achieved {skill2}. I am passionate about {skill3}.\n\nKind regards,\n{name}",
            
            # Template 3: Project focused
            "Hi,\n\nI created my own {project} and want to show it to you. I have experience in {skill1} and {skill2}.\n\nBest regards,\n{name}",
            
            # Template 4: Mixed professional
            "Hello,\n\nI am {name} from {city}. I have expertise in {skill1} and recently worked on {project}.\n\nRegards,\n{name}",
            
            # Template 5: Skill focused
            "Dear Team,\n\nHere is me, I have done {skill1} and achieved {skill2}. I am from {city} and specialize in {skill3}.\n\nBest regards,\n{name}",
            
            # Template 6: Project showcase
            "Hi there,\n\nI created my own {project} and want to show it to you. I am {name} from {city} with skills in {skill1}.\n\nRegards,\n{name}",
            
            # Template 7: Professional introduction
            "Dear Hiring Manager,\n\nI am {name} and I am from {city}. I have experience in {skill1} and {skill2}.\n\nBest regards,\n{name}",
            
            # Template 8: Achievement focused
            "Hello,\n\nHere is me, I have done {skill1} and achieved {skill2}. I created my own {project}.\n\nKind regards,\n{name}"
        ]
        
        self.subjects = [
            "Application for Software Engineer Position",
            "Resume - Full Stack Developer",
            "Job Application - {skill} Developer",
            "Interested in {skill} Role",
            "Application for {skill} Position",
            "Resume Submission - {name}",
            "Job Application from {city}",
            "Software Engineer Application",
            "Developer Position Application",
            "Resume - {skill} Specialist",
            "Application for {project} Developer",
            "Job Interest - {skill} Expert",
            "Resume - {name} from {city}",
            "Application for {skill} Role",
            "Developer Application - {skill}"
        ]
    
    def generate_pdf(self, name, skills, project):
        """Generate a simple PDF resume"""
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, f"{name}'s Resume")
        
        # Contact Info
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Email: {name.lower()}@example.com")
        p.drawString(50, height - 100, f"Phone: (555) 123-4567")
        
        # Skills
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 140, "Skills:")
        p.setFont("Helvetica", 12)
        y_pos = height - 160
        for skill in skills:
            p.drawString(70, y_pos, f"• {skill}")
            y_pos -= 20
        
        # Projects
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos - 20, "Projects:")
        p.setFont("Helvetica", 12)
        y_pos -= 40
        p.drawString(70, y_pos, f"• {project}")
        
        # Experience
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y_pos - 40, "Experience:")
        p.setFont("Helvetica", 12)
        y_pos -= 60
        p.drawString(70, y_pos, "• Software Engineer at Tech Company (2020-2023)")
        p.drawString(70, y_pos - 20, "• Junior Developer at Startup (2018-2020)")
        
        p.save()
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
    
    def generate_email_content(self):
        """Generate random email content"""
        name = random.choice(self.names)
        city = random.choice(self.cities)
        skills = random.sample(self.skills, 3)
        project = random.choice(self.projects)
        
        # Choose body template
        template = random.choice(self.body_templates)
        body = template.format(
            name=name,
            city=city,
            skill1=skills[0],
            skill2=skills[1],
            skill3=skills[2],
            project=project
        )
        
        # Choose subject template
        subject_template = random.choice(self.subjects)
        subject = subject_template.format(
            name=name,
            city=city,
            skill=skills[0],
            project=project
        )
        
        return {
            'name': name,
            'city': city,
            'skills': skills,
            'project': project,
            'body': body,
            'subject': subject
        }
    
    def send_email(self, content, has_pdf=True, has_body=True, has_subject=True):
        """Send a single email"""
        try:
            msg = MIMEMultipart()
            
            # Set sender and recipient
            msg['From'] = self.sender_email
            msg['To'] = "clashofclanschatty@gmail.com"
            
            # Set subject (or empty)
            if has_subject:
                msg['Subject'] = content['subject']
            else:
                msg['Subject'] = ""
            
            # Set body (or empty)
            if has_body:
                msg.attach(MIMEText(content['body'], 'plain'))
            else:
                msg.attach(MIMEText("", 'plain'))
            
            # Attach PDF if needed
            if has_pdf:
                pdf_data = self.generate_pdf(content['name'], content['skills'], content['project'])
                pdf_attachment = MIMEBase('application', 'pdf')
                pdf_attachment.set_payload(pdf_data)
                encoders.encode_base64(pdf_attachment)
                pdf_attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{content["name"]}_Resume.pdf"'
                )
                msg.attach(pdf_attachment)
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, "clashofclanschatty@gmail.com", text)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def generate_test_emails(self, total_emails=200):
        """Generate and send test emails"""
        logger.info(f"Starting to generate {total_emails} test emails...")
        
        # Define email combinations
        email_combinations = [
            # PDF + Body + Subject (most common)
            {'has_pdf': True, 'has_body': True, 'has_subject': True, 'count': 80},
            # PDF + Body + No Subject
            {'has_pdf': True, 'has_body': True, 'has_subject': False, 'count': 20},
            # PDF + No Body + Subject
            {'has_pdf': True, 'has_body': False, 'has_subject': True, 'count': 15},
            # No PDF + Body + Subject
            {'has_pdf': False, 'has_body': True, 'has_subject': True, 'count': 50},
            # No PDF + Body + No Subject
            {'has_pdf': False, 'has_body': True, 'has_subject': False, 'count': 15},
            # No PDF + No Body + Subject
            {'has_pdf': False, 'has_body': False, 'has_subject': True, 'count': 10},
            # No PDF + No Body + No Subject
            {'has_pdf': False, 'has_body': False, 'has_subject': False, 'count': 10}
        ]
        
        sent_count = 0
        
        for combo in email_combinations:
            logger.info(f"Generating {combo['count']} emails with PDF={combo['has_pdf']}, Body={combo['has_body']}, Subject={combo['has_subject']}")
            
            for i in range(combo['count']):
                content = self.generate_email_content()
                
                if self.send_email(content, combo['has_pdf'], combo['has_body'], combo['has_subject']):
                    sent_count += 1
                    logger.info(f"Sent email {sent_count}/{total_emails}: {content['subject'][:50]}...")
                else:
                    logger.error(f"Failed to send email {sent_count + 1}")
                
                # Add delay to avoid rate limits
                time.sleep(1)
        
        logger.info(f"Successfully sent {sent_count}/{total_emails} test emails!")
        return sent_count

def main():
    """Main function to run the test email generator"""
    print("📧 Gmail Test Email Generator")
    print("=" * 40)
    
    # Get sender credentials
    sender_email = input("Enter your Gmail address: ")
    sender_password = input("Enter your Gmail app password: ")
    
    if not sender_email or not sender_password:
        print("❌ Email and password are required!")
        return
    
    # Create generator
    generator = TestEmailGenerator(sender_email, sender_password)
    
    # Confirm before sending
    print(f"\n📋 About to send 200 test emails to clashofclanschatty@gmail.com")
    print("This will include:")
    print("  • 80 emails with PDF + Body + Subject")
    print("  • 20 emails with PDF + Body + No Subject")
    print("  • 15 emails with PDF + No Body + Subject")
    print("  • 50 emails with No PDF + Body + Subject")
    print("  • 15 emails with No PDF + Body + No Subject")
    print("  • 10 emails with No PDF + No Body + Subject")
    print("  • 10 emails with No PDF + No Body + No Subject")
    
    confirm = input("\nContinue? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled!")
        return
    
    # Generate emails
    try:
        sent_count = generator.generate_test_emails(100)
        print(f"\n✅ Successfully sent {sent_count} test emails!")
        print("📧 Check your Gmail inbox for the test emails.")
        
    except Exception as e:
        print(f"❌ Error generating test emails: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 