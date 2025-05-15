import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import io

st.set_page_config(page_title="🟢 Green Finance Dashboard + IA Copilote", layout="wide")

st.title("🟢 Green Finance Dashboard & Copilote IA")

st.markdown("""
Ce dashboard vous permet de :
- Charger vos données de financement public et privé (CSV)
- Calculer automatiquement le Besoin de Financement Vert (BFV) et projeter la dette publique
- Visualiser les résultats sur graphiques interactifs
- Générer des recommandations IA personnalisées selon vos paramètres économiques
- Exporter les résultats au format Excel
""")

# --- Section Upload fichiers CSV ---
st.header("1. Import des données CSV")

uploaded_pub = st.file_uploader("Chargez le fichier de financement public (CSV)", type=["csv"])
uploaded_priv = st.file_uploader("Chargez le fichier de financement privé (CSV)", type=["csv"])

if uploaded_pub and uploaded_priv:
    df_pub = pd.read_csv(uploaded_pub)
    df_priv = pd.read_csv(uploaded_priv)

    st.success("✅ Fichiers chargés avec succès")

    st.subheader("Aperçu des données publiques")
    st.dataframe(df_pub.head())

    st.subheader("Aperçu des données privées")
    st.dataframe(df_priv.head())

    # --- Calcul BFV simple ---
    st.header("2. Calcul automatique & projection")

    # Exemple: BFV = Somme financement public + privé par année (à adapter)
    df_bfv_pub = df_pub.groupby("Année")["Montant (€)"].sum().reset_index(name="BFV_Public")
    df_bfv_priv = df_priv.groupby("Année")["Montant (€)"].sum().reset_index(name="BFV_Privé")

    df_bfv = pd.merge(df_bfv_pub, df_bfv_priv, on="Année", how="outer").fillna(0)
    df_bfv["BFV_Total"] = df_bfv["BFV_Public"] + df_bfv["BFV_Privé"]

    # Projection linéaire BFV (paramétrable)
    croissance_bfv = st.slider("Hypothèse croissance annuelle BFV (%)", 0.0, 10.0, 2.0, step=0.1)/100
    annee_debut = df_bfv["Année"].max()
    nb_annees_proj = st.slider("Nombre d'années de projection", 1, 10, 5)

    dernier_bfv = df_bfv.loc[df_bfv["Année"] == annee_debut, "BFV_Total"].values[0]

    projections = []
    for i in range(1, nb_annees_proj+1):
        annee = annee_debut + i
        bfv_proj = dernier_bfv * ((1 + croissance_bfv) ** i)
        projections.append({"Année": annee, "BFV_Projeté": bfv_proj})

    df_proj = pd.DataFrame(projections)

    st.subheader("Projections BFV")
    st.dataframe(df_proj)

    # --- Données dette publique ---
    st.header("3. Dette publique & paramètres économiques")

    dette_pib_init = st.number_input("Dette publique initiale (% PIB)", value=110.0, step=0.1)
    croissance_pib = st.slider("Croissance PIB annuelle (%)", 0.0, 5.0, 1.0, step=0.1)/100
    taux_inflation = st.slider("Inflation annuelle (%)", 0.0, 10.0, 2.0, step=0.1)/100
    subventions_init = st.number_input("Subventions publiques initiales (Mds €)", value=30.0, step=0.1)
    reduction_subv = st.slider("Réduction annuelle des subventions (%)", 0.0, 10.0, 1.0, step=0.1)/100
    annee_debut_dette = st.number_input("Année de départ dette", value=annee_debut)

    # Projection dette publique simple (croissance dette - subventions)
    dette_pib = [dette_pib_init]
    subventions = [subventions_init]
    annees = [annee_debut_dette]

    for i in range(1, nb_annees_proj+1):
        annee = annee_debut_dette + i
        annees.append(annee)

        subv = subventions[-1] * (1 - reduction_subv)
        subventions.append(subv)

        dette = dette_pib[-1] * (1 + croissance_pib + taux_inflation) - subv / 1000  # subventions impact dette
        dette_pib.append(dette)

    df_dette = pd.DataFrame({"Année": annees, "Dette_PIB (%)": dette_pib, "Subventions (Mds €)": subventions})

    st.subheader("Projection dette publique")
    st.dataframe(df_dette)

    # --- Visualisation graphique ---
    st.header("4. Visualisation interactive")

    fig, ax1 = plt.subplots(figsize=(10,5))
    sns.lineplot(x="Année", y="BFV_Total", data=df_bfv, label="BFV Total (€)", ax=ax1, color="green")
    sns.lineplot(x="Année", y="BFV_Public", data=df_bfv, label="BFV Public (€)", ax=ax1, linestyle="--", color="limegreen")
    sns.lineplot(x="Année", y="BFV_Privé", data=df_bfv, label="BFV Privé (€)", ax=ax1, linestyle=":", color="darkgreen")

    # Ajouter projections BFV
    sns.lineplot(x="Année", y="BFV_Projeté", data=df_proj, label="BFV Projeté (€)", ax=ax1, color="orange")

    ax1.set_ylabel("BFV (M€)")
    ax1.legend(loc="upper left")

    # Double axe dette
    ax2 = ax1.twinx()
    sns.lineplot(x="Année", y="Dette_PIB (%)", data=df_dette, label="Dette publique (% PIB)", ax=ax2, color="red")
    ax2.set_ylabel("Dette publique (% PIB)")
    ax2.legend(loc="upper right")

    st.pyplot(fig)

    # --- Section IA copilote ---
    st.header("5. Copilote IA - recommandations personnalisées")

    api_key = st.text_input("🔑 Entrez votre clé API OpenRouter", type="password")

    if st.button("Générer recommandations IA"):
        if not api_key:
            st.error("Vous devez entrer votre clé API OpenRouter pour utiliser le copilote.")
        else:
            prompt = f"""
            Tu es un expert en finance verte et économie publique.

            Voici les données projetées pour la France :

            BFV (Besoin Financement Vert) en Mds € : {df_proj.to_dict(orient='records')}
            Dette publique en % PIB : {df_dette.to_dict(orient='records')}

            Hypothèses : croissance PIB {croissance_pib*100:.2f}%, inflation {taux_inflation*100:.2f}%, réduction subventions {reduction_subv*100:.2f}% par an.

            Propose une stratégie budgétaire et fiscale en 5 points pour atteindre la neutralité carbone d'ici 2030, tout en maintenant la soutenabilité de la dette publique.
            """

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            url = "https://openrouter.ai/api/v1/chat/completions"
            data = {
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": "Tu es un expert en finance publique verte."},
                    {"role": "user", "content": prompt}
                ],
            }

            with st.spinner("L'IA génère une recommandation..."):
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    answer = response.json()["choices"][0]["message"]["content"]
                    st.success("✅ Recommandation IA générée :")
                    st.markdown(answer)
                else:
                    st.error(f"Erreur API: {response.status_code}")
                    st.json(response.json())

    # --- Export Excel ---
    st.header("6. Export des résultats")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_bfv.to_excel(writer, sheet_name="BFV_Historique", index=False)
        df_proj.to_excel(writer, sheet_name="BFV_Projection", index=False)
        df_dette.to_excel(writer, sheet_name="Dette_Projection", index=False)
    st.download_button(
        label="📥 Télécharger les données Excel",
        data=output.getvalue(),
        file_name="green_finance_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.warning("Veuillez charger les fichiers CSV publics et privés pour commencer.")
