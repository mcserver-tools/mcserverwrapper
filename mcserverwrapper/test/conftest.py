# pylint: disable=unused-wildcard-import
# pylint: disable=wildcard-import
# Needed for making pytest fixtures working correctly
# pylint: disable=wrong-import-position, unused-import

"""
    Pytest configuration
"""
import os
import sys
import pathlib

from pytest import Metafunc

from .integration_tests import test_forge

# Adding source path to sys path
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
sys.path.append(f"{pathlib.Path(__file__).parent.parent}")
sys.path.append(f"{pathlib.Path(__file__).parent}")

test_files_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "temp")
if not os.path.isdir(test_files_path):
    os.mkdir(test_files_path)

from .fixtures import newest_server_jar

from .helpers.common_helper import get_vanilla_urls
#pylint: enable=wrong-import-position

def pytest_generate_tests(metafunc: Metafunc):
    """Pytest hook"""

    if "jar_version_tuple" in metafunc.fixturenames:
        urls = get_vanilla_urls()
        metafunc.parametrize(argnames="jar_version_tuple",
                             argvalues=urls,
                             ids=[f"test_version_{url[1]}" for url in urls])

    if "jar_download_url" in metafunc.fixturenames:
        urls = get_vanilla_urls()
        metafunc.parametrize(argnames="jar_download_url",
                             argvalues=[url[0] for url in urls],
                             ids=[f"test_download_version_{url[1]}" for url in urls])

    if "forge_download_url" in metafunc.fixturenames:
        urls = test_forge.FORGE_URLS
        metafunc.parametrize(argnames="forge_download_url",
                             argvalues=test_forge.FORGE_URLS.values(),
                             ids=[f"test_version_{item}" for item in test_forge.FORGE_URLS])
