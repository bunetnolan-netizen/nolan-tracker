import streamlit as st
import pdfplumber

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


# --- CODE DE L'APPLICATION (ACCESSIBLE UNIQUEMENT SI CONNECTÉ) ---
st.title("🕵️‍♂️ Anti-Fraude Locative — Scanner Professionnel")
st.write("Analyse sécurisée des documents. Zéro fuite de données.")

st.markdown("---")

# 📊 SECTION 1 : VÉRIFICATION MATHÉMATIQUE DES SALAIRES
st.subheader("📊 1. Calculateur de Cohérence des Salaires")
st.write("Entrez les montants du bulletin pour vérifier la cohérence logique.")

col1, col2 = st.columns(2)
with col1:
    net_mensuel = st.number_input("Net à payer ce mois (€)", min_value=0.0, value=0.0, step=100.0)
    mois_cumule = st.number_input("Numéro du mois dans l'année (ex: 3 pour Mars, 6 pour Juin)", min_value=1, max_value=12, value=1)
with col2:
    cumul_net = st.number_input("Cumul Net Imposable indiqué en bas de page (€)", min_value=0.0, value=0.0, step=100.0)

if net_mensuel > 0 and cumul_net > 0:
    cumul_theorique = net_mensuel * mois_cumule
    ecart = abs(cumul_theorique - cumul_net)
    marge_tolerance = cumul_theorique * 0.15 # Marge pour variations (primes, heures sup)
    
    st.markdown("#### **Résultat de l'analyse logique :**")
    if ecart <= marge_tolerance:
        st.success(f"🟢 COHÉRENT : L'écart est de {ecart:.2f}€. Les calculs concordent globalement.")
    else:
        st.error(f"🔴 SUSPECT : Écart important de {ecart:.2f}€ entre le salaire mensuel et le cumul annuel indiqué !")

st.markdown("---")

# 📄 SECTION 2 : EXTRACTION DU TEXTE DU PDF
st.subheader("📄 2. Extraction & Analyse de Document (PDF)")
uploaded_file = st.file_uploader("Glissez-deposez le PDF d'un bulletin ou avis d'imposition ici", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extraction du texte en cours..."):
        with pdfplumber.open(uploaded_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        st.info("✅ Texte extrait avec succès. Analyse des mots-clés de contrôle...")
        
        mots_cles = ["cumul", "imposable", "net à payer", "revenu fiscal"]
        st.markdown("**Éléments clés repérés dans le document :**")
        for mot in mots_cles:
            if mot in full_text.lower():
                st.write(f"✔️ Terme détecté : *'{mot}'*")
        
        with st.expander("👁️ Voir le texte intégral extrait (Pour vérifier les décalages ou anomalies)"):
            st.text(full_text)

st.markdown("---")

# 🔗 SECTION 3 : RACCOURCIS OFFICIELS
st.subheader("🔗 3. Lien de Vérification Officiel")
st.write("Utilisez l'outil officiel de l'État pour vérifier l'authenticité de l'avis d'imposition :")
st.markdown("[Accéder au Vérificateur d'Avis d'Impôt - Impots.gouv](https://cfspart.impots.gouv.fr/fraude/avis)", unsafe_view=True)

st.caption("🔒 Sécurité : Aucune donnée n'est stockée en ligne. Tout reste en mémoire vive locale.")
