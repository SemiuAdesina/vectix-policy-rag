# Production Deployment

**Status:** Deployed on Render.

---

## Live app URL

| App        | URL |
|-----------|-----|
| Streamlit | https://vectix-policy-rag.onrender.com |
| API       | _Optional: Add FastAPI base URL if deployed separately_ |

---

## How to deploy

### Option 1: Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, and deploy.
3. Set **Secrets** in the Streamlit dashboard:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `CHROMA_PERSIST_DIR` = `chroma_data` (or leave default)
4. **Note:** Streamlit Cloud runs from a clean environment. You must either:
   - Build the Chroma store at startup (e.g. in `streamlit_app.py` run `build_store` if the directory is empty), or
   - Use a persistent volume / external store if your host supports it.

### Option 2: Render

1. Push to GitHub and connect the repo at [render.com](https://render.com).
2. Create a **Web Service**; use the repo’s Dockerfile or set build command to `pip install -r requirements.txt` and start command to `streamlit run streamlit_app.py --server.port=$PORT`.
3. In the service **Environment** tab, add:
   - `OPENAI_API_KEY`
   - `CHROMA_PERSIST_DIR` (optional)
4. Add the live URL to the table above.

### Option 3: Railway

1. Push to GitHub and connect at [railway.app](https://railway.app).
2. New project → Deploy from GitHub repo.
3. Add environment variables: `OPENAI_API_KEY`, `CHROMA_PERSIST_DIR` (optional).
4. Set start command for Streamlit or FastAPI (e.g. `uvicorn api.main:app --host 0.0.0.0 --port $PORT`).
5. Add the generated URL to the table above.

---

After deployment, replace the placeholder URLs in the **Live app URL** table with your real links.
