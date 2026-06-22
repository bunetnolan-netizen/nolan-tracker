import streamlit as st
import pdfplumber
import re
from fpdf import FPDF
import io

# 1. CONFIGURATION DE LA PAGE & SÉCURITÉ
st.set_page_config(page_title="Anti-Fraude Scanner Pro", page_icon="🕵️‍♂️", layout="wide")

# Initialisation du mot de passe et de la cagnotte dans la session Streamlit
if "authentifie" not in st.session_state:
    st.session_state["authentifie"] = False

if "cagnotte" not in st.session_state:
    st.session_state["cagnotte"] = 0.0

# ZONE À MODIFIER : Choisis ton mot de passe secret ici
MOT_DE_PASSE_ATTENDU = "Nolan18!!" 

# Écran de connexion si l'utilisateur n'est pas authentifié
if not st.session_state["authentifie"]:
    st.title("🔒 Accès Sécurisé - Anti-Fraude Scanner")
    mdp_saisi = st.text_input("Veuillez entrer le mot de passe expert :", type="password")
    if st.button("Se connecter"):
        if mdp_saisi == MOT_DE_PASSE_ATTENDU:  # <- Correction apportée ici !
            st.session_state["authentifie"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect. Accès refusé.")
    st.stop()

# 2. INTERFACE DE L'APPLICATION (MODE EXPERT ACTIVÉ)
st.title("🕵️‍♂️ Anti-Fraude Scanner — Espace Expert")
st.subheader("Analyse de cohérence logique & graphique en temps réel")

# --- SECTION GAGNE / OBJECTIFS (GAMIFICATION) ---
col_cagnotte, col_bouton = st.columns([2, 1])

with col_cagnotte:
    # Objectif financier pour l'ordinateur portable (Ex: 700€)
    objectif = 700.0
    progression = min(st.session_state["cagnotte"] / objectif, 1.0)
    st.progress(progression)
    st.write(f"**Cagnotte Actuelle :** {st.session_state['cagnotte']}€ / {objectif}€")

with col_bouton:
    if st.button("➕ Encaisser un audit (15 €)"):
        st.session_state["cagnotte"] += 15.0
        st.rerun()

# --- BANDEAU DE CONFORMITÉ RÉGLEMENTAIRE (RGPD & AI ACT 2026) ---
st.info("""
⚖️ **Conformité Réglementaire & Sécurité (RGPD & AI Act 2026)**
* **Zéro Stockage :** Les fichiers téléchargés sont traités exclusivement en mémoire vive (RAM) et sont définitivement détruits dès la fermeture de la session. Aucune base de données n'est conservée.
* **Responsabilité :** Cet outil fournit un rapport d'aide à la décision basé sur la cohérence logique et graphique. Il ne se substitue pas à la validation finale du propriétaire bailleur.
* **Obligation du Client :** En utilisant ce scanner, vous certifiez avoir obtenu l'accord préalable du candidat locataire pour la vérification technique de ses pièces justificatives.
""")

st.write("---")

# 3. FONCTIONS D'EXTRACTION ET DE LOGIQUE METIER
def extraire_texte_pdf(fichier_pdf):
    texte_complet = ""
    with pdfplumber.open(fichier_pdf) as pdf:
        for page in pdf.pages:
            texte_page = page.extract_text()
            if texte_page:
                texte_complet += texte_page + "\n"
    return texte_complet

def analyser_montants_regex(texte):
    """Recherche automatique des montants clés par expressions régulières"""
    net_payer = 0.0
    cumul_imposable = 0.0
    
    # Pattern Regex pour attraper les montants (ex: 2 500,00 ou 1850.50)
    pattern_montant = r"[\d\s]+[.,]\s*\d{2}"
    
    # Recherche du Net à payer
    match_net = re.search(r"(?:net\s+a\s+payer|net\s+paye|remuneration\s+nette)\s*[:\s]*(" + pattern_montant + ")", texte, re.IGNORECASE)
    if match_net:
        net_str = match_net.group(1).replace(" ", "").replace(",", ".")
        try: net_payer = float(net_str)
        except: pass
        
    # Recherche du Cumul Net Imposable
    match_cumul = re.search(r"(?:cumul\s+net\s+imposable|net\s+imposable\s+cumul|cumul\s+imposable)\s*[:\s]*(" + pattern_montant + ")", texte, re.IGNORECASE)
    if match_cumul:
        cumul_str = match_cumul.group(1).replace(" ", "").replace(",", ".")
        try: cumul_imposable = float(cumul_str)
        except: pass
        
    return net_payer, cumul_imposable

# 4. ZONE DE CHARGEMENT DU DOSSIER
st.header("📂 Étape 1 : Analyse du Bulletin de Salaire")
fichier_charge = st.file_uploader("Glissez-déposez le bulletin de salaire (PDF uniquement)", type=["pdf"])

# Initialisation des variables de calcul
net_saisi = 0.0
cumul_saisi = 0.0
nb_mois = 1
texte_extrait = ""

if fichier_charge is not None:
    # Traitement direct en mémoire vive (RAM) - Aucun stockage disque
    texte_extrait = extraire_texte_pdf(fichier_charge)
    
    # Remplissage intelligent automatique par Regex
    net_auto, cumul_auto = analyser_montants_regex(texte_extrait)
    
    st.success("✅ Analyse du document effectuée en mémoire RAM.")
    
    # Affichage du texte extrait pour double vérification visuelle (Optionnel)
    with st.expander("🔍 Voir le texte brut extrait du document (RAM)"):
        st.text(texte_extrait)
else:
    net_auto, cumul_auto = 0.0, 0.0

# Formulaire numérique (pré-rempli si la Regex a trouvé les montants)
col1, col2, col3 = st.columns(3)

with col1:
    net_saisi = st.number_input("Net à payer mensuel (€) :", value=net_auto, step=10.0)
with col2:
    cumul_saisi = st.number_input("Cumul Net Imposable (€) :", value=cumul_auto, step=50.0)
with col3:
    nb_mois = st.number_input("Mois du cumul (Ex: 3 pour Mars, 12 pour Décembre) :", min_value=1, max_value=12, value=1)

# 5. CALCULATEUR D'ÉCART ET LOGIQUE ANTI-FRAUDE
st.header("📊 Étape 2 : Diagnostic de Cohérence Financière")

# Logique mathématique de cohérence
attendu_cumul = net_saisi * nb_mois
ecart = abs(cumul_saisi - attendu_cumul)

if net_saisi > 0 and cumul_saisi > 0:
    st.write(f"**Cumul théorique attendu (Net mensuel x {nb_mois} mois) :** {attendu_cumul:.2f} €")
    st.write(f"**Cumul réel déclaré sur le document :** {cumul_saisi:.2f} €")
    
    # Seuil de tolérance de 50€ pour les variations de cotisations
    if ecart <= 50.0:
        statut_global = "🟢 FIABLE"
        st.success(f" {statut_global} — Parfaite cohérence mathématique (Écart dérisoire de {ecart:.2f} €).")
    else:
        statut_global = "🔴 SUSPECT"
        st.error(f"⚠️ {statut_global} — Incohérence majeure détectée ! L'écart est de {ecart:.2f} €.")
else:
    statut_global = "🟡 VIGILANCE"
    st.warning("Veuillez charger un document valide ou remplir les montants pour générer le diagnostic.")

# 6. GÉNÉRATION AUTOMATIQUE DU RAPPORT PDF CLIENT
st.header("📥 Étape 3 : Téléchargement du Rapport Client")

# Fonction interne pour structurer le livrable PDF officiel
def generer_pdf_rapport(statut, net, cumul, mois, ecart_val):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Pro
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RAPPORT D'AUDIT ANTI-FRAUDE IMMOBILIERE", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "Service d'analyse locale securisee pour propriettaires particuliers", ln=True, align="C")
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Métadonnées du rapport
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Statut Global du Dossier : {statut}", ln=True)
    pdf.ln(5)
    
    # Données chiffrées
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"- Montant net mensuel analyse : {net:.2f} EUR", ln=True)
    pdf.cell(0, 8, f"- Cumul net imposable declare : {cumul:.2f} EUR (sur {mois} mois)", ln=True)
    pdf.cell(0, 8, f"- Ecart de coherence detecte : {ecart_val:.2f} EUR", ln=True)
    pdf.ln(10)
    
    # Note de l'expert technique
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Note de l'expert technique :", ln=True)
    pdf.set_font("Arial", "", 11)
    if statut == "🟢 FIABLE":
        pdf.multi_cell(0, 8, "Les verifications mathematiques et logiques n'ont revele aucune anomalie. Les montants cumules correspondent aux declarations mensuelles transmises.")
    elif statut == "🔴 SUSPECT":
        pdf.multi_cell(0, 8, "ATTENTION : Une anomalie mathematique critique a ete identifiee entre le net mensuel et les cumuls fiscaux declares. Risque eleve de falsification numerique.")
    else:
        pdf.multi_cell(0, 8, "Dossier en attente de pieces complementaires ou de saisie de donnees.")
    
    pdf.ln(20)
    pdf.line(10, 120, 200, 120)
    pdf.ln(5)
    
    # CLAUSE DE CONFIDENTIALITÉ JURIDIQUE (RGPD & AI ACT)
    pdf.set_font("Arial", "I", 9)
    clause_rgpd = (
        "Securite & Confidentialite (Conformite RGPD & AI Act 2026) :\n"
        "Ce document a ete genere par un systeme d'analyse locale securisee. "
        "Conformement au Reglement General sur la Protection des Donnees (RGPD), le prestataire certifie "
        "qu'aucune donnee personnelle ou piece justificative analysee n'est conservee, stockee ou partagee. "
        "L'integralite des fichiers sources (bulletins de salaire, avis d'imposition) a ete definitivement "
        "detruite des la cloture de cet audit. Cet audit is un avis technique base sur la coherence "
        "logique du document et ne constitue pas une garantie d'impaye."
    )
    pdf.multi_cell(0, 5, clause_rgpd)
    
    return pdf.output(dest='S').encode('latin-1', errors='ignore')

# Bouton de téléchargement dynamique
if net_saisi > 0 and cumul_saisi > 0:
    donnees_pdf = generer_pdf_rapport(statut_global, net_saisi, cumul_saisi, nb_mois, ecart)
    
    st.download_button(
        label="📥 Télécharger le Rapport d'Audit (PDF)",
        data=donnees_pdf,
        file_name=f"Rapport_Audit_{statut_global.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
else:
    st.button("📥 Télécharger le Rapport d'Audit (PDF)", disabled=True, help="Veuillez remplir les données d'analyse pour activer le téléchargement.")
