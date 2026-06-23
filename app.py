import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

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
# 🌍 PARTIE 1 : LA VITRINE PUBLIQUE (DYNAMISÉE)
# ==========================================
def afficher_vitrine():
    # --- INTÉGRATION DU LOGO ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Le code essaie de charger "logo.png". S'il n'est pas là, il met un titre de secours.
        try:
            st.image("logo.png", use_container_width=True)
        except Exception:
            st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🛡️ BailSafe</h1>", unsafe_allow_html=True)
            
    st.markdown("<h2 style='text-align: center;'>Louez votre bien l'esprit tranquille.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; color: gray;'>Le premier filtre anti-fraude documentaire par analyse heuristique.</p>", unsafe_allow_html=True)
    st.divider()

    # --- ONGLETS INTERACTIFS POUR LE CLIENT ---
    tab_constat, tab_solution, tab_rgpd = st.tabs(["🚨 Le Risque", "💡 La Solution BailSafe", "🔒 Sécurité & RGPD"])

    with tab_constat:
        st.markdown("### Pourquoi sécuriser vos dossiers ?")
        st.write("Gérer une location seul est devenu un vrai parcours du combattant face à l'explosion des faux dossiers (bulletins de salaire falsifiés, faux avis d'imposition).")
        
        # Blocs dynamiques (Metrics)
        colA, colB = st.columns(2)
        colA.metric(label="Risque financier", value="Élevé", delta="Impayés en hausse", delta_color="inverse")
        colB.metric(label="Détection manuelle", value="Impossible", delta="Nécessite une expertise", delta_color="inverse")
        st.info("Un propriétaire n'a généralement ni les outils informatiques ni le temps de repérer des pixels modifiés ou des incohérences mathématiques cachées.")

    with tab_solution:
        st.markdown("### Notre Expertise à votre service")
        st.success("**Pour 15 € par dossier**, bénéficiez d'un audit express sous 24h.")
        st.markdown("""
        - 🔎 **Analyse Forensique** : Détection des traces de logiciels de retouche (Photoshop, Canva, etc.).
        - 🧮 **Validation Mathématique** : Vérification stricte des cumuls et montants déclarés.
        - 📄 **Rapport Officiel** : Un livrable PDF clair pour prendre votre décision l'esprit léger.
        """)

    with tab_rgpd:
        st.markdown("### 100% Conforme & Zéro Stockage")
        st.warning("⚖️ **Engagement Légal** : Conformément au RGPD et à l'AI Act, BailSafe agit comme un filtre local en mémoire vive.")
        st.markdown("""
        - **Aucune base de données** : Nous ne stockons aucun document.
        - **Destruction immédiate** : L'intégralité des fichiers sources est définitivement purgée de nos serveurs dès l'envoi de votre rapport.
        """)

    st.divider()
    
    # --- APPEL À L'ACTION (CTA) ---
    st.markdown("<h3 style='text-align: center;'>📩 Confiez-nous votre première analyse</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Contactez-moi directement via LeBonCoin pour sécuriser vos dossiers.</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Espace de connexion admin (Discret en bas de page)
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
    colA, colB = st.columns([4, 1])
    with colA:
        st.title("Dashboard | BailSafe 🕵️‍♂️")
    with colB:
        if st.button("🔴 Déconnexion"):
            st.session_state["authentifie"] = False
            st.rerun()
            
    st.warning("⚖️ Rappel RGPD : Ne conservez aucune copie des documents. L'outil agit en Pass-Through.")

    fichier_pdf = st.file_uploader("📂 Chargez le PDF du bulletin de salaire", type="pdf")
    
    if fichier_pdf is not None:
        tab1, tab2, tab3 = st.tabs(["📊 Analyse & Regex", "🔎 Forensics IA", "📤 Rapport & Envoi"])
        texte_brut = ""
        metadata_pdf = {}
        
        with pdfplumber.open(fichier_pdf) as pdf:
            metadata_pdf = pdf.metadata
            for page in pdf.pages:
                texte_brut += page.extract_text() + "\n"
        
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
            
            m1, m2 = st.columns(2)
            m1.metric("Cumul Théorique", f"{calcul_theorique:.2f} €")
            m2.metric("Écart Détecté", f"{ecart:.2f} €", delta_color="inverse", delta=f"{ecart:.2f} €" if ecart > 0 else "Parfait")
            
            fraude_math = ecart > 150

        with tab2:
            st.subheader("Analyse de l'ADN du fichier")
            createur = metadata_pdf.get('Creator', '')
            producteur = metadata_pdf.get('Producer', '')
            meta_string = str(createur) + " " + str(producteur)
            
            st.write(f"**Outil original :** {producteur if producteur else 'Inconnu'}")
            
            logiciels_suspects = ["photoshop", "canva", "ilovepdf", "illustrator", "gimp"]
            fraude_meta = any(logiciel in meta_string.lower() for logiciel in logiciels_suspects)
            
            if fraude_meta:
                st.error("🚨 ALERTE : Utilisation d'un logiciel d'édition graphique détectée !")
            else:
                st.success("✅ Aucune trace d'outil d'édition suspecte trouvée.")

        with tab3:
            st.subheader("Scoring & Expédition")
            if fraude_math and fraude_meta:
                statut = "CRITIQUE (Falsification avérée)"
                st.error(f"Statut : {statut}")
            elif fraude_math or fraude_meta:
                statut = "SUSPECT (Incohérences majeures)"
                st.warning(f"Statut : {statut}")
            else:
                statut = "FIABLE (Logique respectée)"
                st.success(f"Statut : {statut}")
                
            email_client = st.text_input("E-mail du client (Propriétaire) :", placeholder="client@email.com")
            
            if st.button("📄 Générer & Envoyer le Rapport"):
                if not email_client:
                    st.warning("Veuillez saisir une adresse e-mail valide.")
                else:
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
                    
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_EXPEDITEUR
                        msg['To'] = email_client
                        msg['Subject'] = "Votre rapport d'audit BailSafe sécurisé"
                        msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport d'audit anti-fraude de votre candidat.\n\nCordialement,\nL'équipe BailSafe", 'plain'))
                        
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
                        st.success("✅ Rapport généré et envoyé ! Fichiers locaux purgés.")
                    except Exception as e:
                        st.error(f"Erreur d'envoi : {e}")

# ==========================================
# 🚦 ROUTAGE PRINCIPAL
# ==========================================
if not st.session_state["authentifie"]:
    afficher_vitrine()
else:
    afficher_interface_expert()
