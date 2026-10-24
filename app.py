import json, os
from datetime import datetime, timezone
from typing import Any
import streamlit as st
from PIL import Image, UnidentifiedImageError

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

APP_NAME = "Multimodal Construction Intelligence Platform"
MODELS = ("gemini-2.5-flash", "gemini-2.0-flash")
st.set_page_config(page_title=APP_NAME, page_icon="🏗️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;letter-spacing:-.03em}
.stApp{background:linear-gradient(180deg,#f5f8fa,#fff 55%)}
.block-container{padding-top:1.7rem;max-width:1440px}
.hero{padding:1.6rem 1.8rem;border-radius:20px;color:white;background:linear-gradient(120deg,#17232d,#29404e 70%,#99672c);margin-bottom:1rem}
.hero p{color:#dce5eb}.eyebrow{text-transform:uppercase;letter-spacing:.15em;font-size:.72rem;font-weight:700;color:#f2bd69}
.panel{background:white;border:1px solid #e5eaf0;border-radius:15px;padding:1rem 1.2rem;margin:.5rem 0}
.note{color:#64748b;font-size:.86rem}
div[data-testid="stMetric"]{background:white;border:1px solid #e5eaf0;padding:1rem;border-radius:13px}
.stTabs [data-baseweb="tab"]{border-radius:9px 9px 0 0;padding:12px 16px}
[data-testid="stSidebar"]{background:#f1f5f8}
.stButton button,.stDownloadButton button{border-radius:10px;font-weight:600}
</style>""", unsafe_allow_html=True)

def api_key():
    entered = st.session_state.get("gemini_key_input", "").strip()
    if entered: return entered
    try:
        if st.secrets.get("GOOGLE_API_KEY"): return str(st.secrets["GOOGLE_API_KEY"]).strip()
    except Exception: pass
    return os.getenv("GOOGLE_API_KEY", "").strip()

def parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].removesuffix("```").removeprefix("json").strip()
    a,b = raw.find("{"),raw.rfind("}")
    if a < 0 or b < a: raise ValueError("Model did not return valid JSON.")
    value = json.loads(raw[a:b+1])
    if not isinstance(value,dict): raise ValueError("Expected a JSON object.")
    return value

def ask_gemini(prompt, image=None, history=None):
    key = api_key()
    if not key or genai is None: raise RuntimeError("Gemini is unavailable; add a key in the sidebar.")
    client = genai.Client(api_key=key)
    contents=[]
    for turn in history or []:
        contents.append(types.Content(role=turn["role"],parts=[types.Part.from_text(text=turn["text"])]))
    parts=[types.Part.from_text(text=prompt)]
    if image is not None: parts.append(image)
    contents.append(types.Content(role="user",parts=parts))
    last=None
    for model in MODELS:
        try:
            response=client.models.generate_content(model=model,contents=contents)
            if response.text: return response.text
            raise RuntimeError("Empty model response")
        except Exception as exc: last=exc
    raise RuntimeError(str(last))

def analyze(prompt,image,demo):
    if not api_key() or genai is None: return demo,True
    try: return parse_json(ask_gemini(prompt,image)),False
    except Exception as exc:
        st.warning(f"AI analysis failed ({exc}). Showing demonstration data instead.")
        return demo,True

def download(data,filename):
    st.download_button("Download JSON report",json.dumps(data,indent=2,ensure_ascii=False),filename,mime="application/json")

def demo_safety():
    return {"safety_score":78,"overall_status":"Needs attention","ppe_detection":[
      {"item":"Helmet","status":"Observed","notes":"Fit and certification cannot be verified from a photo."},
      {"item":"High-visibility vest","status":"Not clear","notes":"Verify each worker on site."},
      {"item":"Steel-toe boots","status":"Not verifiable","notes":"Toe protection cannot be confirmed visually."},
      {"item":"Harness and tie-off","status":"Context unclear","notes":"Verify when working at height."}],
      "hazards":[{"hazard":"Potential unprotected edge","severity":"High","remedy":"Barricade edges and install approved guardrails or fall-arrest controls."},
      {"hazard":"PPE compliance not confirmed","severity":"Medium","remedy":"Conduct a supervisor-led PPE inspection before work."}],
      "limitations":"Demonstration only; no image analysis performed."}

def demo_crack():
    return {"defect_type":"Hairline","estimated_crack_width_mm":0.3,"root_causes":["Possible shrinkage or thermal movement; illustrative only."],
      "recommended_repairs":["Map and monitor width over time.","Have a qualified structural engineer inspect before selecting a repair."],
      "urgency":"Routine inspection","confidence":"Low — demonstration only",
      "red_flags":["Rapid widening, displacement, water ingress or exposed reinforcement requires prompt professional review."],
      "limitations":"Demonstration only; image was not analyzed."}

with st.sidebar:
    st.markdown("## 🏗️ Site Intelligence")
    st.caption("Skill Wallet · Capstone Project 1")
    st.text_input("Google Gemini API key",type="password",key="gemini_key_input",placeholder="Optional API key")
    st.success("Gemini key detected") if api_key() and genai is not None else st.info("Demonstration mode · no key required")
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("**UI:** Streamlit  \n**Vision + chat:** Gemini  \n**Reports:** JSON download  \n**State:** session-only  \n**Deploy:** Community Cloud")
    st.markdown("---")
    st.markdown("### Modules")
    st.markdown("1. Site safety & PPE  \n2. Crack diagnostics  \n3. Planning & valuation  \n4. Weather-aware assistant")
    st.caption("Never commit API keys. AI output is advisory, not professional certification.")

st.markdown(f'<div class="hero"><div class="eyebrow">Construction intelligence · Capstone Project 1</div><h1 style="color:white;margin:.4rem 0">{APP_NAME}</h1><p>One workspace for site safety, concrete diagnostics, project planning and field guidance.</p></div>',unsafe_allow_html=True)
safety_tab,crack_tab,planning_tab,assistant_tab=st.tabs(["🦺 Site Safety & PPE","🧱 Crack Diagnostics","📐 Planning & Valuation","🌦️ Site Assistant"])

with safety_tab:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a JPG or PNG for a visual PPE checklist and hazard register.")
    file=st.file_uploader("Construction site photo",type=["jpg","jpeg","png"],key="safety_file")
    if file:
        try:
            img=Image.open(file).convert("RGB")
            left,right=st.columns(2)
            left.image(img,caption="Uploaded site photo",use_container_width=True)
            if st.button("Run PPE & hazard audit",type="primary"):
                prompt="""Return only JSON: safety_score integer 0-100; overall_status Compliant/Needs attention/Critical; ppe_detection array objects item/status/notes; hazards array objects hazard/severity Low/Medium/High/Critical/remedy; limitations string. Inspect visible helmets, high-visibility vests, protective footwear and harness/tie-off when relevant. Mark obscured items Not verifiable; do not infer steel-toe certification. Be cautious, do not invent hazards. Consider applicable OSHA guidance. IS 456 is a concrete design standard, not a PPE standard. This is screening, not formal compliance certification."""
                result,is_demo=analyze(prompt,img,demo_safety())
                st.session_state.safety_result=result;st.session_state.safety_demo=is_demo
            result=st.session_state.get("safety_result")
            if result:
                if st.session_state.get("safety_demo"): right.warning("Demo output — not derived from this image.")
                m1,m2=right.columns(2);m1.metric("Safety score",f"{max(0,min(100,int(result.get('safety_score',0))))}/100");m2.metric("Hazards",len(result.get("hazards",[])))
                right.markdown(f"**Overall status:** {result.get('overall_status','Needs attention')}")
                right.markdown("#### PPE checklist")
                for p in result.get("ppe_detection",[]): right.markdown(f"- **{p.get('item','PPE')}** — {p.get('status','Not verifiable')}: {p.get('notes','')}")
                st.markdown("#### Identified hazards")
                hazards=result.get("hazards",[])
                if not hazards: st.success("No hazards returned. This does not guarantee the site is safe.")
                for h in hazards:
                    severity=h.get("severity","Medium")
                    st.markdown(f'<div class="panel"><b>{h.get("hazard","Hazard")}</b> · <b>{severity}</b><br>{h.get("remedy","Review under the site safety plan.")}</div>',unsafe_allow_html=True)
                st.caption(result.get("limitations",""))
                download({"report_type":"site_safety_audit","created_at":datetime.now(timezone.utc).isoformat(),"demo_mode":st.session_state.get("safety_demo",False),"assessment":result},"site_safety_report.json")
        except (UnidentifiedImageError,OSError): st.error("Could not read image. Please upload a valid JPG or PNG.")
    else: st.info("Without an API key, sample output is clearly labelled as demonstration data.")

with crack_tab:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Preliminary visual triage for concrete and wall surfaces.")
    file=st.file_uploader("Concrete or wall surface photo",type=["jpg","jpeg","png"],key="crack_file")
    if file:
        try:
            img=Image.open(file).convert("RGB");left,right=st.columns(2);left.image(img,use_container_width=True)
            if st.button("Assess visible defect",type="primary"):
                prompt="""Return only JSON with defect_type (Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, Unclear), estimated_crack_width_mm number or null, root_causes array, recommended_repairs array, urgency (Routine inspection, Soon, Urgent professional assessment, Immediate area restriction), confidence string, red_flags array, limitations string. Width is only approximate without a scale; use null if not estimable. Never certify structural safety from an image. Epoxy injection and structural re-grouting are options only after an engineer confirms suitability. Escalate active, displaced, widening or load-bearing defects to a structural engineer."""
                result,is_demo=analyze(prompt,img,demo_crack());st.session_state.crack_result=result;st.session_state.crack_demo=is_demo
            result=st.session_state.get("crack_result")
            if result:
                if st.session_state.get("crack_demo"): right.warning("Demo output — not derived from this image.")
                right.metric("Preliminary defect",result.get("defect_type","Unclear"))
                width=result.get("estimated_crack_width_mm");right.metric("Estimated width",f"{width} mm" if width is not None else "Not estimable")
                right.markdown(f"**Urgency:** {result.get('urgency','Engineer review required')}")
                right.markdown(f"**Confidence:** {result.get('confidence','Not stated')}")
                st.markdown("#### Possible causes")
                for x in result.get("root_causes",[]): st.markdown(f"- {x}")
                st.markdown("#### Recommended next steps")
                for x in result.get("recommended_repairs",[]): st.markdown(f"- {x}")
                for x in result.get("red_flags",[]): st.warning(x)
                st.caption(result.get("limitations",""))
                download({"report_type":"crack_diagnostics","created_at":datetime.now(timezone.utc).isoformat(),"demo_mode":st.session_state.get("crack_demo",False),"assessment":result},"crack_diagnostics_report.json")
        except (UnidentifiedImageError,OSError): st.error("Could not read image. Please upload a valid JPG or PNG.")
    else: st.info("A well-lit close-up with a scale reference helps estimate crack width.")

with planning_tab:
    st.subheader("Planning & Real Estate Valuation")
    st.caption("Illustrative planning estimates only; use local BOQs, drawings and current supplier quotes.")
    a,b=st.columns(2)
    with a:
        structure=st.selectbox("Structure type",["Residential RCC","Commercial RCC","Industrial shed","Low-rise masonry"])
        area=st.number_input("Built-up area (sq ft)",min_value=100,max_value=2000000,value=1800,step=100)
        tier=st.selectbox("Location tier",["Tier 1","Tier 2","Tier 3"])
    with b:
        completion=st.slider("Completion percentage",0,100,35,5)
        rates={"Tier 1":2400,"Tier 2":2000,"Tier 3":1700}
        rate=st.number_input("Construction rate (₹ / sq ft)",500,20000,rates[tier],100)
        market_rates={"Tier 1":5000,"Tier 2":3500,"Tier 3":2500}
        market=st.number_input("Indicative market rate (₹ / sq ft)",500,50000,market_rates[tier],100)
    ratios={"Residential RCC":(3.8,.36),"Commercial RCC":(4.5,.42),"Industrial shed":(3.5,.10),"Low-rise masonry":(2.8,.30)}
    steel_ratio,cement_ratio=ratios[structure];budget=area*rate;incurred=budget*completion/100;asset=area*market*completion/100
    x,y,z=st.columns(3);x.metric("Project budget",f"₹{budget/100000:.2f} lakh");y.metric("Capex incurred",f"₹{incurred/100000:.2f} lakh");z.metric("Current asset scenario",f"₹{asset/100000:.2f} lakh" if asset<10000000 else f"₹{asset/10000000:.2f} crore")
    st.progress(completion/100,text=f"Milestone progress · {completion}%")
    x,y,z=st.columns(3);x.metric("Indicative steel",f"{area*steel_ratio/1000:.2f} tonnes");y.metric("Indicative cement",f"{area*cement_ratio:,.0f} bags");z.metric("Budget remaining",f"₹{(budget-incurred)/100000:.2f} lakh")
    st.caption("Material thumb rules are not a structural design or procurement schedule. Market value is not a formal valuation.")
    download({"report_type":"planning_estimate","created_at":datetime.now(timezone.utc).isoformat(),"currency":"INR","inputs":{"structure_type":structure,"built_up_sqft":area,"location_tier":tier,"completion_percent":completion,"construction_rate_inr_sqft":rate,"market_rate_inr_sqft":market},"estimates":{"total_budget_inr":round(budget,2),"capex_incurred_inr":round(incurred,2),"remaining_budget_inr":round(budget-incurred,2),"current_asset_value_inr":round(asset,2),"steel_tonnes_approx":round(area*steel_ratio/1000,2),"cement_bags_approx":round(area*cement_ratio)}},"planning_estimate.json")
    st.markdown("#### Conceptual 3D rendering prompt")
    prompt=f"Photorealistic conceptual architectural visualization of a {structure.lower()} in a {tier.lower()} Indian city, approximately {area} sq ft, construction progress {completion}%, climate-responsive contemporary design, realistic concrete and steel, professional three-quarter daylight view. Concept only, not a construction drawing."
    st.text_area("Prompt for Pollinations AI or another image generator",prompt,height=100)
    st.caption("This creates a prompt only; it does not generate or validate architectural drawings.")

with assistant_tab:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather=st.selectbox("Site condition",["Normal","High Wind","Heavy Rain","Extreme Heat"])
    advisories={
      "High Wind":("High wind protocol","Pause crane lifts when site or manufacturer wind limits are reached; secure loose materials and temporary works; inspect scaffolds and follow the approved lift plan."),
      "Heavy Rain":("Heavy rain protocol","Stop work in flooded or unstable excavations; isolate electrical equipment exposed to water; inspect drainage and slope stability; protect fresh concrete using the approved curing plan."),
      "Extreme Heat":("Heat stress protocol","Provide shade, drinking water, rest cycles and acclimatization; schedule strenuous work for cooler hours; monitor for heat illness and prevent rapid moisture loss from fresh concrete."),
      "Normal":("Routine site controls","Maintain housekeeping, PPE checks, equipment inspections, access control and toolbox talks. Monitor changing weather and permit conditions.")}
    title,advice=advisories[weather]
    st.markdown(f'<div class="panel"><h3>{title}</h3><p>{advice}</p></div>',unsafe_allow_html=True)
    st.caption("Manual condition selector, not a live weather feed. Follow approved site plans and equipment-specific limits.")
    st.markdown("#### Ask the construction assistant")
    if "chat_history" not in st.session_state: st.session_state.chat_history=[]
    for turn in st.session_state.chat_history:
        with st.chat_message(turn["role"]): st.markdown(turn["text"])
    question=st.chat_input("Ask about sequencing, materials, safety or construction concepts…")
    if question:
        st.session_state.chat_history.append({"role":"user","text":question})
        with st.chat_message("user"): st.markdown(question)
        system="You are a cautious construction engineering information assistant. Provide practical general guidance, ask clarifying questions, never certify structures or invent code clauses, and refer urgent hazards or site-specific engineering decisions to qualified professionals. Distinguish Indian standards from OSHA guidance."
        try:
            if api_key() and genai is not None:
                history=[{"role":"model" if t["role"]=="assistant" else "user","text":t["text"]} for t in st.session_state.chat_history[-9:-1]]
                answer=ask_gemini(f"{system}\nCurrent condition: {weather}. Advisory: {advice}\nQuestion: {question}",history=history)
            else: answer=f"**Demonstration mode:** add a Gemini API key for live responses. For {weather.lower()} conditions: {advice}\n\nConfirm drawings, specifications and site constraints with the responsible engineer before acting."
        except Exception as exc: answer=f"Assistant unavailable: {exc}\n\nFollow the approved site safety plan and consult the responsible engineer."
        st.session_state.chat_history.append({"role":"assistant","text":answer})
        with st.chat_message("assistant"): st.markdown(answer)
    if st.button("Clear conversation"):
        st.session_state.chat_history=[];st.rerun()

st.markdown("---")
st.markdown('<p class="note">Skill Wallet Capstone Project 1 · AI output is preliminary and must be verified by qualified professionals.</p>',unsafe_allow_html=True)
