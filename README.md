# RAG_Chatbot

## Description
Retrieval Augmented Generation (RAG) is one of the latest solutions to resolving the built-in context limits in traditional large language models like ChatGPT. It aims to introduce context from outside sources of information by using algorithms to query for outside information such as adding context from a search engine retrieval or from data stored in a vector database.

This project implements my own interpretation of the solution. 

The user will be able to add additional context to chatbot generations by uploading a PDF, and the chatbot's knowledge of the user will grow as the user continues using it.

## How to Run

First, make sure your computer has Streamlit installed.

Then, you will need API keys for Pinecone and OpenAI.

After, create a Pinecone index, and name it "chat."

Create a folder named `.streamlit` in the `src ` folder. Inside `.streamlit`, create a `secrets.toml` file. Input your API keys as follows:
`openai_api_key="api_key"
pinecone_api_key="api_key"
pinecone_environ="gcp-starter"
`
_Replace with actual keys_

## APIs
- **Pinecone**: Vector database solution. Query to add additional context for the generation.
- **OpenAI**: Use to generate completions.
- **Streamlit**: Used for visual display, managing API keys, and document upload.

## Steps in the Process
1) Upload PDFs for additional context.
2) User will type message in Streamlit interface.
3) The user's message is vectorized using OpenAI's embedding engine.
4) Vectorized message is used to query Pinecone DB and retrieve relevant context.
5) Context is added to a data structure with last message and system message.
6) Context is sent to GPT-4 to create a completion.
7) The latest message is inserted into the Pinecone index to be retrieved for future tasks.
