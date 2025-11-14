#!/bin/bash

# Deploy the Cloud Function
gcloud functions deploy generate-and-post-telegram \
  --region=us-central1 \
  --runtime=python312 \
  --entry-point=generate_and_post_telegram \
  --trigger-http \
  --set-env-vars TELEGRAM_TOKEN='YOUR_BOT_TOKEN',CHANNEL_ID='YOUR_CHANNEL_ID',GEMINI_API_KEY='YOUR_GEMINI_API_KEY' \
  --allow-unauthenticated

