from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import streamlit as st
import os
from langchain_core.prompts import PromptTemplate

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


template = PromptTemplate(
    template="""
Please summarize the research paper titled "{paper_input}" with the following specifications:
Explanation Style: {style_input}  
Explanation Length: {length_input}  
1. Mathematical Details:  
   - Include relevant mathematical equations if present in the paper.  
   - Explain the mathematical concepts using simple, intuitive code snippets where applicable.  
2. Analogies:  
   - Use relatable analogies to simplify complex ideas.  
If certain information is not available in the paper, respond with: "Insufficient information available" instead of guessing.  
Ensure the summary is clear, accurate, and aligned with the provided style and length.
""",
input_variables=['paper_input', 'style_input','length_input'],
validate_template=True
)


prompt = template.invoke({
    "paper_input": paper_input,
    "style_input": style_input,
    "length_input": length_input
})

if st.button("Summarize"):
    response = chatModel.invoke(prompt)
    st.subheader("Summary:")
    st.write(response.content)