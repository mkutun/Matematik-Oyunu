# app.py

import streamlit as st
import time

# --- Oturum Durumu Başlatma ---
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'used_topics' not in st.session_state:
    st.session_state.used_topics = []
if 'leaderboard' not in st.session_state:
    st.session_state.leaderboard = {}
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None
if 'solution' not in st.session_state:
    st.session_state.solution = None
if 'solution_visible' not in st.session_state: 
    st.session_state.solution_visible = False 
if 'solution_requested' not in st.session_state: 
    st.session_state.solution_requested = False 


# Sayfa yapılandırması (Menüdeki başlığı düzeltir)
st.set_page_config(
    page_title="Ana Sayfa", 
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🧠 Yapay Zeka Destekli Matematik Oyununa Hoş Geldin!")

# Sol menü başlıkları için
st.sidebar.markdown("# Ana Sayfa") 
st.sidebar.markdown(f"## Skor: {st.session_state.score}")

# --- Kullanıcı Adı Girişi ve Çıkış ---

# Menüden çıkış yapma fonksiyonu (Oyun Alanı'ndan geri dönünce oturumu sıfırlar)
def handle_exit():
    # Skor kaydı Oyun Alanı'nda yapıldı. Burada sadece oturumu sıfırlıyoruz.
    st.session_state.username = ""
    st.session_state.score = 0
    st.session_state.current_question = None
    st.session_state.used_topics = []
    st.session_state.last_answer = None
    st.session_state.solution = None
    st.session_state.solution_visible = False
    st.session_state.solution_requested = False
    st.info("Oturum sonlandırıldı. Tekrar başlamak için kullanıcı adınızı girin.")


if st.session_state.username and st.button("Çıkış Yap ve Oturumu Sıfırla", on_click=handle_exit, type="secondary"):
    pass 
elif not st.session_state.username:
    # Kullanıcı adı girişi
    st.session_state.username = st.text_input(
        "Lütfen adını/kullanıcı adını gir:", 
        value="", 
        key="username_input"
    )


if st.session_state.username:
    st.success(f"Hoş geldin, **{st.session_state.username}**! Oyuna hazırsın.")
    st.info("Oyuna başlamak için sol menüdeki **Oyun Alanı** sayfasına geç.")
    
    st.markdown("---")
    st.subheader("Mevcut Puan Durumun:")
    st.metric(label="Toplam Puan", value=st.session_state.score)

else:
    st.warning("Lütfen başlamak için bir kullanıcı adı gir.")