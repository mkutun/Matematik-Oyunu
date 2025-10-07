# pages/1_Oyun_Alanı.py

import streamlit as st
import json
import time
from google import genai
from google.generativeai import types

# --- Çözüm İsteme Promptu ---
def create_solution_prompt(question, correct_answer):
    """Yapay zekadan detaylı çözüm ve kısayol isteyen prompt'u oluşturur."""
    return f"""
Aşağıdaki matematik probleminin detaylı adım adım çözümünü ve mümkünse bir de kısayol çözümünü (pratik yolunu) oluştur.
Çözümü ve kısayolu Türkçe ve düzgün bir formatta, Markdown kullanarak hazırla.
Sorunun Metni: "{question}"
Doğru Cevap: "{correct_answer}"

### Kısayol Format Kuralı (Çok Önemli)
Kısayol çözüm, mümkünse sorunun çözümünü sadece aritmetik işlemleri göstererek (Örn: 18/2*5=45 gibi) veya en fazla iki kısa cümle ile açıklamalıdır. Uzun bir açıklama veya tekrar detaylı çözümün özetlenmesi KESİNLİKLE YASAKTIR.

### Çıktı Formatı
Yanıtını kesinlikle sadece tek bir JSON formatında döndür. Bu JSON'un dışında hiçbir açıklama veya ek metin OLMAMALIDIR.

{{
  "detayli_cozum": "[Sorunun adım adım, anlaşılır detaylı çözümünü yaz. Formül gerekiyorsa LaTeX kullan]",
  "kisayol_cozum": "[Sorunun en pratik, en kısa çözüm yolunu veya aritmetik işlemini göster. Örn: '18/2 * 5 = 45'. Yoksa 'Kısayol bulunmamaktadır.' yaz.]"
}}
"""

# --- Çözüm Getirici Fonksiyon ---
@st.cache_data(show_spinner=False)
def get_ai_solution(question, correct_answer):
    """Gemini API'sini kullanarak çözüm ve kısayol getirir."""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        return {"detayli_cozum": "API anahtarı eksik.", "kisayol_cozum": "API anahtarı eksik."}

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"
    prompt = create_solution_prompt(question, correct_answer)

    config_dict = {
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "detayli_cozum": {"type": "string"},
                "kisayol_cozum": {"type": "string"}
            }
        }
    }

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_dict 
        )
        
        json_response_str = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_response_str)

    except Exception as e: 
        return {"detayli_cozum": f"Çözüm getirilemedi. API Hatası: {e}", "kisayol_cozum": ""}


# --- Ana Prompt Oluşturucu Fonksiyon: SYNTAX HATASI KESİN DÜZELTİLDİ ---
def create_master_prompt(difficulty, used_topics):
    """Yapay zekaya gönderilecek kısıtlı prompt metnini oluşturur."""
    topics_str = ", ".join(used_topics) if used_topics else "Henüz konu kullanılmadı."
    
    master_prompt = f"""
Sen bir Matematik Oyun Sistemi için gelişmiş bir soru üretme motorusun.
Amacın, belirtilen zorluk seviyesine uygun, **daha önce ürettiğin hiçbir soruya benzemeyen** ve oyuncuyu meşgul edecek tek bir matematik problemi ve cevabını üretmektir.
Lütfen ürettiğin soruyu **Türkçenin doğru standartlarında** ve net bir şekilde yaz. 

### Kısıtlamalar ve Format (ÇOK ÖNEMLİ DÜZELTME)
1.  **Türkçe Karakterler:** Türkçe karakterleri (ş, ç, ğ, ı, ö, ü) kesinlikle doğru kullan. Karakterleri bozma.
2.  **JSON Ayrımı:** Soruyu kesinlikle iki ayrı alana ayır.
    a) **'soru_metni'**: Sadece Türkçe açıklamayı, formülsüz metni içerir.
    b) **'soru_formulu'**: Sadece matematiksel ifadeyi (Saf LaTeX komutları) içerir. Metin ile formülü kesinlikle karıştırma.
3.  **Çıktı Formatı:** Yanıtını kesinlikle sadece tek bir JSON formatında döndür. Bu JSON'un dışında hiçbir açıklama, giriş veya ek metin OLMAMALIDIR.

### Girdi Parametreleri
* **Zorluk Seviyesi:** [{difficulty}]
* **Önceki Soruların Temaları/Konuları (ÖNEMLİ):** [{topics_str}]

### JSON Çıktı Yapısı
Aşağıdaki yapıyı tam olarak izle:
{{
  "soru_metni": "[Sadece Türkçe metin kısmı. Örn: 'Aşağıdaki denklemin çözüm kümesini bulunuz:']",
  "soru_formulu": "[Sadece formül kısmı, LaTeX komutları ile. Örn: 'y' + 2xy = x^4']",
  "cevap": "[Sorunun doğru sayısal veya cebirsel cevabı (sadece sonuç)]",
  "konu_etiketi": "[Sorunun ait olduğu ana matematik konusu (Örn: 'Denklem Çözme', 'Oran-Orantı', 'Limit')]"
}}
Görev
Şu anki zorluk seviyesi {difficulty} ve bu seviyeye uygun, önceki sorulara benzemeyen, tek bir soru üret.
"""
    return master_prompt

