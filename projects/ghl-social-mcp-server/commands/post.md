Create and schedule a social media post.

Steps:
1. Use get_accounts to find account IDs for the target platforms
2. Ask the user what the post is about if not provided: $ARGUMENTS
3. Write platform-specific captions (respect character limits and tone per platform)
4. Use validate_caption to check each caption
5. Use get_next_slot to find the scheduling time
6. If the post needs media, use upload_media first
7. Use create_post to schedule

Writing rules:
- No em dashes, no semicolons, no markdown/asterisks
- No hashtags (exception: 3-5 on carousel posts)
- Active voice, short sentences, human tone
- Emoji limits: X 0-2, LinkedIn 1-2, Facebook 1-3, Instagram 2-4, Threads 0-2
- Avoid banned AI words (delve, leverage, paradigm, etc.)
