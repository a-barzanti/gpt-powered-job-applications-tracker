import sys
import types

# Stub external dependencies used in main.py so it can be imported without them
stubs = {
    "flet": types.ModuleType("flet"),
    "gspread": types.ModuleType("gspread"),
    "bs4": types.ModuleType("bs4"),
    "google": types.ModuleType("google"),
    "google.oauth2": types.ModuleType("google.oauth2"),
    "google.oauth2.service_account": types.ModuleType("google.oauth2.service_account"),
    "openai": types.ModuleType("openai"),
    "playwright": types.ModuleType("playwright"),
    "playwright.async_api": types.ModuleType("playwright.async_api"),
}
# minimal attributes used during import
stubs["bs4"].BeautifulSoup = lambda *args, **kwargs: None
class DummyOpenAI:
    def __init__(self, *args, **kwargs):
        pass
stubs["openai"].OpenAI = DummyOpenAI
stubs["google.oauth2.service_account"].Credentials = object
stubs["playwright.async_api"].async_playwright = lambda: None
stubs["flet"].Page = object
stubs["flet"].app = lambda *args, **kwargs: None
for name, module in stubs.items():
    sys.modules.setdefault(name, module)

from main import is_valid_url


def test_valid_url():
    assert is_valid_url("https://example.com")


def test_invalid_url():
    assert not is_valid_url("not-a-url")
