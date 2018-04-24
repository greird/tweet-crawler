from twitter import Twitter, OAuth
import ConfigParser, csv, json, time, os, sys, re

config = ConfigParser.RawConfigParser()   
config.read('config.cfg')

twitter_auth = {
	'CONSUMER_KEY': config.get('twitter-api', 'CONSUMER_KEY'),
	'CONSUMER_SECRET': config.get('twitter-api', 'CONSUMER_SECRET'),
	'ACCESS_TOKEN_KEY': config.get('twitter-api', 'ACCESS_TOKEN_KEY'),
	'ACCESS_TOKEN_SECRET': config.get('twitter-api', 'ACCESS_TOKEN_SECRET')
}

"""
LIMITED TO 180 REQUEST OF 100 STATUS EVERY 15MIN
TWEETS OLDER THAN A WEEK ARE NOT REACHABLE THROUGH THE API
"""

def crawl(q="", lang=""):
	q = raw_input("Search for (e.g. deezer+flow): ").lower() if q == "" else q.lower()
	lang = raw_input("Language (leave blank for no restriction):").lower() if lang == "" else lang.lower()
	query_id = q.replace('+', '_').replace(' ', '_') + '_' + lang
	csv_file = 'tweets_' + q.replace('+', '_').replace(' ', '_') + '_' + lang + '.csv'
	max_id = 0
	since_id = 0 
	count = 0
	tweets = []
	response = ""

	t = Twitter(auth=OAuth(twitter_auth['ACCESS_TOKEN_KEY'], twitter_auth['ACCESS_TOKEN_SECRET'], twitter_auth['CONSUMER_KEY'], twitter_auth['CONSUMER_SECRET']))

	# Check config file to retrieve last tweet id (if any)
	try:
		if 'history' not in config.sections():
			config.add_section('history')
		max_id = int(config.get('history', query_id))
	except ConfigParser.NoOptionError:
		max_id = 0

	# max_id is not define: Fetch all tweets and populate dataset
	if max_id == 0:
		while  True:
			try:
				print "New search for '%s'. Fetching 100 tweets from %s." % (q, since_id)
				# Retrieve 100 tweets older than the oldest tweet retrieved
				twitter = t.search.tweets(q=q, lang=lang, result_type="recent", count=100, max_id=since_id)

				# Store data in json
				data_count = 0
				for data in twitter['statuses']:
					data_count += 1
					if max_id == 0:
						max_id = data['id_str']
					else:
						since_id = data['id_str']
					tweets.append({
					    'id' : int(data['id_str']),
					    'lang' : data['lang'].encode('utf-8'),
					    'timestamp' : data['created_at'].encode('utf-8'),
					    'text' : " ".join(data['text'].split()).encode('utf-8'),
					    'user' : data['user']['screen_name'].encode('utf-8'),
					    'username' : data['user']['name'].encode('utf-8'),
					    'user_image' : data['user']['profile_image_url_https'].encode('utf-8'),
					    'url' : ('https://twitter.com/'+data['user']['screen_name']+'/status/'+data['id_str']).encode('utf-8')
					})

				print "%s new tweets found." % data_count

				count += data_count

				# If we retrieved less than 2 tweets, stop.
				if data_count < 2:
					print "%s new tweets in total." % count
					break

				if twitter.headers.get('x-rate-limit-remaining') < 10:
					print "Waiting for rate limit to be raised... ^C to interrupt and save to CSV."
					time.sleep(60*15) # should be twitter.headers.get('x-rate-limit-reset')

			except KeyboardInterrupt:
				print "Interrupted. Writing in CSV, do not interrupt !"
				break

	# max_id is defined: Fetch all new tweets since last crawl
	else:
		while True:
			try:
				print "max_id found (%s). Fetching new tweets about %s." % (max_id, q)
				# Retrieve 100 tweets max from last retrieve tweet id
				twitter = t.search.tweets(q=q, lang=lang, result_type="recent", count=100, since_id=max_id)

				# Store data in json
				data_count = 0
				for data in twitter['statuses']:
					data_count += 1
					tweets.append({
					    'id' : int(data['id_str']),
					    'lang' : data['lang'].encode('utf-8'),
					    'timestamp' : data['created_at'].encode('utf-8'),
					    'text' : " ".join(data['text'].split()).encode('utf-8'),
					    'user' : data['user']['screen_name'].encode('utf-8'),
					    'username' : data['user']['name'].encode('utf-8'),
					    'user_image' : data['user']['profile_image_url_https'].encode('utf-8'),
					    'url' : ('https://twitter.com/'+data['user']['screen_name']+'/status/'+data['id_str']).encode('utf-8')
					})

				print "%s new tweets found." % data_count

				count += data_count
				max_id = twitter['search_metadata']['max_id']
				since_id = twitter['search_metadata']['since_id']

				# If we retrieved less than 100 tweets, stop.
				if data_count < 100:
					print "%s new tweets in total." % count
					break
			
			except KeyboardInterrupt:
				print "Interrupted."
				break

	# Append data to CSV
	#with open(csv_file, 'wb+') as csvfile: # to start from scratch
	with open(csv_file, 'a') as csvfile:
		twriter = csv.writer(csvfile, delimiter='\t')

		for t in tweets:
			row = []
			for k, v in t.iteritems():
				row.append(v)
			twriter.writerow(row)

	# Write last tweet id
	with open('config.cfg', 'w') as configfile:		
		config.set('history', query_id, str(max_id))
		config.write(configfile)

	csv_count = len(open(csv_file, 'r').readlines()) 

	return json.dumps({
		'status': 'SUCCESS',
		'code': 200,
		#'completed_in': total_completed_in,
		'count': count,
		'csv_rows': csv_count,
		'max_id': max_id,
		'since_id': since_id,
		'csv_file': csv_file,
		'rate_limit': {
			'total': twitter.headers.get('x-rate-limit-limit'),
			'remaining': twitter.headers.get('x-rate-limit-remaining'),
			'reset_in': twitter.headers.get('x-rate-limit-reset')
		}, 
		#'tweets': tweets
	}, sort_keys=True, indent=4, separators=(',', ': '))

print u'\n TWEET CRAWLER \U0001F98E \n'

print crawl()
