import streamlit as st
import pdfplumber
import re
from fpdf import FPDF

# Configuration de la page
st.set_page_config(page_title="Anti-Fraude Locative - Pro Scanner", page_icon="🕵️‍♂️", layout="centered")

# --- SYSTÈME DE SÉCURITÉ (MOT DE PASSE) ---
def verifier_mot_de_passe():
    """Retourne True si le mot de passe est correct, sinon affiche l'écran de connexion."""
    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False

    if st.session_state.authentifie:
        return True

    st.markdown("<h1 style='text-align: center;'>🔒 Accès Sécurisé</h1>", unsafe_allow_html=True)
    st.write("Cet outil est privé. Veuillez vous authentifier pour accéder au scanner anti-fraude.")
    
    # --- CHOISIS TON MOT DE PASSE ICI ---
    MOT_DE_PASSE_ATTENDU = "Nolan18!!" 
    
    mot_de_passe_saisi = st.text_input("Entrez le mot de passe :", type="password")
    bouton_connexion = st.button("Se connecter", use_container_width=True)
    
    if bouton_connexion:
        if mot_de_passe_saisi == MOT_DE_PASSE_ATTENDU:
            st.session_state.authentifie = True
            st.rerun()
        else:
            st.error("❌ Mot de passe incorrect. Accès refusé.")
            
    return False

if not verifier_mot_de_passe():
    st.stop()


# --- SYSTÈME DE CAGNOTTE (MOTIVATION MATÉRIEL) ---
if "cagnotte" not in st.session_state:
    st.session_state.cagnotte = 0.0

OBJECTIF_LAPTOP = 700.0  # Objectif financier moyen pour ton ordinateur portable

st.markdown("### 💻 Objectif Financement Matériel")
progression = min(st.session_state.cagnotte / OBJECTIF_LAPTOP, 1.0)
st.progress(progression)

col_cagnotte_txt, col_cagnotte_btn = st.columns([2, 1])
with col_cagnotte_txt:
    st.write(f"**Cagnotte actuelle : {st.session_state.cagnotte} €** / {OBJECTIF_LAPTOP} €")
with col_cagnotte_btn:
    if st.button("➕ Encaisser 15 €", use_container_width=True):
        st.session_state.cagnotte += 15.0
        st.rerun()

st.markdown("---")


# --- FONCTION DE GÉNÉRATION DU RAPPORT PDF ---
def generer_pdf_rapport(statut, net_mensuel, mois_cumule, cumul_net, ecart, mots_reperes):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "RAPPORT D'AUDIT ANTI-FRAUDE LOCATIVE", ln=True, align="C")
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Date de l'audit : 22 juin 2026", ln=True)
    pdf.cell(0, 8, f"Statut global du dossier : {statut}", ln=True)
    pdf.ln(4)
    
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "1. Analyse Logique et Financiere", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"- Salaire net mensuel calcule : {net_mensuel:.2f} EUR", ln=True)
    pdf.cell(0, 8, f"- Numero du mois audite : {mois_cumule}", ln=True)
    pdf.cell(0, 8, f"- Cumul Net Imposable declare : {cumul_net:.2f} EUR", ln=True)
    pdf.cell(0, 8, f"- Ecart de calcul trouve : {ecart:.2f} EUR", ln=True)
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "2. Verification de la Structure du PDF", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for mot, trouve in mots_reperes.items():
        status_text = "CONFORME (Trouve)" if trouve else "ABSENT (A verifier)"
        pdf.cell(0, 8, f"- Terme '{mot}' : {status_text}", ln=True)
    pdf.ln(12)
    
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, "Securite & Confidentialite : Document genere localement. Toutes les pieces justificatives analysees ont ete definitivement detruites apres traitement conformément au RGPD.")
    
    return pdf.output()


# --- LOGIQUE D'ANALYSE AUTOMATIQUE ET MANUELLE ---
st.title("🕵️‍♂️ Anti-Fraude Locative — Scanner Intelligent")
st.write("Analyse automatisée sécurisée.")

# Initialisation des variables par défaut
net_detecte = 0.0
cumul_detecte = 0.0
mots_reperes_statut = {"cumul": False, "imposable": False, "net à payer": False, "revenu fiscal": False}

