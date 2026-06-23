import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pdfplumber
import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MOT_DE_PASSE_ATTENDU = ""
EMAIL_EXPEDITEUR = ""
MOT_DE_PASSE_EMAIL = ""


def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def get_report_filename(statut: str) -> str:
    safe_statut = re.sub(r'[^A-Za-z0-9]+', '-', statut).strip('-').lower() or "rapport"
    return f"rapport-bailsafe-{safe_statut}.pdf"


def build_analysis_summary(statut: str, ecart: float, fraude_meta: bool, est_scan: bool) -> str:
    severity = "Alerte critique" if statut.startswith("CRITIQUE") else "Alerte détectée" if "SUSPECT" in statut else "Aucune anomalie majeure"
    details = []
    if est_scan:
        details.append("Analyse limitée par absence de texte numérique dans le document.")
    else:
        details.append(f"Écart budgétaire calculé à {ecart:.2f} €.")
    if fraude_meta:
        details.append("Signatures d’édition graphique détectées.")
    else:
        details.append("Aucune signature d’outil d’édition suspecte observée.")
    return f"{severity} — {statut}. " + " ".join(details)


def build_ai_recommendations(statut: str, ecart: float, fraude_meta: bool, est_scan: bool) -> list[str]:
    if statut.startswith("CRITIQUE") or est_scan:
        return [
            "Bloquer la validation du dossier tant que l’original n’est pas vérifié.",
            "Demander une pièce justificative complémentaire au candidat.",
            "Préparer un message de relance clair et professionnel.",
        ]
    if "SUSPECT" in statut or fraude_meta or ecart > 150:
        return [
            "Mettre en garde le bailleur sur les incohérences détectées.",
            "Proposer une vérification humaine rapide avant signature.",
            "Valoriser l’offre d’audit premium pour sécuriser le dossier.",
        ]
    return [
        "Conserver le dossier avec un suivi simple.",
        "Présenter l’audit comme une preuve de rigueur et de fiabilité.",
        "Rassurer le bailleur sur la qualité du dossier.",
    ]


def build_ai_insight(intent: str, statut: str, ecart: float, fraude_meta: bool, est_scan: bool) -> str:
    recommendations = build_ai_recommendations(statut, ecart, fraude_meta, est_scan)
    first_action = recommendations[0]
    return (
        f"BailSafe détecte une situation {statut.lower()} pour votre objectif : {intent}. "
        f"Le prochain mouvement recommandé est : {first_action} "
        f"L’audit premium reste à 20 € par dossier pour aller plus vite et plus loin."
    )


def build_gain_simulation(dossiers_par_mois: int) -> tuple[int, int, int]:
    minutes_saved = dossiers_par_mois * 25
    risk_reduced = min(95, dossiers_par_mois * 12)
    estimated_value = dossiers_par_mois * 180
    return minutes_saved, risk_reduced, estimated_value


def build_ai_reply(user_message: str) -> str:
    lowered = user_message.lower()
    if "prix" in lowered or "combien" in lowered or "coû" in lowered:
        return "L’audit premium coûte 20 € par dossier, avec un rapport clair livré rapidement."
    if "rapide" in lowered or "vite" in lowered:
        return "Oui, le workflow est pensé pour être ultra rapide : analyse, verdict, rapport PDF."
    if "risque" in lowered or "sécur" in lowered:
        return "BailSafe aide à réduire les risques de dossiers douteux et à gagner en sérénité."
    return "Je peux vous aider à mieux comprendre la valeur de l’audit, son coût ou sa rapidité."


def build_value_pillars() -> list[str]:
    return [
        "Analyse rapide et lisible en moins de 24 heures.",
        "Rapport PDF prêt à partager avec vos partenaires.",
        "Protection contre les incohérences et les dossiers douteux.",
    ]


def build_conversion_pitch() -> str:
    return "Choisir BailSafe, c’est choisir un dossier plus sûr, sécuriser votre décision, gagner du temps et agir avec plus de sérénité sur chaque dossier."


def build_social_proof_items() -> list[dict]:
    return [
        {
            "quote": "« Avant de signer, je veux un dossier plus sûr. BailSafe me donne un argument clair et rapide. »",
            "author": "Bailleur privé, Paris",
        },
        {
            "quote": "« Le rapport est propre, simple à lire et utile pour expliquer une décision. »",
            "author": "Gestionnaire immobilier, Lyon",
        },
        {
            "quote": "« J’évite les mauvaises surprises grâce à une vérification plus sérieuse avant validation. »",
            "author": "Propriétaire, Bordeaux",
        },
    ]


