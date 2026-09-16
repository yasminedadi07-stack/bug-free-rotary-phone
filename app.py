import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURATION FIREBASE CLOUD (BASE DE DONNÉES EN LIGNE)
# ---------------------------------------------------------
FIREBASE_URL = "https://pharmacie-app-default-rtdb.firebaseio.com"

def charger_meds_cloud():
    """Récupère les médicaments depuis le cloud Firebase sous forme de liste propre."""
    try:
        res = requests.get(f"{FIREBASE_URL}/medicaments.json")
        if res.status_code == 200 and res.json():
            data = res.json()
            liste_resultat = []
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, dict):
                        val['firebase_key'] = key  # Conserver la clé Firebase pour la suppression
                        liste_resultat.append(val)
                return liste_resultat
            elif isinstance(data, list):
                return [v for v in data if v is not None]
    except Exception:
        pass
    return []

def sauvegarder_med_cloud(nouveau_med):
    """Ajoute un nouveau médicament directement dans Firebase."""
    try:
        requests.post(f"{FIREBASE_URL}/medicaments.json", data=json.dumps(nouveau_med))
    except Exception as e:
        st.error(f"Erreur de connexion au serveur : {e}")

def supprimer_med_cloud(firebase_key):
    """Supprime un médicament via sa clé Firebase."""
    try:
        if firebase_key:
            requests.delete(f"{FIREBASE_URL}/medicaments/{firebase_key}.json")
    except Exception:
        pass

def charger_categories_cloud():
    """Récupère les catégories depuis Firebase."""
    cats_par_defaut = ["Toutes les catégories", "Douleur & Fièvre", "Yeux & Oreilles"]
    try:
        res = requests.get(f"{FIREBASE_URL}/categories.json")
        if res.status_code == 200 and res.json():
            data = res.json()
            if isinstance(data, dict):
                return list(data.values())
            elif isinstance(data, list):
                return [c for c in data if c is not None]
    except Exception:
        pass
    return cats_par_defaut

def sauvegarder_categories_cloud(categories):
    """Met à jour les catégories sur Firebase sous forme de dictionnaire propre."""
    try:
        cats_dict = {str(i): cat for i, cat in enumerate(categories)}
        requests.put(f"{FIREBASE_URL}/categories.json", data=json.dumps(cats_dict))
    except Exception as e:
        st.error(f"Erreur d'enregistrement : {e}")

