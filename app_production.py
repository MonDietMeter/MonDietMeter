# MonDietMeter – Analyse ciblée (Production)
import streamlit as st
import os
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="MonDietMeter – Analyse ciblée", page_icon="🍏", layout="centered")

# (Facultatif) masquer menu/footer Streamlit pour un rendu plus "produit"
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🎯 MonDietMeter — Analyse ciblée")
st.caption("Ces informations sont éducatives et ne remplacent pas un avis médical.")

with st.expander("ℹ️ Utilisation", expanded=False):
    st.markdown("""
    - Indiquez vos **diagnostics**, **symptômes**, **objectifs**, et précisez si vous suivez un **traitement** ou des **compléments**.
    - Chargez un **catalogue de produits** (`catalog.csv` ou Excel) contenant les colonnes : `name, nutrients, cautions, link`.
    - L’app estime les **nutriments prioritaires** et propose des **aliments clés** + des **produits** correspondants.
    """)

# === Entrées utilisateur ===
st.subheader("1) Vos informations")

col1, col2 = st.columns(2)

with col1:
    diagnostics = st.multiselect("Diagnostics connus", [
        "Diabète (type 2)", "Hypertension", "Anémie", "Hypothyroïdie",
        "Dyslipidémie (cholestérol)", "Ostéoporose", "Dépression / Anxiété",
        "SOPK", "Gastrite / Reflux", "Maladie rénale", "Grossesse / Allaitement"
    ])
    diag_autres = st.text_input("Autres diagnostics (séparés par des virgules)", placeholder="ex: colite, intolérance au gluten")

with col2:
    symptomes = st.multiselect("Symptômes ressentis", [
        "Fatigue", "Crampes musculaires", "Fourmillements / engourdissements",
        "Chute de cheveux", "Peau sèche", "Ongles cassants", "Céphalées fréquentes",
        "Troubles du sommeil", "Ballonnements", "Constipation", "Diarrhée",
        "Infections fréquentes", "Hématomes / saignements faciles",
        "Irritabilité / nervosité", "Brouillard mental / concentration difficile"
    ])
    sympt_autres = st.text_input("Autres symptômes (séparés par des virgules)", placeholder="ex: aphtes, fissures commissures lèvres")

objectifs = st.multiselect("Objectifs prioritaires", [
    "Perdre du poids","Énergie durable","Sommeil réparateur","Immunité renforcée",
    "Digestion / Transit","Glycémie stable","Pression artérielle","Gestion du stress",
    "Peau / Cheveux / Ongles","Mémoire / Concentration"
])

st.divider()

col3, col4 = st.columns(2)
with col3:
    sous_traitement = st.checkbox("Je suis **sous traitement médical**")
    details_traitement = st.text_area("Précisez (médicaments, doses)", disabled=not sous_traitement)

with col4:
    prend_complements = st.checkbox("Je **prends déjà des compléments**")
    details_complements = st.text_area("Précisez (références, doses)", disabled=not prend_complements)

