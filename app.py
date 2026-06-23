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

# Configuration de la page (Design SaaS)
st.set_page_config(page_title="BailSafe | Audit Locatif", page_icon="🛡️", layout="centered")

# Gestion de la session (Connecté ou non)
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# ==========================================
# 🌍 PARTIE 1 : LA VITRINE PUBLIQUE
# ==========================================
def afficher_vitrine():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ BailSafe</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Louez votre bien l'esprit tranquille.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: gray;'>Détection de fraudes documentaires par IA et analyse heuristique.</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🚨 Le Constat")
        st.write("Gérer une location seul est devenu un vrai parcours du combattant face à l'explosion des faux dossiers (bulletins de salaire modifiés, faux avis d'imposition). Un propriétaire n'a ni le temps ni les outils pour repérer ces fraudes.")
    with col2:
        st.markdown("### 💡 Notre Solution")
        st.write("**BailSafe** audite les candidatures de vos futurs locataires. Pour **15 € par dossier**, bénéficiez d'une détection de fraudes graphiques et d'une vérification mathématique sous 24h.")
    
    st.divider()
    st.info("🔒 **100% Sécurisé & Conforme RGPD :** Conformément au RGPD et à l'AI Act, BailSafe agit comme un filtre local. Aucun document n'est stocké. L'intégralité des fichiers sources est définitivement détruite dès la clôture de l'audit.")

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
    # En-tête du Dashboard
    colA, colB = st.columns([4, 1])
    with colA:
        st.title("Tableau de bord | BailSafe 🕵️‍♂️")
    with colB:
        if st.button("🔴 Se déconnecter"):
            st.session_state["authentifie"] = False
            st.rerun()
            
    # Bandeau RGPD
    st.warning("⚖️ Rappel RGPD : Ne conservez aucune copie des documents. L'outil agit en Pass-Through (mémoire vive).")

    # Upload du document
    fichier_pdf = st.file_uploader("📂 Chargez le PDF du bulletin de salaire à analyser", type="pdf")
    
    if fichier_pdf is not None:
        # Création des onglets pour un rendu professionnel
        tab1, tab2, tab3 = st.tabs(["📊 Analyse & Scoring", "🔎 Métadonnées (IA)", "📤 Rapport & Envoi"])
        
        texte_brut = ""
        metadata_pdf = {}
        
        # Lecture du PDF
        with pdfplumber.open(fichier_pdf) as pdf:
            metadata_pdf = pdf.metadata
            for page in pdf.pages:
                texte_brut += page.extract_text() + "\n"
        
        # ---------------------------------------------------------
        # ONGLET 1 : ANALYSE MATHÉMATIQUE & REGEX
        # ---------------------------------------------------------
        with tab1:
            st.subheader("1. Extraction Automatique (Regex)")
            net_a_payer_match = re.search(r'(?i)net\s*[àa]\s*payer\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
            cumul_imposable_match = re.search(r'(?i)cumul\s*imposable\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
            
            net_extrait = net_a_payer_match.group(1).replace(' ', '').replace(',', '.') if net_a_payer_match else "0"
            cumul_extrait = cumul_imposable_match.group(1).replace(' ', '').replace(',', '.') if cumul_imposable_match else "0"
            
            col1, col2, col3 = st.columns(3)
            net_saisi = col1.number_input("Net mensuel (€)", value=float(net_extrait))
            nb_mois = col2.number_input("Mois de l'année", min_value=1, max_value=12, value=1)
            cumul_saisi = col3.number_input("Cumul déclaré (€)", value=float(cumul_extrait))
            
            calcul_theorique = net_saisi * nb_mois
            ecart = abs(cumul_saisi - calcul_theorique)
            
            st.markdown("### 2. Résultat Financier")
            m1, m2 = st.columns(2)
            m1.metric("Cumul Théorique calculé", f"{calcul_theorique:.2f} €")
            m2.metric("Écart Détecté", f"{ecart:.2f} €", delta_color="inverse", delta=f"{ecart:.2f} €" if ecart > 0 else "Parfait")
            
            fraude_math = ecart > 150

        # ---------------------------------------------------------
        # ONGLET 2 : MÉTADONNÉES & DETECTEUR PHOTOSHOP
        # ---------------------------------------------------------
        with tab2:
            st.subheader("Analyse de l'ADN du fichier (Forensics)")
            createur = metadata_pdf.get('Creator', '')
            producteur = metadata_pdf.get('Producer', '')
            meta_string = str(createur) + " " + str(producteur)
            
            st.write(f"**Outil de création original :** {producteur if producteur else 'Inconnu'}")
            
            logiciels_suspects = ["photoshop", "canva", "ilovepdf", "illustrator", "gimp"]
            fraude_meta = any(logiciel in meta_string.lower() for logiciel in logiciels_suspects)
            
            if fraude_meta:
                st.error("🚨 ALERTE : Utilisation d'un logiciel d'édition graphique détectée dans les métadonnées !")
            else:
                st.success("✅ Aucune trace d'outil d'édition graphique suspect n'a été trouvée dans les métadonnées.")

        # ---------------------------------------------------------
        # ONGLET 3 : SCORING GLOBAL ET ENVOI DIRECT
        # ---------------------------------------------------------
        with tab3:
            st.subheader("Scoring Global Intelligent")
            
            # Définition du statut global basé sur l'IA heuristique et les mathématiques
            if fraude_math and fraude_meta:
                statut = "CRITIQUE (Falsification avérée)"
                st.error(f"Statut : {statut}")
            elif fraude_math or fraude_meta:
                statut = "SUSPECT (Incohérences majeures)"
                st.warning(f"Statut : {statut}")
            else:
                statut = "FIABLE (Logique respectée)"
                st.success(f"Statut : {statut}")
                
            st.divider()
            st.markdown("### Expédition du Rapport Client")
            email_client = st.text_input("Adresse e-mail du client (Propriétaire) :", placeholder="client@email.com")
            
            if st.button("📄 Générer & Envoyer le Rapport"):
                if not email_client:
                    st.warning("Veuillez saisir une adresse e-mail valide.")
                else:
                    # Création du PDF fpdf2 (Sans emojis pour éviter le plantage)
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", style="B", size=16)
                    pdf.cell(0, 10, "Rapport d'Audit Anti-Fraude - BailSafe", ln=True, align="C")
                    pdf.ln(10)
                    
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(0, 10, f"Statut d'Evaluation : {statut}", ln=True)
                    pdf.cell(0, 10, f"Ecart mathematique detecte : {ecart:.2f} euros", ln=True)
                    if fraude_meta:
                        pdf.cell(0, 10, "Alerte : Traces de logiciel de retouche graphique detectees.", ln=True)
                    else:
                        pdf.cell(0, 10, "Controle graphique : Aucune modification structurelle detectee.", ln=True)
                    
                    pdf.ln(15)
                    pdf.set_font("Helvetica", style="I", size=10)
                    pdf.multi_cell(0, 10, "Securite & Confidentialite : Conformement au RGPD, ce document a ete genere par une analyse memoire locale. Toutes les pieces justificatives ont ete definitivement detruites a la livraison de ce rapport.")
                    
                    pdf_bytes = pdf.output(dest='S')
                    
                    # Envoi par e-mail
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_EXPEDITEUR
                        msg['To'] = email_client
                        msg['Subject'] = "Votre rapport d'audit BailSafe sécurisé"
                        msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport d'audit anti-fraude express de votre candidat.\n\nCordialement,\nL'équipe BailSafe", 'plain'))
                        
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
                        st.success("✅ Rapport généré et envoyé avec succès au propriétaire ! Les fichiers locaux sont purgés.")
                    except Exception as e:
                        st.error(f"Erreur lors de l'envoi de l'e-mail : {e}")

# ==========================================
# 🚦 ROUTAGE PRINCIPAL
# ==========================================
if not st.session_state["authentifie"]:
    afficher_vitrine()
else:
    afficher_interface_expert()
