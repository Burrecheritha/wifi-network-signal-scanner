def scan_wifi():
    try:
        result = subprocess.check_output(
            ["netsh", "wlan", "show", "networks", "mode=bssid"],
            encoding="utf-8",
            errors="ignore"
        )

        networks = []
        current_ssid = None
        current_auth = "Unknown"
        current_encryption = "Unknown"
        current_signal = "Unknown"
        current_channel = "Unknown"

        for line in result.splitlines():

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
        st.error(f"Wi-Fi scanning error: {e}")
        return []