# === Mappings nutriments ===
N_BY_DIAG = {
    "Diabète (type 2)": {"Magnésium": 3, "Chrome": 3, "Vitamine D": 2, "Oméga-3": 2, "Fibres": 3, "Zinc":1},
    "Hypertension": {"Potassium": 3, "Magnésium": 2, "Calcium": 2, "Oméga-3": 2, "Fibres": 2},
    "Anémie": {"Fer": 3, "Vitamine B12": 2, "Folate (B9)": 2, "Vitamine C": 2},
    "Hypothyroïdie": {"Iode": 3, "Sélénium": 3, "Zinc": 2, "Tyrosine (AA)": 2, "Fer":1},
    "Dyslipidémie (cholestérol)": {"Oméga-3": 3, "Fibres": 2, "Niacine (B3)":1, "Phytostérols":1},
    "Ostéoporose": {"Calcium": 3, "Vitamine D": 3, "Vitamine K2": 2, "Magnésium": 2},
    "Dépression / Anxiété": {"Oméga-3": 3, "Complexe B": 2, "Magnésium": 2, "Vitamine D": 2, "Zinc":1},
    "SOPK": {"Inositol": 3, "Vitamine D": 2, "Magnésium": 2, "Oméga-3": 2, "Chrome": 2},
    "Gastrite / Reflux": {"Zinc carnosine":2, "Betaïne HCl":1, "Oméga-3":1, "Probiotiques": 2, "Vitamine B12":1},
    "Maladie rénale": {"Vitamine D": 2, "Fer":1, "BCAA":1},
    "Grossesse / Allaitement": {"Fer": 2, "Folate (B9)": 3, "Iode": 2, "Choline":2, "DHA (Oméga-3)":2, "Calcium":2, "Vitamine D":2}
}
N_BY_SYMPT = {
    "Fatigue": {"Fer": 2, "Vitamine B12": 2, "Folate (B9)": 1, "Vitamine D": 2, "Magnésium": 1, "CoQ10":1},
    "Crampes musculaires": {"Magnésium": 3, "Potassium": 2, "Calcium": 1},
    "Fourmillements / engourdissements": {"Vitamine B12": 3, "B6":1},
    "Chute de cheveux": {"Fer": 2, "Zinc": 2, "Biotine (B7)": 2, "Vitamine D": 1},
    "Peau sèche": {"Vitamine A":1, "Oméga-3": 2, "Vitamine E":1, "Zinc":1},
    "Ongles cassants": {"Biotine (B7)": 2, "Zinc": 1, "Silice":1},
    "Céphalées fréquentes": {"Magnésium": 2, "Vitamine B2 (Riboflavine)":1, "CoQ10":1},
    "Troubles du sommeil": {"Magnésium": 2, "Glycine":1, "Mélatonine":1},
    "Ballonnements": {"Probiotiques": 2, "Enzymes digestives":1, "Fibres":1},
    "Constipation": {"Fibres": 3, "Magnésium": 1, "Hydratation":1, "Probiotiques":1},
    "Diarrhée": {"Probiotiques": 2, "Zinc":1},
    "Infections fréquentes": {"Vitamine C": 2, "Vitamine D": 2, "Zinc": 2},
    "Hématomes / saignements faciles": {"Vitamine C": 2, "Vitamine K":1},
    "Irritabilité / nervosité": {"Magnésium": 2, "Complexe B": 1, "Oméga-3":1},
    "Brouillard mental / concentration difficile": {"Oméga-3": 2, "Complexe B": 2, "Fer":1, "Iode":1}
}
N_BY_GOAL = {
    "Perdre du poids": {"Fibres": 3, "Protéines": 2, "Chrome": 1, "Oméga-3":1},
    "Énergie durable": {"Complexe B": 2, "Fer": 1, "Vitamine D": 1, "Magnésium": 1, "CoQ10":1, "Protéines":1},
    "Sommeil réparateur": {"Magnésium": 2, "Glycine":1, "Mélatonine":1},
    "Immunité renforcée": {"Vitamine C": 2, "Vitamine D": 2, "Zinc": 2, "Probiotiques":1},
    "Digestion / Transit": {"Probiotiques": 2, "Fibres": 2, "Enzymes digestives":1},
    "Glycémie stable": {"Chrome": 2, "Magnésium": 2, "Fibres": 2},
    "Pression artérielle": {"Potassium": 2, "Magnésium": 2, "Oméga-3": 1},
    "Gestion du stress": {"Magnésium": 2, "Complexe B": 2, "L-théanine":1},
    "Peau / Cheveux / Ongles": {"Biotine (B7)": 2, "Zinc": 2, "Vitamine C": 1, "Vitamine D":1, "Collagène":1},
    "Mémoire / Concentration": {"Oméga-3": 2, "Iode": 1, "Complexe B": 1}
}
FOODS_BY_NUTRI = {
    "Magnésium": "Amandes, cacao brut, graines de courge, haricots, épinards",
    "Chrome": "Levure de bière, brocoli, céréales complètes",
    "Vitamine D": "Poissons gras (sardine, maquereau), œufs; exposition modérée au soleil",
    "Oméga-3": "Sardine, maquereau, saumon, graines de lin/chia (ALA)",
    "Fibres": "Légumineuses, avoine, légumes verts, graines, fruits entiers",
    "Zinc": "Huîtres, viande, graines de courge, haricots",
    "Potassium": "Banane, haricots, patate douce, épinards",
    "Calcium": "Produits laitiers, sardines avec arêtes, légumes verts",
    "Fer": "Foie/viande rouge (fer héminique), légumineuses + Vit C",
    "Vitamine B12": "Produits animaux, œufs; si végétalien → supplémentation",
    "Folate (B9)": "Légumes verts, lentilles, pois chiches",
    "Iode": "Poissons, algues, sel iodé",
    "Sélénium": "Noix du Brésil, poisson, œufs",
    "Vitamine K2": "Fromages fermentés, natto",
    "Complexe B": "Protéines animales, légumineuses, céréales complètes",
    "Biotine (B7)": "Œufs, noix, graines",
    "Vitamine C": "Agrumes, goyave, poivron, baies",
    "Probiotiques": "Yaourt/kéfir, choucroute, kimchi",
    "Enzymes digestives": "Papaye (papaye), ananas (bromélaïne)",
    "Glycine": "Gélatine/collagène, bouillons",
    "Mélatonine": "Cerises acides, noix (faible), ou complémentation ciblée",
    "Niacine (B3)": "Volaille, thon, arachides",
    "Vitamine A": "Foie, patate douce, carotte",
    "Vitamine E": "Amandes, huiles végétales pressées à froid",
    "Vitamine K": "Légumes verts (vit K1); prudence anticoagulants",
    "CoQ10": "Viande, poissons gras (faible), supplémentation possible",
    "Phytostérols": "Graines/noix, huiles végétales",
    "Tyrosine (AA)": "Fromage, poulet, graines, arachides",
    "Choline": "Œufs, foie, soja",
    "Protéines": "Œufs, poisson, volaille, légumineuses, tofu",
    "DHA (Oméga-3)": "Poissons gras (DHA/EPA)"
}