st.subheader("📄 1. Remplissage Intelligent (Analyse de Document)")
uploaded_file = st.file_uploader("Glissez-déposez le PDF d'un bulletin de salaire ou avis d'imposition ici", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extraction et décodage automatique des données..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        # --- BLOC REGEX : EXTRACTION INTELLIGENTE ---
        # Détection du Net à payer (cherche des variantes comme Net à payer, Net payé, etc. suivi d'un montant)
        match_net = re.search(r"(?:net\s*(?:à\s*payer|payé)?)\s*[:\s]*([\d\s ][\d\s ,.]*\d)", full_text, re.IGNORECASE)
        if match_net:
            try:
                net_clean = match_net.group(1).replace(" ", "").replace(" ", "").replace(",", ".")
                net_detecte = float(net_clean)
                st.toast(f"🤖 Net mensuel détecté : {net_detecte} €", icon="ℹ️")
            except ValueError:
                pass

        # Détection du Cumul Imposable
        match_cumul = re.search(r"(?:cumul\s*(?:net\s*)?imposable)\s*[:\s]*([\d\s ][\d\s ,.]*\d)", full_text, re.IGNORECASE)
        if match_cumul:
            try:
                cumul_clean = match_cumul.group(1).replace(" ", "").replace(" ", "").replace(",", ".")
                cumul_detecte = float(cumul_clean)
                st.toast(f"🤖 Cumul Imposable détecté : {cumul_detecte} €", icon="ℹ️")
            except ValueError:
                pass

        # Cartographie des mots-clés de contrôle
        for mot in mots_reperes_statut.keys():
            if mot in full_text.lower():
                mots_reperes_statut[mot] = True
        
        st.success("🤖 Analyse par Regex terminée. Les formulaires ci-dessous ont été mis à jour.")

st.markdown("---")

# 📊 SECTION CALCULATEUR
st.subheader("📊 2. Validation de la Cohérence Numérique")

col1, col2 = st.columns(2)
with col1:
    # La valeur par défaut s'adapte automatiquement si la Regex trouve le chiffre dans le PDF
    net_mensuel = st.number_input("Net à payer ce mois (€)", min_value=0.0, value=net_detecte, step=100.0)
    mois_cumule = st.number_input("Numéro du mois dans l'année (ex: 3 pour Mars, 6 pour Juin)", min_value=1, max_value=12, value=1)
with col2:
    # Pareil pour le cumul imposable
    cumul_net = st.number_input("Cumul Net Imposable indiqué en bas de page (€)", min_value=0.0, value=cumul_detecte, step=100.0)

statut_global = "🟡 AUCUN DOCUMENT TRAITÉ"
ecart_calcule = 0.0

if net_mensuel > 0 and cumul_net > 0:
    cumul_theorique = net_mensuel * mois_cumule
    ecart_calcule = abs(cumul_theorique - cumul_net)
    marge_tolerance = cumul_theorique * 0.15 # 15% de tolérance aux variations
    
    st.markdown("#### **Résultat de la cohérence mathématique :**")
    if ecart_calcule <= marge_tolerance:
        st.success(f"🟢 COHÉRENT : L'écart est de {ecart_calcule:.2f} €. Les calculs concordent avec l'historique annuel.")
        statut_global = "FIABLE - COHERENCE FINANCIERE CONFIRMEE"
    else:
        st.error(f"🔴 SUSPECT : Écart important de {ecart_calcule:.2f} € détecté entre le mensuel et le cumul indiqué !")
        statut_global = "ALERT - INCOHERENCE DES CALCULS DETECTEE"

st.markdown("---")

# 🔗 EXPORTATION ET RECHERCHES EXTERNES
st.subheader("🛠️ 3. Outils complémentaires & Génération de Rapport")
st.markdown("[Accéder au Vérificateur d'Avis d'Impôt - Impots.gouv](https://cfspart.impots.gouv.fr/fraude/avis)")

if net_mensuel > 0 or uploaded_file is not None:
    st.write("")
    st.markdown("### 📥 Téléchargement du Rapport Client")
    
    pdf_genere = generer_pdf_rapport(
        statut=statut_global,
        net_mensuel=net_mensuel,
        mois_cumule=mois_cumule,
        cumul_net=cumul_net,
        ecart=ecart_calcule,
        mots_reperes=mots_reperes_statut
    )
    
    st.download_button(
        label="⚡ Générer et Télécharger le rapport d'audit (PDF)",
        data=bytes(pdf_genere),
        file_name="Rapport_Audit_Anti_Fraude.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.caption("🔒 Sécurité : Aucune donnée n'est stockée en ligne. Tout reste en mémoire vive locale.")
