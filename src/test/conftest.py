"""Pytest configuration"""

# pylint: disable=wrong-import-position, wrong-import-order, missing-function-docstring

import os
# Adding source path to sys path
import pathlib
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../'))
sys.path.append(f"{pathlib.Path(__file__).parent.parent}")
sys.path.append(f"{pathlib.Path(__file__).parent}")
# pylint: enable=wrong-import-position

from test.helpers.common_helper import get_mcserver_log, get_vanilla_urls
from test.integration_tests import test_forge

import pytest

os.environ["DEBUG"] = "True"

if not os.path.isdir("temp"):
    os.mkdir("temp")

def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--skip-linting", action="store_true", default=False, help="skip the pylint test"
    )
    parser.addoption(
        "--skip-test-all", action="store_true", default=False, help="skip testing all supported minecraft versions"
    )

def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    if config.getoption("--skip-linting"):
        skip_pylint = pytest.mark.skip(reason="skipping code linting due to --skip-linting arg")
        for item in items:
            if item.name in ["test_pylint", "test_mypy"]:
                item.add_marker(skip_pylint)

    if config.getoption("--skip-test-all"):
        skip_pylint = pytest.mark.skip(reason="skipping testing all minecraft versions due to --skip-test-all arg")
        for item in items:
            if item.name.startswith("test_all[") or item.name.startswith("test_multiple["):
                item.add_marker(skip_pylint)

    skip_pylint = pytest.mark.skip(reason="skipping testing in online mode as "
                                   "https://github.com/PrismarineJS/prismarine-auth/pull/137 is not yet merged")
    for item in items:
        if item.name in ["test_single_online", "test_mineflayer"]:
            item.add_marker(skip_pylint)

def pytest_generate_tests(metafunc: pytest.Metafunc):
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
    rep: pytest.TestReport = yield

    # we only look at actual failing test calls, not setup/teardown
    if rep.when == "call" and rep.outcome == "failed":
        item.mcserverlog = get_mcserver_log()

    return rep

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: pytest.ExitCode):
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

# pylint: disable-next=unused-wildcard-import, wildcard-import, wrong-import-order
from test.fixtures import *
