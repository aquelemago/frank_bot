from __future__ import annotations

import logging
from dataclasses import dataclass

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

from app.settings import Soft4Settings


LOGGER = logging.getLogger(__name__)


class AuthenticationError(RuntimeError):
    """Falha ao autenticar no Soft4."""


@dataclass(frozen=True)
class AuthenticatedSession:
    context: BrowserContext
    page: Page
    csrf_token: str | None
    headers: dict[str, str]
    cookies: dict[str, str]


class Soft4Browser:
    def __init__(self, settings: Soft4Settings) -> None:
        self.settings = settings
        self._playwright: Playwright | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    def __enter__(self) -> "Soft4Browser":
        self._playwright = sync_playwright().start()
        self._context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.settings.user_data_dir),
            headless=True,
            accept_downloads=True,
            viewport={"width": 1366, "height": 768},
        )
        self._context.set_default_timeout(self.settings.timeout_seconds * 1000)
        self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._context:
            self._context.close()
        if self._playwright:
            self._playwright.stop()

    def ensure_authenticated(self) -> AuthenticatedSession:
        page = self._require_page()
        LOGGER.info("Acessando fila de atendimento")
        page.goto(self.settings.queue_url, wait_until="networkidle")

        if self._is_login_page(page):
            LOGGER.info("Sessao expirada ou inexistente; realizando login")
            self._login(page)
            LOGGER.info("Login realizado")
        else:
            LOGGER.info("Sessao reutilizada")

        page.goto(self.settings.queue_url, wait_until="networkidle")
        if self._is_login_page(page):
            raise AuthenticationError("Falha ao autenticar: tela de login ainda esta visivel.")

        csrf_token = extract_csrf_token(page)
        cookies = self._cookies_as_dict()
        headers = build_headers(page, self.settings.base_url, csrf_token)
        return AuthenticatedSession(
            context=self._require_context(),
            page=page,
            csrf_token=csrf_token,
            headers=headers,
            cookies=cookies,
        )

    def _login(self, page: Page) -> None:
        if not self.settings.usuario or not self.settings.senha:
            raise AuthenticationError("Usuario e senha do Soft4 nao foram informados.")

        usuario = page.locator("input[name='lg_usuario'], input[type='text'], input[type='email']").first
        senha = page.locator("input[name='sh_usuario'], input[type='password']").first

        usuario.wait_for(state="visible")
        usuario.fill(self.settings.usuario)
        senha.wait_for(state="visible")
        senha.fill(self.settings.senha)

        clicked = False
        for selector in (
            "button:has-text('Atendente')",
            "button[type='submit']",
            "input[type='submit']",
        ):
            button = page.locator(selector).first
            try:
                button.wait_for(state="visible", timeout=2500)
                button.click()
                clicked = True
                break
            except Exception:
                continue

        if not clicked:
            page.keyboard.press("Enter")

        page.wait_for_load_state("networkidle")
        try:
            page.wait_for_url(lambda url: "login" not in str(url).lower(), timeout=10000)
        except Exception:
            pass

        if self._is_login_page(page):
            raise AuthenticationError("Falha ao autenticar: confira SOFT4_USUARIO e SOFT4_SENHA.")

    def _is_login_page(self, page: Page) -> bool:
        password_inputs = page.locator("input[name='sh_usuario'], input[type='password']")
        try:
            return password_inputs.first.is_visible(timeout=3000)
        except Exception:
            return False

    def _cookies_as_dict(self) -> dict[str, str]:
        return {
            cookie["name"]: cookie["value"]
            for cookie in self._require_context().cookies(self.settings.base_url)
        }

    def _require_context(self) -> BrowserContext:
        if self._context is None:
            raise RuntimeError("Contexto Playwright nao inicializado.")
        return self._context

    def _require_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Pagina Playwright nao inicializada.")
        return self._page


def extract_csrf_token(page: Page) -> str | None:
    token = page.locator("meta[name='csrf-token']").first
    try:
        content = token.get_attribute("content", timeout=2000)
        if content:
            return content
    except Exception:
        pass

    for selector in ("input[name='_token']", "input[name='csrf_token']", "input[name='csrfmiddlewaretoken']"):
        field = page.locator(selector).first
        try:
            value = field.get_attribute("value", timeout=1000)
            if value:
                return value
        except Exception:
            continue

    return None


def build_headers(page: Page, base_url: str, csrf_token: str | None) -> dict[str, str]:
    user_agent = page.evaluate("() => navigator.userAgent")
    headers = {
        "Accept": "text/csv,application/csv,application/octet-stream,*/*",
        "Origin": base_url,
        "Referer": page.url,
        "User-Agent": user_agent,
        "X-Requested-With": "XMLHttpRequest",
    }
    if csrf_token:
        headers["X-CSRF-TOKEN"] = csrf_token
    return headers
