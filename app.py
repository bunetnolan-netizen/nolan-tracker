import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# ==========================================
# ⚙️ CONFIGURATION & IDENTIFIANTS
# ==========================================
MOT_DE_PASSE_ATTENDU = "Nolan18!!"  # 🔴 À CHANGER AVANT DE METTRE SUR GITHUB
EMAIL_EXPEDITEUR = "bunetnolan@gmail.com" # 🔴 TON ADRESSE GMAIL
MOT_DE_PASSE_EMAIL = "uimd wahc rnbg enmh" # 🔴 TON MOT DE PASSE D'APPLICATION GMAIL
OBJECTIF_ORDINATEUR = 800  # Objectif financier en euros

# Configuration de la page
st.set_page_config(page_title="BailSafe | Audit Locatif Anti-Fraude", page_icon="🛡️", layout="centered")

# Gestion de la session (Connecté ou non + Cagnotte)
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False
if "cagnotte" not in st.session_state:
    st.session_state["cagnotte"] = 0

# ==========================================
# 🌍 PARTIE 1 : LA VITRINE PUBLIQUE
# ==========================================
def afficher_vitrine():
    # En-tête
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ BailSafe</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Louez votre bien l'esprit tranquille.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Ne laissez plus les faux dossiers menacer votre rentabilité.</p>", unsafe_allow_html=True)
    st.divider()

    # Le Problème & La Solution
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚨 Le Constat")
        st.write("Gérer une location seul est devenu un vrai parcours du combattant face à l'explosion des faux dossiers (bulletins de salaire modifiés, faux avis d'imposition). Un propriétaire n'a ni le temps ni les outils pour repérer ces fraudes invisibles à l'œil nu.")
    with col2:
        st.markdown("### 💡 Notre Solution")
        st.write("**BailSafe** audite les candidatures de vos futurs locataires. Pour **15 € par dossier**, bénéficiez d'une détection de fraudes graphiques et d'une vérification mathématique et fiscale sous 24h.")
    
    st.divider()

    # Comment ça marche
    st.markdown("### 🛠️ Comment ça marche ?")
    st.markdown("""
    1. **Transmission :** Vous nous envoyez les pièces justificatives de votre candidat.
    2. **Audit Expert :** Notre protocole analyse la cohérence logique et graphique (test du zoom, calculs des cumuls, vérifications officielles).
    3. **Rapport express :** Vous recevez un rapport de fiabilité clair sous 24h pour choisir votre locataire sereinement.
    """)

    # Réassurance
    st.info("🔒 **100% Sécurisé & Conforme RGPD :** Conformément au Règlement Général sur la Protection des Données (RGPD) et à l'AI Act, BailSafe agit comme un filtre local. **Aucun document n'est stocké.** L'intégralité des fichiers sources est définitivement détruite dès la clôture de l'audit.")

    # Call to action
    st.markdown("<h3 style='text-align: center;'>📩 Sécurisez vos dossiers dès maintenant</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Contactez-moi directement via LeBonCoin pour me confier votre première analyse.</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Espace de connexion admin
    with st.expander("🔐 Accès Expert (Administration)"):
        mdp_saisi = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if mdp_saisi == MOT_DE_PASSE_ATTENDU:
                st.session_state["authentifie"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")

# ==========================================
# 🕵️‍♂️ PARTIE 2 : L'INTERFACE EXPERT (PRIVÉE)
# ==========================================
def afficher_interface_expert():
    # En-tête de déconnexion
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success("🟢 Mode Expert activé.")
    with col2:
        if st.button("Se déconnecter"):
            st.session_state["authentifie"] = False
            st.rerun()
            
    st.title("Scanner BailSafe 🕵️‍♂️")

    # --- 💰 LA CAGNOTTE ---
    st.markdown("### 🎯 Objectif Nouvel Ordinateur")
    progression = st.session_state["cagnotte"] / OBJECTIF_ORDINATEUR
    st.progress(min(progression, 1.0))
    st.write(f"**Cagnotte : {st.session_state['cagnotte']} € / {OBJECTIF_ORDINATEUR} €**")
    
    if st.button("➕ Encaisser 15 €"):
        st.session_state["cagnotte"] += 15
        st.rerun()
        
    st.divider()

    # --- ⚖️ LE BANDEAU RGPD ---
    st.info("""
    **Rappel Légal & Conformité RGPD / AI Act :**
    - **Consentement :** Assurez-vous que le propriétaire a obtenu l'accord explicite de son candidat.
    - **Zéro Stockage :** Ne conservez aucune copie des documents. L'outil efface tout à la fin de la session.
    - **Limites d'investigation :** L'investigation externe (ex: appeler un employeur) est strictement interdite. C'est un audit technique et mathématique.
    """)
    
    # --- 📄 SCANNER & EXTRACTION REGEX ---
    fichier_pdf = st.file_uploader("Chargez le PDF du bulletin de salaire", type="pdf")
    
    if fichier_pdf is not None:
        st.write("### 1. Analyse Mathématique Automatique")
        texte_brut = ""
        with pdfplumber.open(fichier_pdf) as pdf:
            for page in pdf.pages:
                texte_brut += page.extract_text() + "\n"
        
        # Regex pour extraction automatique
        net_a_payer_match = re.search(r'(?i)net\s*[àa]\s*payer\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
        cumul_imposable_match = re.search(r'(?i)cumul\s*imposable\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
        
        net_extrait = net_a_payer_match.group(1).replace(' ', '').replace(',', '.') if net_a_payer_match else "0"
        cumul_extrait = cumul_imposable_match.group(1).replace(' ', '').replace(',', '.') if cumul_imposable_match else "0"
        
        col1, col2, col3 = st.columns(3)
        net_saisi = col1.number_input("Net à payer mensuel (€)", value=float(net_extrait))
        nb_mois = col2.number_input("Mois de l'année (ex: 6 pour Juin)", min_value=1, max_value=12, value=1)
        cumul_saisi = col3.number_input("Cumul Imposable déclaré (€)", value=float(cumul_extrait))
        
        calcul_theorique = net_saisi * nb_mois
        ecart = abs(cumul_saisi - calcul_theorique)
        
        st.write(f"**Cumul Théorique calculé :** {calcul_theorique:.2f} €")
        st.write(f"**Écart détecté :** {ecart:.2f} €")
        
        if ecart > 150:
            st.error("🚨 Écart illogique détecté ! Falsification mathématique probable.")
            statut = "🔴 SUSPECT"
        else:
            st.success("✅ Logique mathématique cohérente.")
            statut = "🟢 FIABLE"
            
        st.write("### 2. Rapport & Envoi")
        email_client = st.text_input("Adresse e-mail du client propriétaire :")
        
        if st.button("Générer et Envoyer le rapport PDF"):
            # Création du PDF fpdf2
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            pdf.cell(0, 10, "Rapport d'Audit - BailSafe", ln=True, align="C")
            statut_propre = statut.replace("🔴", "").replace("🟢", "").replace("🟡", "").strip()
            pdf.cell(0, 10, f"Statut Global : {statut_propre}", ln=True)
            pdf.cell(0, 10, f"Ecart detecte : {ecart:.2f} euros", ln=True)
            pdf.multi_cell(0, 10, "Conformément au RGPD, toutes les pièces analysées pour cet audit ont été définitivement supprimées de nos systèmes à la livraison de ce rapport.")
            
            pdf_bytes = pdf.output(dest='S')
            
            # Code d'envoi par e-mail
            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_EXPEDITEUR
                msg['To'] = email_client
                msg['Subject'] = "Votre rapport d'audit BailSafe"
                msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport d'audit anti-fraude express que vous avez demandé.\n\nCordialement,\nL'équipe BailSafe", 'plain'))
                
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
                st.success("✅ Rapport généré et envoyé avec succès au propriétaire !")
            except Exception as e:
                st.error(f"Erreur lors de l'envoi de l'e-mail : {e}")

# ==========================================
# 🚦 ROUTAGE PRINCIPAL
# ==========================================
if not st.session_state["authentifie"]:
    afficher_vitrine()
else:
    afficher_interface_expert()
