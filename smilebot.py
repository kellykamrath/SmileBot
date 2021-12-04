import tweepy
import time
import random

#Credentials
BEARER_TOKEN = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Create API object
client = tweepy.Client(bearer_token=BEARER_TOKEN,consumer_key=CONSUMER_KEY,consumer_secret=CONSUMER_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)

def get_last_mention_id():
	file = open('last_mention_id.txt','r')
	id = file.read()
	file.close()
	return (int(id.strip()))

def replace_last_mention_id(new_id):
	file = open('last_mention_id.txt', 'w')
	file.write(str(new_id))
	file.close()

#Gathers mentions recieved in the current loop and returns them as a tuple of (mention_id, tweet_text)
def get_new_mentions():
	mentions_raw = client.get_users_mentions('568721865')
	mentions_no_replies = []
	mentions_clean = []

	for mention in mentions_raw[0]:
		try:
			mention.in_reply_to_status_id_str
		except AttributeError:
			mentions_no_replies.append(mention)

	newest_id = mentions_no_replies[0].id
	last_id = get_last_mention_id()

	if newest_id != last_id:
		replace_last_mention_id(newest_id)
	else:
		return mentions_clean

	for mention in mentions_no_replies:
		current_id = mention.id
		if current_id == last_id:
			return mentions_clean
		tweet = mention.text
		mentions_clean.append((current_id,tweet))

#Chooses a random message of encouragement from a paragraph-separated text file
def get_message():
	file = open('encourage.txt', 'r', encoding='utf-8')
	messages = file.readlines()
	file.close()

	max_int = len(messages) - 1
	rand_int = random.randint(0,max_int)
	return messages[rand_int].strip()


def respond_to_mentions(mentions):
	tweets_sent = 0
	message = ""
	for mention in mentions:
		client.like(mention[0])
		tweet_sent = False
		text = mention[1]
		ngrams = text.split()
		del ngrams[0]
		for ngram in ngrams:
			if '@' in ngram and ngram.lower() is not '@therealsmilebot':
				message = get_message()
				client.create_tweet(text='{} {}'.format(ngram, message))
				tweets_sent += 1
				print("{} tweets sent (new message).".format(tweets_sent))
				tweet_sent = True

		if not tweet_sent:
			message = get_message()
			client.create_tweet(in_reply_to_tweet_id=mention[0],text=message)
			tweets_sent += 1
			print("{} tweets sent (reply).".format(tweets_sent))

#Updates and sends out new messages every 60 seconds
while True:
	mentions = get_new_mentions()
	if len(mentions) > 0:
		respond_to_mentions(mentions)
	time.sleep(60)