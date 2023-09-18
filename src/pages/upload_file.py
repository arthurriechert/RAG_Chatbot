import streamlit as st
import openai
import pinecone
import uuid
from pdfminer.high_level import extract_text

file = st.file_uploader("Upload a file.")

if file:

    text = ""

    with st.spinner("Extracting text..."):
        text = extract_text(file)

    st.success("Extracted text from PDF!")

    with st.spinner("Indexing PDF..."):
        openai.api_key = st.secrets["openai_api_key"]

        words = text.split()
        segments = [' '.join(words[i:i+1000]) for i in range(0, len(words), 1000)]

        pinecone.init(
            api_key=st.secrets["pinecone_api_key"], 
            environment=st.secrets["pinecone_environ"],
        )
        index = pinecone.Index("chat")
        vecs = []
        metadata =[]

        for segment in segments:
            vecs.append(
                openai.Embedding.create(
                    engine="text-embedding-ada-002",
                    input=segment
                )["data"][0]["embedding"]
            )
            metadata.append({"role": "system", "content": segment, "points_to": ""})

        ids = [
            str(uuid.uuid4()) for _ in vecs
        ]

        index.upsert(
            vectors=zip(ids, vecs, metadata)
        )

    st.success("Successfully indexed file!")

