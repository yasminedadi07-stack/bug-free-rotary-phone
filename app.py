import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuration de la page (Forcer l'ouverture de la barre latérale sur mobile)
st.set_page_config(
    page_title="Pharmacie",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Masquage des éléments de l'interface Streamlit (Logo rouge, footer, menu)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
""", unsafe_allow_html=True)

FIREBASE_URL = "https://pharmacie-app-default-rtdb.firebaseio.com"

# Fonctions de gestion Firebase
def charger_meds_cloud():
    try:
        r = requests.get(f"{FIREBASE_URL}/medicaments.json")
        if r.status_code == 200 and r.json():
            data = r.json()
            liste = []
            for k, v in data.items():
                v['id_cloud'] = k
                liste.append(v)
            return liste
    except Exception:
        pass
    return []

def ajouter_med_cloud(med):
    try:
        requests.post(f"{FIREBASE_URL}/medicaments.json", json=med)
    except Exception:
        pass

def supprimer_med_cloud(id_cloud):
    try:
        requests.delete(f"{FIREBASE_URL}/medicaments/{id_cloud}.json")
    except Exception:
        pass

# Initialisation des données
meds_liste = charger_meds_cloud()

# Choix de la langue
langue = st.sidebar.selectbox("Globe / Langue", ["العربية", "Français"])

# Contenu selon la langue
if langue == "العربية":
    st.title("💊 صيدلية المنزل")
    st.sidebar.header("الفئات")
    categories = ["جميع الفئات", "أدوية يومية", "أدوية عند الحاجة", "المسكنات", "المضادات الحيوية", "أخرى"]
    cat_choisie = st.sidebar.radio("اختر الفئة:", categories)
    
    st.subheader("إضافة دواء جديد")
    with st.form("add_form", clear_on_submit=True):
        nom = st.text_input("اسم الدواء")
        cat = st.selectbox("الفئة", categories[1:])
        quantite = st.number_input("الكمية", min_value=1, value=1)
        peremption = st.date_input("تاريخ انتهاء الصلاحية")
        submit = st.form_submit_button("إضافة")
        
        if submit and nom:
            nouveau_med = {
                "nom": nom,
                "categorie": cat,
                "quantite": quantite,
                "peremption": str(peremption)
            }
            ajouter_med_cloud(nouveau_med)
            st.success("تمت إضافة الدواء بنجاح!")
            st.rerun()

    st.divider()
    st.subheader(f"قائمة الأدوية ({cat_choisie})")

else:
    st.title("💊 Pharmacie Maison")
    st.sidebar.header("Catégories")
    categories = ["Toutes les catégories", "Quotidien", "Au besoin", "Antidouleurs", "Antibiotiques", "Autres"]
    cat_choisie = st.sidebar.radio("Choisir une catégorie:", categories)
    
    st.subheader("Ajouter un médicament")
    with st.form("add_form", clear_on_submit=True):
        nom = st.text_input("Nom du médicament")
        cat = st.selectbox("Catégorie", categories[1:])
        quantite = st.number_input("Quantité", min_value=1, value=1)
        peremption = st.date_input("Date de péremption")
        submit = st.form_submit_button("Ajouter")
        
        if submit and nom:
            nouveau_med = {
                "nom": nom,
                "categorie": cat,
                "quantite": quantite,
                "peremption": str(peremption)
            }
            ajouter_med_cloud(nouveau_med)
            st.success("Médicament ajouté avec succès !")
            st.rerun()

    st.divider()
    st.subheader(f"Liste des médicaments ({cat_choisie})")

# Affichage des médicaments
if meds_liste:
    df = pd.DataFrame(meds_liste)
    
    # Filtrage par catégorie
    if cat_choisie not in ["جميع الفئات", "Toutes les catégories"]:
        df = df[df['categorie'] == cat_choisie]
    
    if not df.empty:
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{row['nom']}** ({row['categorie']})")
            with col2:
                st.write(f"Qté: {row['quantite']} | Exp: {row['peremption']}")
            with col3:
                if st.button("❌", key=row['id_cloud']):
                    supprimer_med_cloud(row['id_cloud'])
                    st.rerun()
    else:
        st.info("Aucun médicament dans cette catégorie." if langue == "Français" else "لا يوجد أي دواء في هذه الفئة.")
else:
    st.info("Aucun médicament enregistré." if langue == "Français" else "لا يوجد أي دواء مسجل.")
