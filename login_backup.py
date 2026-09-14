import re
from pathlib import Path

import streamlit as st

from auth import generate_otp, send_otp, get_user_by_email, create_user


# ============================================================
# EMAIL VALIDATION
# ============================================================

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z][A-Za-z0-9.-]*\.[A-Za-z]{2,}$"
    return re.fullmatch(pattern, email) is not None


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():

    # --------------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------------

    defaults = {
        "otp_sent": False,
        "verified": False,
        "user_email": "",
        "otp": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # --------------------------------------------------------
    # CSS
    # --------------------------------------------------------

    st.markdown(
        """
        <style>

        /* ---------- STREAMLIT CLEANUP ---------- */

        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

        #MainMenu,
        header,
        footer {
            visibility: hidden !important;
            height: 0 !important;
        }

        .stApp {
            background:
                radial-gradient(
                    circle at 10% 15%,
                    rgba(174, 239, 232, 0.55),
                    transparent 32%
                ),
                radial-gradient(
                    circle at 90% 20%,
                    rgba(181, 207, 255, 0.55),
                    transparent 35%
                ),
                linear-gradient(
                    135deg,
                    #eefbf9 0%,
                    #f7fbff 48%,
                    #edf4ff 100%
                );
            min-height: 100vh;
        }

        .block-container {
            max-width: 1500px !important;
            padding-top: 28px !important;
            padding-bottom: 20px !important;
            padding-left: 30px !important;
            padding-right: 30px !important;
        }

        /* ---------- REMOVE THE OLD STRETCHED COLUMN CARD ---------- */

        [data-testid="column"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            min-height: 0 !important;
        }

        /* ---------- BRAND ---------- */

        .brand-title {
            color: #123b67;
            font-size: 36px;
            line-height: 1.05;
            font-weight: 800;
            letter-spacing: -1.2px;
        }

        .brand-title span {
            color: #16b5b1;
        }

        .brand-subtitle {
            color: #5f7891;
            font-size: 16px;
            font-weight: 500;
            margin-top: 6px;
        }

        /* ---------- HERO ---------- */

        .hero-image-wrap {
            width: 100%;
            overflow: hidden;
            border-radius: 18px;
            border: 1px solid rgba(205, 225, 239, 0.75);
            box-shadow: 0 16px 42px rgba(48, 107, 151, 0.10);
        }

        .hero-image-wrap img {
            display: block;
            width: 100%;
            border-radius: 18px;
        }

        /* ---------- REAL STREAMLIT BORDERED CARDS ---------- */

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.90) !important;
            border: 1px solid #d8e5ee !important;
            border-radius: 20px !important;
            box-shadow: 0 12px 34px rgba(45, 91, 117, 0.08) !important;
        }

        /* ---------- LEFT FEATURE CARD ---------- */

        .feature-icon {
            font-size: 28px;
            text-align: center;
            margin-bottom: 7px;
        }

        .feature-title {
            color: #12365f;
            font-size: 18px;
            font-weight: 800;
            line-height: 1.2;
            text-align: center;
        }

        .feature-description {
            color: #637b91;
            font-size: 14px;
            line-height: 1.55;
            text-align: center;
            margin-top: 7px;
        }

        /* ---------- LOGIN CARD ---------- */

        .login-logo {
            width: 84px;
            height: 84px;
            margin: 4px auto 24px auto;
            border-radius: 50%;
            background: #ffffff;
            border: 1px solid #d8edf2;
            box-shadow:
                0 0 0 11px rgba(228, 250, 250, 0.72),
                0 10px 28px rgba(34, 174, 190, 0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 43px;
        }

        .login-heading {
            color: #12385f;
            font-size: 32px;
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: -0.5px;
            text-align: center;
            margin-bottom: 8px;
        }

        .login-description {
            color: #6a8097;
            font-size: 15px;
            line-height: 1.65;
            text-align: center;
            margin-bottom: 25px;
        }

        /* ---------- INPUT ---------- */

        div[data-testid="stTextInput"] {
            margin-bottom: 9px;
        }

        div[data-testid="stTextInput"] label {
            color: #234c6b !important;
            font-size: 14px !important;
            font-weight: 600 !important;
        }

        div[data-testid="stTextInput"] input {
            height: 50px !important;
            min-height: 50px !important;
            padding: 0 15px !important;
            background: #ffffff !important;
            color: #173c59 !important;
            border: 1px solid #c9d9e5 !important;
            border-radius: 11px !important;
            font-size: 15px !important;
            box-shadow: none !important;
        }

        div[data-testid="stTextInput"] input:focus {
            border-color: #27b5c3 !important;
            box-shadow: 0 0 0 3px rgba(39, 181, 195, 0.12) !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #93a7ba !important;
            opacity: 1 !important;
        }

        /* ---------- BUTTON ---------- */

        div.stButton > button {
            width: 100%;
            min-height: 50px !important;
            border: none !important;
            border-radius: 11px !important;
            font-size: 15px !important;
            font-weight: 750 !important;
            color: white !important;
            background: linear-gradient(
                90deg,
                #13b7b5 0%,
                #168fe1 100%
            ) !important;
            box-shadow: 0 10px 22px rgba(21, 154, 203, 0.18) !important;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 13px 28px rgba(21, 154, 203, 0.24) !important;
        }

        /* ---------- WHY HEALTHGUARD ---------- */

        .why-title {
            color: #173b60;
            font-size: 17px;
            font-weight: 800;
            line-height: 1.25;
        }

        .why-description {
            color: #6d8398;
            font-size: 14px;
            line-height: 1.45;
            margin-top: 4px;
        }

        .why-icon {
            font-size: 25px;
            line-height: 1;
        }

        /* ---------- FOOTER ---------- */

        .footer-text {
            color: #70869d;
            font-size: 13px;
            text-align: center;
            margin-top: 18px;
        }

        /* ---------- MOBILE ---------- */

        @media (max-width: 900px) {
            .block-container {
                padding-left: 18px !important;
                padding-right: 18px !important;
            }

            .brand-title {
                font-size: 30px;
            }

            .login-heading {
                font-size: 28px;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # TWO COLUMN PAGE
    #
    # IMPORTANT:
    # The login card is now a REAL Streamlit bordered
    # container. It is NOT a styled column, so it cannot
    # stretch to the height of the left side.
    # ========================================================

    left, right = st.columns([1.03, 0.97], gap="large")

    # ========================================================
    # LEFT SIDE
    # ========================================================

    with left:

        brand_icon_col, brand_text_col = st.columns([0.11, 0.89], vertical_alignment="center")

        with brand_icon_col:
            st.markdown(
                """
                <div style="
                    width:62px;
                    height:62px;
                    border-radius:18px;
                    background:rgba(255,255,255,.90);
                    border:1px solid #d0e3ed;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:34px;
                    box-shadow:0 10px 28px rgba(47,119,145,.10);
                ">🛡️</div>
                """,
                unsafe_allow_html=True,
            )

        with brand_text_col:
            st.markdown(
                """
                <div class="brand-title">
                    HealthGuard <span>AI</span>
                </div>
                <div class="brand-subtitle">
                    AI-powered health risk prediction &amp; monitoring
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        image_path = Path(__file__).resolve().parent / "assets" / "healthguard_hero.png"

        if image_path.exists():
            st.markdown(
                '<div class="hero-image-wrap">',
                unsafe_allow_html=True,
            )
            st.image(str(image_path), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning(
                "Hero image not found. Put healthguard_hero.png inside the assets folder."
            )

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # REAL STREAMLIT CARD -- NO HTML CODE CAN APPEAR HERE
        with st.container(border=True):

            c1, c2, c3 = st.columns(3, gap="medium")

            with c1:
                st.markdown('<div class="feature-icon">🧠</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="feature-title">AI-Powered<br>Prediction</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="feature-description">'
                    'Advanced machine learning for accurate risk prediction'
                    '</div>',
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown('<div class="feature-icon">🔐</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="feature-title">Secure &amp;<br>Private</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="feature-description">'
                    'Your health data is encrypted and fully protected'
                    '</div>',
                    unsafe_allow_html=True,
                )

            with c3:
                st.markdown('<div class="feature-icon">📊</div>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="feature-title">Smart<br>Insights</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<div class="feature-description">'
                    'Personalized insights to help you live a healthier life'
                    '</div>',
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<div class="footer-text">© 2026 HealthGuard AI. All rights reserved.</div>',
            unsafe_allow_html=True,
        )

    # ========================================================
    # RIGHT SIDE
    # ========================================================

    with right:

        # REAL STREAMLIT CARD
        # This is the key fix for the giant empty white area.
        with st.container(border=True):

            st.markdown(
                '<div class="login-logo">🩺</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="login-heading">Welcome back! 👋</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="login-description">'
                'Enter your email address to securely log in<br>'
                'or create your HealthGuard AI account.'
                '</div>',
                unsafe_allow_html=True,
            )

            # ------------------------------------------------
            # STEP 1: EMAIL
            # ------------------------------------------------

            if not st.session_state.otp_sent:

                email = st.text_input(
                    "Email Address",
                    placeholder="you@example.com",
                    key="login_email",
                )

                if st.button(
                    "Send OTP  →",
                    type="primary",
                    use_container_width=True,
                    key="send_otp",
                ):
                    email = email.strip().lower()

                    if not email:
                        st.error("Please enter your email address.")

                    elif not is_valid_email(email):
                        st.error(
                            "Please enter a valid email address "
                            "(example: name@gmail.com)."
                        )

                    else:
                        otp = generate_otp()

                        st.session_state.otp = otp
                        st.session_state.user_email = email

                        with st.spinner("Sending verification code..."):
                            if send_otp(email, otp):
                                st.session_state.otp_sent = True
                                st.success(
                                    "OTP sent successfully! Check your email."
                                )
                                st.rerun()
                            else:
                                st.error(
                                    "Unable to send OTP. Please try again."
                                )

            # ------------------------------------------------
            # STEP 2: OTP
            # ------------------------------------------------

            else:

                st.divider()

                st.markdown(
                    "### Verify your email",
                )

                st.info(
                    f"🔐 Verification code sent to "
                    f"**{st.session_state.user_email}**"
                )

                entered_otp = st.text_input(
                    "Enter 6-digit OTP",
                    max_chars=6,
                    placeholder="123456",
                    key="login_otp",
                )

                verify_col, resend_col = st.columns(2, gap="small")

                with verify_col:
                    if st.button(
                        "Verify OTP",
                        type="primary",
                        use_container_width=True,
                        key="verify_otp",
                    ):
                        if entered_otp == st.session_state.otp:

                            email = st.session_state.user_email
                            existing_user = get_user_by_email(email)

                            if existing_user is None:
                                user_id = create_user(email)
                                st.session_state.user_id = user_id
                                st.session_state.is_logged_in = True
                                st.success(
                                    "Account created successfully! 🎉"
                                )
                            else:
                                st.session_state.user_id = existing_user[0]
                                st.session_state.is_logged_in = True
                                st.success("Login successful! 🎉")

                            st.session_state.verified = True
                            st.rerun()

                        else:
                            st.error(
                                "Incorrect OTP. Please check your email "
                                "and try again."
                            )

                with resend_col:
                    if st.button(
                        "Resend OTP",
                        use_container_width=True,
                        key="resend_otp",
                    ):
                        otp = generate_otp()
                        st.session_state.otp = otp

                        if send_otp(
                            st.session_state.user_email,
                            otp,
                        ):
                            st.success("New OTP sent!")
                        else:
                            st.error(
                                "Unable to send OTP. Please try again."
                            )

                if st.button(
                    "← Use a different email",
                    use_container_width=True,
                    key="change_email",
                ):
                    st.session_state.otp_sent = False
                    st.session_state.otp = None
                    st.session_state.user_email = ""
                    st.session_state.verified = False
                    st.rerun()

            # ------------------------------------------------
            # WHY HEALTHGUARD AI
            # ------------------------------------------------

            st.divider()

            st.markdown(
                "<h3 style='text-align:center;color:#173b60;"
                "font-size:17px;margin:0 0 12px 0;'>"
                "Why HealthGuard AI?</h3>",
                unsafe_allow_html=True,
            )

            why_items = [
                (
                    "🧠",
                    "AI-Powered Prediction",
                    "Intelligent health risk analysis",
                ),
                (
                    "📊",
                    "Personalized Monitoring",
                    "Track your health insights in real-time",
                ),
                (
                    "🔐",
                    "Secure Access",
                    "Verified email-based authentication",
                ),
            ]

            for index, (icon, title, description) in enumerate(why_items):

                icon_col, text_col = st.columns([0.13, 0.87], vertical_alignment="center")

                with icon_col:
                    st.markdown(
                        f'<div class="why-icon">{icon}</div>',
                        unsafe_allow_html=True,
                    )

                with text_col:
                    st.markdown(
                        f'<div class="why-title">{title}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="why-description">{description}</div>',
                        unsafe_allow_html=True,
                    )

                if index < len(why_items) - 1:
                    st.markdown(
                        "<hr style='border:none;border-top:1px solid #e5edf2;"
                        "margin:10px 0 2px 0;'>",
                        unsafe_allow_html=True,
                    )

            st.markdown(
                "<div style='text-align:center;color:#71869a;font-size:12.5px;"
                "margin-top:20px;'>"
                "🔒 <b>Secure email verification</b>"
                "&nbsp; • &nbsp;"
                "Your health data stays protected"
                "</div>",
                unsafe_allow_html=True,
            )


# ============================================================
# OPTIONAL: RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="HealthGuard AI",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    login_page()
