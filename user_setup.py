import yaml
import os

def init_config(f_path='config.yaml'):
    if not os.path.exists(f_path):
        default_config = { 
            'rss_feed_url': 'https://letterboxd.com/fakefriend/rss/',  # Initial placeholder
            'rss_feed': [],  # To store enriched movies from the RSS feed
            'batch_size': 5,  # Number of pages (or 100 movies) to fetch per batch
            'sleep_interval': 300,  # Time (in seconds) between API calls
            'user_preferences': {
                'update_frequency': 'weekly',  # Options: daily, weekly, etc.
                'genre_filter': [],  # Filter by genres
                'runtime_filter': {'min': 60, 'max': 270}  # Runtime filtering
            }
        }
        with open(f_path, 'w') as file:
            yaml.safe_dump(default_config, file)
        print(f'User config initialized at {f_path}')
    else:
        print(f'User config already initialized at {f_path}')

# Load the YAML config file
def load_config(f_path='config.yaml'):
    if os.path.exists(f_path):
        with open(f_path, 'r') as file:
            return yaml.safe_load(file)
    else:
        return {"rss_feed": [], "user_preferences": {}, "batch_size": 5, "sleep_interval": 300}

# Write updates to the YAML config file
def write_config(config_data, f_path='config.yaml'):
    with open(f_path, 'w') as file:
        yaml.safe_dump(config_data, file)

# Update RSS movies in the YAML config
def update_rss_feed_data(rss, enriched_movies, f_path='config.yaml'):
     # Load the existing config
    config = load_config(f_path)
    existing_movies = config.get('rss_feed', [])
    
    # Update existing movies and append new ones
    for movie in enriched_movies:
        match = next((m for m in existing_movies if m['tmdb_id'] == movie['tmdb_id']), None)
        if match:
            # Remove or convert non-serializable fields like 'similar_movies' before storing
            if 'similar_movies' in movie:
                movie['similar_movies'] = [
                    {
                        'tmdb_id': sm['tmdb_id'],
                        'similarity_score': str(sm['similarity_score'])  # Convert similarity score to string
                    }
                    for sm in movie['similar_movies']
                ]
            match.update(movie)  # Update existing movie details
        else:
            # Handle new movie similarly
            if 'similar_movies' in movie:
                movie['similar_movies'] = [
                    {
                        'tmdb_id': sm['tmdb_id'],
                        'similarity_score': str(sm['similarity_score'])  # Convert similarity score to string
                    }
                    for sm in movie['similar_movies']
                ]
            existing_movies.append(movie)  # Add new movie
    
    # Write the updated config back to the YAML file
    config['rss_feed'] = existing_movies
    write_config(config, f_path)   

# Update user preferences in the YAML config
def update_user_preferences(new_preferences, f_path='config.yaml'):
    config = load_config(f_path)
    
    # Update preferences
    config['user_preferences'].update(new_preferences)
    
    # Write the updated preferences back to the YAML file
    write_config(config, f_path)
    print('User config updated successfully')
