import streamlit as st
import numpy as np
import requests
import json
from datetime import datetime, timezone
import uuid

def main():
    
    st.set_page_config(page_title='Realmate Challenge' ,layout="wide",page_icon='👨‍🔬')
    st.header('Realmate Challenge')
    
    conversations = get_conversations()    
    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.subheader("Open Conversations:")
        for conversation in conversations:
            if conversation["state"] == "OPEN":
                c1, c2 = st.columns([4, 1])  # Layout para ID e botão de fechar
                with c1:
                    if st.button(conversation["id"]):
                        st.session_state.selected_conversation = conversation
                with c2:
                    if st.button("❌", key=f"close_{conversation['id']}"):
                        close_conversation(conversation["id"])
                        st.session_state.selected_conversation = None
                        st.rerun()

        # Botão para adicionar nova conversa
        if st.button("➕ New Conversation"):
            new_conversation_id = str(uuid.uuid4())  # Gera um ID único
            new_conversation(new_conversation_id)
            st.session_state.selected_conversation = get_conversation(new_conversation_id)
            st.rerun()
        
    with col2:
        if st.session_state.selected_conversation:
            updated_conversation = get_conversation(st.session_state.selected_conversation["id"])
            st.session_state.selected_conversation = updated_conversation
            conversation = updated_conversation
            if conversation:
                with st.container(border=True, height=500):
                    for message in conversation["messages"]:
                        if message["direction"] == "SENT":
                            with st.chat_message("user"):
                                st.write(message["content"])
                        else:
                            with st.chat_message("assistant"):
                                st.write(message["content"])

                i, b1, b2 = st.columns([8, 1, 1], vertical_alignment="bottom", gap="small")

                content = i.text_input("Digite sua mensagem", key="msg_input")

                if b1.button("SENT") and content:
                    send_message(conversation["id"], content)
                    st.rerun()

                if b2.button("RECEIVED") and content:
                    receive_message(conversation["id"], content)
                    st.rerun()

def new_conversation(conversation_id):
    """Função para simular o webhook de criação de conversa"""
    payload = {
        "type": "NEW_CONVERSATION",
        "timestamp": st.session_state.get("current_time", "2025-02-21T10:20:41.349308"),
        "data": {"id": conversation_id}
    }
    process_webhook(payload)

def close_conversation(conversation_id):
    """Função para simular o webhook de fechamento de conversa"""
    payload = {
        "type": "CLOSE_CONVERSATION",
        "timestamp": st.session_state.get("current_time", "2025-02-21T10:20:45.349308"),
        "data": {"id": conversation_id}
    }
    process_webhook(payload)
    
def send_message(conversation_id, content):
    payload = {
        "type": "NEW_MESSAGE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "id": f"msg-{datetime.now(timezone.utc).timestamp()}",  # ID único baseado no timestamp
            "conversation_id": conversation_id,
            "direction": "SENT",
            "content": content
        }
    }
    process_webhook(payload)
    
def receive_message(conversation_id, content):
    payload = {
        "type": "NEW_MESSAGE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "id": f"msg-{datetime.now(timezone.utc).timestamp()}",  # ID único baseado no timestamp
            "conversation_id": conversation_id,
            "direction": "RECEIVED",
            "content": content
        }
    }
    process_webhook(payload)

def process_webhook(payload):
    WEBHOOK_URL = "http://127.0.0.1:8000/webhook/"
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()  # Lança uma exceção para erros HTTP (4xx e 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def get_conversation(id):
    url = f"http://127.0.0.1:8000/conversations/{id}/" 
    response = requests.get(url)
    if response.status_code == 200:
        conversation = response.json()
        return conversation
    else:
        st.error(f"Erro ao acessar a API: {response.status_code}")
        return None

def get_conversations():
    url = f"http://127.0.0.1:8000/api-auth/conversations/"
    response = requests.get(url)
    if response.status_code == 200:
        conversations = response.json()
        return conversations
    else:
        st.error(f"Erro ao acessar a API: {response.status_code}")
        return None

if __name__ == '__main__':
    main()