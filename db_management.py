import threading
import time
import yaml
from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import logging
from rss_data import *  # Assuming rss_data.py has all necessary functions like parsing and enrichment
from user_setup import *  # Assuming user_setup.py has config management functions

# Set up logging
logging.basicConfig(
    filename='background_fetch.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load YAML config file
config = load_config('config.yaml')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_recommendation']
movies_collection = db['movies']

# Insert movie data into MongoDB
def store_movie(movie_data):
    movies_collection.update_one({'tmdb_id': movie_data['tmdb_id']}, {'$set': movie_data}, upsert=True)
    logging.info(f"Stored movie: {movie_data['title']} (TMDB ID: {movie_data['tmdb_id']})")

# Combine genres, keywords, and overview into a single string for TF-IDF
def combine_movie_features(movie):
    combined_features = " ".join(movie['genres']) + " " + " ".join(movie['keywords']) + " " + movie['overview']
    return combined_features

# Compute cosine similarity using TF-IDF vectorization
def compute_similarity_with_tfidf(movies):
    combined_features = [combine_movie_features(movie) for movie in movies]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(combined_features)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

# Create edges for recommendations based on cosine similarity
def create_edges_for_movie(movie, all_movies, similarity_matrix, movie_index):
    similar_movies = []
    movie_similarities = similarity_matrix[movie_index]
    
    for i, similarity_score in enumerate(movie_similarities):
        if i != movie_index and similarity_score > 0.2:  # Threshold for similarity
            similar_movies.append({'tmdb_id': all_movies[i]['tmdb_id'], 'similarity_score': similarity_score})
    
    return similar_movies

# Store movie with its edges in MongoDB
def store_movie_with_edges(movie, all_movies, similarity_matrix, movie_index):
    similar_movies = create_edges_for_movie(movie, all_movies, similarity_matrix, movie_index)
    movie['similar_movies'] = similar_movies
    store_movie(movie)
    logging.info(f"Stored movie with edges: {movie['title']} (TMDB ID: {movie['tmdb_id']})")

# Fetch a batch of movies from TMDB
def fetch_movies_batch(page=1, max_pages=5):
    all_movies = []
    for p in range(page, page + max_pages):
        url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&page={p}"
        response = requests.get(url).json()
        if 'results' in response:
            for movie in response['results']:
                movie_data = get_tmdb_metadata(movie['title'])  # Fetch enriched movie data from TMDB
                if movie_data:
                    all_movies.append(movie_data)
                    logging.info(f"Fetched movie: {movie_data['title']} (TMDB ID: {movie_data['tmdb_id']})")
    return all_movies

# Fetch and store movies in batches and compute similarity
def fetch_and_store_movies_with_similarity_in_batches(start_page=1, max_pages=5):
    page = start_page
    while True:
        batch_movies = fetch_movies_batch(page=page, max_pages=max_pages)
        if not batch_movies:
            logging.info(f"No more movies to fetch at page {page}.")
            break
        
        similarity_matrix = compute_similarity_with_tfidf(batch_movies)
        
        for index, movie in enumerate(batch_movies):
            store_movie_with_edges(movie, batch_movies, similarity_matrix, index)
        
        logging.info(f"Finished fetching and storing movies from page {page}.")
        page += max_pages

# Background thread for fetching movies in batches
def background_fetch_movies():
    start_page = 1
    max_pages = config.get('batch_size', 5)  # Use batch size from config or default to 5
    sleep_interval = config.get('sleep_interval', 60)  # Default sleep interval to 60 seconds
    
    while True:
        logging.info(f"Fetching movies from page {start_page}...")
        fetch_and_store_movies_with_similarity_in_batches(start_page=start_page, max_pages=max_pages)
        
        start_page += max_pages
        
        logging.info(f"Sleeping for {sleep_interval} seconds before fetching more movies.")
        time.sleep(sleep_interval)

# Start the background thread for fetching movies
def start_background_fetching():
    logging.info("Starting background fetching process...")
    threading.Thread(target=background_fetch_movies, daemon=True).start()

# Process and update the RSS feed movies from the YAML config
def process_rss_feed_and_store_movies_from_yaml():
    rss_movies = config.get('rss_feed', [])
    enriched_movies = enrich_movies_with_tmdb(rss_movies)  # Enrich RSS movies with TMDB data

    for rss_movie in enriched_movies:
        movie_data = movies_collection.find_one({'tmdb_id': rss_movie['tmdb_id']})
        
        # If the movie is already in the database, update its info
        if movie_data:
            movie_data.update(rss_movie)
            store_movie(movie_data)
        else:
            store_movie(rss_movie)
    
    # If there are new movies, compute similarities and store them
    if enriched_movies:
        similarity_matrix = compute_similarity_with_tfidf(enriched_movies)
        for index, movie in enumerate(enriched_movies):
            store_movie_with_edges(movie, enriched_movies, similarity_matrix, index)
    
    # Update the YAML file with new data if needed
    update_rss_feed_data(rss_movies, enriched_movies)
    logging.info("RSS feed processed and stored to MongoDB.")

# Example: Process the RSS feed from YAML and start background fetching
process_rss_feed_and_store_movies_from_yaml()


logging.info("RSS feed processed and background fetching started.")
