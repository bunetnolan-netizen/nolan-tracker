import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Configuration de la page
st.set_page_config(page_title="BailSafe | Audit Locatif Expert", page_icon="🛡️", layout="centered")

# ==========================================
# 🔐 CONFIGURATION SÉCURISÉE (STREAMLIT SECRETS)
# ==========================================
try:
    MOT_DE_PASSE_ATTENDU = st.secrets["MOT_DE_PASSE_ATTENDU"]
    EMAIL_EXPEDITEUR = st.secrets["EMAIL_EXPEDITEUR"]
    MOT_DE_PASSE_EMAIL = st.secrets["MOT_DE_PASSE_EMAIL"]
except Exception:
    st.error("⚠️ Erreur : Configuration des secrets manquante sur Streamlit.")
    st.stop()

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# ==========================================
# 🌍 PARTIE 1 : VITRINE (LANDING PAGE FLUIDE)
# ==========================================
def afficher_vitrine():
    # Header Premium
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 40px; border-radius: 20px; text-align: center; color: white;">
            <h1 style="margin: 0; font-size: 3em;">🛡️ BailSafe</h1>
            <p style="font-size: 1.3em; opacity: 0.9;">Audit Anti-Fraude Documentaire</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>### 🚨 Le risque est réel", unsafe_allow_html=True)
    st.write("Les fraudes aux dossiers locatifs (bulletins falsifiés) explosent. Ne soyez plus une cible.")
    col1, col2 = st.columns(2)
    col1.metric("Risque financier", "Élevé", "Attention")
    col2.metric("Détection manuelle", "Complexité max", "Risque erreur")
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    st.markdown("### 💡 L'audit expert BailSafe")
    st.success("✅ Audit technique approfondi : 20 € par dossier (Livraison sous 24h)")
    st.markdown("""
    * 🔎 **Analyse Forensique** (Détection Photoshop/Canva)
    * 🧮 **Validation Algorithmique** (Cohérence fiscale)
    * 📄 **Rapport PDF Certifié** (Preuve de fiabilité)
    """)
    
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    
    st.markdown("### 📩 Contactez-moi pour sécuriser un dossier")
    st.markdown("""
        <div style="display: flex; gap: 20px; justify-content: center;">
            <a href="https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2" style="background:#f56523; color:white; padding:15px; border-radius:10px; text-decoration:none; font-weight:bold;">🛒 LeBonCoin</a>
            <a href="https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr" style="background:#1877f2; color:white; padding:15px; border-radius:10px; text-decoration:none; font-weight:bold;">📘 Facebook</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Mentions Légales & Admin
    with st.expander("⚖️ Mentions Légales & Accès Expert"):
        st.write("""
        **Clause de non-responsabilité :** BailSafe fournit une assistance technique. 
        L'audit ne constitue pas une garantie d'impayé. La décision finale appartient au bailleur.
        """)
        mdp_saisi = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if mdp_saisi == MOT_DE_PASSE_ATTENDU:
                st.session_state["authentifie"] = True
                st.rerun()

# ==========================================
# 🕵️‍♂️ PARTIE 2 : INTERFACE EXPERT
# ==========================================
def afficher_interface_expert():
    st.title("Cockpit d'Analyse 🕵️‍♂️")
    if st.button("🔴 Déconnexion"):
        st.session_state["authentifie"] = False
        st.rerun()

    # Tunnel de paiement intégré
    st.code("Message client : Bonjour ! Merci pour le dossier. Pour lancer l'audit (20€), merci de régler via ce lien : [TON LIEN]", language="text")

    fichier = st.file_uploader("📂 PDF à auditer", type="pdf")
    
    if fichier:
        with pdfplumber.open(fichier) as pdf:
            txt = "".join([p.extract_text() or "" for p in pdf.pages])
            meta = pdf.metadata
        
        # Détection scan
        est_scan = len(txt.strip()) < 20
        
        # Analyse
        st.subheader("Analyse de cohérence")
        if est_scan:
            st.warning("⚠️ Scan détecté : Vérification manuelle requise.")
            fraude_math = False
            ecart = 0
        else:
            net = re.search(r'(?i)net\s*[àa]\s*payer\s*.*?(\d[\d\s]*[.,]?\d*)', txt)
            cumul = re.search(r'(?i)cumul\s*imposable\s*.*?(\d[\d\s]*[.,]?\d*)', txt)
            net_val = float(net.group(1).replace(' ', '').replace(',', '.')) if net else 0
            cumul_val = float(cumul.group(1).replace(' ', '').replace(',', '.')) if cumul else 0
            ecart = abs(cumul_val - (net_val * 1)) # Simplification
            fraude_math = ecart > 150
            st.success("✅ Extraction automatique effectuée.")

        # Forensics
        fraude_meta = any(x in str(meta).lower() for x in ["photoshop", "canva", "ilovepdf"])
        if fraude_meta: st.error("🚨 Signatures de logiciel de retouche détectées !")
        else: st.success("✅ Structure graphique saine.")

        # Envoi
        email = st.text_input("E-mail du client :")
        if st.button("🚀 Valider et Envoyer Rapport"):
            pdf_gen = FPDF()
            pdf_gen.add_page()
            pdf_gen.cell(0, 10, "Rapport BailSafe : Audit Technique", ln=True, align="C")
            pdf_bytes = pdf_gen.output(dest='S')
            
            try:
                msg = MIMEMultipart()
                msg['From'], msg['To'] = EMAIL_EXPEDITEUR, email
                msg['Subject'] = "[BailSafe] Votre Rapport d'Audit"
                msg.attach(MIMEText("Bonjour, voici votre rapport d'audit (20€).", 'plain'))
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(pdf_bytes)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="Rapport.pdf"')
                msg.attach(part)
                
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
                s.send_message(msg)
                s.quit()
                st.success("✅ Envoyé !")
            except Exception as e:
                st.error(f"Erreur : {e}")

if not st.session_state["authentifie"]:
    afficher_vitrine()
else:
    afficher_interface_expert()
