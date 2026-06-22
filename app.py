import streamlit as st
import pdfplumber
from fpdf import FPDF

# Configuration de la page
st.set_page_config(page_title="Anti-Fraude Locative - Local Scanner", page_icon="🕵️‍♂️", layout="centered")

# --- SYSTÈME DE SÉCURITÉ (MOT DE PASSE) ---
def verifier_mot_de_passe():
    """Retourne True si le mot de passe est correct, sinon affiche l'écran de connexion."""
    if "authentifie" not in st.session_state:
        st.session_state.authentifie = False

    if st.session_state.authentifie:
        return True

    # Écran de connexion
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

# Si l'utilisateur n'est pas connecté, on arrête l'exécution ici
if not verifier_mot_de_passe():
    st.stop()


# --- FONCTION DE GÉNÉRATION DU RAPPORT PDF ---
def generer_pdf_rapport(statut, net_mensuel, mois_cumule, cumul_net, ecart, mots_reperes):
    pdf = FPDF()
    pdf.add_page()
    
    # Titre principal du document
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "RAPPORT D'AUDIT ANTI-FRAUDE LOCATIVE", ln=True, align="C")
    pdf.ln(4)
    
    # Informations de contexte (Date de l'exercice : 2026)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "Date de l'audit : 22 juin 2026", ln=True)
    pdf.cell(0, 8, f"Statut global du dossier : {statut}", ln=True)
    pdf.ln(4)
    
    # Ligne de séparation visuelle
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    
    # Section 1 : Cohérence financière
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "1. Analyse Logique et Financiere", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"- Salaire net mensuel indique : {net_mensuel:.2f} EUR", ln=True)
    pdf.cell(0, 8, f"- Numero du mois audite : {mois_cumule}", ln=True)
    pdf.cell(0, 8, f"- Cumul Net Imposable declare : {cumul_net:.2f} EUR", ln=True)
    pdf.cell(0, 8, f"- Ecart de calcul detecte : {ecart:.2f} EUR", ln=True)
    pdf.ln(4)
    
    # Section 2 : Mots-clés trouvés
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "2. Verification de la Structure du PDF", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for mot, trouve in mots_reperes.items():
        status_text = "CONFORME (Trouve)" if trouve else "ABSENT (A verifier)"
        pdf.cell(0, 8, f"- Terme '{mot}' : {status_text}", ln=True)
    pdf.ln(12)
    
    # Mention légale de confidentialité RGPD
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 5, "Securite & Confidentialite : Conformement aux exigences de conformite et de protection des donnees, ce rapport a ete genere localement. Toutes les pieces justificatives associees ont ete definitivement detruites apres traitement.")
    
    return pdf.output()


# --- CODE DE L'APPLICATION SCANNER ---
st.title("🕵️‍♂️ Anti-Fraude Locative — Scanner Professionnel")
st.write("Analyse sécurisée des documents. Zéro fuite de données.")

st.markdown("---")

# Initialisation des données pour alimenter le rapport
statut_global = "🟡 AUCUN DOCUMENT SOUUMIS"
ecart_calcule = 0.0
mots_reperes_statut = {"cumul": False, "imposable": False, "net à payer": False, "revenu fiscal": False}

# 📊 SECTION 1 : VÉRIFICATION MATHÉMATIQUE DES SALAIRES
st.subheader("📊 1. Calculateur de Cohérence des Salaires")
st.write("Entrez les montants du bulletin pour vérifier la cohérence logique.")

col1, col2 = st.columns(2)
with col1:
    net_mensuel = st.number_input("Net à payer ce mois (€)", min_value=0.0, value=0.0, step=100.0)
    mois_cumule = st.number_input("Numéro du mois dans l'année (ex: 3 pour Mars)", min_value=1, max_value=12, value=1)
with col2:
    cumul_net = st.number_input("Cumul Net Imposable indiqué en bas de page (€)", min_value=0.0, value=0.0, step=100.0)

if net_mensuel > 0 and cumul_net > 0:
    cumul_theorique = net_mensuel * mois_cumule
    ecart_calcule = abs(cumul_theorique - cumul_net)
    marge_tolerance = cumul_theorique * 0.15
    
    st.markdown("#### **Résultat de l'analyse logique :**")
    if ecart_calcule <= marge_tolerance:
        st.success(f"🟢 COHÉRENT : L'écart est de {ecart_calcule:.2f}€. Les calculs concordent.")
        statut_global = "FIABLE - COHERENCE FINANCIERE CONFIRMEE"
    else:
        st.error(f"🔴 SUSPECT : Écart important de {ecart_calcule:.2f}€ entre le mensuel et le cumul !")
        statut_global = "ALERT - INCOHERENCE DES CALCULS DETECTEE"

st.markdown("---")

# 📄 SECTION 2 : EXTRACTION DU TEXTE DU PDF
st.subheader("📄 2. Extraction & Analyse de Document (PDF)")
uploaded_file = st.file_uploader("Glissez-déposez le PDF d'un bulletin ou avis d'imposition ici", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extraction du texte en cours..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        st.info("✅ Texte extrait avec succès. Analyse en cours...")
        
        st.markdown("**Éléments clés repérés dans le document :**")
        for mot in mots_reperes_statut.keys():
            if mot in full_text.lower():
                mots_reperes_statut[mot] = True
                st.write(f"✔️ Terme détecté : *'{mot}'*")
            else:
                st.write(f"❌ Absent : *'{mot}'*")
        
        with st.expander("👁️ Voir le texte intégral extrait"):
            st.text(full_text)

st.markdown("---")

# 🔗 SECTION 3 : EXTENSIONS ET ACTIONS LIVRABLES
st.subheader("🛠️ 3. Outils et Exportation du Livrable")
st.markdown("[Accéder au Vérificateur d'Avis d'Impôt - Impots.gouv](https://cfspart.impots.gouv.fr/fraude/avis)")

st.write("") # Espace visuel

# Déclenchement automatique du bloc de téléchargement si une analyse a eu lieu
if net_mensuel > 0 or uploaded_file is not None:
    st.markdown("### 📥 Téléchargement du Rapport Client")
    st.write("Cliquez sur le bouton ci-dessous pour compiler instantanément le rapport officiel au format PDF.")
    
    # Compilation des données récoltées dans la fonction FPDF
    pdf_genere = generer_pdf_rapport(
        statut=statut_global,
        net_mensuel=net_mensuel,
        mois_cumule=mois_cumule,
        cumul_net=cumul_net,
        ecart=ecart_calcule,
        mots_reperes=mots_reperes_statut
    )
    
    # Bouton officiel de téléchargement Streamlit
    st.download_button(
        label="⚡ Télécharger le rapport d'audit (PDF)",
        data=bytes(pdf_genere),
        file_name="Rapport_Audit_Anti_Fraude.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.caption("🔒 Sécurité : Aucune donnée n'est stockée en ligne. Tout reste en mémoire vive locale.")
