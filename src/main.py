import streamlit as st
import openai
import pinecone
import uuid

st.set_page_config(
    page_title="Have a chat.",
    page_icon="👋",
)

st.title("AI Assistant")

system_message = {"role": "system", "content": "You are Artie's personal assistant."}

# Seed a system message for our companion using built-in state management
if "system_message" not in st.session_state:
    st.session_state["system_message"] = [
        system_message,
    ]

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        system_message,
    ]

if "latest_conversation" not in st.session_state:
    st.session_state["latest_conversation"] = []

# Displays previous messages
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# Create input area and generate completions
if prompt := st.chat_input():
    openai.api_key = st.secrets["openai_api_key"]

    pinecone.init(
        api_key=st.secrets["pinecone_api_key"], 
        environment=st.secrets["pinecone_environ"],
    )
    index = pinecone.Index("chat")

    # Find relevant context
    encoded_prompt = openai.Embedding.create(
        input=prompt,
        engine="text-embedding-ada-002",
    )["data"][0]["embedding"]

    prompt_neighbors = index.query(encoded_prompt, top_k=3, include_metadata=True)

    context = []
    matches = prompt_neighbors["matches"]

    # Build context here
    if matches:
        for neighbor in matches:
            try: 
                if role := neighbor["metadata"]["role"]:
                    points_to = neighbor["metadata"]["points_to"]

                    context.append({
                        "role": role,
                        "content": neighbor["metadata"]["content"]
                    })
            
                    if points_to:
                        partner = index.fetch(ids=[points_to])["vectors"][points_to]["metadata"]["content"]
                        
                        if role == "assistant":
                            context.insert(len(matches)-1, {"role": "user", "content": partner})
                        elif role == "user":
                            context.append({"role": "assistant", "content": partner})
            except:
                if content := neighbor["metadata"]["content"]:
                    context.append({"role": "user", "content": f"For contex...\n{content}"})

    user_message = {"role": "user", "content": prompt}

    if st.session_state["latest_conversation"]:
        context.extend(st.session_state["latest_conversation"])

    context.append(user_message)
    context.insert(0, system_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        assistant_chat = st.empty()
        st.session_state["messages"].append(user_message)

        # Stream
        in_progress = ""
        print(context)
        for chunk in openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=context,
            temperature=0.7,
            max_tokens=4000,
            stream=True,
        ):
            delta = chunk.choices[0].delta.get("content", "")
            in_progress += delta
            assistant_chat.markdown(in_progress)
        
        encoded_response = openai.Embedding.create(
            input=in_progress,
            engine="text-embedding-ada-002",
        )["data"][0]["embedding"]

        vecs = [
            encoded_prompt,
            encoded_response
        ]

        ids = [
            str(uuid.uuid4()) for _ in vecs
        ]

        metadata = [
            {"role": "user", "content": prompt, "points_to": ids[1]},
            {"role": "assistant", "content": in_progress, "points_to": ids[0]}
        ]

        index.upsert(
            vectors=zip(ids, vecs, metadata)
        )
        
        assistant_message = {"role": "assistant", "content": in_progress}

        st.session_state["latest_conversation"] = [
            user_message,
            assistant_message,
        ]

        st.session_state["messages"].append(assistant_message)