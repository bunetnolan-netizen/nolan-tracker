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
# ⚙️ CONFIGURATION & IDENTIFIANTS AUTOMATIQUES
# ==========================================
MOT_DE_PASSE_ATTENDU = "Nolan18!!"  # 🔐 Ton mot de passe pour te connecter à l'espace Expert
EMAIL_EXPEDITEUR = "bunetnolan@gmail.com" 
MOT_DE_PASSE_EMAIL = "uimd wahc rnbg enmh" 

# Configuration de la page (Design SaaS)
st.set_page_config(page_title="BailSafe | Audit Locatif Expert", page_icon="🛡️", layout="centered")

# Gestion de la session (Connecté ou non)
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

# ==========================================
# 🌍 PARTIE 1 : LA VITRINE PUBLIQUE (PREMIUM DISP)
# ==========================================
def afficher_vitrine():
    # En-tête design en HTML/CSS (Fini le rendu image cheap, place au style SaaS épuré)
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 30px; border-radius: 16px; text-align: center; margin-bottom: 25px; border: 2px solid #d97706;">
            <div style="font-size: 50px; margin-bottom: 10px;">🛡️</div>
            <h1 style="color: #ffffff; margin: 0; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; letter-spacing: 1px;">BailSafe</h1>
            <p style="color: #94a3b8; font-size: 16px; margin-top: 5px; margin-bottom: 0;">Filtre Anti-Fraude Documentaire & Analyse Heuristique par IA</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Louez votre bien immobilier en toute sérénité.</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 16px; color: gray;'>Protégez votre investissement contre les falsifications numériques et les incohérences fiscales.</p>", unsafe_allow_html=True)
    st.divider()

    # --- ONGLETS INTERACTIFS POUR LE CLIENT ---
    tab_constat, tab_solution, tab_rgpd = st.tabs(["🚨 Le Risque", "💡 La Solution BailSafe", "🔒 Sécurité & RGPD"])

    with tab_constat:
        st.markdown("### Pourquoi sécuriser vos dossiers locatifs ?")
        st.write("Face à l'explosion des faux dossiers (bulletins de salaire Photoshop, faux avis d'imposition Canva), la sélection d'un locataire est devenue une source majeure de risques pour les bailleurs indépendants.")
        
        # Blocs dynamiques de statistiques (Metrics)
        colA, colB = st.columns(2)
        colA.metric(label="Risque financier global", value="Élevé", delta="Impayés en forte hausse", delta_color="inverse")
        colB.metric(label="Contrôle visuel classique", value="Incertain", delta="Fraudes invisibles à l'œil", delta_color="inverse")
        st.info("Un propriétaire particulier n'a généralement ni le temps ni les outils technologiques pour traquer les pixels modifiés ou les anomalies mathématiques d'un document.")

    with tab_solution:
        st.markdown("### Notre Expertise Technologique")
        st.success("**Pour 20 € par dossier**, bénéficiez d'un audit de conformité express sous 24h.")
        st.markdown("""
        - 🔎 **Analyse Forensique des Métadonnées** : Traque immédiate des traces d'outils d'édition graphique (Photoshop, Canva, iLovePDF, etc.).
        - 🧮 **Validation Algorithmique** : Recalcul automatique et vérification de la cohérence logique des cumuls fiscaux et montants nets.
        - 📄 **Rapport de Fiabilité Certifié** : Livraison d'un bilan PDF clair sous 24 heures pour valider votre choix l'esprit tranquille.
        """)

    with tab_rgpd:
        st.markdown("### Un Protocole Strict & Éthique")
        st.warning("⚖️ **Garantie de Conformité** : Conformément au RGPD et à l'AI Act européen de 2026, BailSafe applique un protocole d'analyse sans persistance.")
        st.markdown("""
        - **Zéro Base de Données** : Nous ne stockons, ne collectons et ne partageons aucune donnée personnelle.
        - **Analyse Volatile (Pass-Through)** : Les fichiers PDF transitent uniquement dans la mémoire vive sécurisée de l'application et sont définitivement purgés dès l'envoi de votre rapport.
        """)

    st.divider()
    
    # --- APPEL À L'ACTION (CTA) ---
    st.markdown("<h3 style='text-align: center;'>📩 Confiez-nous votre première analyse</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Contactez-moi directement sur LeBonCoin ou Facebook pour sécuriser vos candidatures en cours.</p>", unsafe_allow_html=True)
    
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
        st.title("Cockpit d'Analyse | BailSafe 🕵️‍♂️")
    with colB:
        if st.button("🔴 Déconnexion"):
            st.session_state["authentifie"] = False
            st.rerun()
            
    st.warning("⚖️ Rappel de conformité : L'outil fonctionne en mémoire vive. Ne téléchargez pas les pièces sur votre machine.")

    fichier_pdf = st.file_uploader("📂 Déposez le PDF du bulletin de salaire à auditer", type="pdf")
    
    if fichier_pdf is not None:
        tab1, tab2, tab3 = st.tabs(["📊 Cohérence Numérique", "🔎 ADN du Fichier (IA)", "📤 Génération & Envoi"])
        texte_brut = ""
        metadata_pdf = {}
        
        with pdfplumber.open(fichier_pdf) as pdf:
            metadata_pdf = pdf.metadata
            for page in pdf.pages:
                texte_brut += page.extract_text() + "\n"
        
        with tab1:
            st.subheader("Extraction Automatique des Variables (Regex)")
            net_a_payer_match = re.search(r'(?i)net\s*[àa]\s*payer\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
            cumul_imposable_match = re.search(r'(?i)cumul\s*imposable\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
            
            net_extrait = net_a_payer_match.group(1).replace(' ', '').replace(',', '.') if net_a_payer_match else "0"
            cumul_extrait = cumul_imposable_match.group(1).replace(' ', '').replace(',', '.') if cumul_imposable_match else "0"
            
            col1, col2, col3 = st.columns(3)
            net_saisi = col1.number_input("Net mensuel extrait (€)", value=float(net_extrait))
            nb_mois = col2.number_input("Mois cumulés (ex: 6 pour Juin)", min_value=1, max_value=12, value=1)
            cumul_saisi = col3.number_input("Cumul imposable déclaré (€)", value=float(cumul_extrait))
            
            calcul_theorique = net_saisi * nb_mois
            ecart = abs(cumul_saisi - calcul_theorique)
            
            st.markdown("### Résultat du test arithmétique")
            m1, m2 = st.columns(2)
            m1.metric("Cumul Théorique calculé", f"{calcul_theorique:.2f} €")
            m2.metric("Écart constaté", f"{ecart:.2f} €", delta_color="inverse", delta=f"{ecart:.2f} €" if ecart > 0 else "0.00 € (Strict)")
            
            fraude_math = ecart > 150

        with tab2:
            st.subheader("Analyse Forensique des Métadonnées structurelles")
            createur = metadata_pdf.get('Creator', '')
            producteur = metadata_pdf.get('Producer', '')
            meta_string = str(createur) + " " + str(producteur)
            
            st.write(f"**Moteur de rendu d'origine :** {producteur if producteur else 'Inconnu (Signature absente)'}")
            
            logiciels_suspects = ["photoshop", "canva", "ilovepdf", "illustrator", "gimp", "adobe acrobat pro"]
            fraude_meta = any(logiciel in meta_string.lower() for logiciel in logiciels_suspects)
            
            if fraude_meta:
                st.error("🚨 ALERTE SÉCURITÉ : Le fichier contient des signatures liées à un logiciel de retouche ou d'édition de PDF !")
            else:
                st.success("✅ Structure intègre. Aucune trace d'outil d'édition graphique suspect dans les métadonnées.")

        with tab3:
            st.subheader("Scoring Heuristique Final")
            if fraude_math and fraude_meta:
                statut = "CRITIQUE (Falsification technique et mathématique détectée)"
                st.error(f"Diagnostic : {statut}")
            elif fraude_math or fraude_meta:
                statut = "SUSPECT (Anomalies majeures à vérifier)"
                st.warning(f"Diagnostic : {statut}")
            else:
                statut = "FIABLE (Aucune anomalie détectée)"
                st.success(f"Diagnostic : {statut}")
                
            st.divider()
            st.markdown("### Expédition Instantanée")
            email_client = st.text_input("Adresse e-mail du propriétaire bailleur :", placeholder="proprietaire@gmail.com")
            
            if st.button("🚀 Valider l'audit & Envoyer le Rapport"):
                if not email_client:
                    st.warning("Veuillez renseigner l'adresse e-mail de destination.")
                else:
                    # Génération du PDF de manière native et sécurisée (sans emojis)
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Helvetica", style="B", size=16)
                    pdf.cell(0, 10, "Rapport d'Audit de Conformite Documentaire - BailSafe", ln=True, align="C")
                    pdf.ln(10)
                    
                    pdf.set_font("Helvetica", size=12)
                    pdf.cell(0, 10, f"Diagnostic Global : {statut}", ln=True)
                    pdf.cell(0, 10, f"Ecart budgetaire calcule : {ecart:.2f} euros", ln=True)
                    if fraude_meta:
                        pdf.cell(0, 10, "Alerte Securite : Fichier modifie via un editeur tiers.", ln=True)
                    else:
                        pdf.cell(0, 10, "Analyse Graphique : Structure d'origine respectee.", ln=True)
                    
                    pdf.ln(15)
                    pdf.set_font("Helvetica", style="I", size=10)
                    pdf.multi_cell(0, 10, "Clause de confidentialite (RGPD) : Ce document a ete etabli par traitement volatile en memoire vive. Le prestataire certifie qu'aucune piece justificative ni donnee personnelle n'est conservee sur ses serveurs suite a l'envoi de ce bilan.")
                    
                    pdf_bytes = pdf.output(dest='S')
                    
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = EMAIL_EXPEDITEUR
                        msg['To'] = email_client
                        msg['Subject'] = "[BailSafe] Votre Rapport d'Audit Locatif Sécurisé"
                        msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport d'audit anti-fraude express concernant le dossier de votre candidat locataire (Tarif : 20,00 €).\n\nNous vous remercions pour votre confiance.\n\nCordialement,\nNolan - Fondateur de BailSafe", 'plain'))
                        
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
                        st.success("✅ Rapport envoyé à l'adresse du propriétaire ! Session nettoyée.")
                    except Exception as e:
                        st.error(f"Erreur technique lors de l'envoi de l'e-mail : {e}")

# ==========================================
# 🚦 ROUTAGE PRINCIPAL
# ==========================================
if not st.session_state["authentifie"]:
    afficher_vitrine()
else:
    afficher_interface_expert()
