import streamlit as st
import pandas as pd
import platform
import subprocess
import re

# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Wi-Fi Network & Signal Scanner",
    page_icon="📶",
    layout="wide"
)

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #888;
        font-size: 18px;
        margin-bottom: 25px;
    }

    .info-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.markdown(
    '<div class="title">📶 Wi-Fi Network & Signal Scanner</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Scan nearby Wi-Fi networks and analyze signal strength and security'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# -------------------------------------------------
# LIVE WINDOWS WIFI SCANNER
# -------------------------------------------------

def scan_windows_wifi():

    try:

        result = subprocess.run(
            [
                "netsh",
                "wlan",
                "show",
                "networks",
                "mode=bssid"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        output = result.stdout

        if not output:
            return []

        networks = []

        ssid = None
        security = "Unknown"
        encryption = "Unknown"
        signal = "0%"
        channel = "Unknown"

        for line in output.splitlines():

            line = line.strip()

            # SSID
            if re.match(r"^SSID\s+\d+\s*:", line):

                ssid = line.split(":", 1)[1].strip()

                security = "Unknown"
                encryption = "Unknown"
                signal = "0%"
                channel = "Unknown"

            # Authentication
            elif line.startswith("Authentication"):

                security = line.split(":", 1)[1].strip()

            # Encryption
            elif line.startswith("Encryption"):

                encryption = line.split(":", 1)[1].strip()

            # Signal
            elif line.startswith("Signal"):

                signal = line.split(":", 1)[1].strip()

            # Channel
            elif line.startswith("Channel"):

                channel = line.split(":", 1)[1].strip()

                if ssid:

                    networks.append({
                        "SSID": ssid,
                        "Signal": signal,
                        "Channel": channel,
                        "Security": security,
                        "Encryption": encryption
                    })

        return networks

    except Exception:

        return []


# -------------------------------------------------
# DEMO WIFI DATA
# -------------------------------------------------

def demo_wifi():

    return [
        {
            "SSID": "Home_WiFi",
            "Signal": "92%",
            "Channel": "6",
            "Security": "WPA2-Personal",
            "Encryption": "CCMP"
        },
        {
            "SSID": "JioFiber_5G",
            "Signal": "84%",
            "Channel": "36",
            "Security": "WPA3-Personal",
            "Encryption": "CCMP"
        },
        {
            "SSID": "Office_WiFi",
            "Signal": "71%",
            "Channel": "11",
            "Security": "WPA2-Personal",
            "Encryption": "CCMP"
        },
        {
            "SSID": "Airtel_5G",
            "Signal": "63%",
            "Channel": "44",
            "Security": "WPA2-Personal",
            "Encryption": "CCMP"
        },
        {
            "SSID": "Guest_Network",
            "Signal": "48%",
            "Channel": "1",
            "Security": "WPA2-Personal",
            "Encryption": "CCMP"
        },
        {
            "SSID": "College_WiFi",
            "Signal": "35%",
            "Channel": "11",
            "Security": "WPA2-Enterprise",
            "Encryption": "CCMP"
        }
    ]


# -------------------------------------------------
# SIGNAL QUALITY
# -------------------------------------------------

def signal_quality(signal):

    try:

        value = int(signal.replace("%", ""))

        if value >= 80:
            return "Excellent 🟢"

        elif value >= 60:
            return "Good 🟡"

        elif value >= 40:
            return "Fair 🟠"

        else:
            return "Weak 🔴"

    except:

        return "Unknown"


# -------------------------------------------------
# BUTTONS
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    live_scan = st.button(
        "🔍 Scan Wi-Fi Networks",
        use_container_width=True
    )

with col2:

    demo_scan = st.button(
        "🧪 Demo Scan",
        use_container_width=True
    )


# -------------------------------------------------
# LIVE SCAN
# -------------------------------------------------

if live_scan:

    if platform.system() == "Windows":

        networks = scan_windows_wifi()

        if networks:

            st.session_state["networks"] = networks
            st.session_state["scan_type"] = "Live"

        else:

            st.warning(
                "Live Wi-Fi scanning is not available in this environment."
            )

            st.info(
                "Click 'Demo Scan' to view the complete application."
            )

    else:

        st.warning(
            "Live scanning is supported on Windows when running locally."
        )

        st.info(
            "Click 'Demo Scan' to view the application."
        )


# -------------------------------------------------
# DEMO SCAN
# -------------------------------------------------

if demo_scan:

    st.session_state["networks"] = demo_wifi()
    st.session_state["scan_type"] = "Demo"


# -------------------------------------------------
# DISPLAY RESULTS
# -------------------------------------------------

if "networks" in st.session_state:

    networks = st.session_state["networks"]

    if st.session_state["scan_type"] == "Live":

        st.success(
            f"✅ Live scan completed — {len(networks)} networks found."
        )

    else:

        st.info(
            "🧪 Demo scan completed — sample Wi-Fi networks displayed."
        )

    st.divider()

    # -------------------------------------------------
    # STATISTICS
    # -------------------------------------------------

    signal_values = []

    for network in networks:

        try:

            value = int(
                network["Signal"].replace("%", "")
            )

            signal_values.append(value)

        except:

            pass

    total_networks = len(networks)

    average_signal = round(
        sum(signal_values) / len(signal_values),
        1
    )

    strongest_signal = max(signal_values)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "📡 Networks Found",
            total_networks
        )

    with col2:

        st.metric(
            "📊 Average Signal",
            f"{average_signal}%"
        )

    with col3:

        st.metric(
            "💪 Strongest Signal",
            f"{strongest_signal}%"
        )

    st.divider()

    # -------------------------------------------------
    # NETWORK TABLE
    # -------------------------------------------------

    st.subheader("📋 Available Wi-Fi Networks")

    table = []

    for network in networks:

        table.append({
            "SSID": network["SSID"],
            "Signal": network["Signal"],
            "Quality": signal_quality(network["Signal"]),
            "Channel": network["Channel"],
            "Security": network["Security"],
            "Encryption": network["Encryption"]
        })

    df = pd.DataFrame(table)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -------------------------------------------------
    # SIGNAL CHART
    # -------------------------------------------------

    st.subheader("📈 Signal Strength Analysis")

    chart = pd.DataFrame({

        "SSID": [
            n["SSID"] for n in networks
        ],

        "Signal Strength (%)": [
            int(n["Signal"].replace("%", ""))
            for n in networks
        ]

    })

    chart = chart.set_index("SSID")

    st.bar_chart(chart)

    st.divider()

    # -------------------------------------------------
    # SECURITY ANALYSIS
    # -------------------------------------------------

    st.subheader("🔐 Security Analysis")

    security_count = {}

    for network in networks:

        security = network["Security"]

        security_count[security] = (
            security_count.get(security, 0) + 1
        )

    security_df = pd.DataFrame(
        list(security_count.items()),
        columns=[
            "Security Type",
            "Number of Networks"
        ]
    )

    st.dataframe(
        security_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # -------------------------------------------------
    # RECOMMENDATION
    # -------------------------------------------------

    st.subheader("💡 Network Performance Recommendation")

    if average_signal >= 80:

        st.success(
            "Excellent overall Wi-Fi signal strength."
        )

    elif average_signal >= 60:

        st.info(
            "Good overall Wi-Fi signal strength."
        )

    elif average_signal >= 40:

        st.warning(
            "Moderate signal strength. "
            "Consider moving closer to the router."
        )

    else:

        st.error(
            "Weak signal strength detected. "
            "Consider checking router placement."
        )

    # -------------------------------------------------
    # SECURITY TIP
    # -------------------------------------------------

    st.subheader("🔒 Security Tip")

    st.write(
        "WPA2 and WPA3 are commonly used Wi-Fi security standards. "
        "For better protection, prefer WPA3 when your router and devices support it."
    )


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "Basic Wi-Fi Network & Signal Scanner | "
    "Developed using Python + Streamlit"
)
