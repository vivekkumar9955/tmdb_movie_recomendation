import streamlit as st
import pickle
import pandas as pd
import requests
import gdown

# TMDB API Key
API_KEY = '91bb3be760d3f4d1bb9081511fb91109'

# Function to fetch poster with error handling
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en',
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return "https://image.tmdb.org/t/p/w500" + data['poster_path']
    except Exception as e:
        st.error(f"Failed to fetch poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=No+Image"

# Function to fetch movie details
def fetch_movie_details(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en',
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch movie details: {e}")
        return {}
    
# Recommendation function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_ids = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].id
        recommended_ids.append(movie_id)
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters, recommended_ids

# Load movie data and similarity matrix
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title('🎬 Movie Recommendation System')

# Read URL query parameters
query_params = st.query_params
movie_id_clicked = query_params.get("movie_id")

# If poster was clicked, show detailed movie info
if movie_id_clicked:
    movie_data = fetch_movie_details(movie_id_clicked)
    if movie_data:  
        st.subheader(f"You clicked on: {movie_data.get('title', 'Unknown')}")
        st.image("https://image.tmdb.org/t/p/w500" + movie_data.get('poster_path', ''))
        st.markdown(f"**Overview:** {movie_data.get('overview', 'No overview available.')}")
        st.markdown(f"**Rating:** {movie_data.get('vote_average', 'N/A')} / 10")
        st.markdown("---")

# Dropdown for selecting a movie
selected_movie_name = st.selectbox("Select a movie:", movies['title'].values)

# On button click, show recommendations
if st.button("Recommend"):
    names, posters, ids = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <a href="?movie_id={ids[idx]}" target="_self">
                    <img src="{posters[idx]}" width="100%"/><br>
                    <center><b>{names[idx]}</b></center>
                </a>
                """,
                unsafe_allow_html=True
            )
            #for create command requirements.txt file
#pip freeze > requirements.txt