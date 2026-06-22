import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

# 1. CONFIGURATION DE LA PAGE & SÉCURITÉ
st.set_page_config(page_title="Anti-Fraude Scanner Pro", page_icon="🕵️‍♂️", layout="wide")

# Initialisation des variables de session
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False
if "cagnotte" not in st.session_state:
    st.session_state["cagnotte"] = 0.0

# ==========================================
# 🛑 ZONE À MODIFIER PAR TES SOINS
# ==========================================
MOT_DE_PASSE_ATTENDU = "Nolan18!!" 

# Identifiants pour l'envoi d'e-mail automatique
EMAIL_EXPEDITEUR = "bunetnolan@gmail.com" 
MOT_DE_PASSE_EMAIL = "uimd wahc rnbg enmh" 
# ==========================================

# Écran de connexion
if not st.session_state["authentifie"]:
    st.title("🔒 Accès Sécurisé - Anti-Fraude Scanner")
    mdp_saisi = st.text_input("Veuillez entrer le mot de passe expert :", type="password")
    if st.button("Se connecter"):
        if mdp_saisi == MOT_DE_PASSE_ATTENDU:
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect. Accès refusé.")
    st.stop()

# 2. INTERFACE DE L'APPLICATION
st.title("🕵️‍♂️ Anti-Fraude Scanner — Espace Expert")
st.subheader("Analyse de cohérence logique & graphique en temps réel")

# --- SECTION CAGNOTTE ---
col_cagnotte, col_bouton = st.columns([2, 1])
with col_cagnotte:
    objectif = 700.0
    progression = min(st.session_state["cagnotte"] / objectif, 1.0)
    st.progress(progression)
    st.write(f"**Cagnotte Actuelle :** {st.session_state['cagnotte']}€ / {objectif}€")
with col_bouton:
    if st.button("➕ Encaisser un audit (15 €)"):
        st.session_state["cagnotte"] += 15.0
        st.rerun()

# --- BANDEAU DE CONFORMITÉ RÉGLEMENTAIRE ---
st.info("""
⚖️ **Conformité Réglementaire & Sécurité (RGPD & AI Act 2026)**
* **Zéro Stockage :** Les fichiers téléchargés sont traités exclusivement en mémoire vive (RAM) et sont définitivement détruits dès la fermeture de la session. Aucune base de données n'est conservée.
* **Responsabilité :** Cet outil fournit un rapport d'aide à la décision basé sur la cohérence logique et graphique. Il ne se substitue pas à la validation finale du propriétaire bailleur.
* **Obligation du Client :** En utilisant ce scanner, vous certifiez avoir obtenu l'accord préalable du candidat locataire pour la vérification technique de ses pièces justificatives.
""")
st.write("---")

# 3. FONCTIONS D'EXTRACTION ET D'EMAIL
def extraire_texte_pdf(fichier_pdf):
    texte_complet = ""
    with pdfplumber.open(fichier_pdf) as pdf:
        for page in pdf.pages:
            texte_page = page.extract_text()
            if texte_page:
                texte_complet += texte_page + "\n"
    return texte_complet

def analyser_montants_regex(texte):
    net_payer, cumul_imposable = 0.0, 0.0
    pattern_montant = r"[\d\s]+[.,]\s*\d{2}"
    
    match_net = re.search(r"(?:net\s+a\s+payer|net\s+paye|remuneration\s+nette)\s*[:\s]*(" + pattern_montant + ")", texte, re.IGNORECASE)
    if match_net:
        try: net_payer = float(match_net.group(1).replace(" ", "").replace(",", "."))
        except: pass
        
    match_cumul = re.search(r"(?:cumul\s+net\s+imposable|net\s+imposable\s+cumul|cumul\s+imposable)\s*[:\s]*(" + pattern_montant + ")", texte, re.IGNORECASE)
    if match_cumul:
        try: cumul_imposable = float(match_cumul.group(1).replace(" ", "").replace(",", "."))
        except: pass
        
    return net_payer, cumul_imposable

def envoyer_rapport_email(email_destinataire, donnees_pdf, nom_fichier):
    msg = EmailMessage()
    msg['Subject'] = "🔒 Votre Rapport d'Audit Anti-Fraude (Confidentiel)"
    msg['From'] = f"Service Audit <{EMAIL_EXPEDITEUR}>"
    msg['To'] = email_destinataire
    
    corps_email = """Bonjour,

Veuillez trouver ci-joint le rapport d'audit anti-fraude concernant le dossier de votre candidat locataire. 

Conformément à nos engagements de confidentialité (RGPD), toutes les pièces justificatives analysées ont été supprimées de nos serveurs sécurisés sitôt l'audit terminé.

Nous restons à votre entière disposition.

Cordialement,
Votre Expert Anti-Fraude"""
    
    msg.set_content(corps_email)
    msg.add_attachment(donnees_pdf, maintype='application', subtype='pdf', filename=nom_fichier)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return False

