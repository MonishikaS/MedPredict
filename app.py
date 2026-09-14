import streamlit as st

# ============================================================
# STREAMLIT PAGE CONFIGURATION
# Must be the first Streamlit command in the application.
# ============================================================

st.set_page_config(
    page_title="HealthAI | EXHRA",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# IMPORTS
# ============================================================

import streamlit.components.v1 as components
from pathlib import Path
from textwrap import dedent

from utils import apply_custom_css
from login import login_page
from auth import verify_family_email_token
from database import initialize_database, process_family_email_action


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False


# ============================================================
# FAMILY EMAIL ACTIONS
# ============================================================

initialize_database()

_family_action = st.query_params.get("family_action")
_family_token = st.query_params.get("family_token")

if _family_action and _family_token:
    _verified = verify_family_email_token(_family_token)

    if _verified is None:
        st.error("This family email link is invalid or has expired.")
        st.stop()

    _connection_id, _recipient_user_id = _verified

    _ok, _msg, _requester_email = process_family_email_action(
        _connection_id,
        _recipient_user_id,
        _family_action,
    )

    if _ok:
        st.success("✓ " + _msg)
        st.info("You can now log in to HealthGuard AI and open Family Health.")
    else:
        st.warning(_msg)

    st.stop()


# ============================================================
# LOGIN CHECK
# ============================================================

if not st.session_state.get("is_logged_in", False):
    login_page()
    st.stop()


# ============================================================
# EXHRA / HEALTHAI HOME
# ============================================================

# Persistent theme.
# Every page imports the same utils.py and CSS.

if "healthai_theme" not in st.session_state:
    st.session_state.healthai_theme = "light"

apply_custom_css()


# A DOM marker allows style.css to theme the entire Streamlit
# document, including the sidebar.

theme_marker = (
    "healthai-theme-dark-marker"
    if st.session_state.healthai_theme == "dark"
    else "healthai-theme-light-marker"
)

st.markdown(
    f'<div class="{theme_marker}" aria-hidden="true"></div>',
    unsafe_allow_html=True,
)


# ============================================================
# TOP BAR — REAL STREAMLIT CONTROLS
# ============================================================

left, search_col, theme_col = st.columns(
    [4.6, 2.5, 0.65],
    vertical_alignment="center",
)

with left:
    st.markdown(
        """
        <div class="healthai-native-chips">
            <span class="healthai-chip active">
                ✦ <b>Research Prototype</b>
            </span>
            <span class="healthai-chip">
                • Explainable AI
            </span>
            <span class="healthai-chip">
                • Machine Learning
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


with search_col:
    with st.form("healthai_search_form", clear_on_submit=False):
        q_col, b_col = st.columns(
            [5, 1],
            vertical_alignment="center",
        )

        with q_col:
            search_query = st.text_input(
                "Disease search",
                placeholder="Search disease…",
                label_visibility="collapsed",
                key="healthai_search",
            )

        with b_col:
            submitted = st.form_submit_button(
                "⌕",
                use_container_width=True,
            )


if submitted and search_query.strip():
    q = search_query.strip().lower()

    if any(
        x in q
        for x in ["breast", "cancer", "tumor", "tumour"]
    ):
        st.switch_page("pages/breast_app.py")

    elif any(
        x in q
        for x in ["diabetes", "diabetic", "sugar"]
    ):
        st.switch_page("pages/diabetes_app.py")

    elif any(
        x in q
        for x in ["heart", "cardiac", "cardiovascular"]
    ):
        st.switch_page("pages/heart_app.py")

    else:
        st.warning(
            "I couldn't find that disease. "
            "Try Diabetes, Heart Disease, or Breast Cancer."
        )


with theme_col:
    theme_icon = (
        "☀"
        if st.session_state.healthai_theme == "dark"
        else "☾"
    )

    if st.button(
        theme_icon,
        key="healthai_theme_toggle",
        help="Switch light / dark theme",
        use_container_width=True,
    ):
        st.session_state.healthai_theme = (
            "light"
            if st.session_state.healthai_theme == "dark"
            else "dark"
        )

        st.rerun()


# ============================================================
# HERO + DASHBOARD VISUAL
# ============================================================

PAGE_CSS = (
    Path(__file__).parent / "style.css"
).read_text(encoding="utf-8")

dark = st.session_state.healthai_theme == "dark"
iframe_theme = "dark" if dark else "light"


# The hero is displayed inside an iframe so the HTML/CSS
# does not appear as visible source code in the Streamlit page.

hero_html = f"""
<!doctype html>
<html>
<head>
    <meta charset="utf-8">

    <style>
        {PAGE_CSS}

        :root {{
            color-scheme: {iframe_theme};
        }}

        html,
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
        }}
    </style>
</head>

