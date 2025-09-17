import streamlit as st, pandas as pd, os
from collections import defaultdict

st.set_page_config(page_title="MonDietMeter – Analyse ciblée", page_icon="assets/favicon.png", layout="wide")
st.markdown("<style>#MainMenu{visibility:hidden} footer{visibility:hidden}</style>", unsafe_allow_html=True)
if os.path.exists("assets/logo.png"): st.image("assets/logo.png", width=220)
st.title("🎯 MonDietMeter — Analyse ciblée")
st.caption("Outil éducatif — ne remplace pas un avis médical.")

@st.cache_data(show_spinner=False)
def read_catalog():
    for p in ["data/catalog.csv", "catalog.csv"]:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, sep=None, engine="python")
                if {"name","nutrients"}.issubset(df.columns): return df, p
            except Exception: pass
    return None, None

cat_df, cat_src = read_catalog()
if cat_df is None: st.error("Catalogue intégré introuvable (data/catalog.csv)."); st.stop()
st.success(f"Catalogue intégré chargé ({len(cat_df)} produits) — {cat_src}")
st.dataframe(cat_df.head(10), use_container_width=True)

N_BY_DIAG={"Diabète (type 2)":{"Magnésium":3,"Chrome":3,"Vitamine D":2,"Oméga-3":2,"Fibres":3,"Zinc":1},
"Hypertension":{"Potassium":3,"Magnésium":2,"Calcium":2,"Oméga-3":2,"Fibres":2},
"Anémie":{"Fer":3,"Vitamine B12":2,"Folate (B9)":2,"Vitamine C":2},
"Hypothyroïdie":{"Iode":3,"Sélénium":3,"Zinc":2,"Tyrosine (AA)":2,"Fer":1},
"Dyslipidémie (cholestérol)":{"Oméga-3":3,"Fibres":2,"Niacine (B3)":1,"Phytostérols":1},
"Ostéoporose":{"Calcium":3,"Vitamine D":3,"Vitamine K2":2,"Magnésium":2},
"Dépression / Anxiété":{"Oméga-3":3,"Complexe B":2,"Magnésium":2,"Vitamine D":2,"Zinc":1},
"SOPK":{"Inositol":3,"Vitamine D":2,"Magnésium":2,"Oméga-3":2,"Chrome":2},
"Gastrite / Reflux":{"Zinc carnosine":2,"Betaïne HCl":1,"Oméga-3":1,"Probiotiques":2,"Vitamine B12":1},
"Maladie rénale":{"Vitamine D":2,"Fer":1,"BCAA":1},
"Grossesse / Allaitement":{"Fer":2,"Folate (B9)":3,"Iode":2,"Choline":2,"DHA (Oméga-3)":2,"Calcium":2,"Vitamine D":2}}
N_BY_SYMPT={"Fatigue":{"Fer":2,"Vitamine B12":2,"Folate (B9)":1,"Vitamine D":2,"Magnésium":1,"CoQ10":1},
"Crampes musculaires":{"Magnésium":3,"Potassium":2,"Calcium":1},
"Fourmillements / engourdissements":{"Vitamine B12":3,"B6":1},
"Chute de cheveux":{"Fer":2,"Zinc":2,"Biotine (B7)":2,"Vitamine D":1},
"Peau sèche":{"Vitamine A":1,"Oméga-3":2,"Vitamine E":1,"Zinc":1},
"Ongles cassants":{"Biotine (B7)":2,"Zinc":1,"Silice":1},
"Céphalées fréquentes":{"Magnésium":2,"Vitamine B2 (Riboflavine)":1,"CoQ10":1},
"Troubles du sommeil":{"Magnésium":2,"Glycine":1,"Mélatonine":1},
"Ballonnements":{"Probiotiques":2,"Enzymes digestives":1,"Fibres":1},
"Constipation":{"Fibres":3,"Magnésium":1,"Hydratation":1,"Probiotiques":1},
"Diarrhée":{"Probiotiques":2,"Zinc":1},
"Infections fréquentes":{"Vitamine C":2,"Vitamine D":2,"Zinc":2},
"Hématomes / saignements faciles":{"Vitamine C":2,"Vitamine K":1},
"Irritabilité / nervosité":{"Magnésium":2,"Complexe B":1,"Oméga-3":1},
"Brouillard mental / concentration difficile":{"Oméga-3":2,"Complexe B":2,"Fer":1,"Iode":1}}
N_BY_GOAL={"Perdre du poids":{"Fibres":3,"Protéines":2,"Chrome":1,"Oméga-3":1},
"Énergie durable":{"Complexe B":2,"Fer":1,"Vitamine D":1,"Magnésium":1,"CoQ10":1,"Protéines":1},
"Sommeil réparateur":{"Magnésium":2,"Glycine":1,"Mélatonine":1},
"Immunité renforcée":{"Vitamine C":2,"Vitamine D":2,"Zinc":2,"Probiotiques":1},
"Digestion / Transit":{"Probiotiques":2,"Fibres":2,"Enzymes digestives":1},
"Glycémie stable":{"Chrome":2,"Magnésium":2,"Fibres":2},
"Pression artérielle":{"Potassium":2,"Magnésium":2,"Oméga-3":1},
"Gestion du stress":{"Magnésium":2,"Complexe B":2,"L-théanine":1},
"Peau / Cheveux / Ongles":{"Biotine (B7)":2,"Zinc":2,"Vitamine C":1,"Vitamine D":1,"Collagène":1},
"Mémoire / Concentration":{"Oméga-3":2,"Iode":1,"Complexe B":1}}
FOODS_BY_NUTRI={"Magnésium":"Amandes, cacao, graines de courge, haricots, épinards","Chrome":"Levure de bière, brocoli, céréales complètes",
"Vitamine D":"Poissons gras, œufs; soleil modéré","Oméga-3":"Sardine, maquereau, saumon, lin/chia","Fibres":"Légumineuses, avoine, légumes verts, fruits",
"Zinc":"Huîtres, viande, graines de courge","Potassium":"Banane, haricots, patate douce","Calcium":"Laitages, sardines, légumes verts",
"Fer":"Viande rouge/foie, légumineuses + Vit C","Vitamine B12":"Produits animaux; si végétalien → supplémentation","Folate (B9)":"Légumes verts, lentilles",
"Iode":"Poissons, algues, sel iodé","Sélénium":"Noix du Brésil, poisson, œufs","Vitamine K2":"Fromages fermentés, natto","Complexe B":"Protéines animales, légumineuses",
"Biotine (B7)":"Œufs, noix, graines","Vitamine C":"Agrumes, goyave, poivron","Probiotiques":"Yaourt/kéfir, choucroute","Enzymes digestives":"Papaye, ananas",
"Glycine":"Collagène/bouillons","Mélatonine":"Cerises acides, noix","Niacine (B3)":"Volaille, thon, arachides","Vitamine A":"Foie, patate douce, carotte",
"Vitamine E":"Amandes, huiles végétales","Vitamine K":"Légumes verts (prudence anticoagulants)","CoQ10":"Viande, poissons gras (faible)","Phytostérols":"Graines/noix",
"Tyrosine (AA)":"Fromage, poulet, graines","Choline":"Œufs, foie, soja","Protéines":"Œufs, poisson, volaille, légumineuses","DHA (Oméga-3)":"Poissons gras"}