# 4. ZONE DE CHARGEMENT DU DOSSIER
st.header("📂 Étape 1 : Analyse du Bulletin de Salaire")
fichier_charge = st.file_uploader("Glissez-déposez le bulletin de salaire (PDF uniquement)", type=["pdf"])

net_saisi, cumul_saisi, nb_mois = 0.0, 0.0, 1

if fichier_charge is not None:
    texte_extrait = extraire_texte_pdf(fichier_charge)
    net_auto, cumul_auto = analyser_montants_regex(texte_extrait)
    st.success("✅ Analyse du document effectuée en mémoire RAM.")
else:
    net_auto, cumul_auto = 0.0, 0.0

col1, col2, col3 = st.columns(3)
with col1: net_saisi = st.number_input("Net à payer mensuel (€) :", value=net_auto, step=10.0)
with col2: cumul_saisi = st.number_input("Cumul Net Imposable (€) :", value=cumul_auto, step=50.0)
with col3: nb_mois = st.number_input("Mois du cumul :", min_value=1, max_value=12, value=1)

# 5. DIAGNOSTIC
st.header("📊 Étape 2 : Diagnostic de Cohérence Financière")
attendu_cumul = net_saisi * nb_mois
ecart = abs(cumul_saisi - attendu_cumul)

statut_global = "🟡 VIGILANCE"

if net_saisi > 0 and cumul_saisi > 0:
    st.write(f"**Cumul théorique attendu :** {attendu_cumul:.2f} €")
    st.write(f"**Cumul réel déclaré :** {cumul_saisi:.2f} €")
    if ecart <= 50.0:
        statut_global = "🟢 FIABLE"
        st.success(f" {statut_global} — Parfaite cohérence mathématique.")
    else:
        statut_global = "🔴 SUSPECT"
        st.error(f"⚠️ {statut_global} — Incohérence majeure ! Écart : {ecart:.2f} €.")

# 6. GÉNÉRATION DU PDF ET ENVOI
st.header("📥 Étape 3 : Livraison du Rapport")

def generer_pdf_rapport(statut, net, cumul, mois, ecart_val):
    pdf = FPDF()
    pdf.add_page()
    
    # NETTOYAGE : On retire l'emoji pour que le PDF ne plante pas
    statut_propre = statut.replace("🟢 ", "").replace("🔴 ", "").replace("🟡 ", "")
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RAPPORT D'AUDIT ANTI-FRAUDE IMMOBILIERE", ln=True, align="C")
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    # Utilisation de la variable propre (sans emoji)
    pdf.cell(0, 10, f"Statut Global : {statut_propre}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Montant net mensuel analyse : {net:.2f} EUR", ln=True)
    pdf.cell(0, 8, f"- Cumul net imposable declare : {cumul:.2f} EUR (sur {mois} mois)", ln=True)
    pdf.cell(0, 8, f"- Ecart detecte : {ecart_val:.2f} EUR", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 5, "Securite & Confidentialite (RGPD & AI Act 2026) : Ce rapport est genere par analyse locale. Aucune donnee source n'est stockee.")
    
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

if net_saisi > 0 and cumul_saisi > 0:
    donnees_pdf = generer_pdf_rapport(statut_global, net_saisi, cumul_saisi, nb_mois, ecart)
    nom_fichier_export = f"Rapport_Audit_{statut_global.replace(' ', '_').replace('🟢_', '').replace('🔴_', '').replace('🟡_', '')}.pdf"
    
    st.download_button(label="📥 Télécharger le Rapport (PDF)", data=donnees_pdf, file_name=nom_fichier_export, mime="application/pdf")
    
    st.write("---")
    st.subheader("📧 Envoi direct au client")
    email_client = st.text_input("Adresse e-mail du propriétaire (Optionnel) :", placeholder="exemple@client.com")
    
    if st.button("🚀 Envoyer le rapport par e-mail"):
        with st.spinner("Envoi de l'e-mail en cours..."):
            if email_client:
                succes = envoyer_rapport_email(email_client, donnees_pdf, nom_fichier_export)
                if succes:
                    st.success(f"✅ Le rapport a été envoyé avec succès à l'adresse : {email_client}")
                else:
                    st.error("❌ Échec de l'envoi. Veuillez vérifier vos identifiants (Email et Mot de passe d'application) dans le code source.")
            else:
                st.warning("⚠️ Veuillez entrer une adresse e-mail valide avant de cliquer sur Envoyer.")
else:
    st.info("Veuillez charger un document ou remplir les données d'analyse pour débloquer l'export et l'envoi du rapport.")