# --- GERÇEK GEMINI API BAĞLANTISI ---
def get_ai_question(difficulty, used_topics):
    """Gemini API'sini kullanarak benzersiz bir matematik sorusu üretir."""
    
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("API Anahtarı bulunamadı. Lütfen '.streamlit/secrets.toml' dosyasını kontrol edin.")
        return None

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash" 
    prompt = create_master_prompt(difficulty, used_topics)
    
    config_dict = {
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "soru_metni": {"type": "string"},
                "soru_formulu": {"type": "string"}, 
                "cevap": {"type": "string"},
                "konu_etiketi": {"type": "string"}
            }
        }
    }

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config_dict 
        )
        
        json_response_str = response.text.strip()
        
        if json_response_str.startswith("```json"):
            json_response_str = json_response_str.strip().replace("```json", "").replace("```", "")
            
        return json_response_str

    except Exception as e: 
        st.error(f"API Bağlantı Hatası: Yapay zekaya ulaşılamıyor veya anahtarınız geçersiz. Hata Detayı: {e}")
        return None

# --- Yardımcı Fonksiyonlar: CEVAP KONTROLÜ HASSASİYETİ ARTIRILDI ---
def check_answer(user_answer, correct_answer):
    """Kullanıcının cevabını (sayısal veya cebirsel) doğru cevapla daha hassas karşılaştırır."""
    user_str = str(user_answer).strip().lower().replace(" ", "")
    correct_str = str(correct_answer).strip().lower().replace(" ", "")

    # 1. Tam Eşleşme Kontrolü
    if user_str == correct_str:
        return True

    # 2. Sayısal/Kesirsel Eşleşme Kontrolü
    try:
        # Pi'yi daha yüksek hassasiyetle değiştiriyoruz.
        val_user = eval(user_str.replace('pi', '3.1415926535'))
        val_correct = eval(correct_str.replace('\\pi', '3.1415926535'))

        # Yüksek hassasiyetli float karşılaştırması (10^-4 tolerans)
        TOLERANCE = 1e-4 
        if abs(float(val_user) - float(val_correct)) < TOLERANCE:
            return True
        
    except:
        # Sayısal olmayan ifadeler için
        pass
    
    return False

def get_points(difficulty):
    """Zorluğa göre puan döndürür."""
    return {"KOLAY": 10, "ORTA": 30, "ZOR": 60, "DAHA ZOR": 100}.get(difficulty, 0)

