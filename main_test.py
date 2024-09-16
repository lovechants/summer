from user_setup import *
from rss_data import * 

init_config()
rss_url = 'https://letterboxd.com/fakefriend/rss/'
rss_feed = parse_letterboxd_rss(rss_url)
enrich_rss = enrich_movies_with_tmdb(rss_feed)
update_rss_feed_data(rss_feed, enrich_rss)
new_preferences = {'update_frequency': 'daily'}
update_user_preferences(new_preferences)
