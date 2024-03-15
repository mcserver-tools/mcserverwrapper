"""Module containing tests for Forge servers"""

from ..helpers.forge_helper import run_forge_test_url

FORGE_URLS = {
    "1.20.4": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.4-49.0.31/forge-1.20.4-49.0.31-installer.jar",
    "1.20.3": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.3-49.0.2/forge-1.20.3-49.0.2-installer.jar",
    "1.16.5": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.16.5-36.2.42/forge-1.16.5-36.2.42-installer.jar",
    "1.14.4": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.14.4-28.2.26/forge-1.14.4-28.2.26-installer.jar",
    "1.12.2": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.12.2-14.23.5.2860/forge-1.12.2-14.23.5.2860-installer.jar",
    "1.10.2": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.10.2-12.18.3.2511/forge-1.10.2-12.18.3.2511-installer.jar",
    "1.8.9": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.8.9-11.15.1.2318-1.8.9/forge-1.8.9-11.15.1.2318-1.8.9-installer.jar",
    "1.7.10": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.7.10-10.13.4.1614-1.7.10/forge-1.7.10-10.13.4.1614-1.7.10-installer.jar"
}

def test_multiple(forge_download_url: str):
    """Test multiple supported Forge server versions"""

    run_forge_test_url(forge_download_url)

def test_single_online():
    """Test a single Forge version in online mode"""

    url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.4-49.0.31/forge-1.20.4-49.0.31-installer.jar"

    run_forge_test_url(url)

def test_single_offline():
    """Test a single Forge version in offline mode"""

    url = "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.4-49.0.31/forge-1.20.4-49.0.31-installer.jar"

    run_forge_test_url(url, offline_mode=True)
