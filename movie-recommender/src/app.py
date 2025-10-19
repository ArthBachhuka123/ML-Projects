import requests
import streamlit as st
import pickle
import pandas as pd
import os

BASE_DIR = os.path.dirname(__file__)  # src folder
DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # move up to repo root then data

movies = pickle.load(open(os.path.join(DATA_DIR, "movies.pkl"), "rb"))
similarity = pickle.load(open(os.path.join(DATA_DIR, "similarity.pkl"), "rb"))
movies_list = movies["title"].values


API_KEY = st.secrets["TMDB_API_KEY"]

def fetch_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    similar_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_poster = []

    for i in similar_movies:
        movie_row = movies.iloc[i[0]]
        actual_id = movie_row.movie_id
        data = fetch_data(actual_id)
        poster_path = data.get("poster_path", None)

        if poster_path is None:
            print("No poster_path found for this movie:", data)
            poster_url = "https://example.com/default-poster.jpg"  # fallback
        else:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

        recommended_movies.append(movie_row.title)
        recommended_movie_poster.append(poster_url)

    return recommended_movies, recommended_movie_poster


st.title("Movie Recommender System")
st.header("This is a movie Recommender system.")
st.write("Write the name of the movie for which you want recommendations")

# Input
selected_movie_name = st.selectbox("Select Movie", movies_list)

# Button
if st.button("Suggest"):
    recommended_movies_title,recommended_movies_poster = recommend(selected_movie_name)
    cols = st.columns(5)
    for i in range(len(recommended_movies_title)):
        with cols[i]:
            st.image(recommended_movies_poster[i], use_container_width=True)
            st.caption(recommended_movies_title[i])