def build_cta_banner() -> dict:
    return {
        "title": "Sécurisez vos dossiers en 24 heures",
        "body": "Pour seulement 20 € par dossier, obtenez un audit express, un rapport PDF clair et une décision plus solide.",
    }


def build_report_pdf(statut: str, ecart: float, fraude_meta: bool, est_scan: bool) -> bytes:
    statut_safe = re.sub(r'[^\x00-\x7F]+', '', statut)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Rapport d'Audit - BailSafe", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Diagnostic Global : {statut_safe}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if not est_scan:
        pdf.cell(0, 10, f"Ecart budgetaire calcule : {ecart:.2f} euros", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if fraude_meta:
        pdf.cell(0, 10, "Alerte : Fichier modifie via un editeur tiers.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(15)
    pdf.set_font("Helvetica", style="I", size=10)
    pdf.multi_cell(0, 10, "RGPD : Audit realise en memoire locale. Aucune donnee conservee.")

    return bytes(pdf.output(dest='S'))


def charger_secrets() -> None:
    global MOT_DE_PASSE_ATTENDU, EMAIL_EXPEDITEUR, MOT_DE_PASSE_EMAIL
    try:
        MOT_DE_PASSE_ATTENDU = st.secrets["MOT_DE_PASSE_ATTENDU"]
        EMAIL_EXPEDITEUR = st.secrets["EMAIL_EXPEDITEUR"]
        MOT_DE_PASSE_EMAIL = st.secrets["MOT_DE_PASSE_EMAIL"]
    except Exception:
        MOT_DE_PASSE_ATTENDU = "demo-password"
        EMAIL_EXPEDITEUR = "demo@example.com"
        MOT_DE_PASSE_EMAIL = "demo-password"
        st.warning("⚠️ Secrets non configurés : mode démo activé localement.")


def extract_pdf_content(uploaded_file) -> tuple[str, dict, str | None]:
    text = ""
    metadata = {}
    error = None

    try:
        with pdfplumber.open(uploaded_file) as pdf:
            metadata = pdf.metadata or {}
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text += page_text + "\n"
    except Exception as exc:
        error = str(exc)

    return text, metadata, error


def build_home_shortcuts() -> list[dict]:
    return [
        {"title": "Le risque", "slug": "risque", "icon": "🚨", "description": "Comprendre pourquoi les dossiers locatifs méritent une vérification."},
        {"title": "La solution", "slug": "solution", "icon": "💡", "description": "Découvrir l’analyse forensique et l’audit express."},
        {"title": "Exemple de rapport", "slug": "rapport", "icon": "📄", "description": "Voir ce que vous recevez à la fin de l’analyse."},
        {"title": "Sécurité", "slug": "securite", "icon": "🔒", "description": "Comprendre la protection, la confidentialité et la conformité."},
        {"title": "Mentions légales", "slug": "mentions", "icon": "⚖️", "description": "Consulter les informations juridiques et de responsabilité."},
    ]


def set_active_home_category(slug: str) -> None:
    st.session_state["active_home_category"] = slug


def get_home_section_info(slug: str) -> dict:
    sections = {
        "risque": {
            "title": "Pourquoi sécuriser vos dossiers locatifs ?",
            "content": "Un propriétaire particulier n'a généralement ni le temps ni les outils pour traquer les pixels modifiés ou les anomalies mathématiques d'un document.",
        },
        "solution": {
            "title": "Notre Expertise Technologique",
            "content": "Pour 20 € par dossier, bénéficiez d'un audit de conformité express sous 24h, avec un rapport clair et exploitable.",
        },
        "rapport": {
            "title": "À quoi ressemble notre audit ?",
            "content": "Voici un exemple des éléments livrés dans notre rapport confidentiel.",
        },
        "securite": {
            "title": "Garantie de conformité",
            "content": "Conformément au RGPD, BailSafe agit sans persistance et sans stockage durable.",
        },
        "mentions": {
            "title": "Mentions Légales & Clause de Non-Responsabilité",
            "content": "BailSafe propose une assistance technique algorithmique et forensique, sans garantie d'impayé.",
        },
    }
    return sections.get(slug, sections["risque"])


# ==========================================
# 🌍 PARTIE 1 : LA VITRINE PUBLIQUE
# ==========================================
def afficher_vitrine():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 34px; border-radius: 18px; text-align: center; margin-bottom: 25px; border: 2px solid #f59e0b; box-shadow: 0 12px 30px rgba(0,0,0,0.25);">
            <div style="font-size: 56px; margin-bottom: 10px;">🛡️</div>
            <h1 style="color: #ffffff; margin: 0; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: 1px;">BailSafe</h1>
            <p style="color: #cbd5e1; font-size: 17px; margin-top: 7px; margin-bottom: 0;">Filtre Anti-Fraude Documentaire & Analyse Heuristique par IA</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Louez votre bien immobilier en toute sérénité.</h3>", unsafe_allow_html=True)

    if "active_home_category" not in st.session_state:
        st.session_state["active_home_category"] = "risque"

    shortcuts = build_home_shortcuts()
    st.markdown("<h4 style='margin-bottom: 8px;'>🧭 Accès rapide</h4>", unsafe_allow_html=True)
    shortcut_cols = st.columns(len(shortcuts))
    for col, shortcut in zip(shortcut_cols, shortcuts):
        with col:
            if st.button(
                f"{shortcut['icon']} {shortcut['title']}",
                key=f"home_shortcut_{shortcut['slug']}",
                use_container_width=True,
            ):
                set_active_home_category(shortcut["slug"])

    active_shortcut = next((item for item in shortcuts if item["slug"] == st.session_state["active_home_category"]), shortcuts[0])
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 1px solid #93c5fd; border-radius: 14px; padding: 16px 18px; margin: 16px 0 10px 0;">
            <h4 style="margin-top: 0; color: #0f172a;">{active_shortcut['icon']} {active_shortcut['title']}</h4>
            <p style="margin: 0; color: #334155;">{active_shortcut['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    active_slug = st.session_state["active_home_category"]
    info = get_home_section_info(active_slug)

    if active_slug == "risque":
        st.markdown("### " + info["title"])
        colA, colB, colC = st.columns(3)
        colA.metric(label="Risque financier global", value="Élevé", delta="Impayés en forte hausse", delta_color="inverse")
        colB.metric(label="Contrôle visuel classique", value="Incertain", delta="Fraudes invisibles à l'œil", delta_color="inverse")
        colC.metric(label="Temps de détection", value="< 24h", delta="Analyse express", delta_color="normal")
        st.info(info["content"])

    elif active_slug == "solution":
        st.markdown("### " + info["title"])
        st.success("**Pour 20 € par dossier**, bénéficiez d'un audit de conformité express sous 24h, avec un rapport clair et exploitables en quelques minutes.")
        st.markdown("""
        - 🔎 **Analyse Forensique** : Traque des traces d'outils d'édition (Photoshop, Canva...).
        - 🧮 **Validation Algorithmique** : Recalcul automatique des cumuls fiscaux.
        - 📄 **Rapport de Fiabilité** : Livraison d'un bilan PDF clair.
        """)

    elif active_slug == "rapport":
        st.markdown("### " + info["title"])
        st.write(info["content"])
        st.markdown("""
        > **📋 RAPPORT D'AUDIT BAILSAFE**
        > - **Statut de l'analyse :** 🔴 SUSPECT (Anomalies majeures)
        > - **Vérification mathématique :** Écart de 1 240,00 € détecté entre le net à payer et le cumul imposable.
        > - **Empreinte numérique :** Utilisation d'un logiciel de retouche (*Adobe Photoshop 2023*) détectée dans le code source du fichier.
        """)

    elif active_slug == "securite":
        st.markdown("### " + info["title"])
        st.warning("🛡️ **Garantie de Conformité** : Conformément au RGPD, BailSafe agit sans persistance.")
        st.markdown("- **Zéro Base de Données** : Aucun stockage.\n- **Analyse Volatile** : Fichiers purgés après l'envoi du rapport.")

    elif active_slug == "mentions":
        st.markdown("### " + info["title"])
        st.markdown("""
        **Éditeur du service :** BailSafe – Service d'assistance technique à la gestion immobilière proposé par Nolan Bunet.
        Contact : bunetnolan@gmail.com
        
        **Hébergement :** Ce service est exécuté de manière sécurisée et éphémère via la plateforme **Streamlit Community Cloud**.
        
        **Exclusion Totale de Responsabilité (Protection Juridique) :** BailSafe fournit exclusivement une **assistance technique algorithmique et forensique** basée sur l'état informatique des documents numériques soumis. 
        - **Aucune Garantie d'Impayé :** Cet audit constitue un avis technique consultatif.
        - **Limites Techniques :** BailSafe ne saurait être tenu responsable en cas de falsification matérielle ou numérique d'un niveau de retouche indétectable par analyse heuristique.
        - **Souveraineté du Bailleur :** La décision finale d'acceptation, de validation ou de refus d'une candidature locative relève de la responsabilité unique, entière et souveraine du propriétaire bailleur.
        """)

    st.divider()
    st.markdown("<h3 style='text-align: center;'>⚡ Une offre claire, rapide et crédible</h3>", unsafe_allow_html=True)
    col_offer_1, col_offer_2, col_offer_3 = st.columns(3)
    col_offer_1.metric("Prix", "20 €", "par dossier")
    col_offer_2.metric("Délai", "< 24h", "analyse express")
    col_offer_3.metric("Livrable", "PDF", "rapport prêt à envoyer")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 1px solid #f59e0b; border-radius: 16px; padding: 20px; margin: 16px 0 22px 0; color: white;">
        <h4 style="margin-top: 0; color: white;">Pourquoi les propriétaires nous choisissent</h4>
        <ul style="margin: 0; padding-left: 20px; color: #e5e7eb;">
            <li>Analyse rapide, claire et actionnable.</li>
            <li>Rapport prêt à envoyer au client en quelques minutes.</li>
            <li>Protection contre les documents manipulés ou incohérents.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fff7ed 100%); border: 1px solid #f59e0b; border-radius: 14px; padding: 16px 18px; margin: 14px 0 18px 0;">
        <h4 style="margin-top: 0; color: #92400e;">💰 Le vrai coût d’une mauvaise décision</h4>
        <p style="margin: 0; color: #78350f;">Un dossier douteux peut coûter beaucoup plus cher qu’un audit préventif. BailSafe vous aide à éviter les erreurs avant qu’elles ne deviennent coûteuses.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Comment ça marche")
    step1, step2, step3 = st.columns(3)
    with step1:
        st.info("1. Le propriétaire dépose le dossier PDF")
    with step2:
        st.info("2. BailSafe analyse les anomalies et le scoring")
    with step3:
        st.info("3. Un rapport PDF clair est livré et partageable")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #ecfeff 0%, #f8fafc 100%); border: 1px solid #22d3ee; border-radius: 14px; padding: 16px 18px; margin: 16px 0 8px 0;">
        <h4 style="margin-top: 0; color: #0f172a;">🎯 Pourquoi cette démarche est intelligente</h4>
        <p style="margin: 0; color: #334155;">Vous ne réagissez pas après l’erreur : vous sécurisez la décision dès le départ, avec une preuve claire et un langage compréhensible.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%); border: 1px solid #93c5fd; border-radius: 14px; padding: 18px; margin: 20px 0;">
        <h4 style="margin-top: 0; color: #0f172a;">🎯 Ce que vous gagnez immédiatement</h4>
        <p style="margin: 0; color: #334155;">Vous réduisez les risques d’acceptation d’un dossier douteux, vous gagnez du temps et vous disposez d’un argument solide pour justifier votre décision.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 1px solid #93c5fd; border-radius: 14px; padding: 16px 18px; margin: 12px 0 20px 0; color: #0f172a;">
        <b>✅ Résultat attendu :</b> un dossier de location plus sûr, une décision plus rapide, et un argument clair pour justifier votre choix.
    </div>
    """, unsafe_allow_html=True)

    cta = build_cta_banner()
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #111827 100%); border: 1px solid #f59e0b; border-radius: 18px; padding: 24px; margin: 24px 0; color: white; text-align: center;">
            <h3 style="margin-top: 0; color: white;">{cta['title']}</h3>
            <p style="margin-bottom: 16px; color: #e5e7eb;">{cta['body']}</p>
            <div style="display: flex; justify-content: center; gap: 14px; flex-wrap: wrap;">
                <a href="https://leboncoin.fr/profil/3780fc14-e927-43d6-b826-40c02a3300c2" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #f56523; color: white; padding: 12px 24px; border-radius: 10px; font-weight: bold;">🛒 Contact LeBonCoin</div>
                </a>
                <a href="https://www.facebook.com/share/1KKBK1mfpV/?mibextid=wwXlfr" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #2563eb; color: white; padding: 12px 24px; border-radius: 10px; font-weight: bold;">📘 Contact Facebook</div>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 1px solid #93c5fd; border-radius: 14px; padding: 16px 18px; margin: 18px 0 14px 0;">
        <h4 style="margin-top: 0; color: #0f172a;">⭐ Témoignages de confiance</h4>
    </div>
    """, unsafe_allow_html=True)
    proof_items = build_social_proof_items()
    proof_cols = st.columns(len(proof_items))
    for col, item in zip(proof_cols, proof_items):
        with col:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #dbeafe; border-radius: 12px; padding: 14px; min-height: 120px;">
                    <p style="margin: 0 0 8px 0; color: #0f172a; font-style: italic;">“{item['quote']}”</p>
                    <p style="margin: 0; color: #475569; font-size: 0.92rem;">{item['author']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #cbd5e1; border-radius: 14px; padding: 18px; margin: 16px 0;">
        <h4 style="margin-top: 0; color: #0f172a;">🧠 Pourquoi c’est convaincant</h4>
        <p style="margin: 0 0 10px 0; color: #334155;">""" + build_conversion_pitch() + """</p>
        <ul style="margin: 0; padding-left: 18px; color: #475569;">
            <li>Transparence du diagnostic.</li>
            <li>Rapport clair en quelques minutes.</li>
            <li>Confiance au moment de la décision.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    value_columns = st.columns(3)
    for column, item in zip(value_columns, build_value_pillars()):
        with column:
            st.info(item)

    with st.expander("❓ FAQ rapide"):
        st.write("- Un audit est-il utile si le dossier semble correct ?")
        st.write("- Oui, car certains signes de fraude restent invisibles à l’œil nu.")
        st.write("- Combien de temps faut-il ?")
        st.write("- En général, l’analyse est livrée sous 24 heures.")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 1px solid #f59e0b; border-radius: 16px; padding: 20px; margin: 20px 0; color: white;">
        <h4 style="margin-top: 0; color: white;">💼 Offre premium</h4>
        <p style="margin: 0 0 10px 0; color: #e5e7eb;">Audit express à 20 € par dossier, livré sous 24h avec un rapport clair, exploitable et prêt à partager.</p>
        <ul style="margin: 0; padding-left: 18px; color: #f9fafb;">
            <li>Analyse forensique du document</li>
            <li>Validation des incohérences financières</li>
            <li>Rapport PDF prêt à transmettre</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%); border: 1px solid #93c5fd; border-radius: 16px; padding: 18px; margin: 18px 0;">
        <h4 style="margin-top: 0; color: #0f172a;">🤖 Assistant IA de conversion</h4>
        <p style="margin: 0 0 10px 0; color: #334155;">Choisissez votre objectif et l’outil vous propose un message de vente plus percutant en quelques secondes.</p>
        <ul style="margin: 0 0 10px 0; padding-left: 18px; color: #475569;">
            <li>Met en avant la valeur de l’audit en 3 phrases.</li>
            <li>Rassure le bailleur sur la sécurité du dossier.</li>
            <li>Donne un effet de sérieux, de contrôle et de protection.</li>
        </ul>
        <div style="background: #ffffff; border: 1px solid #dbeafe; border-radius: 10px; padding: 10px; color: #0f172a;">
            <b>Exemple prêt à utiliser :</b><br>
            “Avant de signer, faisons un contrôle sérieux du dossier. BailSafe permet de détecter les incohérences, d’éviter les mauvaises surprises et de sécuriser votre décision.”
        </div>
    </div>
    """, unsafe_allow_html=True)

    intent = st.selectbox("Objectif du message", ["Je veux rassurer un bailleur", "Je veux accélérer une décision", "Je veux faire peur aux dossiers douteux"])
    ai_preview = build_ai_insight(intent, "SUSPECT", 250.0, True, False)
    st.success(ai_preview)
    st.caption("Exemple généré par l’IA de démonstration pour renforcer la crédibilité du service.")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fff7ed 100%); border: 1px solid #f59e0b; border-radius: 14px; padding: 16px; margin: 16px 0;">
        <h4 style="margin-top: 0; color: #92400e;">📈 Simulateur de gain</h4>
        <p style="margin: 0; color: #78350f;">Visualisez l’impact concret d’un audit régulier sur votre temps et votre sécurité.</p>
    </div>
    """, unsafe_allow_html=True)
    dossiers_par_mois = st.slider("Nombre de dossiers par mois", 1, 20, 5)
    minutes_saved, risk_reduced, estimated_value = build_gain_simulation(dossiers_par_mois)
    c1, c2, c3 = st.columns(3)
    c1.metric("Temps gagné", f"{minutes_saved} min")
    c2.metric("Risque réduit", f"{risk_reduced}%")
    c3.metric("Valeur estimée", f"{estimated_value} €")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #cbd5e1; border-radius: 12px; padding: 14px; margin: 12px 0 0 0;">
        <b>💬 Mini-chat IA :</b> écrivez un message pour tester l’assistant.
    </div>
    """, unsafe_allow_html=True)
    user_message = st.text_input("Votre question", placeholder="Combien ça coûte ?")
    if user_message:
        st.info(build_ai_reply(user_message))
    
    st.divider()
    with st.expander("🔐 Accès Expert"):
        mdp_saisi = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if mdp_saisi == MOT_DE_PASSE_ATTENDU:
                st.session_state["authentifie"] = True
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")

# ==========================================
# 🕵️‍♂️ PARTIE 2 : L'INTERFACE EXPERT
# ==========================================
def afficher_interface_expert():
    st.markdown("""
    <div style="background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border: 1px solid #f59e0b; border-radius: 16px; padding: 20px; margin-bottom: 16px; color: white;">
        <h2 style="margin: 0 0 6px 0; color: white;">Cockpit d’Analyse Premium</h2>
        <p style="margin: 0; color: #d1d5db;">Détection rapide, scoring clair, rapport prêt à partager.</p>
    </div>
    """, unsafe_allow_html=True)

    colA, colB = st.columns([4, 1])
    with colA:
        st.title("Cockpit d'Analyse 🕵️‍♂️")
    with colB:
        if st.button("🔴 Déconnexion"):
            st.session_state["authentifie"] = False
            st.rerun()

    with st.expander("💸 Tunnel de paiement (Message client)"):
        st.write("Copie-colle ce message à ton client pour encaisser l'audit :")
        st.code("""Bonjour ! J'ai bien reçu le dossier de votre candidat.
