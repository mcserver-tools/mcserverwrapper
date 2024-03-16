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

import pytest
from pytest import Metafunc, TestReport, Session, ExitCode

from .helpers.common_helper import get_mcserver_log
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
# pylint: enable=wrong-import-position

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

# the arguments are needed for the pytest hooks to work correctly
# pylint: disable=unused-argument
@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Save mcserverwrapper.log to the current pytest item"""

    # execute all other hooks to obtain the report object
    rep: TestReport = yield

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.outcome == "failed":
        item.mcserverlog = get_mcserver_log()

    return rep

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: Session, exitstatus: ExitCode):
    """Print all saved mcserverwrapper.log after all tests finished"""

    if len(session.items) == 0:
        return

    print("")
    print("")
    print("=" * 20, end="")
    print(" McServerWrapper.log ", end="")
    print("=" * 20)

    for item in session.items:
        # skip tests that didn't fail
        if hasattr(item, "mcserverlog"):
            print("")
            print("-" * 20, end="")
            print(f" {item.name} ", end="")
            print("-" * 20, end="\n")
            for line in item.mcserverlog.split("\n"):
                print(line)
# pylint: enable=unused-argument