# --- Çıkış Fonksiyonu ---
def handle_exit_and_save():
    """Skoru kaydeder ve Ana Sayfa'ya yönlendirir."""
    current_username = st.session_state.get('username')
    current_score = st.session_state.get('score', 0)
    
    if current_username and current_score > st.session_state.leaderboard.get(current_username, 0):
        st.session_state.leaderboard[current_username] = current_score
        
    st.switch_page("app.py")

# --- Yeni Soru Üretme Fonksiyonu ---
def clear_question_state():
    """Yeni soru için oturum durumlarını temizler."""
    st.session_state.last_answer = None 
    st.session_state.user_answer_text = ""
    st.session_state.solution = None 
    st.session_state.solution_visible = False
    st.session_state.solution_requested = False
    st.session_state.current_question = None 

# --- Çözüm İstemeyi Tetikleme Fonksiyonu ---
def request_solution():
    """Çözümün analiz edilmesi ve gösterilmesi için bayrakları ayarlar."""
    st.session_state.solution_requested = True
    st.session_state.solution_visible = True
    # Rerun'a gerek yok, ana akışta kontrol edilecek.

# --- Ana Gövde ---
st.set_page_config(page_title="Oyun Alanı", layout="centered")

# Oturum Durumu Kontrolü (Gereken tüm session stateleri başlatıldı)

# Kullanıcı adı kontrolü
if not st.session_state.username:
    st.warning("Lütfen başlamadan önce **Ana Sayfa**'da kullanıcı adınızı giriniz.")
    st.stop()

st.title(f"🎮 {st.session_state.username} - Oyun Alanı")
st.sidebar.markdown(f"## Skor: {st.session_state.score}")

# --- Ayarlar ve Konu Takibi ---
st.sidebar.subheader("Ayarlar")
difficulty = st.sidebar.selectbox(
    "Zorluk Seviyesi Seçin:",
    ("KOLAY", "ORTA", "ZOR", "DAHA ZOR"),
    key="difficulty_select"
)

# Çıkış Butonu
st.sidebar.button("🔴 Oyunu Bitir ve Puanı Kaydet", on_click=handle_exit_and_save, type="secondary")

st.sidebar.markdown("---")
st.sidebar.subheader("Kullanılan Konular")
st.sidebar.caption(", ".join(st.session_state.used_topics) if st.session_state.used_topics else "Henüz konu kullanılmadı.")

# --- Soru Üretme Alanı ---
st.header("Mevcut Soru")

if st.button("🚀 Yeni Soru Üret", on_click=clear_question_state):
    pass

# --- Soru Üretme ve Yükleme Mantığı ---
if st.session_state.current_question is None:
    with st.spinner(f"**{difficulty}** seviyesinde benzersiz soru üretiliyor..."):
        json_response_str = get_ai_question(difficulty, st.session_state.used_topics)
        
        if json_response_str:
            try:
                question_data = json.loads(json_response_str)
                st.session_state.current_question = question_data
                
                new_topic = question_data.get("konu_etiketi")
                if new_topic and new_topic not in st.session_state.used_topics:
                    st.session_state.used_topics.append(new_topic)
                    
                st.rerun() 
                    
            except json.JSONDecodeError:
                st.error("Yapay Zeka Geçersiz JSON formatında cevap verdi. Lütfen tekrar deneyin.")
                st.session_state.current_question = None

