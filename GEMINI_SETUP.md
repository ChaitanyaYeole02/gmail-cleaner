# Google Gemini Setup Guide

This guide will help you set up Google Gemini integration for intelligent email categorization.

## Prerequisites

1. **Google AI Studio Account**: Sign up at [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Python Environment**: Make sure you have the required dependencies installed

## Setup Steps

### 1. Install Dependencies

```bash
pip install google-generativeai==0.3.0
```

### 2. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure Gemini

Edit `config.py` and set your Gemini API key:

```python
# AI Configuration
GEMINI_API_KEY = "your-gemini-api-key-here"  # Replace with your actual API key
USE_GEMINI = True  # Set to True to enable Gemini
USE_OPENAI = False  # Set to False to disable OpenAI
```

## Gemini Free Tier Benefits

### 🎉 **Generous Free Tier:**
- **15 requests per minute** (vs OpenAI's 3)
- **1,500 requests per day** (vs OpenAI's 200)
- **No credit card required** for basic usage
- **No monthly fees** - completely free for most use cases

### 💰 **Cost Comparison:**
- **OpenAI**: $0.002 per 1K tokens
- **Gemini**: **FREE** for most usage
- **Your use case**: Likely completely free

### 📊 **Rate Limits:**
- **Requests per minute**: 15 (5x more than OpenAI)
- **Requests per day**: 1,500 (7.5x more than OpenAI)
- **Perfect for**: Email processing and batch operations

## Usage Examples

### Example 1: Simple Body Check
**Prompt:**
```
"Mark emails with body containing 'I am XYZ from ABC city' as To be deleted"
```

**Gemini will create rules like:**
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

### Example 2: Complex Multi-Condition
**Prompt:**
```
"Label emails with subject containing 'Resume' and body containing 'Java developer' as To be reviewed, else mark as To be deleted"
```

**Gemini will create rules like:**
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

### Example 3: Skill-Based Analysis
**Prompt:**
```
"Mark emails with PDF containing Python skills as To be reviewed, JavaScript skills as To be interviewed, others as To be deleted"
```

## Benefits of Gemini Approach

### ✅ **Completely Free**
- No credit card required
- No monthly fees
- Generous rate limits

### ✅ **High Performance**
- Fast response times
- Reliable API
- Good uptime

### ✅ **Natural Language Understanding**
- Understands complex prompts
- Handles context well
- Good at pattern matching

### ✅ **Easy Integration**
- Simple API
- Good documentation
- Python SDK available

## Cost Analysis

### **Gemini (Recommended):**
- **Cost**: FREE for most usage
- **Rate Limits**: 15 requests/minute, 1,500/day
- **Best for**: Personal and small business use

### **OpenAI:**
- **Cost**: $0.002 per 1K tokens
- **Rate Limits**: 3 requests/minute, 200/day
- **Best for**: High-volume commercial use

## Troubleshooting

### API Key Issues
- Make sure your API key is valid
- Check that you've enabled the Gemini API
- Verify the key is correctly set in `config.py`

### Rate Limits
- Gemini: 15 requests per minute
- The script includes delays to respect limits
- For high volume, consider batching

### No Results
- Check the logs for Gemini responses
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

The scanner will automatically detect if Gemini is configured and use it for intelligent categorization!

## Why Choose Gemini?

1. **Free**: No costs for most usage
2. **Generous Limits**: 15 requests/minute vs 3 for OpenAI
3. **No Credit Card**: Sign up with Google account
4. **Reliable**: Google's infrastructure
5. **Fast**: Quick response times

**Perfect for your email categorization needs!** 🚀 