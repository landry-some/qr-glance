import pytest

from qr_glance.payloads import wifi_payload


def test_basic_wpa():
    assert wifi_payload("HomeNet", "correct horse") == "WIFI:T:WPA;S:HomeNet;P:correct horse;;"


def test_special_characters_are_escaped():
    assert wifi_payload('a;b,c:d"e\\f', "pa;ss:word") == (
        r'WIFI:T:WPA;S:a\;b\,c\:d\"e\\f;P:pa\;ss\:word;;'
    )


def test_open_and_hidden():
    assert wifi_payload("Cafe", security="nopass", hidden=True) == "WIFI:T:nopass;S:Cafe;H:true;;"


def test_wep_skips_wpa_length_rule():
    assert wifi_payload("Old", "abcde", security="WEP") == "WIFI:T:WEP;S:Old;P:abcde;;"


@pytest.mark.parametrize("kwargs, message", [
    ({"ssid": "", "password": "12345678"}, "SSID"),
    ({"ssid": "x", "password": None}, "needs a password"),
    ({"ssid": "x", "password": "short"}, "8 to 63"),
    ({"ssid": "x", "password": "p" * 64}, "8 to 63"),
    ({"ssid": "x", "password": "secret12", "security": "nopass"}, "takes no password"),
    ({"ssid": "x", "password": "secret12", "security": "WPA9"}, "security must be"),
])
def test_invalid(kwargs, message):
    with pytest.raises(ValueError, match=message):
        wifi_payload(**kwargs)
