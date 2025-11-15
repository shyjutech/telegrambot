import os
import time
import requests
from google import genai
from google.genai import types


def generate_and_post_telegram(request):
    """Generates 2 short, clear posts using Gemini and sends them to Telegram."""
    
    # Retrieve secrets from the deployment environment variables
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    CHANNEL_ID = os.environ.get("CHANNEL_ID")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
    
    if not all([TELEGRAM_TOKEN, CHANNEL_ID, GEMINI_API_KEY]):
        print("ERROR: Missing required environment variables.")
        return "Configuration Error.", 500

    # 1. THE GEMINI API CALL AND CONTENT GENERATION
    gemini_prompt = """
    Generate exactly TWO distinct, short, and highly engaging Telegram posts for a channel focused on passive income and development/tech. 
    
    * **Post 1 (Passive Income):** Find the single most important, current news item or simple tip regarding passive income, side hustles, or financial technology in the last 24 hours. The summary must be under 75 words.
    * **Post 2 (Tech/Dev):** Provide one quick, practical tip or insight about development, coding, or tech tools. Topics can include: Flutter, mobile app development, vibe coding, Cursor AI, ChatGPT, programming languages, frameworks, developer tools, AI coding assistants, or any trending tech topic. Include a very short code snippet, tool recommendation, or practical tip. The explanation must be under 75 words. Vary the topics - don't always focus on Python.
    
    IMPORTANT: Output ONLY the two posts directly. Do NOT include any introductory text, explanations, or meta-commentary like "here are two posts" or "here is the content". Start immediately with the first post.
    
    Format the entire output as a single, ready-to-post Telegram message using markdown for clear reading, separated by a horizontal rule (***) between posts. Do not include external links in the final text.
    """
    
    # Retry logic for Gemini API (handles 503 and other transient errors)
    max_retries = 3
    retry_delay = 2  # seconds
    post_text = None
    api_success = False
    
    for attempt in range(max_retries):
        try:
            # Pass the key directly to the client
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=gemini_prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}] 
                )
            )
            
            # Check if response is successful (equivalent to HTTP 200/201)
            # If no exception was raised, the API call was successful
            raw_text = response.text
            
            # Clean up the response - remove common introductory phrases
            post_text = raw_text.strip()
            
            # Remove common introductory phrases that Gemini might add
            intro_phrases = [
                "here are two engaging telegram posts",
                "here are two posts",
                "here is the content",
                "here are the posts",
                "below are two posts",
                "here are two distinct posts",
                "here are two short posts",
                "here are the two posts",
            ]
            
            post_lower = post_text.lower()
            for phrase in intro_phrases:
                if post_lower.startswith(phrase.lower()):
                    # Remove the phrase and any following punctuation/whitespace
                    idx = len(phrase)
                    # Skip punctuation and whitespace after the phrase
                    while idx < len(post_text) and post_text[idx] in [':', '.', ',', ' ', '\n', '\t', '-']:
                        idx += 1
                    post_text = post_text[idx:].strip()
                    break
            
            # API call succeeded (equivalent to 200/201)
            api_success = True
            print(f"Successfully generated content on attempt {attempt + 1} (API response: success)")
            break  # Success, exit retry loop
            
        except Exception as e:
            error_str = str(e)
            print(f"Gemini API Error (attempt {attempt + 1}/{max_retries}): {e}")
            
            # Check if it's a retryable error (503, 429, or connection errors)
            is_retryable = (
                '503' in error_str or 
                '429' in error_str or 
                'UNAVAILABLE' in error_str or
                'overloaded' in error_str.lower() or
                'timeout' in error_str.lower()
            )
            
            if attempt < max_retries - 1 and is_retryable:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                # Last attempt failed or non-retryable error
                api_success = False
                post_text = None
                print(f"All retry attempts failed. API response was not successful (200/201). Skipping Telegram post.")
                break

    # 2. TELEGRAM DELIVERY
    # Only post if API response was successful (200/201 equivalent) and we have content
    if not api_success:
        print("Gemini API did not return success response (200/201). Skipping Telegram post.")
        return "Content generation failed. No post sent.", 200
    
    if post_text is None or post_text.strip() == "":
        print("No content generated from Gemini API despite success response. Skipping Telegram post.")
        return "Content generation failed. No post sent.", 200
    
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Ensure channel ID has @ prefix if it's a username
    chat_id = CHANNEL_ID if CHANNEL_ID.startswith('@') or CHANNEL_ID.startswith('-') else f'@{CHANNEL_ID}'
    
    # Try with Markdown first
    payload = {
        'chat_id': chat_id,
        'text': post_text,
        'parse_mode': 'Markdown' 
    }

    try:
        response = requests.post(telegram_url, data=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get('ok'):
            print("Successfully posted daily digest to Telegram.")
            return f"Success. Posted to {chat_id}", 200
        else:
            error_msg = result.get('description', 'Unknown error')
            # If Markdown parsing failed, try without parse_mode
            if 'parse' in error_msg.lower() or 'markdown' in error_msg.lower():
                print(f"Markdown parsing failed, retrying without Markdown: {error_msg}")
                payload_no_md = {
                    'chat_id': chat_id,
                    'text': post_text
                }
                response2 = requests.post(telegram_url, data=payload_no_md, timeout=10)
                response2.raise_for_status()
                result2 = response2.json()
                if result2.get('ok'):
                    print("Successfully posted daily digest to Telegram (without Markdown).")
                    return f"Success. Posted to {chat_id} (plain text)", 200
            print(f"Telegram API Error: {error_msg}")
            return f"Telegram send failed: {error_msg}", 500

    except requests.exceptions.HTTPError as err:
        error_detail = ""
        try:
            error_response = err.response.json()
            error_detail = error_response.get('description', str(err))
            # If Markdown parsing failed, try without parse_mode
            if 'parse' in error_detail.lower() or 'markdown' in error_detail.lower():
                print(f"Markdown parsing failed, retrying without Markdown: {error_detail}")
                payload_no_md = {
                    'chat_id': chat_id,
                    'text': post_text
                }
                response2 = requests.post(telegram_url, data=payload_no_md, timeout=10)
                response2.raise_for_status()
                result2 = response2.json()
                if result2.get('ok'):
                    print("Successfully posted daily digest to Telegram (without Markdown).")
                    return f"Success. Posted to {chat_id} (plain text)", 200
        except:
            error_detail = str(err)
        print(f"Telegram Post HTTP Error: {error_detail}")
        return f"Telegram send failed: {error_detail}", 500
    except Exception as e:
        print(f"Telegram Post Error: {type(e).__name__}: {str(e)}")
        return f"Telegram send failed: {str(e)}", 500