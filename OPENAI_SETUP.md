# OpenAI Setup Guide

This guide will help you set up OpenAI integration for intelligent email categorization.

## Prerequisites

1. **OpenAI API Key**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Python Environment**: Make sure you have the required dependencies installed

## Setup Steps

### 1. Install Dependencies

```bash
pip install openai==1.3.0
```

### 2. Configure OpenAI

Edit `config.py` and set your OpenAI API key:

```python
# OpenAI Configuration
OPENAI_API_KEY = "your-openai-api-key-here"  # Replace with your actual API key
USE_OPENAI = True  # Set to True to enable OpenAI
```

### 3. Usage Examples

#### Example 1: Simple Body Check
**Prompt:**
```
"Mark emails with body containing 'I am XYZ from ABC city' as To be deleted"
```

**OpenAI will create rules like:**
```json
[
    {
        "Subject": ["Exists"],
        "Body": ["Contains", "I am XYZ from ABC city"],
        "PDF": ["Exists"],
        "Label Action": ["To be deleted"]
    }
]
```

#### Example 2: Multiple Conditions
**Prompt:**
```
"Label emails with subject containing 'Resume' and body containing 'Java developer' as To be reviewed, else mark as To be deleted"
```

**OpenAI will create rules like:**
```json
[
    {
        "Subject": ["Contains", "Resume"],
        "Body": ["Contains", "Java developer"],
        "PDF": ["Exists"],
        "Label Action": ["To be reviewed"]
    },
    {
        "Subject": ["Does not contain", "Resume"],
        "Body": ["Does not contain", "Java developer"],
        "PDF": ["Exists"],
        "Label Action": ["To be deleted"]
    }
]
```

#### Example 3: Skill-Based Analysis
**Prompt:**
```
"Mark emails with PDF containing Python skills as To be reviewed, JavaScript skills as To be interviewed, others as To be deleted"
```

**OpenAI will create rules like:**
```json
[
    {
        "Subject": ["Exists"],
        "Body": ["Exists"],
        "PDF": ["Contains skill", "Python"],
        "Label Action": ["To be reviewed"]
    },
    {
        "Subject": ["Exists"],
        "Body": ["Exists"],
        "PDF": ["Contains skill", "JavaScript"],
        "Label Action": ["To be interviewed"]
    },
    {
        "Subject": ["Exists"],
        "Body": ["Exists"],
        "PDF": ["Does not contain skill", "Python"],
        "Label Action": ["To be deleted"]
    }
]
```

## Benefits of OpenAI Approach

### ✅ **Natural Language Understanding**
- Understands complex prompts in plain English
- No need to learn specific syntax or patterns
- Handles ambiguity and context

### ✅ **Flexible Categorization**
- Multiple rules and conditions
- Complex logic (AND, OR, NOT)
- Skill-based analysis
- Context-aware matching

### ✅ **Intelligent Matching**
- Understands synonyms and variations
- Handles different writing styles
- Context-aware text matching
- Better than regex patterns

### ✅ **Easy to Use**
- Write prompts in natural language
- No technical knowledge required
- Handles edge cases automatically

## Cost Considerations

- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Typical usage**: ~100-500 tokens per email
- **Cost per 1000 emails**: ~$0.20-$1.00

## Troubleshooting

### API Key Issues
- Make sure your API key is valid
- Check your OpenAI account balance
- Verify the key is correctly set in `config.py`

### Rate Limits
- OpenAI has rate limits (3 requests per second for free tier)
- The script includes delays to respect limits
- Consider upgrading for higher limits

### No Results
- Check the logs for OpenAI responses
- Verify your prompt is clear and specific
- Try simpler prompts first

## Example Prompts

### Simple Prompts
```
"Mark emails without subject as To be deleted"
"Label emails with PDF as To be reviewed"
"Mark emails with body containing 'spam' as To be deleted"
```

### Complex Prompts
```
"Label emails with subject containing 'Resume' and body containing 'Java' as To be reviewed, emails with 'Python' as To be interviewed, others as To be deleted"
"Mark emails with PDF containing 'senior' or 'lead' as To be reviewed, 'junior' as To be considered, others as To be deleted"
"Label emails with body containing 'I am XYZ from ABC company' as To be reviewed, emails without body as To be deleted"
```

## Running the Scanner

```bash
python3 gmail_resume_scanner.py
```

The scanner will automatically detect if OpenAI is configured and use it for intelligent categorization! 