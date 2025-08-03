import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster from TMDB API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# Load data
@st.cache_data  # Cache the data for better performance
def load_data():
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()
movies_list = movies['title'].values  # For dropdown options

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:  # Get top 5 recommendations
        movie_id = movies.iloc[i[0]].movie_id
        try:
            recommended_movie_posters.append(fetch_poster(movie_id))
            recommended_movie_names.append(movies.iloc[i[0]].title)
        except:
            # Skip if poster can't be loaded
            continue
    return recommended_movie_names, recommended_movie_posters

# Streamlit UI
st.title('Movie Recommender System')

# Add some styling
st.markdown("""
<style>
    .stSelectbox {margin-bottom: 20px;}
    .stButton button {width: 100%;}
    .recommendation {text-align: center;}
</style>
""", unsafe_allow_html=True)

selected_movie_name = st.selectbox('Select a movie you like:', movies_list)

if st.button('Get Recommendations'):
    with st.spinner('Finding similar movies...'):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie_name)
    
    if not recommended_movie_names:
        st.warning("Couldn't find recommendations for this movie. Please try another one.")
    else:
        st.success("Here are some movies you might like:")
        
        # Display recommendations in columns
        cols = st.columns(5)
        for i in range(min(5, len(recommended_movie_names))):  # Ensure we don't exceed available recommendations
            with cols[i]:
                st.image(recommended_movie_posters[i], use_container_width=True)
                st.markdown(f"<div class='recommendation'>{recommended_movie_names[i]}</div>", unsafe_allow_html=True)
