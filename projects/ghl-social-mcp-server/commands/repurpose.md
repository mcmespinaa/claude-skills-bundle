Repurpose a YouTube video into social media posts.

Video URL or search query: $ARGUMENTS

Steps:
1. Use youtube_search to find or get video metadata (title, description, stats)
2. Use youtube_transcript to extract the full transcript
3. Identify 3-5 key takeaways from the transcript
4. Use get_accounts to find connected social accounts
5. For each takeaway, draft a platform-specific post
6. Validate each caption with validate_caption
7. Use get_next_slot to find scheduling times (space 24h apart)
8. Present all posts for review, then use create_post to schedule each

Credit the original video in each post.
