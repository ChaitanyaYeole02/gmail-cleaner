# Configuration file for Gmail Resume Scanner
import os
from dotenv import load_dotenv

load_dotenv()

# Gmail API Configuration
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Resume Qualification Settings
MATCH_THRESHOLD = 0.5  # 50% of keywords must match to qualify
MIN_KEYWORD_LENGTH = 3  # Minimum length for keywords to be considered

# Common words to exclude from keyword analysis
COMMON_WORDS = {
    'find', 'me', 'a', 'candidate', 'who', 'is', 'skilled', 'in', 'the', 'and', 'or', 'but', 
    'with', 'has', 'have', 'had', 'been', 'being', 'be', 'am', 'is', 'are', 'was', 'were',
    'looking', 'for', 'someone', 'need', 'person', 'developer', 'engineer', 'programmer',
    'experience', 'years', 'of', 'work', 'job', 'position', 'role', 'team', 'company'
}

# Label Configuration
DELETE_LABEL_NAME = "To Be Deleted"

# Email Search Configuration
PDF_SEARCH_QUERY = 'has:attachment filename:pdf'

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Processing Configuration
MAX_EMAILS_TO_PROCESS = None  # Set to a number to limit processing, None for all
PROCESS_ONLY_FIRST_PDF = True  # Only process the first PDF attachment per email

# AI Configuration
USE_OPENAI = False
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Set your OpenAI API key here

USE_GEMINI = True
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')  # Set your Google Gemini API key here



# Advanced Keyword Matching (Optional)
# Add industry-specific keyword mappings for better matching
INDUSTRY_KEYWORDS = {
    'java': ['java', 'spring', 'hibernate', 'maven', 'gradle', 'junit', 'jvm'],
    'python': ['python', 'django', 'flask', 'numpy', 'pandas', 'scikit-learn', 'pip'],
    'javascript': ['javascript', 'node.js', 'react', 'angular', 'vue', 'typescript', 'npm'],
    'frontend': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'bootstrap'],
    'backend': ['java', 'python', 'node.js', 'php', 'c#', 'database', 'api'],
    'devops': ['docker', 'kubernetes', 'aws', 'azure', 'jenkins', 'git', 'ci/cd'],
    'data': ['python', 'sql', 'pandas', 'numpy', 'machine learning', 'data analysis'],
    'mobile': ['android', 'ios', 'react native', 'flutter', 'swift', 'kotlin']
} 

GOOGLE_APP_PASSWORD = os.getenv('GOOGLE_APP_PASSWORD')