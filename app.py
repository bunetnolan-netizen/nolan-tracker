import streamlit as st
import pdfplumber, re, smtplib
from fpdf import FPDF
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- CONFIGURATION ---
st.set_page_config(page_title="BailSafe | Audit Locatif", layout="wide")

# --- STYLE CSS POUR L'INTERACTIVITÉ ---
st.markdown("""
    <style>
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; background: #FFD700; color: black; font-weight: bold; }
        .section-box { padding: 20px; border-radius: 10px; background-color: #0E1117; border: 1px solid #333; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- VITRINE INTERACTIVE ---
# Menu de navigation fixe
menu = st.sidebar.radio("Navigation", ["🚨 Le Risque", "💡 La Solution", "📄 Exemple Rapport", "🔒 Sécurité", "⚖️ Mentions Légales"])

st.title("🛡️ BailSafe")

if menu == "🚨 Le Risque":
    st.subheader("Pourquoi sécuriser vos dossiers ?")
    st.write("Les faux bulletins de salaire et avis d'imposition menacent votre rentabilité.")
    st.metric("Risque financier", "Élevé", "Impayés en hausse")

elif menu == "💡 La Solution":
    st.subheader("Notre Expertise 24h")
    st.success("Audit complet pour 20€ par dossier.")
    st.write("- 🔎 Analyse Forensique\n- 🧮 Validation Algorithmique")

# (Ajoute les autres conditions elif pour chaque section...)

st.divider()
st.markdown("### 💬 Prêt à sécuriser vos dossiers ?")
col1, col2 = st.columns(2)
col1.markdown("[![LeBonCoin](https://img.shields.io/badge/LeBonCoin-FF6E00?style=for-the-badge&logo=leboncoin)](https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2)")
col2.markdown("[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook)](https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr)")