def parse_list_field(raw):
    if not raw: return []
    return [x.strip() for x in raw.split(",") if x.strip()]

def score_from_mapping(selected, mapping):
    scores = defaultdict(int)
    for item in selected:
        if item in mapping:
            for nutri, w in mapping[item].items():
                scores[nutri] += int(w)
    return scores

# === Chargement du catalogue (CSV/Excel + detection auto) ===
def try_read_df(uploaded):
    if uploaded is None: return None
    try:
        if uploaded.name.lower().endswith((".xlsx",".xls")):
            return pd.read_excel(uploaded)
        return pd.read_csv(uploaded, sep=None, engine="python")
    except Exception:
        return None

def find_catalog_df(uploaded_file=None):
    df = try_read_df(uploaded_file)
    if df is not None and {"name","nutrients"}.issubset(df.columns):
        return df, f"(upload) {uploaded_file.name}"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for c in [os.path.join(script_dir, "catalog.csv"),
              os.path.join(script_dir, "data", "catalog.csv")]:
        if os.path.exists(c):
            try:
                tmp = pd.read_csv(c, sep=None, engine="python")
                if {"name","nutrients"}.issubset(tmp.columns):
                    return tmp, c
            except Exception:
                pass
    return None, None

st.subheader("Catalogue (produits)")
up = st.file_uploader("Téléverser un catalogue (CSV ou Excel)", type=["csv","xlsx","xls"])

cat_df, cat_src = find_catalog_df(uploaded_file=up)
if cat_df is None:
    st.warning("Aucun `catalog.csv` détecté. Téléversez un fichier ci-dessus ou placez `catalog.csv` à côté du script.")
else:
    st.success(f"Catalogue chargé depuis : `{cat_src}`")
    st.dataframe(cat_df.head(10), use_container_width=True)

# === Calcul & recommandations ===
if st.button("Calculer les priorités nutritionnelles"):
    diags = diagnostics + parse_list_field(diag_autres)
    sympts = symptomes + parse_list_field(sympt_autres)
    goals = objectifs

    total = defaultdict(int)
    for block in [score_from_mapping(diags, N_BY_DIAG), score_from_mapping(sympts, N_BY_SYMPT), score_from_mapping(goals, N_BY_GOAL)]:
        for k, v in block.items():
            total[k] += v

    if not total:
        st.warning("Veuillez sélectionner au moins un **diagnostic**, **symptôme** ou **objectif**.")
    else:
        ranked = sorted(total.items(), key=lambda x: x[1], reverse=True)
        top5 = ranked[:5]

        st.subheader("2) Nutriments prioritaires")
        for nutri, score in top5:
            tip = FOODS_BY_NUTRI.get(nutri, "—")
            st.markdown(f"- **{nutri}** (score {score}) — aliments clés : {tip}")

        st.divider()
        st.subheader("3) Recommandations du catalogue")
        if cat_df is None or cat_df.empty:
            st.info("Pas de catalogue chargé. Téléversez un fichier pour obtenir des produits correspondants.")
        else:
            wanted = [n for n, _ in top5]

            def normalize_token(t): return str(t).strip().lower()
            def product_score(nutrient_list, wanted_list):
                s = 0
                for i, w in enumerate(wanted_list):
                    if normalize_token(w) in [normalize_token(x) for x in nutrient_list]:
                        s += (len(wanted_list) - i)
                return s

            prod_rows = []
            for _, row in cat_df.iterrows():
                nutrients_str = str(row.get("nutrients", ""))
                nutrients_list = [x.strip() for x in nutrients_str.replace(",", ";").split(";") if x.strip()]
                s = product_score(nutrients_list, wanted)
                prod_rows.append((s, row))

            ranked_products = sorted(prod_rows, key=lambda x: x[0], reverse=True)
            top_products = [r for r in ranked_products if r[0] > 0][:5]

            if not top_products:
                st.info("Aucun produit ne correspond directement aux nutriments prioritaires. Vérifiez la colonne **nutrients** de votre catalogue.")
            else:
                for score, row in top_products:
                    name = row.get("name", "Produit")
                    link = row.get("link", "")
                    caut = row.get("cautions", "")
                    nuts = row.get("nutrients", "")
                    if link:
                        st.markdown(f"**[{name}]({link})** — nutriments: _{nuts}_  •  ⚠️ {caut}")
                    else:
                        st.markdown(f"**{name}** — nutriments: _{nuts}_  •  ⚠️ {caut}")

        st.divider()
        st.subheader("4) Export")
        exp_rows = [{"Nutriment prioritaire": n, "Score": s} for n, s in top5]
        exp_df = pd.DataFrame(exp_rows)
        st.dataframe(exp_df, use_container_width=True)
        csv = exp_df.to_csv(index=False).encode("utf-8")
        st.download_button("Télécharger (CSV)", csv, file_name="recommandations.csv", mime="text/csv")

st.markdown("---")
st.caption("MonDietMeter © — Informations éducatives, ne remplace pas un avis médical professionnel.")
