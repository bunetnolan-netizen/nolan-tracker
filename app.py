import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="BailSafe | Audit Locatif", page_icon="🛡️", layout="wide")

# --- GESTION DES SECRETS ---
try:
    MOT_DE_PASSE_ATTENDU = st.secrets["MOT_DE_PASSE_ATTENDU"]
    EMAIL_EXPEDITEUR = st.secrets["EMAIL_EXPEDITEUR"]
    MOT_DE_PASSE_EMAIL = st.secrets["MOT_DE_PASSE_EMAIL"]
except Exception:
    st.error("⚠️ Secrets non configurés. Veuillez configurer les secrets Streamlit.")
    st.stop()

if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# --- FONCTION NETTOYAGE PDF ---
def clean_text(text):
    """Supprime les caractères non-ASCII pour éviter les erreurs d'encodage FPDF."""
    return re.sub(r'[^\x00-\x7F]+', '', str(text))

# --- GÉNÉRATION PDF PRO ---
def generer_pdf_pro(statut, ecart, fraude_meta):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Institutionnel
    pdf.set_fill_color(31, 58, 147)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", 'B', 20)
    pdf.cell(0, 20, "RAPPORT D'AUDIT BAILSAFE", ln=True, align="C")
    
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    
    # Section Diagnostic
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, clean_text("Diagnostic Global:"), ln=True)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, clean_text(statut), ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Section Technique
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, clean_text("Analyse Technique:"), ln=True)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, clean_text(f"Ecart budgetaire constate : {ecart:.2f} EUR"), ln=True)
    
    meta_msg = "Analyse graphique : Structure informatique standard." if not fraude_meta else "Alerte : Fichier modifie via editeur tiers (Photoshop/Canva)."
    pdf.multi_cell(0, 10, clean_text(meta_msg))
    
    # Pied de page Légal (RGPD)
    pdf.set_y(-50)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 40, 'F')
    pdf.set_font("Helvetica", 'I', 9)
    pdf.multi_cell(0, 5, clean_text("Mentions Legales : BailSafe - Assistance technique.\n" 
                                    "RGPD : Audit realise en memoire locale, aucune donnee conservee.\n"
                                    "Exclusion de responsabilite : Cet audit est un avis technique consultatif.\n"
                                    "Il ne constitue en aucun cas une garantie contre les impayes."))
    
    return pdf.output(dest='S')

# --- VITRINE PUBLIQUE ---
def afficher_vitrine():
    st.markdown("<h1 style='text-align: center; color: #1f3a93;'>🛡️ BailSafe</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Filtre Anti-Fraude & Analyse Documentaire Express</p>", unsafe_allow_html=True)
    st.divider()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚨 Le Risque", "💡 La Solution", "📄 Exemple", "🔒 Sécurité", "⚖️ Mentions"])
    
    with tab1:
        st.markdown("### Pourquoi sécuriser vos dossiers ?")
        colA, colB = st.columns(2)
        colA.metric("Risque financier", "Elevé")
        colB.metric("Contrôle visuel", "Incertain")
    with tab2:
        st.markdown("### Notre Expertise")
        st.success("Audit complet pour 20 € par dossier.")
        st.write("- 🔎 Analyse Forensique (Détection retouche)\n- 🧮 Validation Mathématique (Cumul)\n- 📄 Rapport Pro livré sous 24h")
    with tab3:
        st.write("Exemple d'un dossier suspect : Écart de 1240€ détecté avec trace de Photoshop.")
    with tab4:
        st.warning("Garantie RGPD : Analyse volatile, zéro stockage base de données.")
    with tab5:
        st.markdown("### Mentions Légales")
        st.write("Service proposé par BailSafe. Contact : bunetnolan@gmail.com")

    st.divider()
    col1, col2 = st.columns(2)
    col1.link_button("📘 Contact Facebook", "https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr")
    col2.link_button("🛒 Contact LeBonCoin", "https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2")

    with st.expander("🔐 Accès Expert"):
        mdp = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if mdp == MOT_DE_PASSE_ATTENDU:
                st.session_state["authentifie"] = True
                st.rerun()
            else:
                st.error("Accès refusé.")