<body class="hero-iframe-body {iframe_theme}">

    <div
        class="healthai-theme-dark-marker"
        aria-hidden="true"
        style="display:none"
    ></div>

    <section class="healthai-hero">

        <div class="healthai-hero-copy">

            <div class="healthai-eyebrow">
                <span>✦</span> EXPLAINABLE AI
            </div>

            <h1>
                Multi-Disease Health<br>
                <span>Risk Assessment</span>
            </h1>

            <p class="healthai-lead">
                A modern AI-powered research prototype that uses
                multiple machine-learning models to predict health
                risks and explain the reasons behind each prediction.
            </p>

            <div class="healthai-actions">
                <a
                    href="#assessment-section"
                    target="_top"
                    class="healthai-btn primary"
                >
                    Get Started&nbsp; →
                </a>

                <a
                    href="#models"
                    target="_top"
                    class="healthai-btn secondary"
                >
                    ▥&nbsp; Explore Models
                </a>
            </div>

            <div class="healthai-mini-note">
                <span>✓</span>
                Three health assessments&nbsp;&nbsp;•&nbsp;&nbsp;
                Five ML models&nbsp;&nbsp;•&nbsp;&nbsp;
                Explainable results
            </div>

        </div>


        <div class="healthai-hero-art">

            <div class="healthai-orbit orbit-one"></div>
            <div class="healthai-orbit orbit-two"></div>
            <div class="healthai-glow"></div>

            <div
                class="heart-stage anatomical-heart-stage"
                aria-label="Anatomical heart visual"
            >
                <img
                    class="anatomical-heart"
                    src="https://commons.wikimedia.org/wiki/Special:Redirect/file/Human_Heart_(NIH_BioArt_228_-_630872).png"
                    alt="Human anatomical heart"
                />

                <div class="heart-caption">
                    <b>Heart Health</b>
                    <small>
                        Explore our AI-powered risk assessments
                    </small>
                </div>
            </div>


            <div class="healthai-float-card diabetes">
                <span class="float-icon diabetes-icon">●</span>

                <div>
                    <strong>Diabetes</strong>
                    <small>Risk Assessment</small>
                </div>

                <b>→</b>
            </div>


            <div class="healthai-float-card breast">
                <span class="float-icon breast-icon">🎗</span>

                <div>
                    <strong>Breast Cancer</strong>
                    <small>Risk Assessment</small>
                </div>

                <b>→</b>
            </div>


            <div class="healthai-float-card heart">
                <span class="float-icon heart-icon">♥</span>

                <div>
                    <strong>Heart Disease</strong>
                    <small>Risk Assessment</small>
                </div>

                <b>→</b>
            </div>

        </div>

    </section>

