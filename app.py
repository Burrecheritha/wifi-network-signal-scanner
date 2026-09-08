import streamlit as st
import subprocess
import re
import pandas as pd
from datetime import datetime

# -------------------------------------------------
# Page Configuration
# -------------------------------------------------

st.set_page_config(
    page_title="Wi-Fi Network & Signal Scanner",
    page_icon="📶",
    layout="wide"
)

# -------------------------------------------------
# Custom CSS
# -------------------------------------------------

st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .network-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Wi-Fi Scanner Function
# -------------------------------------------------

def scan_wifi():
    try:
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            encoding="utf-8",
            errors="ignore"
        )

        lines = result.splitlines()

        networks = []

        current_ssid = ""
        current_auth = "Unknown"
        current_encryption = "Unknown"
        current_signal = ""
        current_channel = ""

        for line in lines:

            line = line.strip()

            # SSID
            if line.startswith("SSID ") and ":" in line:
                match = re.match(r"SSID\s+\d+\s*:\s*(.*)", line)

                if match:
                    ssid = match.group(1).strip()

                    # Skip hidden/empty SSIDs
                    if ssid:
                        current_ssid = ssid

                        # Reset values
                        current_auth = "Unknown"
                        current_encryption = "Unknown"
                        current_signal = ""
                        current_channel = ""

            # Authentication
            elif line.startswith("Authentication") and ":" in line:
                current_auth = line.split(":", 1)[1].strip()

            # Encryption
            elif line.startswith("Encryption") and ":" in line:
                current_encryption = line.split(":", 1)[1].strip()

            # Signal
            elif line.startswith("Signal") and ":" in line:
                current_signal = line.split(":", 1)[1].strip()

            # Channel
            elif line.startswith("Channel") and ":" in line:
                current_channel = line.split(":", 1)[1].strip()

                # Save network when channel information is found
                if current_ssid:
                    networks.append({
                        "SSID": current_ssid,
                        "Signal": current_signal,
                        "Channel": current_channel,
                        "Security": current_auth,
                        "Encryption": current_encryption
                    })

        # Remove duplicate BSSID entries
        unique_networks = []

        seen = set()

        for network in networks:

            key = (
                network["SSID"],
                network["Channel"],
                network["Signal"]
            )

            if key not in seen:
                seen.add(key)
                unique_networks.append(network)

        return unique_networks

    except subprocess.CalledProcessError:
        return []

    except FileNotFoundError:
        return []

# -------------------------------------------------
# Signal Strength Conversion
# -------------------------------------------------

def signal_level(signal):

    try:
        value = int(signal.replace("%", "").strip())

        if value >= 80:
            return "🟢 Excellent"

        elif value >= 60:
            return "🟡 Good"

        elif value >= 40:
            return "🟠 Fair"

        else:
            return "🔴 Weak"

    except:
        return "Unknown"

# -------------------------------------------------
# Header
# -------------------------------------------------

st.markdown(
    '<div class="main-title">📶 Wi-Fi Network & Signal Scanner</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Scan nearby Wi-Fi networks and analyze signal strength and security'
    '</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------
# Scan Button
# -------------------------------------------------

col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    scan_button = st.button(
        "🔍 Scan Wi-Fi Networks",
        use_container_width=True
    )

# -------------------------------------------------
# Perform Scan
# -------------------------------------------------

if scan_button:

    with st.spinner("Scanning nearby Wi-Fi networks..."):

        wifi_networks = scan_wifi()

    if wifi_networks:

        st.session_state["wifi_networks"] = wifi_networks
        st.session_state["scan_time"] = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        st.success(
            f"Scan completed! Found {len(wifi_networks)} Wi-Fi network(s)."
        )

    else:

        st.error(
            "No Wi-Fi networks found. Make sure Wi-Fi is turned ON."
        )

# -------------------------------------------------
# Display Results
# -------------------------------------------------

if "wifi_networks" in st.session_state:

    networks = st.session_state["wifi_networks"]

    st.write("")

    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    total_networks = len(networks)

    signals = []

    for network in networks:

        try:
            signal = int(
                network["Signal"].replace("%", "").strip()
            )

            signals.append(signal)

        except:
            pass

    if signals:
        average_signal = round(sum(signals) / len(signals), 1)
        strongest_signal = max(signals)
    else:
        average_signal = 0
        strongest_signal = 0

    col1, col2, col3, col4 = st.columns(4)

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

    with col4:
        st.metric(
            "🕒 Last Scan",
            st.session_state["scan_time"]
        )

    st.divider()

    # -------------------------------------------------
    # Network Table
    # -------------------------------------------------

    st.subheader("📋 Available Wi-Fi Networks")

    display_data = []

    for network in networks:

        display_data.append({
            "SSID": network["SSID"],
            "Signal Strength": network["Signal"],
            "Signal Quality": signal_level(
                network["Signal"]
            ),
            "Channel": network["Channel"],
            "Security": network["Security"],
            "Encryption": network["Encryption"]
        })

    df = pd.DataFrame(display_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------------------------------
    # Signal Chart
    # -------------------------------------------------

    st.subheader("📈 Signal Strength Analysis")

    chart_data = pd.DataFrame({
        "SSID": [
            network["SSID"]
            for network in networks
        ],
        "Signal Strength (%)": [
            int(
                network["Signal"]
                .replace("%", "")
                .strip()
            )
            if network["Signal"]
            else 0
            for network in networks
        ]
    })

    chart_data = chart_data.set_index("SSID")

    st.bar_chart(
        chart_data
    )

    # -------------------------------------------------
    # Security Information
    # -------------------------------------------------

    st.subheader("🔐 Security Analysis")

    security_count = {}

    for network in networks:

        security = network["Security"]

        if security in security_count:
            security_count[security] += 1
        else:
            security_count[security] = 1

    security_df = pd.DataFrame(
        list(security_count.items()),
        columns=["Security Type", "Number of Networks"]
    )

    st.dataframe(
        security_df,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------

    st.subheader("💡 Network Performance Tips")

    if average_signal >= 70:

        st.success(
            "Most detected networks have good signal strength."
        )

    elif average_signal >= 40:

        st.warning(
            "Signal strength is moderate. Consider moving "
            "closer to the router for better performance."
        )

    else:

        st.error(
            "Signal strength appears weak. Check your "
            "router position or Wi-Fi adapter."
        )

    st.info(
        "💡 Tip: 5 GHz networks usually provide higher speed "
        "but may have shorter range than 2.4 GHz networks."
    )

# -------------------------------------------------
# Footer
# -------------------------------------------------

st.divider()

st.caption(
    "Basic Wi-Fi Network & Signal Scanner | "
    "Developed using Python + Streamlit"
)
