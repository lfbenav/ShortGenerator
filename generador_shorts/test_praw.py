import praw

# Configura tu cliente de Reddit con las credenciales
reddit = praw.Reddit(client_id='J8ByLE2aTELSgPFCHnp9DQ',  # Tu client_id
                     client_secret='0Z5tTYTOha2PKvFxfoBL7qRLUL3NVg',  # Tu client_secret
                     user_agent='python:MyRedditApp:1.0 (by /u/my_reddit_username)')  # Tu user_agent

# Selecciona el subreddit y obtén los posts más populares
subreddit_name = 'aitah'  # Puedes cambiarlo a cualquier subreddit, por ejemplo 'python', 'funny', etc.
subreddit = reddit.subreddit(subreddit_name)

# Obtener los 10 posts más populares de las últimas 24 horas
for submission in subreddit.top(time_filter='day', limit=10):  # Puedes cambiar 'day' por 'week', 'month', 'year', etc.
    print(f"Title: {submission.title}")
    if submission.is_self:  # Verifica si la publicación tiene texto (es un post de texto)
        print(f"Text: {submission.selftext}")
    else:
        print(f"Text: No text content (This is a link post)")
    print("-" * 50)
