from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import streamlit as st
import os
from langchain_core.prompts import PromptTemplate,load_prompt

load_dotenv()

hf_token = os.getenv("HUGGINGFACE_API_KEY")
model_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm = HuggingFaceEndpoint(
        repo_id = model_id,
        task="text2text-generation",
        huggingfacehub_api_token=hf_token,
    )

chatModel = ChatHuggingFace(llm=llm)

st.header("Summarization using Hugging Face Api")

paper_input = st.selectbox("Select a research paper to summarize : ",
    ["Attention Is All You Need",
    "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
    "GPT-3: Language Models are Few-Shot Learners",
    "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
    "T5: Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer"]
)

style_input = st.selectbox("Select the style of summarization : ",
    ["Technical Summary",
    "Layman Summary",
    "Bullet Point Summary",
    "Math-Heavy Summary",
    "Code-Heavy Summary"]
)

length_input = st.selectbox("Select the length of the summary : ",
    ["Very Short (1-2 sentences)",
    "Short (3-5 sentences)",
    "Medium (1 paragraph)",
    "Long (2-3 paragraphs)",
    "Very Long (4+ paragraphs)"]
)



template= load_prompt("template.json")
  

if st.button("Summarize"):
    chain = template | chatModel
    response = chain.invoke({
        "paper_input": paper_input,
        "style_input": style_input,
        "length_input": length_input
    })
    st.subheader("Summary:")
    st.write(response.content)