st.subheader("1) Vos informations")
c1,c2=st.columns(2)
with c1:
    diagnostics=st.multiselect("Diagnostics connus", list(N_BY_DIAG.keys()))
    diag_autres=st.text_input("Autres diagnostics (séparés par des virgules)")
with c2:
    symptomes=st.multiselect("Symptômes ressentis", list(N_BY_SYMPT.keys()))
    sympt_autres=st.text_input("Autres symptômes (séparés par des virgules)")
objectifs=st.multiselect("Objectifs prioritaires", list(N_BY_GOAL.keys()))

st.divider()
c3,c4=st.columns(2)
with c3:
    t=st.checkbox("Je suis **sous traitement médical**"); st.text_area("Précisez (médicaments, doses)", disabled=not t)
with c4:
    c=st.checkbox("Je **prends déjà des compléments**"); st.text_area("Précisez (références, doses)", disabled=not c)

def parse_csv(s): return [x.strip() for x in s.split(",") if x.strip()] if s else []

def score(sel, mapping):
    out=defaultdict(int)
    for k in sel:
        if k in mapping:
            for n,w in mapping[k].items(): out[n]+=int(w)
    return out

if st.button("Calculer les priorités nutritionnelles"):
    total=defaultdict(int)
    for part in (score(diagnostics+parse_csv(diag_autres),N_BY_DIAG),
                 score(symptomes+parse_csv(sympt_autres),N_BY_SYMPT),
                 score(objectifs,N_BY_GOAL)):
        for k,v in part.items(): total[k]+=v
    if not total: st.warning("Sélectionnez au moins un élément."); st.stop()
    ranked=sorted(total.items(), key=lambda x:x[1], reverse=True)[:5]
    st.subheader("2) Nutriments prioritaires")
    for n,s in ranked: st.markdown(f"- **{n}** (score {s}) — {FOODS_BY_NUTRI.get(n,'—')}")
    st.divider(); st.subheader("3) Recommandations du catalogue (intégré)")
    wanted=[n for n,_ in ranked]
    def norm(t): return str(t).strip().lower()
    def pscore(lst, want):
        lst=[norm(x) for x in lst]
        sc=0
        for i,w in enumerate(want):
            if norm(w) in lst: sc+=(len(want)-i)
        return sc
    rows=[]
    for _,r in cat_df.iterrows():
        nuts=[x.strip() for x in str(r.get("nutrients","")).replace(",", ";").split(";") if x.strip()]
        rows.append((pscore(nuts,wanted), r))
    top=[r for r in sorted(rows, key=lambda x:x[0], reverse=True) if r[0]>0][:5]
    if not top: st.info("Aucun produit ne correspond directement aux nutriments prioritaires."); 
    else:
        for sc,r in top:
            name=r.get("name","Produit"); link=r.get("link",""); caut=r.get("cautions",""); nuts=r.get("nutrients","")
            st.markdown(f"**[{name}]({link})** — _{nuts}_  •  ⚠️ {caut}" if link else f"**{name}** — _{nuts}_  •  ⚠️ {caut}")
    st.divider(); st.subheader("4) Export")
    out=pd.DataFrame([{"Nutriment prioritaire":n,"Score":s} for n,s in ranked])
    st.dataframe(out, use_container_width=True)
    st.download_button("Télécharger (CSV)", out.to_csv(index=False).encode("utf-8"), "recommandations.csv","text/csv")
