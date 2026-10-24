# Multimodal Construction Intelligence Platform
**Skill Wallet Capstone Project 1** · Streamlit · Google Gemini

A database-free construction intelligence dashboard with four modules:
- **Site Safety & PPE Audit:** visual PPE checklist, hazard severity/remedies, downloadable JSON.
- **Crack Diagnostics:** preliminary defect triage, possible causes, urgency and next steps.
- **Planning & Valuation:** configurable area/rates, budget/capex, progress, approximate steel/cement quantities, and a conceptual rendering prompt.
- **Daily Site Assistant:** weather-condition advisories and multi-turn construction Q&A.

## Run locally

Python 3.10+ recommended.

```bash
git clone https://github.com/dakshs12/Multimodal-Construction-Intelligence-Platform.git
cd Multimodal-Construction-Intelligence-Platform
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.

The app runs without a key in **demonstration mode**. Sample results are labelled and are not analyses of uploaded images.

## Enable Gemini

Create a Gemini API key in Google AI Studio and paste it into the password-protected sidebar field. Alternatively, create `.streamlit/secrets.toml` locally (gitignored):

```toml
GOOGLE_API_KEY = "your-key-here"
```

For Streamlit Community Cloud, set `GOOGLE_API_KEY` under **App → Settings → Secrets**. Never commit API keys. The app tries `gemini-2.5-flash`, then `gemini-2.0-flash` if a request fails.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from this repository.
3. Select branch `main` and entry file `app.py`, then deploy.
4. Add `GOOGLE_API_KEY` in the app's Secrets settings to enable live Gemini features. Demo mode works without it.

## Architecture

- `app.py`: Streamlit UI, prompts, JSON parsing, planning calculations, chat session state.
- `requirements.txt`: minimal runtime dependencies.
- `.streamlit/config.toml`: theme.
- `.gitignore`: excludes local secrets and Python artifacts.

No database is required. Uploaded images and chat history live only in the current Streamlit session; this is not durable storage.

## Safety and engineering limitations

- This capstone is not a certified inspection, structural assessment, bill of quantities, quantity survey, or professional valuation.
- Vision models may miss hazards. A photo cannot reliably establish PPE certification, steel-toe protection, crack depth, or structural integrity. Lighting, occlusion and missing scale affect results.
- A model-generated safety score is not an OSHA compliance score. IS 456 concerns plain and reinforced concrete design; it is not a PPE standard. Verify applicable standards with qualified professionals.
- Crack widths are rough estimates without a calibrated scale. Epoxy injection or re-grouting must not be selected without an engineer confirming suitability.
- Material quantities are thumb-rule estimates only. Actual requirements depend on design, drawings, soil, specifications and local practice.
- Asset value is a simple area-rate scenario, not a formal valuation.
- Weather is manually selected; there is no live weather feed. Follow approved site plans, equipment limits and current local forecasts.
- Do not upload sensitive site imagery unless authorized. Review external AI provider terms and organizational privacy requirements.

## Reports

Each module provides downloadable JSON. Image reports include a `demo_mode` flag to distinguish sample content from live model output.

## License

Add a license file if you intend to distribute or reuse this project publicly.
