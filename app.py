import streamlit as st
import pdfplumber, re, smtplib
from fpdf import FPDF
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- CONFIGURATION ---
st.set_page_config(page_title="BailSafe | Audit Locatif", layout="centered")

try:
    MOT_DE_PASSE_ATTENDU = st.secrets["MOT_DE_PASSE_ATTENDU"]
    EMAIL_EXPEDITEUR = st.secrets["EMAIL_EXPEDITEUR"]
    MOT_DE_PASSE_EMAIL = st.secrets["MOT_DE_PASSE_EMAIL"]
except:
    st.error("Configuration des secrets manquante.")
    st.stop()

if "authentifie" not in st.session_state: st.session_state.authentifie = False

# --- VITRINE PUBLIQUE (LINEAIRE) ---
def afficher_vitrine():
    st.markdown("<h1 style='text-align:center;'>🛡️ BailSafe</h1>", unsafe_allow_html=True)
    
    st.subheader("🚨 Le risque des faux dossiers")
    st.write("Les faux bulletins de salaire menacent votre rentabilité. Un seul impayé peut ruiner votre investissement.")
    
    st.subheader("🛡️ Notre solution : Audit 24h")
    st.write("Pour 20 €, j'analyse vos dossiers : détection Photoshop, vérification mathématique et cohérence fiscale.")
    
    st.subheader("📄 Exemple de rapport")
    st.info("Vous recevez un PDF clair : Statut (Fiable/Suspect), écarts détectés et empreinte numérique.")
    
    st.subheader("⚖️ Mentions Légales & RGPD")
    st.write("Service d'assistance technique. Zéro stockage, destruction immédiate des documents après audit.")
    
    if st.text_input("Accès Expert", type="password") == MOT_DE_PASSE_ATTENDU:
        if st.button("Connexion"): st.session_state.authentifie = True; st.rerun()

    st.markdown("### 💬 Contactez-nous :")
    col1, col2 = st.columns(2)
    col1.markdown("[![LeBonCoin](https://img.shields.io/badge/LeBonCoin-FF6E00?style=for-the-badge&logo=leboncoin)](https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2)")
    col2.markdown("[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook)](https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr)")

# --- INTERFACE EXPERT ---
def afficher_expert():
    st.title("🕵️‍♂️ Cockpit BailSafe")
    if st.button("🔴 Déconnexion"): st.session_state.authentifie = False; st.rerun()
    
    file = st.file_uploader("Déposer PDF", type="pdf")
    if file:
        with pdfplumber.open(file) as pdf:
            text = "".join([p.extract_text() or "" for p in pdf.pages])
            meta = str(pdf.metadata)
        
        # Regex auto
        net = re.search(r"(Net à payer|Net payé)[\s:]*(\d+[\.,]\d+)", text, re.IGNORECASE)
        cumul = re.search(r"(Cumul|Net imposable)[\s:]*(\d+[\.,]\d+)", text, re.IGNORECASE)
        
        n = st.number_input("Net", value=float(net.group(2).replace(',','.')) if net else 0.0)
        c = st.number_input("Cumul", value=float(cumul.group(2).replace(',','.')) if cumul else 0.0)
        
        fraude = any(x in meta.lower() for x in ["photoshop", "canva", "ilovepdf"])
        if fraude: st.error("🚨 Signatures Photoshop/Canva détectées !")
        
        email = st.text_input("E-mail client")
        if st.button("🚀 Générer et Envoyer Rapport"):
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Rapport d'Audit BailSafe", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Statut : {'SUSPECT' if fraude else 'FIABLE'}", ln=True)
            
            # Envoi
            msg = MIMEMultipart()
            msg['From'], msg['To'] = EMAIL_EXPEDITEUR, email
            msg['Subject'] = "Rapport BailSafe"
            msg.attach(MIMEText("Voici votre audit.", 'plain'))
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf.output(dest='S'))
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="Audit.pdf"')
            msg.attach(part)
            
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls(); s.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
            s.send_message(msg); s.quit()
            st.success("✅ Envoyé !")

if st.session_state.authentifie: afficher_expert()
else: afficher_vitrine()