# Configuration de la page (Forcer la barre latérale ouverte sur mobile)
st.set_page_config(
    page_title="Pharmacie", 
    page_icon="💊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CSS : MASQUAGE DES LOGOS ROUGES ET BRANDING STREAMLIT
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Masquer le menu hamburger à droite, le footer et le bouton Deploy */
    #MainMenu { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    .stAppDeployButton { display: none !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    button[title="View source"] { display: none !important; }
    .viewerBadge_container__1S-S7 { display: none !important; }
    a[href*="github.com"] { display: none !important; }
    
    /* Conserver l'en-tête transparent pour préserver le bouton de la flèche (Sidebar Toggle) */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99999 !important;
    }

    /* Style global sombre */
    .stApp { background-color: #121824 !important; color: #E2E8F0 !important; }
    
    .header-container {
        text-align: center;
        background-color: #0F172A;
        border: 1px solid #1E293B;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .header-title {
        color: #60A5FA !important;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }

    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }

    .med-card {
        background-color: #1E293B !important;
        border: 1px solid #334155;
        border-left: 5px solid #3B82F6 !important;
        padding: 18px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    
    .alert-card-expired {
        background-color: #2D1517 !important;
        border: 1px solid #7F1D1D;
        border-left: 5px solid #EF4444 !important;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .alert-card-low {
        background-color: #2D2215 !important;
        border: 1px solid #78350F;
        border-left: 5px solid #F59E0B !important;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #334155 !important;
        border-radius: 6px;
    }
    .stButton>button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover { background-color: #1D4ED8 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DONNÉES ET DICO DE TRADUCTION
# ---------------------------------------------------------
TRAD_CATS = {
    "Toutes les catégories": "جميع الفئات",
    "Douleur & Fièvre": "الألم والحمى",
    "Yeux & Oreilles": "العيون والأذن",
    "جميع الفئات": "Toutes les catégories",
    "الألم والحمى": "Douleur & Fièvre",
    "العيون والأذن": "Yeux & Oreilles"
}

TRAD_MOTS = {
    "حمى": "fievre", "الحمى": "fievre", "فليفر": "fievre",
    "ألم": "douleur", "الألم": "douleur", "وجع": "douleur",
    "صداع": "tete", "الصداع": "tete", "رأس": "tete",
    "سعال": "toux", "السعال": "toux",
    "عين": "yeux", "العيون": "yeux",
    "أذن": "oreille", "الأذن": "oreille",
    "دوليبران": "doliprane", "باراسيتامول": "paracetamol"
}

# ---------------------------------------------------------
# 1. BARRE EN HAUT (TITRE CENTRÉ + TRADUCTION)
# ---------------------------------------------------------
col_empty, col_title, col_lang = st.columns([1, 4, 1])

with col_lang:
    lang = st.selectbox("🌐 Langue / اللغة", ["العربية", "Français"], label_visibility="collapsed")

if lang == "العربية":
    titre_app = "💊 صيدلية"
    T = {
        "cat_title": "📌 الفئات",
        "all_cats": "جميع الفئات",
        "add_cat": "➕ إضافة فئة جديدة",
        "del_cat": "🗑️ حذف فئة",
        "add_cat_ph": "اسم الفئة...",
        "add_cat_btn": "تأكيد الإضافة",
        "del_cat_btn": "تأكيد الحذف",
        "search_ph": "🔍 بحث...", 
        "btn_add_med": "➕ إضافة دواء جديد",
        "form_title": "📝 نموذج إضافة دواء",
        "nom_med": "اسم الدواء (بالفرنسية دائماً)",
        "cat_label": "الفئة",
        "sympt_label": "الأعراض / دواعي الاستعمال",
        "sympt_ph": "مثال: Fièvre, Douleur أو الحمى، الصداع...",
        "qty_label": "الكمية",
        "peremp_label": "تاريخ انتهاء الصلاحية",
        "btn_save": "✅ حفظ",
        "btn_cancel": "❌ إلغاء",
        "stock_title": "📦 الفئة :",
        "no_med": "لا يوجد أي دواء.",
        "sympt_card": "الأعراض",
        "cat_card": "الفئة",
        "qty_card": "الكمية",
        "peremp_card": "تاريخ الصلاحية",
        "expired_title": "🚨 أدوية منتهية الصلاحية",
        "low_qty_title": "📉 أدوية على وشك النفاد",
        "no_expired": "✅ لا توجد أدوية منتهية الصلاحية.",
        "no_low": "✅ جميع الكميات متوفرة.",
        "del_med": "🗑️ حذف"
    }
else:
    titre_app = "💊 PHARMACIE"
    T = {
        "cat_title": "📌 Catégories",
        "all_cats": "Toutes les catégories",
        "add_cat": "➕ Ajouter une catégorie",
        "del_cat": "🗑️ Supprimer une catégorie",
        "add_cat_ph": "Nom de la catégorie...",
        "add_cat_btn": "Valider l'ajout",
        "del_cat_btn": "Confirmer la suppression",
        "search_ph": "🔍 Recherche...",
        "btn_add_med": "➕ Ajouter un nouveau médicament",
        "form_title": "📝 Formulaire d'ajout de médicament",
        "nom_med": "Nom du médicament (en Français)",
        "cat_label": "Catégorie",
        "sympt_label": "Symptômes / Indications",
        "sympt_ph": "Ex: Fièvre, Douleur...",
        "qty_label": "Quantité",
        "peremp_label": "Date de péremption",
        "btn_save": "✅ Enregistrer",
        "btn_cancel": "❌ Annuler",
        "stock_title": "📦 Catégorie :",
        "no_med": "Aucun médicament disponible.",
        "sympt_card": "Symptômes",
        "cat_card": "Catégorie",
        "qty_card": "Quantité",
        "peremp_card": "Péremption",
        "expired_title": "🚨 Médicaments Expirés",
        "low_qty_title": "📉 Stock Faible",
        "no_expired": "✅ Aucun médicament expiré.",
        "no_low": "✅ Tous les stocks sont suffisants.",
        "del_med": "🗑️ Supprimer"
    }

with col_title:
    st.markdown(f'<div class="header-container"><h1 class="header-title">{titre_app}</h1></div>', unsafe_allow_html=True)

# Synchronisation avec le Cloud
categories_base = charger_categories_cloud()
if "Toutes les catégories" not in categories_base:
    categories_base.insert(0, "Toutes les catégories")

meds_liste = charger_meds_cloud()

# Initialisation sûre du DataFrame
cols_attendues = ["ID", "Nom", "Categorie", "Symptomes", "Quantite", "Peremption", "firebase_key"]
if meds_liste:
    df_meds = pd.DataFrame(meds_liste)
    for col in cols_attendues:
        if col not in df_meds.columns:
            df_meds[col] = "" if col != "ID" and col != "Quantite" else 0
else:
    df_meds = pd.DataFrame(columns=cols_attendues)

# ---------------------------------------------------------
# 2. MENU À GAUCHE (SIDEBAR)
# ---------------------------------------------------------
st.sidebar.title(T["cat_title"])

if "cat_selectionnee" not in st.session_state:
    st.session_state.cat_selectionnee = "Toutes les catégories"

for c_fr in categories_base:
    c_display = TRAD_CATS.get(c_fr, c_fr) if lang == "العربية" else c_fr
    prefix = "🔹 " if st.session_state.cat_selectionnee == c_fr else ""
    if st.sidebar.button(f"{prefix}{c_display}", key=f"btn_cat_{c_fr}"):
        st.session_state.cat_selectionnee = c_fr
        st.rerun()

st.sidebar.markdown("---")

with st.sidebar.expander(T["add_cat"]):
    nouvelle_cat = st.text_input("Name", placeholder=T["add_cat_ph"], label_visibility="collapsed", key="input_new_cat")
    if st.button(T["add_cat_btn"], key="btn_add_cat"):
        if nouvelle_cat.strip() != "" and nouvelle_cat not in categories_base:
            categories_base.append(nouvelle_cat.strip())
            sauvegarder_categories_cloud(categories_base)
            st.rerun()

with st.sidebar.expander(T["del_cat"]):
    cats_supprimables = [c for c in categories_base if c != "Toutes les catégories"]
    
    if cats_supprimables:
        cat_map = {TRAD_CATS.get(c, c) if lang == "العربية" else c: c for c in cats_supprimables}
        cat_to_del_display = st.selectbox("Select", list(cat_map.keys()), label_visibility="collapsed", key="select_del_cat")
        
        if st.button(T["del_cat_btn"], key="btn_del_cat"):
            cat_to_del_real = cat_map[cat_to_del_display]
            if cat_to_del_real in categories_base:
                categories_base.remove(cat_to_del_real)
                sauvegarder_categories_cloud(categories_base)
                if st.session_state.cat_selectionnee == cat_to_del_real:
                    st.session_state.cat_selectionnee = "Toutes les catégories"
                st.rerun()

# ---------------------------------------------------------
# 3. ESPACE PRINCIPAL : RECHERCHE ET FORMULAIRE
# ---------------------------------------------------------
symptome_search = st.text_input("Search", placeholder=T["search_ph"], label_visibility="collapsed")

if "afficher_formulaire" not in st.session_state:
    st.session_state.afficher_formulaire = False

if st.button(T["btn_add_med"]):
    st.session_state.afficher_formulaire = not st.session_state.afficher_formulaire

if st.session_state.afficher_formulaire:
    with st.expander(T["form_title"], expanded=True):
        with st.form("form_ajout_med", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nom_med = st.text_input(T["nom_med"])
                cat_choices_fr = [c for c in categories_base if c != "Toutes les catégories"]
                cat_map_form = {TRAD_CATS.get(c, c) if lang == "العربية" else c: c for c in cat_choices_fr}
                
                cat_med_display = st.selectbox(T["cat_label"], list(cat_map_form.keys()) if cat_map_form else ["Autre"])
                symptomes_med = st.text_area(T["sympt_label"], placeholder=T["sympt_ph"])
            
            with col2:
                quantite_med = st.number_input(T["qty_label"], min_value=1, step=1, value=1)
                peremption_med = st.date_input(T["peremp_label"])
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                btn_enregistrer = st.form_submit_button(T["btn_save"])
            with col_cancel:
                btn_annuler = st.form_submit_button(T["btn_cancel"])
            
            if btn_enregistrer:
                if nom_med.strip() == "":
                    st.error("Nom obligatoire.")
                else:
                    cat_final_fr = cat_map_form.get(cat_med_display, cat_med_display)
                    nouveau_id = 1 if df_meds.empty or "ID" not in df_meds.columns else int(pd.to_numeric(df_meds["ID"], errors='coerce').fillna(0).max()) + 1
                    
                    nouveau_med_dict = {
                        "ID": nouveau_id,
                        "Nom": nom_med.strip(),
                        "Categorie": cat_final_fr,
                        "Symptomes": symptomes_med.strip(),
                        "Quantite": int(quantite_med),
                        "Peremption": str(peremption_med)
                    }
                    
                    sauvegarder_med_cloud(nouveau_med_dict)
                    st.session_state.afficher_formulaire = False
                    st.rerun()
            
            if btn_annuler:
                st.session_state.afficher_formulaire = False
                st.rerun()

st.markdown("---")

# ---------------------------------------------------------
# 4. STATISTIQUES CLIQUABLES
# ---------------------------------------------------------
today_str = datetime.today().strftime('%Y-%m-%d')

df_expired = df_meds[df_meds["Peremption"].astype(str) <= today_str] if not df_meds.empty else pd.DataFrame()
df_low = df_meds[pd.to_numeric(df_meds["Quantite"], errors='coerce').fillna(0) <= 2] if not df_meds.empty else pd.DataFrame()

col_stat1, col_stat2 = st.columns(2)

with col_stat1:
    with st.expander(f"🚨 {T['expired_title']} ({len(df_expired)})"):
        if df_expired.empty:
            st.success(T["no_expired"])
        else:
            for idx, row in df_expired.iterrows():
                st.markdown(f"""
                    <div class="alert-card-expired">
                        <b style="color:#FCA5A5;">💊 {row['Nom']}</b><br>
                        📅 <b>{T['peremp_card']}:</b> {row['Peremption']} | 📦 <b>{T['qty_card']}:</b> {row['Quantite']}
                    </div>
                """, unsafe_allow_html=True)

with col_stat2:
    with st.expander(f"📉 {T['low_qty_title']} ({len(df_low)})"):
        if df_low.empty:
            st.success(T["no_low"])
        else:
            for idx, row in df_low.iterrows():
                st.markdown(f"""
                    <div class="alert-card-low">
                        <b style="color:#FCD34D;">💊 {row['Nom']}</b><br>
                        📦 <b>{T['qty_card']}:</b> {row['Quantite']} | 📅 <b>{T['peremp_card']}:</b> {row['Peremption']}
                    </div>
                """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 5. LISTE PRINCIPALE DES MÉDICAMENTS
# ---------------------------------------------------------
cat_current_display = TRAD_CATS.get(st.session_state.cat_selectionnee, st.session_state.cat_selectionnee) if lang == "العربية" else st.session_state.cat_selectionnee
st.subheader(f"{T['stock_title']} {cat_current_display}")

df_affiche = df_meds.copy()

if st.session_state.cat_selectionnee != "Toutes les catégories" and not df_affiche.empty:
    df_affiche = df_affiche[df_affiche["Categorie"] == st.session_state.cat_selectionnee]

if symptome_search.strip() != "" and not df_affiche.empty:
    query = symptome_search.strip().lower()
    query_fr = TRAD_MOTS.get(query, query)
    
    df_affiche = df_affiche[
        df_affiche["Nom"].astype(str).str.lower().str.contains(query, na=False) |
        df_affiche["Nom"].astype(str).str.lower().str.contains(query_fr, na=False) |
        df_affiche["Symptomes"].astype(str).str.lower().str.contains(query, na=False) |
        df_affiche["Symptomes"].astype(str).str.lower().str.contains(query_fr, na=False)
    ]

if df_affiche.empty:
    st.info(T["no_med"])
else:
    for idx, row in df_affiche.iterrows():
        cat_card = TRAD_CATS.get(row['Categorie'], row['Categorie']) if lang == "العربية" else row['Categorie']
        
        # Affichage de la carte de médicament
        st.markdown(f"""
            <div class="med-card">
                <h3 style="margin:0; color:#60A5FA;">💊 {row['Nom']}</h3>
                <p style="margin:5px 0;">🎯 <b>{T['sympt_card']} :</b> {row['Symptomes']}</p>
                <p style="margin:5px 0;">🏷️ <b>{T['cat_card']} :</b> {cat_card}</p>
                <p style="margin:5px 0;">📦 <b>{T['qty_card']} :</b> {row['Quantite']} | 📅 <b>{T['peremp_card']} :</b> {row['Peremption']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Bouton de suppression individuelle propre sous la carte
        if st.button(f"{T['del_med']} {row['Nom']}", key=f"del_med_btn_{row.get('firebase_key', idx)}"):
            supprimer_med_cloud(row.get('firebase_key'))
            st.rerun()
