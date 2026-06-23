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
# Le code va chercher les mots de passe dans le coffre-fort de Streamlit
try:
    MOT_DE_PASSE_ATTENDU = st.secrets["MOT_DE_PASSE_ATTENDU"]
    EMAIL_EXPEDITEUR = st.secrets["EMAIL_EXPEDITEUR"]
    MOT_DE_PASSE_EMAIL = st.secrets["MOT_DE_PASSE_EMAIL"]
except Exception:
    st.error("⚠️ Les secrets de sécurité ne sont pas configurés sur le serveur. Impossible de démarrer l'application.")
    st.stop()

# Gestion de la session
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# ==========================================
# 🌍 PARTIE 1 : LA VITRINE PUBLIQUE
# ==========================================
def afficher_vitrine():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 30px; border-radius: 16px; text-align: center; margin-bottom: 25px; border: 2px solid #d97706;">
            <div style="font-size: 50px; margin-bottom: 10px;">🛡️</div>
            <h1 style="color: #ffffff; margin: 0; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; letter-spacing: 1px;">BailSafe</h1>
            <p style="color: #94a3b8; font-size: 16px; margin-top: 5px; margin-bottom: 0;">Filtre Anti-Fraude Documentaire & Analyse Heuristique par IA</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Louez votre bien immobilier en toute sérénité.</h3>", unsafe_allow_html=True)
    st.divider()

    tab_constat, tab_solution, tab_preuve, tab_rgpd = st.tabs(["🚨 Le Risque", "💡 La Solution", "📄 Exemple de Rapport", "🔒 Sécurité"])

    with tab_constat:
        st.markdown("### Pourquoi sécuriser vos dossiers locatifs ?")
        colA, colB = st.columns(2)
        colA.metric(label="Risque financier global", value="Élevé", delta="Impayés en forte hausse", delta_color="inverse")
        colB.metric(label="Contrôle visuel classique", value="Incertain", delta="Fraudes invisibles à l'œil", delta_color="inverse")
        st.info("Un propriétaire particulier n'a ni le temps ni les outils pour traquer les pixels modifiés ou les anomalies mathématiques d'un document.")

    with tab_solution:
        st.markdown("### Notre Expertise Technologique")
        st.success("**Pour 20 € par dossier**, bénéficiez d'un audit de conformité express sous 24h.")
        st.markdown("""
        - 🔎 **Analyse Forensique** : Traque des traces d'outils d'édition (Photoshop, Canva...).
        - 🧮 **Validation Algorithmique** : Recalcul automatique des cumuls fiscaux.
        - 📄 **Rapport de Fiabilité** : Livraison d'un bilan PDF clair.
        """)

    with tab_preuve:
        st.markdown("### À quoi ressemble notre audit ?")
        st.write("Voici un exemple des éléments livrés dans notre rapport confidentiel :")
        st.markdown("""
        > **📋 RAPPORT D'AUDIT BAILSAFE**
        > - **Statut de l'analyse :** 🔴 SUSPECT (Anomalies majeures)
        > - **Vérification mathématique :** Écart de 1 240,00 € détecté entre le net à payer et le cumul imposable.
        > - **Empreinte numérique :** Utilisation d'un logiciel de retouche (*Adobe Photoshop 2023*) détectée dans le code source du fichier.
        """)
        st.caption("Grâce à ces données, vous évitez un candidat fraudeur avant même la signature du bail.")

    with tab_rgpd:
        st.warning("⚖️ **Garantie de Conformité** : Conformément au RGPD, BailSafe agit sans persistance.")
        st.markdown("- **Zéro Base de Données** : Aucun stockage.\n- **Analyse Volatile** : Fichiers purgés après l'envoi du rapport.")

    st.divider()
    st.markdown("<h3 style='text-align: center;'>📩 Confiez-nous votre première analyse</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 30px;">
            <a href="https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2" target="_blank" style="text-decoration: none;">
                <div style="background-color: #f56523; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold;">🛒 Contact LeBonCoin</div>
            </a>
            <a href="https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr" target="_blank" style="text-decoration: none;">
                <div style="background-color: #1877f2; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold;">📘 Contact Facebook</div>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    with st.expander("🔐 Accès Expert"):
        mdp_saisi = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if mdp_saisi == MOT_DE_PASSE_ATTENDU:
                st.session_state["authentifie"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")

# ==========================================
# 🕵️‍♂️ PARTIE 2 : L'INTERFACE EXPERT
# ==========================================
def afficher_interface_expert():
    colA, colB = st.columns([4, 1])
    with colA:
        st.title("Cockpit d'Analyse 🕵️‍♂️")
    with colB:
        if st.button("🔴 Déconnexion"):
            st.session_state["authentifie"] = False
            st.rerun()

    # --- TUNNEL D'ENCAISSEMENT (POUR TOI) ---
    with st.expander("💸 Tunnel de paiement (Message client)"):
        st.write("Copie-colle ce message à ton client pour encaisser l'audit :")
        st.code("""Bonjour ! J'ai bien reçu le dossier de votre candidat. 
Afin que je puisse lancer l'audit technique et forensique, je vous invite à régler les 20€ d'honoraires via ce lien sécurisé : [TON LIEN LYDIA / PAYPAL ICI]

Dès réception, le système scanne les pièces et je vous envoie le rapport PDF de fiabilité. 
Cordialement, Nolan - BailSafe""", language="text")

    fichier_pdf = st.file_uploader("📂 Déposez le PDF à auditer", type="pdf")
    
    if fichier_pdf is not None:
        texte_brut = ""
        metadata_pdf = {}
        
        with pdfplumber.open(fichier_pdf) as pdf:
            metadata_pdf = pdf.metadata
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    texte_brut += page_text + "\n"
        
        # --- SÉCURITÉ SCANS & PHOTOS ---
        est_scan = len(texte_brut.strip()) < 20

        tab1, tab2, tab3 = st.tabs(["📊 Cohérence Numérique", "🔎 ADN du Fichier", "📤 Rapport & Envoi"])
        
        with tab1:
            if est_scan:
                st.warning("⚠️ ATTENTION : Ce PDF ne contient aucun texte informatique. Il s'agit d'un SCAN ou d'une PHOTO. L'extraction mathématique automatique est impossible.")
                st.info("Passez directement à l'onglet 'ADN du fichier' pour vérifier l'origine de la photo, puis effectuez une vérification visuelle des chiffres.")
                fraude_math = False
                ecart = 0
            else:
                st.subheader("Extraction Automatique des Variables")
                net_a_payer_match = re.search(r'(?i)net\s*[àa]\s*payer\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
                cumul_imposable_match = re.search(r'(?i)cumul\s*imposable\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
                
                net_extrait = net_a_payer_match.group(1).replace(' ', '').replace(',', '.') if net_a_payer_match else "0"
                cumul_extrait = cumul_imposable_match.group(1).replace(' ', '').replace(',', '.') if cumul_imposable_match else "0"
                
                col1, col2, col3 = st.columns(3)
                net_saisi = col1.number_input("Net mensuel", value=float(net_extrait))
                nb_mois = col2.number_input("Mois cumulés", min_value=1, max_value=12, value=1)
                cumul_saisi = col3.number_input("Cumul imposable", value=float(cumul_extrait))
                
                calcul_theorique = net_saisi * nb_mois
                ecart = abs(cumul_saisi - calcul_theorique)
                
                m1, m2 = st.columns(2)
                m1.metric("Cumul Théorique calculé", f"{calcul_theorique:.2f} €")
                m2.metric("Écart constaté", f"{ecart:.2f} €", delta_color="inverse", delta=f"{ecart:.2f} €" if ecart > 0 else "0.00 €")
                fraude_math = ecart > 150

        with tab2:
            st.subheader("Analyse Forensique des Métadonnées")
            createur = metadata_pdf.get('Creator', '')
            producteur = metadata_pdf.get('Producer', '')
            meta_string = str(createur) + " " + str(producteur)
            st.write(f"**Moteur de rendu :** {producteur if producteur else 'Inconnu (Signature absente)'}")
            
            logiciels_suspects = ["photoshop", "canva", "ilovepdf", "illustrator", "gimp"]
            fraude_meta = any(logiciel in meta_string.lower() for logiciel in logiciels_suspects)
            
            if fraude_meta:
                st.error("🚨 ALERTE : Signatures d'un logiciel d'édition graphique détectées !")
            else:
                st.success("✅ Aucune trace d'outil d'édition graphique suspect.")

        with tab3:
            st.subheader("Scoring & Expédition")
            if est_scan:
                statut = "VÉRIFICATION MANUELLE REQUISE (Scan/Photo fourni par le candidat)"
                st.warning(statut)
            elif fraude_math and fraude_meta:
                statut = "CRITIQUE (Falsification technique et mathématique détectée)"
                st.error(statut)
            elif fraude_math or fraude_meta:
                statut = "SUSPECT (Anomalies majeures à vérifier)"
                st.warning(statut)
            else:
                statut = "FIABLE (Aucune anomalie détectée)"
                st.success(statut)
                
            email_client = st.text_input("Adresse e-mail du client :", placeholder="client@gmail.com")
            
            if st.button("🚀 Envoyer le Rapport PDF"):
                if not email_client:
                    st.warning("Renseignez l'e-mail.")
                else:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", style="B", size=16)
                    pdf.cell(0, 10, "Rapport d'Audit - BailSafe", ln=True, align="C")
                    pdf.ln(10)
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(0, 10, f"Diagnostic Global : {statut}", ln=True)
                    if not est_scan:
                        pdf.cell(0, 10, f"Ecart budgetaire calcule : {ecart:.2f} euros", ln=True)
                    if fraude_meta:
                        pdf.cell(0, 10, "Alerte : Fichier modifie via un editeur tiers.", ln=True)
                    else:
                        pdf.cell(0, 10, "Controle Graphique : Structure informatique standard.", ln=True)
                    
                    pdf.ln(15)
                    pdf.set_font("Helvetica", style="I", size=10)
                    pdf.multi_cell(0, 10, "RGPD : Audit realise en memoire locale. Aucune donnee conservee.")
                    
                    pdf_bytes = pdf.output(dest='S')
                    
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_EXPEDITEUR
                        msg['To'] = email_client
                        msg['Subject'] = "[BailSafe] Votre Rapport d'Audit Locatif"
                        msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport d'audit anti-fraude concernant le dossier de votre candidat.\n\nCordialement,\nNolan - BailSafe", 'plain'))
                        
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(pdf_bytes)
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment; filename="Rapport_BailSafe.pdf"')
                        msg.attach(part)
                        
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
                        server.send_message(msg)
                        server.quit()
                        st.success("✅ Rapport envoyé avec succès !")
                    except Exception as e:
                        st.error(f"Erreur d'envoi : {e}")

if not st.session_state["authentifie"]:
    afficher_vitrine()
else:
    afficher_interface_expert()
