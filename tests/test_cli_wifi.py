import zxingcpp
from PIL import Image

from qr_glance.cli import main
from qr_glance.encode import make_qr
from qr_glance.render import to_terminal


def test_wifi_prints_code(capsys):
    assert main(["wifi", "--ssid", "HomeNet", "--password", "example-pass"]) == 0
    expected = to_terminal(make_qr("WIFI:T:WPA;S:HomeNet;P:example-pass;;").matrix)
    assert capsys.readouterr().out == expected + "\n"


def test_wifi_prompts_for_password(monkeypatch, tmp_path):
    asked = []
    monkeypatch.setattr("getpass.getpass", lambda prompt: asked.append(prompt) or "from-prompt")
    out = tmp_path / "wifi.png"
    assert main(["wifi", "--ssid", "HomeNet", "-o", str(out)]) == 0
    assert asked == ["Password for HomeNet: "]
    [found] = zxingcpp.read_barcodes(Image.open(out))
    assert found.text == "WIFI:T:WPA;S:HomeNet;P:from-prompt;;"


def test_open_network_does_not_prompt(monkeypatch, capsys):
    monkeypatch.setattr("getpass.getpass", lambda prompt: (_ for _ in ()).throw(AssertionError))
    assert main(["wifi", "--ssid", "Cafe", "--security", "nopass"]) == 0


def test_wifi_validation_error(capsys):
    assert main(["wifi", "--ssid", "HomeNet", "--password", "short"]) == 2
    assert "8 to 63" in capsys.readouterr().err