# --- INTERFACE EXPERT ---
def afficher_interface_expert():
    st.title("🕵️‍♂️ Cockpit BailSafe")
    if st.button("🔴 Déconnexion"):
        st.session_state["authentifie"] = False
        st.rerun()

    with st.expander("💸 Messagerie Client"):
        st.code("Bonjour ! J'ai bien reçu le dossier. Pour lancer l'audit (20€), merci de régler ici : [TON LIEN]. Dès réception, je lance le scan.")

    fichier_pdf = st.file_uploader("📂 Déposer PDF", type="pdf")
    
    if fichier_pdf:
        with pdfplumber.open(fichier_pdf) as pdf:
            metadata = pdf.metadata
            texte = "\n".join([page.extract_text() or "" for page in pdf.pages])
            est_scan = len(texte.strip()) < 20

        tab1, tab2, tab3 = st.tabs(["📊 Cohérence", "🔎 ADN", "📤 Rapport"])
        
        with tab1:
            if est_scan:
                st.warning("⚠️ Scan détecté : Lecture auto impossible. Vérification visuelle requise.")
                ecart, fraude_math = 0, False
            else:
                # Regex robustes
                n_match = re.search(r'(?i)net\s*[àa]\s*payer\s*[:\s]*(\d[\d\s]*[.,]?\d*)', texte)
                c_match = re.search(r'(?i)cumul\s*imposable\s*[:\s]*(\d[\d\s]*[.,]?\d*)', texte)
                
                # Conversion sécurisée
                def parse_val(m): 
                    return float(m.group(1).replace(' ','').replace(',', '.')) if m else 0.0
                
                net = parse_val(n_match)
                cumul = parse_val(c_match)
                
                c1, c2, c3 = st.columns(3)
                net_saisi = c1.number_input("Net", value=net)
                mois = c2.number_input("Mois", 1, 12, 1)
                cumul_saisi = c3.number_input("Cumul", value=cumul)
                
                ecart = abs(cumul_saisi - (net_saisi * mois))
                st.metric("Écart constaté", f"{ecart:.2f} €")
                fraude_math = ecart > 150

        with tab2:
            meta_str = str(metadata.get('Creator', '')) + " " + str(metadata.get('Producer', ''))
            fraude_meta = any(s in meta_str.lower() for s in ["photoshop", "canva", "ilovepdf", "gimp"])
            if fraude_meta: st.error("🚨 ALERTE : Logiciel tiers détecté !")
            else: st.success("✅ Signature standard.")

        with tab3:
            if est_scan: statut = "VÉRIFICATION MANUELLE"
            elif fraude_math or fraude_meta: statut = "SUSPECT"
            else: statut = "FIABLE"
            
            st.write(f"**Statut :** {statut}")
            email_client = st.text_input("E-mail client :")
            if st.button("🚀 Générer et Envoyer Rapport"):
                pdf_bytes = generer_pdf_pro(statut, ecart if not est_scan else 0, fraude_meta if not est_scan else False)
                
                msg = MIMEMultipart()
                msg['From'], msg['To'] = EMAIL_EXPEDITEUR, email_client
                msg['Subject'] = "[BailSafe] Rapport d'Audit"
                msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver votre rapport BailSafe en pièce jointe.", 'plain'))
                
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(pdf_bytes)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="Rapport_BailSafe.pdf"')
                msg.attach(part)
                
                try:
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
                    server.send_message(msg)
                    server.quit()
                    st.success("✅ Envoyé !")
                except Exception as e:
                    st.error(f"Erreur SMTP : {e}")

# --- LANCEMENT ---
if not st.session_state["authentifie"]: afficher_vitrine()
else: afficher_interface_expert()
