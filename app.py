import streamlit as st
import pdfplumber
import re

# Configuration de la page
st.set_page_config(page_title="Anti-Fraude Locative - Local Scanner", page_icon="🕵️‍♂️", layout="centered")

st.title("🕵️‍♂️ Anti-Fraude Locative — Scanner Local")
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
    # Calcul théorique attendu
    cumul_theorique = net_mensuel * mois_cumule
    ecart = abs(cumul_theorique - cumul_net)
    marge_tolerance = cumul_theorique * 0.15 # Marge pour variations (primes, heures sup)
    
    st.markdown("#### **Résultat de l'analyse logique :**")
    if ecart <= marge_tolerance:
        st.success(f"🟢 COHÉRENT : L'écart est de {ecart:.2f}€. Les calculs concordent globalement avec le mois de l'année.")
    else:
        st.error(f"🔴 SUSPECT : Écart important de {ecart:.2f}€ entre le salaire mensuel et le cumul annuel indiqué !")

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
        
        st.info("✅ Texte extrait avec succès. Analyse des mots-clés de contrôle...")
        
        # Recherche de patterns ou d'mots-clés essentiels
        mots_cles = ["cumul", "imposable", "net à payer", "revenu fiscal"]
        st.markdown("**Éléments clés repérés dans le document :**")
        for mot in mots_cles:
            if mot in full_text.lower():
                st.write(f"✔️ Terme détecté : *'{mot}'*")
        
        # Affichage du texte brut pour vérification visuelle des lignes
        with st.expander("👁️ Voir le texte intégral extrait (Pour vérifier les décalages ou anomalies)"):
            st.text(full_text)

st.markdown("---")

# 🔗 SECTION 3 : RACCOURCIS OFFICIELS
st.subheader("🔗 3. Lien de Vérification Officiel")
st.write("Utilisez l'outil officiel de l'État pour vérifier l'authenticité de l'avis d'imposition avec les codes fournis par le candidat :")
st.markdown("[Accéder au Vérificateur d'Avis d'Impôt - Impots.gouv](https://cfspart.impots.gouv.fr/fraude/avis)", unsafe_view=True)

st.caption("🔒 Sécurité : Aucune donnée n'est stockée en ligne. Tout reste en mémoire vive locale.")
