# Telegram Bot - AI Content Generator

An automated Telegram bot that generates and posts daily content to your Telegram channel using Google's Gemini AI. The bot creates two types of posts: one about passive income and another about mobile development/coding tips.

## Features

- 🤖 **AI-Powered Content Generation**: Uses Google Gemini AI to generate engaging posts
- 📱 **Telegram Integration**: Automatically posts to your Telegram channel
- 🔄 **Automatic Retry Logic**: Handles API rate limits and temporary failures
- 🎨 **Markdown Support**: Formats posts with Markdown (with automatic fallback to plain text)
- ☁️ **Cloud Functions**: Deploys to Google Cloud Functions for serverless execution
- ⏰ **Schedulable**: Can be triggered via HTTP or scheduled with Cloud Scheduler

## Prerequisites

Before you begin, ensure you have:

1. **Google Cloud Account** with billing enabled
2. **Telegram Bot Token** - Create a bot via [@BotFather](https://t.me/botfather)
3. **Telegram Channel** - Create a channel and add your bot as an admin
4. **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
5. **Google Cloud SDK (gcloud)** - [Installation guide](https://cloud.google.com/sdk/docs/install)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/shyjutech/telegrambot.git
cd telegrambot
```

### 2. Get Your API Keys

#### Telegram Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Telegram Channel ID
1. Create a Telegram channel or use an existing one
2. Add your bot as an administrator to the channel
3. Get your channel username (e.g., `@mychannel`) or numeric ID (starts with `-100`)
4. For public channels, use `@channelname`
5. For private channels, you'll need the numeric ID (you can get it by forwarding a message from the channel to [@userinfobot](https://t.me/userinfobot))

#### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### 3. Install Google Cloud SDK

#### macOS
```bash
brew install --cask google-cloud-sdk
```

#### Linux
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

#### Windows
Download and install from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

### 4. Authenticate and Configure

```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 5. Deploy to Google Cloud Functions

#### Option A: Using the Deploy Script

1. Edit `deploy.sh` and replace the environment variables with your values:
   ```bash
   TELEGRAM_TOKEN='YOUR_BOT_TOKEN'
   CHANNEL_ID='your_channel_id'  # e.g., @mychannel or -1001234567890
   GEMINI_API_KEY='YOUR_GEMINI_API_KEY'
   ```

2. Make the script executable and run it:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

#### Option B: Manual Deployment

```bash
gcloud functions deploy generate-and-post-telegram \
  --gen2 \
  --region=us-central1 \
  --runtime=python312 \
  --source=. \
  --entry-point=generate_and_post_telegram \
  --trigger-http \
  --set-env-vars TELEGRAM_TOKEN='YOUR_BOT_TOKEN',CHANNEL_ID='YOUR_CHANNEL_ID',GEMINI_API_KEY='YOUR_GEMINI_API_KEY' \
  --allow-unauthenticated
```

**Replace:**
- `YOUR_BOT_TOKEN` - Your Telegram bot token
- `YOUR_CHANNEL_ID` - Your Telegram channel ID (e.g., `@mychannel` or `-1001234567890`)
- `YOUR_GEMINI_API_KEY` - Your Google Gemini API key

### 6. Test the Function

After deployment, you'll receive a function URL. Test it by:

```bash
# Using curl
curl https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/generate-and-post-telegram

# Or open in browser
open https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/generate-and-post-telegram
```

### 7. Schedule with Cloud Scheduler (Optional)

To run automatically on a schedule:

```bash
gcloud scheduler jobs create http daily-telegram-posts \
  --location=us-central1 \
  --schedule="0 9 * * *" \
  --uri="https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/generate-and-post-telegram" \
  --http-method=GET \
  --time-zone="America/New_York"
```

**Schedule Examples:**
- `0 9 * * *` - Daily at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 9 * * 1-5` - Weekdays at 9:00 AM

## Project Structure

```
telegrambot/
├── main.py              # Main function code
├── requirements.txt     # Python dependencies
├── deploy.sh           # Deployment script
└── README.md           # This file
```

## Configuration

### Environment Variables

The function uses these environment variables:

- `TELEGRAM_TOKEN` - Your Telegram bot token
- `CHANNEL_ID` - Your Telegram channel ID or username
- `GEMINI_API_KEY` - Your Google Gemini API key

### Customizing Content

Edit the `gemini_prompt` variable in `main.py` to customize:
- Post topics
- Content length
- Post format
- Number of posts

## Monitoring and Logs

### View Logs via CLI

```bash
# View recent logs
gcloud functions logs read generate-and-post-telegram --region=us-central1 --limit=50

# Follow logs in real-time
gcloud functions logs read generate-and-post-telegram --region=us-central1 --limit=50 --follow
```

### View Logs via Console

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to **Cloud Functions**
3. Click on `generate-and-post-telegram`
4. Click the **LOGS** tab

Or use the direct link:
```
https://console.cloud.google.com/functions/details/us-central1/generate-and-post-telegram?project=YOUR_PROJECT_ID
```

## Troubleshooting

### Common Issues

#### 1. "Telegram send failed"
- **Check**: Bot is added as admin to the channel
- **Check**: Channel ID is correct (use `@channelname` for public channels)
- **Check**: Bot token is valid

#### 2. "Content generation failed"
- **Check**: Gemini API key is valid
- **Check**: API quota hasn't been exceeded
- **Note**: The function retries automatically on 503 errors

#### 3. "Configuration Error"
- **Check**: All environment variables are set correctly
- **Check**: No extra spaces or quotes in environment variables

#### 4. Markdown Parsing Errors
- The function automatically falls back to plain text if Markdown fails
- Check logs for specific parsing errors

### Error Codes

- `503 UNAVAILABLE` - Gemini API is overloaded (auto-retries)
- `429` - Rate limit exceeded (auto-retries)
- `400` - Bad request (check channel ID and bot permissions)

## Features Explained

### Retry Logic
The function automatically retries up to 3 times with exponential backoff (2s, 4s, 8s) for:
- 503 errors (service unavailable)
- 429 errors (rate limited)
- Connection timeouts

### Content Cleanup
Automatically removes common introductory phrases from Gemini responses:
- "here are two posts"
- "here is the content"
- etc.

### Markdown Fallback
If Markdown parsing fails, the function automatically retries sending as plain text.

## Security Best Practices

1. **Never commit API keys** - Use environment variables only
2. **Use Secret Manager** (optional) - For production, consider using [Google Secret Manager](https://cloud.google.com/secret-manager)
3. **Restrict access** - Remove `--allow-unauthenticated` and use authentication for production
4. **Monitor usage** - Set up billing alerts in Google Cloud Console

## Cost Estimation

- **Cloud Functions**: Free tier includes 2 million invocations/month
- **Gemini API**: Check [pricing](https://ai.google.dev/pricing)
- **Cloud Scheduler**: Free tier includes 3 jobs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/shyjutech/telegrambot/issues)
- Check the [troubleshooting section](#troubleshooting)

## Acknowledgments

- [Google Gemini AI](https://ai.google.dev/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Google Cloud Functions](https://cloud.google.com/functions)

---

Made with ❤️ for automated content generation

