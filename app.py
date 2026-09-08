import streamlit as st
import subprocess
import re
import pandas as pd

st.set_page_config(
    page_title="Wi-Fi Network & Signal Scanner",
    page_icon="📶",
    layout="wide"
)

st.title("📶 Wi-Fi Network & Signal Scanner")
st.write("Scan nearby Wi-Fi networks and analyze signal strength and security.")

st.divider()


def scan_wifi():
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            text=True,
            errors="ignore"
        )

        lines = output.splitlines()

        networks = []
        current_ssid = None
        current_auth = "Unknown"
        current_encryption = "Unknown"
        current_signal = "Unknown"
        current_channel = "Unknown"

        for line in lines:
            line = line.strip()

            # SSID
            if re.match(r"^SSID\s+\d+\s*:", line):
                current_ssid = line.split(":", 1)[1].strip()

                current_auth = "Unknown"
                current_encryption = "Unknown"
                current_signal = "Unknown"
                current_channel = "Unknown"

            # Authentication
            elif line.startswith("Authentication"):
                current_auth = line.split(":", 1)[1].strip()

            # Encryption
            elif line.startswith("Encryption"):
                current_encryption = line.split(":", 1)[1].strip()

            # Signal
            elif line.startswith("Signal"):
                current_signal = line.split(":", 1)[1].strip()

            # Channel
            elif line.startswith("Channel"):
                current_channel = line.split(":", 1)[1].strip()

                if current_ssid:
                    networks.append({
                        "SSID": current_ssid,
                        "Signal": current_signal,
                        "Channel": current_channel,
                        "Security": current_auth,
                        "Encryption": current_encryption
                    })

        return networks

    except Exception as e:
        st.error(f"Scanning error: {e}")
        return []


def signal_quality(signal):
    try:
        value = int(signal.replace("%", "").strip())

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


if st.button("🔍 Scan Wi-Fi Networks", use_container_width=True):

    with st.spinner("Scanning nearby Wi-Fi networks..."):

        networks = scan_wifi()

    if networks:

        st.success(f"Found {len(networks)} Wi-Fi networks!")

        # -------------------------
        # Statistics
        # -------------------------

        signal_values = []

        for network in networks:
            try:
                signal_values.append(
                    int(network["Signal"].replace("%", "").strip())
                )
            except:
                pass

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "📡 Networks Found",
                len(networks)
            )

        with col2:
            if signal_values:
                avg = round(sum(signal_values) / len(signal_values), 1)
                st.metric(
                    "📊 Average Signal",
                    f"{avg}%"
                )
            else:
                st.metric(
                    "📊 Average Signal",
                    "N/A"
                )

        with col3:
            if signal_values:
                strongest = max(signal_values)
                st.metric(
                    "💪 Strongest Signal",
                    f"{strongest}%"
                )
            else:
                st.metric(
                    "💪 Strongest Signal",
                    "N/A"
                )

        st.divider()

        # -------------------------
        # Network Table
        # -------------------------

        st.subheader("📋 Available Wi-Fi Networks")

        data = []

        for network in networks:

            data.append({
                "SSID": network["SSID"],
                "Signal": network["Signal"],
                "Quality": signal_quality(network["Signal"]),
                "Channel": network["Channel"],
                "Security": network["Security"],
                "Encryption": network["Encryption"]
            })

        df = pd.DataFrame(data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # -------------------------
        # Signal Chart
        # -------------------------

        st.subheader("📈 Signal Strength")

        chart_df = pd.DataFrame({
            "SSID": [x["SSID"] for x in networks],
            "Signal Strength (%)": [
                int(x["Signal"].replace("%", "").strip())
                if "%" in x["Signal"]
                else 0
                for x in networks
            ]
        })

        chart_df = chart_df.set_index("SSID")

        st.bar_chart(chart_df)

        st.divider()

        # -------------------------
        # Security Analysis
        # -------------------------

        st.subheader("🔐 Security Analysis")

        security_types = {}

        for network in networks:

            security = network["Security"]

            if security in security_types:
                security_types[security] += 1
            else:
                security_types[security] = 1

        security_df = pd.DataFrame(
            list(security_types.items()),
            columns=["Security Type", "Networks"]
        )

        st.dataframe(
            security_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No Wi-Fi networks found. Make sure Wi-Fi is turned ON."
        )


st.divider()

st.caption(
    "Basic Wi-Fi Network & Signal Scanner | Python + Streamlit"
)