Afin que je puisse lancer l'audit technique et forensique, je vous invite à régler les 20€ d'honoraires via ce lien sécurisé : [TON LIEN LYDIA / PAYPAL HERE]

Dès réception, le système scanne les pièces et je vous envoie le rapport PDF de fiabilité, avec un résumé clair de la conformité du dossier et les points d’attention prioritaires.
Cordialement, Nolan - BailSafe""", language="text")

    fichier_pdf = st.file_uploader("📂 Déposez le PDF à auditer", type="pdf")
    
    if fichier_pdf is not None:
        texte_brut, metadata_pdf, extraction_error = extract_pdf_content(fichier_pdf)
        if extraction_error:
            st.warning(f"⚠️ Lecture du PDF partielle : {extraction_error}")
        
        est_scan = len(texte_brut.strip()) < 20

        tab1, tab2, tab3 = st.tabs(["📊 Cohérence Numérique", "🔎 ADN du Fichier", "📤 Rapport & Envoi"])
        
        with tab1:
            if est_scan:
                st.warning("⚠️ ATTENTION : Ce PDF ne contient aucun texte informatique (Scan ou Photo). L'extraction mathématique automatique est impossible.")
                st.info("Passez à l'onglet 'ADN du fichier' pour vérifier l'origine de la photo, puis effectuez une vérification visuelle des chiffres.")
                fraude_math = False
                ecart = 0
            else:
                st.subheader("Extraction Automatique des Variables")
                net_a_payer_match = re.search(r'(?i)net\s*[àa]\s*payer\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
                cumul_imposable_match = re.search(r'(?i)cumul\s*imposable\s*.*?(\d[\d\s]*[.,]?\d*)', texte_brut)
                
                net_extrait = net_a_payer_match.group(1).replace(' ', '').replace(',', '.') if net_a_payer_match else "0"
                cumul_extrait = cumul_imposable_match.group(1).replace(' ', '').replace(',', '.') if cumul_imposable_match else "0"
                
                col1, col2, col3 = st.columns(3)
                net_saisi = col1.number_input("Net mensuel", value=float(net_extrait))
                nb_mois = col2.number_input("Mois cumulés", min_value=1, max_value=12, value=1)
                cumul_saisi = col3.number_input("Cumul imposable", value=float(cumul_extrait))
                
                calcul_theorique = net_saisi * nb_mois
                ecart = abs(cumul_saisi - calcul_theorique)
                
                m1, m2 = st.columns(2)
                m1.metric("Cumul Théorique calculé", f"{calcul_theorique:.2f} €")
                m2.metric("Écart constaté", f"{ecart:.2f} €", delta=f"{ecart:.2f} €" if ecart > 0 else "0.00 €")
                fraude_math = ecart > 150

        with tab2:
            st.subheader("Analyse Forensique des Métadonnées")
            createur = metadata_pdf.get('Creator', '')
            producteur = metadata_pdf.get('Producer', '')
            meta_string = str(createur) + " " + str(producteur)
            st.write(f"**Moteur de rendu :** {producteur if producteur else 'Inconnu (Signature absente)'}")
            
            logiciels_suspects = ["photoshop", "canva", "ilovepdf", "illustrator", "gimp"]
            fraude_meta = any(logiciel in meta_string.lower() for logiciel in logiciels_suspects)
            
            if fraude_meta:
                st.error("🚨 ALERTE : Signatures d'un logiciel d'édition graphique détectées !")
            else:
                st.success("✅ Aucune trace d'outil d'édition graphique suspect.")

        with tab3:
            st.subheader("Scoring & Expédition")
            if est_scan:
                statut = "VÉRIFICATION MANUELLE REQUISE"
            elif fraude_math and fraude_meta:
                statut = "CRITIQUE (Falsification détectée)"
            elif fraude_math or fraude_meta:
                statut = "SUSPECT (Anomalies majeures)"
            else:
                statut = "FIABLE (Aucune anomalie détectée)"
                
            st.info(f"Statut calculé : {statut}")
            st.markdown(f"<div style='background:#111827;padding:16px;border-radius:12px;color:#f9fafb;border:1px solid #374151;'> <b>Résumé expert :</b> {build_analysis_summary(statut, ecart, fraude_meta, est_scan)}</div>", unsafe_allow_html=True)
            recommendations = build_ai_recommendations(statut, ecart, fraude_meta, est_scan)
            st.markdown("### 🎯 Recommandations IA")
            for item in recommendations:
                st.write(f"- {item}")
            email_client = st.text_input("Adresse e-mail du client :", placeholder="client@gmail.com")
            
            score_risque = 0
            if est_scan:
                score_risque = 70
            elif fraude_math and fraude_meta:
                score_risque = 95
            elif fraude_math or fraude_meta:
                score_risque = 75
            else:
                score_risque = 20

            st.progress(score_risque / 100)
            st.caption(f"Niveau de risque estimé : {score_risque}/100")
            
            col_send, col_download = st.columns(2)
            with col_send:
                if st.button("🚀 Envoyer le Rapport PDF"):
                    if not is_valid_email(email_client):
                        st.error("Veuillez saisir une adresse e-mail client valide avant l'envoi.")
                    else:
                        pdf_bytes = build_report_pdf(statut, ecart, fraude_meta, est_scan)

                        try:
                            msg = MIMEMultipart()
                            msg['From'] = EMAIL_EXPEDITEUR
                            msg['To'] = email_client
                            msg['Subject'] = "[BailSafe] Votre Rapport d'Audit Locatif"
                            msg.attach(MIMEText("Bonjour,\n\nVeuillez trouver ci-joint le rapport d'audit anti-fraude express concernant le dossier de votre candidat.\n\nCordialement,\nNolan - BailSafe", 'plain'))

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
                            st.success("✅ Rapport envoyé avec succès !")
                        except Exception as e:
                            st.error(f"Erreur d'envoi : {e}")

            with col_download:
                pdf_bytes = build_report_pdf(statut, ecart, fraude_meta, est_scan)
                st.download_button(
                    label="⬇️ Télécharger le rapport",
                    data=pdf_bytes,
                    file_name=get_report_filename(statut),
                    mime="application/pdf",
                )

def main() -> None:
    st.set_page_config(page_title="BailSafe | Audit Locatif Expert", page_icon="🛡️", layout="centered")
    charger_secrets()

    if "authentifie" not in st.session_state:
        st.session_state["authentifie"] = False

    if not st.session_state["authentifie"]:
        afficher_vitrine()
    else:
        afficher_interface_expert()


if __name__ == "__main__":
    main()
