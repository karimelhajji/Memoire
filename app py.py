import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="🤖 Green Finance Copilote AI", layout="wide")

st.title("🤖 Copilote IA pour arbitrage de financement vert")

st.markdown("""
Utilisez ce copilote pour **générer des recommandations budgétaires et fiscales** selon les besoins de financement vert (BFV), la dette publique et d'autres paramètres économiques.

🔐 Ce copilote utilise l'API [OpenRouter.ai](https://openrouter.ai) avec un modèle gratuit.  
⚠️ Vous devez entrer votre propre clé API OpenRouter pour l'utiliser.
""")

# === API Key Input ===
api_key = st.text_input("🔑 Clé API OpenRouter.ai", type="password")

# Modèle gratuit
model = "mistralai/mistral-7b-instruct:free"

st.divider()

# === Inputs ===
pays = st.selectbox("🌍 Pays analysé", ["France", "Allemagne", "Italie", "Espagne", "Belgique"])
bfv = st.number_input("💸 Besoin de Financement Vert (en Mds €)", min_value=0.0, value=45.0)
dette = st.number_input("📉 Dette publique (% du PIB)", min_value=0.0, value=110.0)
invest_prive = st.number_input("🏦 Financement privé estimé (Mds €)", min_value=0.0, value=20.0)
taux_ecb = st.slider("🏛️ Taux directeur de la BCE (%)", 0.0, 6.0, 3.75, step=0.25)
annee = st.selectbox("📅 Année de projection", list(range(2023, 2031)))

st.divider()

if st.button("🤖 Générer une stratégie avec IA"):
    if not api_key:
        st.warning("Merci d'ajouter votre clé API OpenRouter pour utiliser le copilote.")
    else:
        with st.spinner("L'IA réfléchit à une stratégie budgétaire durable..."):
            prompt = f"""
Tu es un économiste spécialisé en finance publique verte.

Pays : {pays}  
Année : {annee}  
BFV estimé : {bfv} milliards €  
Dette publique actuelle : {dette}% du PIB  
Financement privé attendu : {invest_prive} milliards €  
Taux ECB : {taux_ecb}%

Donne-moi une **proposition de stratégie budgétaire** en 5 points pour atteindre la neutralité carbone avec ces contraintes :
- Réduire la dette publique à terme
- Inciter au financement privé
- Utiliser des leviers réalistes : taxe Zucman, TVA verte, fiscalité carbone
- Proposer une trajectoire 2024-2030

Présente la réponse sous forme claire, pédagogique et hiérarchisée.
"""

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            url = "https://openrouter.ai/api/v1/chat/completions"
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "Tu es un expert en transition écologique et stratégie financière."},
                    {"role": "user", "content": prompt}
                ]
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                st.success("✅ Recommandation IA générée :")
                st.markdown(answer)
            else:
                st.error("Erreur de requête API :")
                st.json(response.json())

st.divider()

st.info("💡 Conseil : créez un compte gratuit sur https://openrouter.ai pour générer une clé API.")
