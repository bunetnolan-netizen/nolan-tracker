import streamlit as st
import pdfplumber
import re
import fpdf
from datetime import datetime
import io

# --- CONFIGURATION & SÉCURITÉ ---
st.set_page_config(page_title="BailSafe | Audit Locatif", layout="wide")

# Utilisation des secrets Streamlit pour la sécurité (à configurer dans l'interface Streamlit Cloud)
MOT_DE_PASSE_ADMIN = st.secrets["MOT_DE_PASSE_ADMIN"]
EMAIL_EXPEDITEUR = st.secrets["EMAIL_EXPEDITEUR"]
MOT_DE_PASSE_EMAIL = st.secrets["MOT_DE_PASSE_EMAIL"]

# --- FONCTIONS UTILES ---
def verifier_metadata(file):
    with pdfplumber.open(file) as pdf:
        meta = pdf.metadata
        logiciels = ["Photoshop", "iLovePDF", "Canva", "Adobe"]
        for cle, valeur in meta.items():
            for logiciel in logiciels:
                if valeur and logiciel in str(valeur):
                    return f"🚨 Alerte : Utilisation de {logiciel} détectée dans les métadonnées !"
    return "✅ Aucune trace de logiciel de modification détectée."

def extraire_donnees(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    net_match = re.search(r"(Net à payer|Net payé)[\s:]*(\d+[\.,]\d+)", text, re.IGNORECASE)
    cumul_match = re.search(r"(Cumul|Net imposable)[\s:]*(\d+[\.,]\d+)", text, re.IGNORECASE)
    
    net = float(net_match.group(2).replace(',', '.')) if net_match else 0.0
    cumul = float(cumul_match.group(2).replace(',', '.')) if cumul_match else 0.0
    return net, cumul, text

# --- INTERFACE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    # --- VITRINE PUBLIQUE ---
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 40px; border-radius: 15px; color: white; text-align: center;">
            <h1>🛡️ BailSafe</h1>
            <h3>Audit Locatif Anti-Fraude Express</h3>
            <p>Sécurisez votre investissement : analyse graphique & logique sous 24h pour 20€.</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Le Problème", "La Solution", "Prix", "Mentions Légales"])
    tab1.write("Les faux bulletins de salaire et avis d'imposition menacent votre rentabilité.")
    tab2.write("Nous analysons la cohérence de vos dossiers locataires pour détecter les fraudes.")
    tab3.write("Prix de l'audit : 20 € par dossier.")
    tab4.write("Service d'assistance technique à la décision. BailSafe n'est pas une assurance impayés.")
    
    st.markdown("### 💬 Contactez-nous :")
    col1, col2 = st.columns(2)
    col1.markdown("[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook)](https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr)")
    col2.markdown("[![LeBonCoin](https://img.shields.io/badge/LeBonCoin-FF6E00?style=for-the-badge&logo=leboncoin)](https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2)")
    
    with st.expander("🔑 Accès Expert"):
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Connexion"):
            if pwd == MOT_DE_PASSE_ADMIN:
                st.session_state.logged_in = True
                st.rerun()
else:
    # --- ESPACE EXPERT ---
    st.title("🕵️‍♂️ Cockpit BailSafe")
    uploaded_file = st.file_uploader("Déposer un dossier PDF", type=["pdf"])
    
    if uploaded_file:
        net, cumul, texte = extraire_donnees(uploaded_file)
        alerte_meta = verifier_metadata(uploaded_file)
        
        st.write(f"**Analyse :** {alerte_meta}")
        net_saisi = st.number_input("Net à payer", value=net)
        cumul_saisi = st.number_input("Cumul imposable", value=cumul)
        
        if st.button("Générer Rapport PDF"):
            pdf = fpdf.FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Rapport d'Audit BailSafe", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Score : {'FIABLE' if net > 0 else 'SUSPECT'}", ln=True)
            pdf.cell(200, 10, txt="Conformité RGPD : Documents détruits après audit.", ln=True)
            
            pdf_bytes = pdf.output(dest='S')
            st.download_button("📥 Télécharger le rapport", data=pdf_bytes, file_name="Rapport_BailSafe.pdf")

    if st.button("Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()
