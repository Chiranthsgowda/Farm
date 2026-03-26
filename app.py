import streamlit as st
from google import genai
from PIL import Image
import json
import numpy as np
import tensorflow as tf
from PIL import Image
from google.genai import types
import pdfplumber
import json
import requests
import pandas as pd
import google.generativeai as gi
from dotenv import load_dotenv
import os


load_dotenv()

language_codes = {
    "English": "en",
    "Kannada": "kn",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta"
}

st.set_page_config(page_title="AgriAI", page_icon="🌿", layout="wide")

# ── Session State ───────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# ── LIGHT PROFESSIONAL CSS ──────────────────────────────────
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(180deg, #f5f9ff, #eaf4ff);
    color: #1b2a41;
}
/* Fix metric labels and values */
[data-testid="stMetricLabel"] p,
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #000000 !important;
}

/* Fix info/success/warning box text */
[data-testid="stAlert"] p,
[data-testid="stAlert"] {
    color: #000000 !important;
}



/* Navbar */
.top-nav {
    position: sticky;
    top: 0;
    z-index: 999;

    margin-left: -1rem;
    margin-right: -1rem;
    padding: 14px 1rem;

    background: white;
    border-bottom: 1px solid #e0e6ed;

    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Buttons */
div.stButton > button {
    height: 55px;
    border-radius: 10px;

    background: linear-gradient(135deg, #2d9cdb, #56ccf2);
    color: white;
    font-weight: 600;

    border: none;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(45,156,219,0.3);
}

/* Cards */
.card {
    padding: 22px;
    border-radius: 14px;

    background: white;
    border: 1px solid #e6edf5;

    box-shadow: 0 4px 12px rgba(0,0,0,0.05);

    transition: all 0.25s ease;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

/* Divider */
.divider-line {
    height: 1px;
    background: #e0e6ed;
}

/* Headings */
h1, h2, h3 {
    color: #1b2a41;
}

/* Images */
img {
    border-radius: 10px;
}

/* Spacing */
.content-start {
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# ── NAVBAR ──────────────────────────────────────────────────
st.markdown('<div class="top-nav">', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

if c1.button("🥦 Veg Grader"):
    st.session_state.page = "🥦 Vegetable Grader"
    st.rerun()

if c2.button("🍃 Leaf Disease"):
    st.session_state.page = "🍃 Leaf Disease"
    st.rerun()

if c3.button("📊 Report"):
    st.session_state.page = "📊 Report Analyzer"
    st.rerun()

if c4.button("🏛️ Schemes"):
    st.session_state.page = "🏛️ Govt Schemes"
    st.rerun()

if c5.button("📈 Market"):
    st.session_state.page = "📈 Crop Market"
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown('<div class="content-start">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# HOME
# ════════════════════════════════════════════════════════════
if st.session_state.page == "🏠 Home":
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🌱 Smart Farming Dashboard")
        st.write("AI-powered tools to help farmers improve yield, detect diseases, and maximize profits.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef", use_container_width=True)

# ════════════════════════════════════════════════════════════
# VEGETABLE GRADER
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🥦 Vegetable Grader":
    col1, col2 = st.columns(2)
    API_KEY = os.getenv("GOOGLE_API_KEY")  


    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🥦 Vegetable Grader")
        uploaded_file = st.file_uploader("Upload vegetable image")

        # --- The Master Prompt ---
        SYSTEM_PROMPT = """
        You are an expert agricultural produce inspector and global market commodity analyst. 
        Your task is to analyze the provided image of a fruit or vegetable and evaluate its quality, freshness, and market value.

        Grading Rubric:
        * Grade 1 (Premium): Perfect or near-perfect shape, uniform color, completely free from blemishes, bruising, or disease. Optimal ripeness.
        * Grade 2 (Good/Standard): Minor variations in shape or color. Very slight, superficial blemishes that do not affect the flesh or shelf life. Good for general retail.
        * Grade 3 (Substandard/Processing): Noticeable blemishes, irregular shape, minor bruising, or over-ripeness. Safe to consume but visually unappealing. Best suited for processing, juicing, or immediate discount sale.
        * Reject: Showing active rot, mold, or severe damage. Unfit for consumption.

        Analyze the image carefully and output your findings STRICTLY as a JSON object with the following exact keys. Do not include any markdown formatting (like ```json), conversational text, or explanations outside of the JSON object.

        {
        "produce_type": "The specific name of the fruit/vegetable",
        "grade": "Grade 1, Grade 2, Grade 3, or Reject",
        "quality_score_out_of_100": 0,
        "freshness_percentage": 0,
        "estimated_shelf_life_days": 0,
        "analysis_reasoning": "Explanation detailing visual evidence."
        }
        """

        if uploaded_file is not None:
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Produce")

            if st.button("Analyze Produce Quality", type="primary"):
                if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
                    st.error("Please add your Gemini API Key to the API_KEY variable in the code.")
                else:
                    with st.spinner("Inspecting produce..."):
                        try:
                            # Configure the NEW GenAI Client
                            client = genai.Client(api_key=API_KEY)
                            
                            # Call the API using the new generation method and the 3.0-flash model
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[SYSTEM_PROMPT, image]
                            )
                            
                            # Clean up the response in case the model added markdown blocks
                            response_text = response.text.strip()
                            if response_text.startswith("```json"):
                                response_text = response_text[7:]
                            if response_text.endswith("```"):
                                response_text = response_text[:-3]
                            
                            # Parse JSON
                            result = json.loads(response_text)
                            
                            # --- Display Results ---
                            st.success("Analysis Complete!")
                            
                            st.subheader(f"Produce: {result.get('produce_type', 'Unknown').title()}")
                            
                            # Metrics Row 1
                            coll1, coll2, coll3 = st.columns(3)
                            coll1.metric("Grade", result.get("grade", "N/A"))
                            coll2.metric("Quality Score", f"{result.get('quality_score_out_of_100', 0)}/100")
                            coll3.metric("Freshness", f"{result.get('freshness_percentage', 0)}%")
                            
                            # Metrics Row 2
                            coll4, coll5 = st.columns(2)
                            coll4.metric("Est. Shelf Life", f"{result.get('estimated_shelf_life_days', 0)} Days")
                            
                            
                            # Detailed Analysis Expander
                            st.divider()
                            st.markdown("### Inspector's Notes")
                            st.info(result.get("analysis_reasoning", "No detailed reasoning provided."))
                            
                        except json.JSONDecodeError:
                            st.error("The AI returned a response that couldn't be parsed correctly. Please try again.")
                            with st.expander("Show raw AI response"):
                                st.write(response.text)
                        except Exception as e:
                            st.error(f"An error occurred: {e}")

    with col2:
        st.image("https://images.unsplash.com/photo-1567306226416-28f0efdc88ce", use_container_width =True)

# ════════════════════════════════════════════════════════════
# LEAF DISEASE
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🍃 Leaf Disease":
    
    MODEL_PATH     = r"D:\codes\Fram2Future\plantvillage_efficientnet.keras"
    LABEL_MAP_PATH = r"D:\codes\Fram2Future\class_names.json"
    IMG_SIZE       = (224, 224)
    TOP_K          = 5

    col1, col2 = st.columns(2)

    # ──────────────────────────────────────────────
    # LOAD MODEL & CLASS NAMES (cached)
    # ──────────────────────────────────────────────
    @st.cache_resource
    def load_model():
        model = tf.keras.models.load_model(MODEL_PATH)
        with open(LABEL_MAP_PATH) as f:
            class_names = list(json.load(f).values())
        return model, class_names

    # ──────────────────────────────────────────────
    # PREDICT
    # ──────────────────────────────────────────────
    def predict(image: Image.Image, model, class_names):
        img  = image.convert("RGB").resize(IMG_SIZE)
        arr  = tf.keras.utils.img_to_array(img)[None]          # (1, 224, 224, 3)
        prob = model.predict(arr, verbose=0)[0]
        top  = np.argsort(prob)[::-1][:TOP_K]
        return [
            {"label": class_names[i],
            "plant": class_names[i].split("___")[0].replace("_", " "),
            "disease": class_names[i].split("___")[1].replace("_", " "),
            "confidence": float(prob[i])}
            for i in top
        ]
    
    with st.spinner("Loading model …"):
        try:
            model, class_names = load_model()
            st.success(f"✅ Model loaded —  classes", icon="✅")
        except FileNotFoundError as e:
            st.error(f"❌ Could not load model: {e}\n\nMake sure `{MODEL_PATH}` and `{LABEL_MAP_PATH}` are in the same folder as this script.")
            st.stop()

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🍃 Leaf Disease Detection")
        uploaded = st.file_uploader(
            "Upload a leaf image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a clear photo of a plant leaf"
        )

        language_option = st.selectbox("Select the language for Response:", ["English", "Kannada", "Hindi", "Telugu", "Tamil"])

        API_KEY = os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=API_KEY)

        def get_disease_advice(client, plant_name, disease_name, language_option):
                    prompt = f"""
                        You are an expert plant pathologist and agronomist.
                        The user is growing '{top['plant']}' and it is affected by the disease '{top['disease']}'.
                        Provide actionable, practical advice on how to prevent this disease and how to treat or manage it.

                        CRITICAL INSTRUCTION: Output your response STRICTLY as a JSON object with the following exact keys. 
                        Translate all values inside the JSON into the {language_option} language.

                        {{
                            "plant": "{top['plant']}",
                            "disease": "{top['disease']}",
                            "prevention_tips": [
                                "Actionable prevention tip 1",
                                "Actionable prevention tip 2",
                                "Actionable prevention tip 3"
                            ],
                            "treatment_steps": [
                                "Actionable treatment or mitigation step 1",
                                "Actionable treatment or mitigation step 2"
                            ]
                        }}
                        """
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.2 # Kept low for factual, structured agricultural advice
                        )
                    )
                    
                    # The response.text is a JSON string. We parse it into a Python dictionary before returning.
                    try:
                        advice_dict = json.loads(response.text)
                        return advice_dict
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse the response into JSON."}

        if uploaded:
            image = Image.open(uploaded)

            coll1, coll2 = st.columns([1, 1], gap="large")

            with coll1:
                st.image(image, caption="Uploaded image", use_container_width=True)

            with coll2:
                with st.spinner("Analysing …"):
                    results = predict(image, model, class_names)

                top = results[0]
                confidence = top["confidence"]

                # Colour-code confidence
                if confidence >= 0.90:
                    badge = "🟢"
                elif confidence >= 0.70:
                    badge = "🟡"
                else:
                    badge = "🔴"
                
                
                st.subheader("Top Prediction")
                st.markdown(f"**🌱 Plant** : {top['plant']}")
                st.markdown(f"**🦠 Condition** : {top['disease']}")
                st.metric(label="Confidence", value=f"{confidence*100:.1f}%", delta=badge)

                st.divider()

                st.subheader(f"Top {TOP_K} Predictions")
                for i, r in enumerate(results):
                    bar_label = f"{i+1}. {r['plant']} — {r['disease']}"
                    st.progress(r["confidence"], text=f"{bar_label}  ({r['confidence']*100:.1f}%)")
                
                

        else:
            st.info("👆 Upload an image to get started", icon="ℹ️")

        st.divider()

    with col2:
        st.image("https://images.unsplash.com/photo-1501004318641-b39e6451bec6", use_container_width=True)
    
    advice = get_disease_advice(
        client=client,
        plant_name=top["plant"],       # e.g., "Tomato"
        disease_name=top["disease"],  # e.g., "Late Blight"
        language_option=language_option # e.g., "Kannada"
    )
    if "error" not in advice:
        st.subheader(f"Advice for {advice['plant']} - {advice['disease']}")
                    
        st.write("**Prevention Tips:**")
        for tip in advice["prevention_tips"]:
            st.write(f"- {tip}")
                        
        st.write("**Treatment Steps:**")
        for step in advice["treatment_steps"]:
            st.write(f"- {step}")
    else:
        st.error("There was an issue generating the advice.")

# ════════════════════════════════════════════════════════════
# REPORT ANALYZER
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "📊 Report Analyzer":
    col1, col2 = st.columns(2)
    API_KEY = os.getenv("GOOGLE_API_KEY")


    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📊 Soil Report Analyzer")
        uploaded_file = st.file_uploader("Choose a Soil Report PDF...", type=["pdf"])

        language_option = st.selectbox("Select the language for voice input and Response:", ["English", "Kannada", "Hindi", "Telugu", "Tamil"])

        # --- The Master Prompt ---
        SYSTEM_PROMPT = """
        You are an expert agronomist for farms in Karnataka, India (e.g., Mysuru, Mandya).
        Read the provided soil test report text.
        Extract the key metrics, recommend 3 suitable crops for the local climate, and give 3 soil improvement tips.

        CRITICAL INSTRUCTION: Analyze the text carefully and output your findings STRICTLY as a JSON object with the following exact keys. Do not include any markdown formatting or conversational text.

        {
        "metrics": {
            "pH": "extracted value or N/A",
            "soil_type": "extracted value or N/A",
            "nitrogen": "extracted value or N/A",
            "phosphorus": "extracted value or N/A",
            "potassium": "extracted value or N/A"
        },
        "crops": [
            {"name": "Crop 1 (e.g., Ragi, Sugarcane)", "yield_estimate": "Expected yield per acre"},
            {"name": "Crop 2", "yield_estimate": "Expected yield per acre"},
            {"name": "Crop 3", "yield_estimate": "Expected yield per acre"}
        ],
        "tips": [
            "Actionable tip 1",
            "Actionable tip 2",
            "Actionable tip 3"
        ]
        }}
        """ + f"give response in {language_option} language"
        if uploaded_file is not None:
            # --- TEXT EXTRACTION ---
            with st.spinner("📄 Extracting text from PDF..."):
                pdf_text = ""
                try:
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages:
                            extracted = page.extract_text()
                            if extracted:
                                pdf_text += extracted + "\n"
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
                    st.stop()
                    
            if not pdf_text.strip():
                st.error("Could not find readable text in this PDF. It might be a scanned image.")
                st.stop()
                
            st.success("PDF Text Extracted!")

            if st.button("Analyze Soil Report", type="primary"):
                if not API_KEY or API_KEY == "YOUR_NEW_GEMINI_API_KEY":
                    st.error("Please add your Gemini API Key to the API_KEY variable in the code.")
                else:
                    with st.spinner("Analyzing soil data..."):
                        try:
                            # Configure the NEW GenAI Client
                            client = genai.Client(api_key=API_KEY)
                            
                            # Call the API. 
                            # We pass the System Prompt + The Extracted PDF Text.
                            # We also use the config dictionary to natively force JSON output!
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[SYSTEM_PROMPT, f"SOIL REPORT TEXT:\n{pdf_text}"],
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json",
                                    temperature=0.1
                                )
                            )
                            
                            # Because we used response_mime_type="application/json", 
                            # we don't need to manually strip markdown backticks!
                            result = json.loads(response.text)
                            
                            # --- Display Results ---
                            st.success("Analysis Complete!")
                            st.divider()
                            
                            # Section 1: Key Metrics
                            st.subheader("🧪 Soil Health Metrics")
                            metrics = result.get("metrics", {})
                            
                            coll1, coll2, coll3 = st.columns(3)
                            coll1.metric("pH Level", metrics.get("pH", "N/A"))
                            coll2.metric("Soil Type", metrics.get("soil_type", "N/A"))
                            coll3.metric("Nitrogen (N)", metrics.get("nitrogen", "N/A"))
                            
                            coll4, coll5, coll6 = st.columns(3)
                            coll4.metric("Phosphorus (P)", metrics.get("phosphorus", "N/A"))
                            coll5.metric("Potassium (K)", metrics.get("potassium", "N/A"))
                            coll6.write("") # Empty column for spacing
                            
                            st.divider()
                            
                            # Section 2 & 3: Crops and Tips
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.subheader("🌾 Recommended Crops")
                                crops = result.get("crops", [])
                                for crop in crops:
                                    with st.expander(f"**{crop.get('name', 'Unknown')}**", expanded=True):
                                        st.write(f"**Est. Yield:** {crop.get('yield_estimate', 'N/A')}")
                            
                            with col_b:
                                st.subheader("🛠️ Action Plan")
                                tips = result.get("tips", [])
                                for tip in tips:
                                    st.info(tip)
                                    
                        except json.JSONDecodeError:
                            st.error("The AI returned a response that couldn't be parsed correctly. Please try again.")
                            with st.expander("Show raw AI response"):
                                st.write(response.text)
                        except Exception as e:
                            st.error(f"An error occurred: {e}")

    with col2:
        st.image("https://images.unsplash.com/photo-1586773860418-d37222d8fce3", use_container_width=True)

