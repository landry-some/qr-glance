"""Build structured QR payloads that phone cameras act on."""

SECURITY_TYPES = ("WPA", "WEP", "nopass")

# Characters that must be backslash-escaped inside WIFI: fields
_WIFI_SPECIAL = ("\\", ";", ",", ":", '"')


def _escape(value: str) -> str:
    return "".join("\\" + c if c in _WIFI_SPECIAL else c for c in value)


def wifi_payload(ssid: str, password: str | None = None, security: str = "WPA",
                 hidden: bool = False) -> str:
    """Return a ``WIFI:`` string that iOS and Android cameras offer to join.

    ``security`` is WPA (also covers WPA2/WPA3), WEP or nopass for open networks.
    """
    if not ssid:
        raise ValueError("network name (SSID) can't be empty")
    if security not in SECURITY_TYPES:
        raise ValueError(f"security must be one of {', '.join(SECURITY_TYPES)}, got {security!r}")

    fields = [f"T:{security}", f"S:{_escape(ssid)}"]
    if security == "nopass":
        if password:
            raise ValueError("an open network (nopass) takes no password")
    else:
        if not password:
            raise ValueError(f"a {security} network needs a password")
        if security == "WPA" and not 8 <= len(password) <= 63:
            raise ValueError("a WPA password is 8 to 63 characters long")
        fields.append(f"P:{_escape(password)}")
    if hidden:
        fields.append("H:true")
    return "WIFI:" + ";".join(fields) + ";;"
