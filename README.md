# Big Data Project 
##### Jayden Ferguson 

---
###### Preface 

Main_test.py was only used to test user config initilaization and functions 

## Initial idea 

My inital idea was to expand upon an idea from last semester creating a recommendation system with a more efficent algorithm instead of KNN. 
When I found the dataset I thought that I had enough tools to successfully create a recommendation system, something akin to the Netflix homepage with anGUI interface and the ability to connect a users letterboxd to create a baseline for the model to branch off considering the size of the dataset I choose.I also figured that I would use libraries such as polars which are written in rust which has more efficent functions than something like pandas to storeand structure the data. Specifically I wanted to use a mix of chunking and lazy loading the data, fetching the data in batches and applyng lazy computationon the data when needed. As I learned more about the algorithms and systems used in recommendation systems I knew I wanted to apply many of the techniques such as different levels of vectorization and distance calculation to find the best recommendations for the user.

## Challenges and Setbacks 

One of the early issues I faced was with the letterboxd api, which hindered my ability to use collabrative filtering techniques since the user would not be able to interact with the recommendation or link connections without access to the endpoints. This left me with only able to process the RSS feed thatletterboxd provides to create a baseline of user data. While I was able to overcome that setback, and even called on the original API to bolster the datathat was returned from that RSS feed the next challenge I routinely faced as I tried to iteratively expand on the project was the limitation or my misunderstanding of polars. Due to the complexity and explicitness of rust, I found that I was often fighting the compiler or looking at the stack traces polars provided when it came time to process categorical data and the list of strings I needed for vectorization. Paired with that was the high computational usage that tf-idf vectorization and the vectorization needed for cosine similairty, to get the resulting similairty matrix my shell would often kill itself before getting through even half the batches or chunks of data I attempted to use. Even with polars explicit nature casting and mapping certain features to i8 or f32 over the i32 and f64 data types did not help at all. I tried to bite the bullet and write some of the more computationally taxing components of the project in pure rust for the memory management and the speed of processing versus python to no success. I even tried processing the data into JSON format to try and keep consistent data structures throughout. My final idea was to put the data into a database, but it didn't feel right to put kaggle data into a database when I didn't go and clean the data myself outside of the rss feed. 

## Current Implementation and Big Data processing 

Since I was having problems processing the big data I decided to research a few techniques when it came to handling large datasets. As I metioned before I didn't feel comformtable putting data I didn't retrive and process myself in a database especially a database I thought to use in a standalone application that I planned to use often and develop more, so in turn since I have experience with the API I thought to create my own large data. My idea was to fill the database to something along the lines of 100-500,000 different films including the ability to update from the rss feed and instead of producing ahome page like GUI, I thought to keep a minimilistic and very visual graph strucutred visualization in the application. Since this was meant to be a local application I tried to keep everything python and with as little obtrusion to the user as possible. 
The structure the application flows like this:
1. The user inputs their letterboxd username to get their rss feed for a baseline (Required)
2. The rss data is then blostered and enriched with the proper features from the TMDB api 
3. The rss feed is processed and is stored and kept presistent through a config file 
4. A noSQL database is initialized (required) and the rss feed is initially processed 
5. As the user is using the application the TMDB api is called in batches and gather N amount of movies per page of the api as it is called it goes through the same vectorization steps and is saved to the database. 
    - The reason I went with mongo over a graph database was because it allowed for a little flexibility. Even though this ended up with a graph structure I would evenetually think about using a graph database like Neo4j for the speed of query. 
6. Right now there is alot of boilerplate and proof of concept ideas in the creation of the GUI and canvas (the randomness) the idea is that intially once the user config is created the graph is initialized with that data and that is what you see but as you go around and use the application new nodes and edges will naturally pop up similar to a mindmap and heavily inspired by the obisidan mind map. 

#### Current Issues 
The biggest issue currently a graphical bug, which is forgetting to redraw the canvas on update and not giving the system time to process the computation and drawing of new nodes and edges. 

## Further Development 
While I am not proud of the current state of the application at this point I do think that I will continue working on this project for the time being. I figured it would be a good opporutunity to create a recommendation algorithm after looking at data engineering internship roles and what they're looking for after going to the career center. I do eventually want to have this in a state that I feel comfortable showing off to others. 

## Readability 
I tried to keep functions as readable as possible since this is my 6th overall implementation of a system like this 
```bash
├── ballad
|  ├── README.md
|  ├── __pycache__
|  ├── config.yaml
|  ├── db_management.py
|  ├── main.py
|  ├── main_test.py
|  ├── rss_data.py
|  └── user_setup.py
├── data
|  ├── guess_who.csv
|  └── movie_show.csv
├── graph_recommendation
|  ├── node_processing.py
|  └── user_dataset.json
├├── recommendation
|  ├── Cargo.lock
|  ├── Cargo.toml
|  ├── __pycache__
|  ├── content_filtering.py
|  ├── data_processing.py
|  ├── driver.py
|  ├── gui.py
|  ├── lib.py
|  ├── rss_feed.py
|  ├── sources.txt
|  ├── src
|  ├── target
|  └── user_profile.py
└── rl_recs
   ├── __pycache__
   ├── graph_approach.py
   ├── main.py
   └── movies_data.json
```
Eventually once it is done I do plan on talking about this in video format. I feel like I learned alot about processing and working with big data, I would like to follow up on better techniques instead of defaulting to a noSQL database. I also learned alot about both collabrative and content based filtering algorithms along with methods that go with it, furthermore, I found alot of interesting techniques and methods from hybrid, neural network, and reinforcement learning apporachs that I would be interested in trying and implmenting. 

#### Sources 

- QT documentation 
- TMDB API documentation 
- Old KNN recommendation system 
- Old Chess engine 
- Medium Blogs (Recommendation algorithm and Big data techniques)


###### Only realizing this after github would not allow me to upload the config file
The structure is something like this 
```
batch_size: 5
rss_feed:
- genres:
  - Drama
  keywords:
  - found footage
  language: ja
  overview: In Tokyo, a Goth girl and an Internet voyeur connect in the post 9-11
    world of surveillance and paranoia.
  popularity: 1.096
  rating: '3.0'
  runtime: 98
  similar_movies: []
  title: Peep "TV" Show
  tmdb_id: 210736
- genres:
  - Crime
  - Thriller
  - Drama
  keywords:
  - daughter
  - journalist
  - sadistic
  - mass murder
  - yellow press
  - pop culture
  - trauma
  - controversy
  - satire
  - young couple
  - abuse
  language: en
  overview: Two victims of traumatized childhoods become lovers and serial murderers
    irresponsibly glorified by the mass media.
  popularity: 25.963
  rating: '3.5'
  runtime: 118
  similar_movies: []
  title: Natural Born Killers
  tmdb_id: 241
rss_feed_url: https://letterboxd.com/fakefriend/rss/
sleep_interval: 300
user_preferences:
  genre_filter: []
  runtime_filter:
    max: 270
    min: 60
  update_frequency: daily
```
There was alot of config file modification that I didn't get to implment yet