# ════════════════════════════════════════════════════════════
# GOVT SCHEMES
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "🏛️ Govt Schemes":
    col1, col2 = st.columns(2)
    API_KEY = os.getenv("GOOGLE_API_KEY")
    gi.configure(api_key=API_KEY)

# Initialize Gemini Model (Using flash for faster data generation)
    model = gi.GenerativeModel('gemini-2.5-flash') 

    with col1:
        # --- Dynamic Data Fetching ---
        @st.cache_data(ttl=3600) # Caches the result for 1 hour so search filtering is instant
        def fetch_all_schemes_from_gemini():
            if API_KEY == "YOUR_GEMINI_API_KEY":
                return pd.DataFrame()
                
            prompt = """
            Provide a comprehensive list of 10 to 15 active Indian government agricultural schemes (both Central and major State schemes).
            Output the data strictly as a JSON array of objects. 
            Do not use markdown formatting like ```json ... ```, just output the raw JSON array.
            Each object must have exactly these keys: "Scheme Name", "Category", "Description".
            """
            try:
                response = model.generate_content(prompt)
                
                # Clean up the response in case the model adds markdown ticks
                json_text = response.text.strip()
                if json_text.startswith("```json"):
                    json_text = json_text[7:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                    
                data = json.loads(json_text)
                return pd.DataFrame(data)
            except Exception as e:
                st.error(f"Error fetching schemes from Gemini: {e}")
                return pd.DataFrame()

        
            
        st.title("Block 4 — 🏛️ Govt Schemes")
        st.write("Explore and apply for the latest central and state agricultural schemes.")

        # --- Section 1: Regional Popularity (Moved to Top) ---
        st.subheader("📍 What are farmers in your region applying for?")
        st.write("Enter your state, district, or region, and we'll show you the most relevant schemes based on local crops and climate.")
            
        coll1, coll2 = st.columns([3, 1])
        with coll1:
                # Pre-filling with a default region for better UX
                region_input = st.text_input("Enter Region", value="Mysuru, Karnataka")
        with coll2:
                st.write("") 
                st.write("")
                analyze_btn = st.button("Find Local Trends", type="primary")

        if analyze_btn:
                if not region_input:
                    st.warning("Please enter a region first.")
                elif API_KEY == "YOUR_GEMINI_API_KEY":
                    st.error("Please add your Gemini API Key to the code to use this feature.")
                else:
                    with st.spinner(f"Analyzing agricultural trends for {region_input}..."):
                        try:
                            prompt = f"""
                            You are an expert Indian Agritech assistant. A farmer is checking an app from the following region: "{region_input}".
                            
                            Based on the typical climate, geography, and primary crops grown in this specific region, tell me:
                            1. Which 2-3 government agricultural schemes are farmers in this area most likely applying for right now?
                            2. A brief 1-sentence reason WHY for each scheme (e.g., relating to local water scarcity, specific cash crops, etc.).
                            
                            Keep the response very concise, structured with bullet points, and easy for a farmer to read.
                            """
                            
                            response = model.generate_content(prompt)
                            
                            st.success("Analysis Complete!")
                            st.markdown("### 📈 Trending Schemes in Your Area")
                            st.write(response.text)
                            
                        except Exception as e:
                            st.error(f"An error occurred while communicating with Gemini: {e}")
                            
        st.markdown("---")

            # --- Section 2: Auto-load & Search (Powered entirely by Gemini) ---
        st.subheader("🔍 All Live Schemes")
            
        if API_KEY == "YOUR_GEMINI_API_KEY":
                st.warning("Please set your Gemini API key to auto-load the schemes database.")
        else:
                with st.spinner("Fetching latest schemes live from Gemini... this may take a few seconds."):
                    df = fetch_all_schemes_from_gemini()
                    
                if not df.empty:
                    # Search Bar
                    search_query = st.text_input("Search for a scheme by name, category, or keyword...")
                    
                    # Filter logic
                    if search_query:
                        # Case-insensitive search across all columns
                        mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                        filtered_df = df[mask]
                    else:
                        filtered_df = df
                        
                    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        

    with col2:
        st.image("https://images.unsplash.com/photo-1502082553048-f009c37129b9", use_container_width=True)

# ════════════════════════════════════════════════════════════
# MARKET
# ════════════════════════════════════════════════════════════
elif st.session_state.page == "📈 Crop Market":
    col1, col2 = st.columns(2)

    with col1:
        # =========================
        # 📦 Fetch Data (Cached)
        # =========================
        @st.cache_data(ttl=3600)  # Caches the data for 1 hour to prevent API spam
        def fetch_data():
            API_KEY = "579b464db66ec23bdd000001c4a38233a7304d9b738796636eb7c787"
            url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            
            # Increased limit to 1000 to ensure a wider spread of states
            params = {
                "api-key": API_KEY,
                "format": "json",
                "limit": 1000 
            }

            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])
                    
                    # 🔥 GUARANTEE KARNATAKA IS PRESENT
                    # If Karnataka isn't in the fetched data, we inject a fallback record
                    has_karnataka = any(r.get("state", "").title() == "Karnataka" for r in records)
                    if not has_karnataka and records:
                        records.append({
                            "state": "Karnataka",
                            "district": "Mysore",
                            "market": "Demo Market",
                            "commodity": "Maize",
                            "arrival_date": "26/03/2026",
                            "min_price": "1500",
                            "max_price": "2000",
                            "modal_price": "1800"
                        })
                    
                    if records:
                        return records
                        
            except Exception as e:
                st.error("API Error: Falling back to demo data.")

            # 🛑 Fallback Data (If API totally fails)
            return [{
                "state": "Karnataka",
                "district": "Mysore",
                "market": "Demo Market",
                "commodity": "Maize",
                "arrival_date": "26/03/2026",
                "min_price": "1500",
                "max_price": "2000",
                "modal_price": "1800"
            }]

        # Load the data
        records = fetch_data()
        # 🌍 Select State
        states = sorted(list(set(r["state"].title() for r in records)))
        state_input = st.selectbox("📍 Select State", states)

        # 🏙️ Select District
        districts = sorted(list(set(r["district"].title() for r in records if r["state"].title() == state_input)))
        district_input = st.selectbox("🏙️ Select District", districts)

        # 🌾 Select Crop
        commodities = sorted(list(set(
            r["commodity"].title() for r in records 
            if r["state"].title() == state_input and r["district"].title() == district_input
        )))
        commodity_input = st.selectbox("🌾 Select Crop", commodities)

        st.divider()

        # =========================
        # 🔍 Filter Data
        # =========================
        filtered_data = [
            r for r in records 
            if r["state"].title() == state_input 
            and r["district"].title() == district_input 
            and r["commodity"].title() == commodity_input
        ]

        # =========================
        # 📊 Output
        # =========================

        if filtered_data:
            record = filtered_data[0]
            
            # Safely convert prices to floats
            min_price = float(record["min_price"])
            max_price = float(record["max_price"])
            modal_price = float(record["modal_price"])
            date = record["arrival_date"]
            price_per_kg = modal_price / 100

            # Header info
            st.markdown(f"**📍 Location:** {district_input}, {state_input} | **📅 Date:** {date}")
            st.markdown(f"**🌾 Crop:** {commodity_input}")

            # Display prices using Streamlit metrics
            st.subheader("📊 Market Prices (₹/quintal)")
            price_col1, price_col2, price_col3 = st.columns(3)
            price_col1.metric("Min Price", f"₹{min_price:,.0f}")
            price_col2.metric("Modal Price", f"₹{modal_price:,.0f}")
            price_col3.metric("Max Price", f"₹{max_price:,.0f}")

            st.markdown(f"### 📦 ≈ ₹{price_per_kg:.2f} per kg")
            st.write("") # Spacer

            # 🔥 Insight Layer
            st.subheader("💡 Market Insights")
            if modal_price < 2000:
                st.error("**📉 Market Trend: Low Price ⚠️**\n\n**Suggestion:** Consider delaying sale if storage is available.")
            elif modal_price > 4000:
                st.success("**📈 Market Trend: High Price 🚀**\n\n**Suggestion:** Good time to sell and lock in profits.")
            else:
                st.info("**📊 Market Trend: Moderate 👍**\n\n**Suggestion:** Monitor market conditions closely.")

        else:
            st.warning("⚠️ No data found for the selected combination.")

    with col2:
        st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef", use_container_width=True)

# Close container
st.markdown('</div>', unsafe_allow_html=True)
