import feedparser
import requests
import re
import logging 
# TMDB API Key
TMDB_API_KEY = '56b7978a58b581985e796e2e89fe8ac0'
logging.basicConfig(
    filename='api_fetch.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to clean the title by removing the year and star rating from rss feed json return. 
def clean_title(title):
    title = re.sub(r', \d{4}', '', title)
    title = re.sub(r' - .+$', '', title)
    return title.strip()

def parse_letterboxd_rss(rss_url):
    feed = feedparser.parse(rss_url)
    watched_movies = []
    
    for entry in feed.entries:
        movie_title = entry.title
        cleaned_title = clean_title(movie_title) 
        movie_rating = entry.letterboxd_memberrating if 'letterboxd_memberrating' in entry else None
        watched_movies.append({
            'title': cleaned_title,  
            'rating': movie_rating
        })
    
    return watched_movies



def get_tmdb_metadata(movie_title):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_title}"
        response = requests.get(search_url).json()
        
        if response.get('results'):  # Make sure 'results' exists
            movie_data = response['results'][0]
            movie_id = movie_data.get('id')  # Get movie ID safely
            
            if not movie_id:
                logging.warning(f"No TMDB ID found for {movie_title}.")
                return None
            
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
            details_response = requests.get(details_url).json()

            keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={TMDB_API_KEY}"
            keywords_response = requests.get(keywords_url).json()
            keywords = [keyword['name'] for keyword in keywords_response.get('keywords', [])]
            
            return {
                'tmdb_id': movie_id,
                'title': movie_data.get('title', 'Unknown Title'),  # Ensure the title is always there
                'genres': [genre['name'] for genre in details_response.get('genres', [])],
                'runtime': details_response.get('runtime', 'N/A'),
                'popularity': details_response.get('popularity', 'N/A'),
                'overview': details_response.get('overview', 'No overview available'),
                'language': details_response.get('original_language', 'N/A'),
                'keywords': keywords
            }
        else:
            logging.warning(f"No movie found for {movie_title}.")
            return None

    except Exception as e:
        logging.error(f"Error fetching metadata for {movie_title}: {str(e)}")
        return None

def enrich_movies_with_tmdb(movies):
    enriched_movies = []
    
    for movie in movies:
        cleaned_title = clean_title(movie['title'])
        tmdb_data = get_tmdb_metadata(cleaned_title)
        if tmdb_data:
            movie.update(tmdb_data)
        enriched_movies.append(movie)
    
    return enriched_movies