</body>
</html>
"""


components.html(
    hero_html,
    height=585,
    scrolling=False,
)


# ============================================================
# HOMEPAGE DASHBOARD PANELS
# ============================================================

st.markdown(
    """
    <div class="healthai-stat-grid">

        <div class="healthai-stat-card">
            <div class="stat-symbol cyan">♧</div>
            <div>
                <strong>03</strong>
                <span>Health Assessments</span>
                <small>Breast • Diabetes • Heart</small>
            </div>
        </div>

        <div class="healthai-stat-card">
            <div class="stat-symbol blue">▱</div>
            <div>
                <strong>05</strong>
                <span>ML Models</span>
                <small>Ensemble Approach</small>
            </div>
        </div>

        <div class="healthai-stat-card">
            <div class="stat-symbol purple">◉</div>
            <div>
                <strong>XAI</strong>
                <span>Explainable AI</span>
                <small>SHAP &amp; Feature Importance</small>
            </div>
        </div>

        <div class="healthai-stat-card">
            <div class="stat-symbol teal">▥</div>
            <div>
                <strong>100%</strong>
                <span>Interactive</span>
                <small>Visual Explanations</small>
            </div>
        </div>

    </div>


    <div id="models" class="healthai-section-grid">

        <section class="healthai-panel models-panel">

            <div class="panel-heading">
                <span class="panel-icon">⚙</span>

                <div>
                    <h3>AI Models Used</h3>
                    <p>
                        Five trained models work together to estimate risk.
                    </p>
                </div>
            </div>

            <div class="model-list">

                <div class="model-item">
                    <span>⌁</span>
                    <b>Logistic<br>Regression</b>
                </div>

                <div class="model-item">
                    <span>╱</span>
                    <b>SVM</b>
                </div>

                <div class="model-item">
                    <span>♧</span>
                    <b>KNN</b>
                </div>

                <div class="model-item">
                    <span>✣</span>
                    <b>Random<br>Forest</b>
                </div>

                <div class="model-item">
                    <span>𝕏</span>
                    <b>XGBoost</b>
                </div>

            </div>

        </section>


        <section class="healthai-panel explain-panel">

            <div class="panel-heading">
                <span class="panel-icon purple-bg">◉</span>

                <div>
                    <h3>Why Explainability?</h3>
                    <p>
                        See which inputs influence a prediction.
                    </p>
                </div>
            </div>

            <div class="explain-content">

                <div class="explain-copy">
                    <b>Transparent predictions</b>

                    <span>
                        Feature importance and SHAP make model behaviour
                        easier to inspect and explain.
                    </span>
                </div>

                <div class="feature-bars">

                    <div>
                        <label>Age</label>
                        <i style="width:88%"></i>
                    </div>

                    <div>
                        <label>BMI</label>
                        <i style="width:70%"></i>
                    </div>

                    <div>
                        <label>Glucose</label>
                        <i style="width:55%"></i>
                    </div>

                    <div>
                        <label>Blood Pressure</label>
                        <i style="width:43%"></i>
                    </div>

                    <div>
                        <label>Cholesterol</label>
                        <i style="width:32%"></i>
                    </div>

                </div>

            </div>

        </section>


        <section class="healthai-panel prediction-panel">

            <div class="panel-heading">
                <span class="panel-icon teal-bg">◈</span>

                <div>
                    <h3>Sample Prediction</h3>
                    <p>Example risk result.</p>
                </div>
            </div>

            <div class="sample-risk">

                <div class="risk-ring">
                    <span>12%</span>
                    <small>risk</small>
                </div>

                <div>
                    <span class="low-pill">✓ Low Risk</span>
                    <strong>12%</strong>
                    <small>Risk Probability</small>

                    <div class="risk-line">
                        <i></i>
                    </div>
                </div>

            </div>

        </section>

    </div>


    <section class="healthai-workflow">

        <div class="workflow-title">
            <span>⚙</span>

            <div>
                <h2>How HealthAI Works</h2>
                <p>
                    From patient information to an interpretable AI result.
                </p>
            </div>
        </div>


        <div class="workflow-steps">

            <div class="workflow-step">
                <span>01</span>

                <div>
                    <b>Enter Information</b>
                    <p>
                        Provide health details through the assessment form.
                    </p>
                </div>
            </div>

            <em>→</em>

            <div class="workflow-step">
                <span>02</span>

                <div>
                    <b>AI Models Analyze</b>
                    <p>
                        Multiple trained models calculate risk probability.
                    </p>
                </div>
            </div>

            <em>→</em>

            <div class="workflow-step">
                <span>03</span>

                <div>
                    <b>Compare Results</b>
                    <p>
                        Review model predictions and the ensemble result.
                    </p>
                </div>
            </div>

            <em>→</em>

            <div class="workflow-step">
                <span>04</span>

                <div>
                    <b>Understand with XAI</b>
                    <p>
                        Inspect feature importance and SHAP explanations.
                    </p>
                </div>
            </div>

        </div>

    </section>


    <div class="healthai-footer-note">
        <span>♥</span>
        HealthAI &nbsp;•&nbsp;
        Research / Academic Prototype &nbsp;•&nbsp;
        AI Health Risk Assessment
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ASSESSMENT SECTION
# ============================================================

st.markdown(
    '<div id="assessment" class="healthai-parent-anchor"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    dedent(
        """
        <div id="assessment-section" class="section-heading">

            <span class="section-number">01</span>

            <div>
                <h2>Choose your assessment</h2>
                <p>
                    Select a health condition to begin the AI-based
                    risk assessment.
                </p>
            </div>

        </div>

        <p class="assessment-intro">
            Choose one of the available assessments to continue.
        </p>
        """
    ),
    unsafe_allow_html=True,
)


card1, card2, card3 = st.columns(3)


# ============================================================
# DIABETES CARD
# ============================================================

with card1:
    st.markdown(
        """
        <div class="disease-card">

            <div class="disease-icon">🩸</div>

            <div class="disease-card-title">
                Diabetes
            </div>

            <div class="disease-card-text">
                Assess diabetes-related risk using patient symptoms
                and health information.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Assess Diabetes →",
        key="open_diabetes",
        use_container_width=True,
    ):
        st.switch_page("pages/diabetes_app.py")


# ============================================================
# HEART DISEASE CARD
# ============================================================

with card2:
    st.markdown(
        """
        <div class="disease-card">

            <div class="disease-icon">❤️</div>

            <div class="disease-card-title">
                Heart Disease
            </div>

            <div class="disease-card-text">
                Assess cardiovascular risk from clinical measurements
                and symptoms.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Assess Heart Disease →",
        key="open_heart",
        use_container_width=True,
    ):
        st.switch_page("pages/heart_app.py")


# ============================================================
# BREAST CANCER CARD
# ============================================================

with card3:
    st.markdown(
        """
        <div class="disease-card">

            <div class="disease-icon">🎗️</div>

            <div class="disease-card-title">
                Breast Cancer
            </div>

            <div class="disease-card-text">
                Assess risk from diagnostic tumor measurement features
                and predict risks.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Assess Breast Cancer →",
        key="open_breast",
        use_container_width=True,
    ):
        st.switch_page("pages/breast_app.py")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="healthai-bottom-note">
        HealthAI • EXHRA • Research / Academic Prototype •
        Not a medical diagnosis
    </div>
    """,
    unsafe_allow_html=True,
)