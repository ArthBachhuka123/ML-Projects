import streamlit as st
import pandas as pd
import numpy as np
import pickle
import nltk
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nltk.download('wordnet')

tfidf = pickle.load(open("../data/vectorizer.pkl", 'rb'))
model = pickle.load(open("../data/model.pkl", 'rb'))

import string
def text_transform(text):
  exclude = string.punctuation
  text = text.lower()
  text = nltk.word_tokenize(text)

  y= []
  for word in text :
    if word.isalnum():
      y.append(word)
  text = y[:]
  y.clear()

  for word in text:
    if word not in nltk.corpus.stopwords.words('english') and word not in string.punctuation:
      y.append(word)
  text = y[:]
  y.clear()

  for word in text:
    y.append(nltk.stem.WordNetLemmatizer().lemmatize(word))
  return " ".join(y)
  text = y[:]
  y.clear()
  return text

import streamlit as st

st.set_page_config(page_title="SMS Spam Detector", page_icon="📩")

# Page Title
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>📩 SMS Spam Detector</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:gray;'>Let’s find out if that message is spam or safe ✅</h4>", unsafe_allow_html=True)

sms = st.text_input("Type your SMS below:", placeholder="Enter SMS")

if st.button("Analyze Message 🔍"):
    if sms.strip() == "":
        st.warning("Enter a message first 😄")
    else:
        text = text_transform(sms)
        VECTORIZED_TEXT = tfidf.transform([text])
        prediction = model.predict(VECTORIZED_TEXT)[0]

        if prediction == 1:
            st.error("🚫 This message looks like **Spam**!", icon="⚠️")
        else:
            st.success("✅ You're good! This message seems **Safe**.", icon="✔️")

# Footer
st.markdown("<br><hr><p style='text-align:center;'>Made by Arth Bachhuka</p>", unsafe_allow_html=True)