# --- Soru Gösterimi ve Cevaplama ---
if st.session_state.current_question:
    q = st.session_state.current_question
    
    st.info(f"Konu: **{q['konu_etiketi']}** | Puan Değeri: **{get_points(difficulty)}**")
    
    # YENİ SORU GÖSTERİM MANTIĞI: KARAKTER HATASINI ÖNLEME
    
    # 1. Türkçe Metin Kısmını Göster
    if q.get('soru_metni'):
        st.write(q['soru_metni'].strip())
    
    # 2. Formül Kısmını Göster (Daha güvenilir)
    if q.get('soru_formulu'):
        # Tüm ters eğik çizgiler çift ters eğik çizgi ile değiştirilir (LaTeX için standart)
        formül_kısmı = q['soru_formulu'].strip().replace('\\', '\\\\')
        st.latex(formül_kısmı)
        
    # Eski formata göre sadece "soru_metni" alanını doldurduysa (geçici önlem)
    elif r'\int' in q.get('soru_metni', '') or r'\frac' in q.get('soru_metni', ''):
        st.markdown(q['soru_metni'].strip()) 

    st.markdown("---")
    
    # Kullanıcının Cevap Giriş Alanı
    user_answer = st.text_input(
        "Cevabın (Örn: 1/2 veya 3.14):", 
        key="user_answer_text",
        disabled=(st.session_state.last_answer is not None) 
    )
    
    # Cevap Kontrolü
    if st.button("Cevabımı Kontrol Et", disabled=(st.session_state.last_answer is not None)):
        if user_answer.strip() == "":
            st.warning("Lütfen cevap girmeden kontrol etmeyin.")
            st.stop()
            
        correct_answer = str(q.get("cevap", "")).strip()
        
        # --- KONTROL VE PUANLAMA ---
        if check_answer(user_answer, correct_answer):
            points = get_points(difficulty)
            st.session_state.score += points
            st.session_state.last_answer = True
        else:
            st.session_state.last_answer = False
            
        # Çözüm ve görünürlük durumlarını temizle
        st.session_state.solution = None
        st.session_state.solution_visible = False
        st.session_state.solution_requested = False
        st.rerun() # Sonucu göstermek için yeniden yükle

    # --- ÇÖZÜM ANALİZİ VE GÖSTERİMİ AKIŞI ---
    
    # 1. Çözüm İstenmişse ve Henüz Analiz Edilmemişse, API'yi çağır
    if st.session_state.last_answer is not None and st.session_state.solution_requested and st.session_state.solution is None:
        q = st.session_state.current_question
        
        correct_answer_for_solution = str(q.get("cevap", "")).strip() 
        
        # Soru metni ve formülü birleştirilerek çözüme gönderilir.
        full_question_text = q.get('soru_metni', '') + " " + q.get('soru_formulu', '') 
        
        with st.spinner("Çözüm ve kısayol analiz ediliyor..."):
            st.session_state.solution = get_ai_solution(full_question_text, correct_answer_for_solution)
        
        st.session_state.solution_requested = False 
        st.rerun() 

    # 2. Sonuç mesajı, Devam Et ve Çözümü Gör butonu
    if st.session_state.last_answer is not None:
        
        st.markdown("---")
        
        if st.session_state.last_answer:
             st.success(f"🎉 Tebrikler! Doğru cevap! **+{get_points(difficulty)} Puan** kazandın.")
        else:
             st.error(f"❌ Yanlış cevap! Doğru cevap: **{q['cevap']}** idi.")

        
        col1, col2 = st.columns(2)
        
        with col1:
            # DEVAM BUTONU
            st.button("➡️ Devam Et (Yeni Soru Üret)", on_click=clear_question_state, type="primary")

        with col2:
            # ÇÖZÜMÜ GÖR BUTONU
            st.button(
                "🔎 Çözümü Gör", 
                on_click=request_solution, 
                disabled=st.session_state.solution_visible,
                type="secondary"
            )


    # 3. ÇÖZÜM VE KISAYOL GÖSTERİMİ
    if st.session_state.solution_visible and st.session_state.solution:
        solution_data = st.session_state.solution
        
        st.markdown("---")
        st.subheader("💡 Detaylı Çözüm")
        # Çözüm metinlerinde de çift ters eğik çizgi kullanılmasını sağlıyoruz
        st.markdown(solution_data.get("detayli_cozum", "Çözüm bulunamadı.").replace('\\', '\\\\'))
        
        st.subheader("⚡ Kısayol Çözümü")
        st.markdown(solution_data.get("kisayol_cozum", "Kısayol bulunmamaktadır.").replace('\\', '\\\\'))