from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

_ARTICLE_HOSTS = frozenset(
    {"chequeado.com", "lagaceta.com.ar", "lanacion.com.ar", "clarin.com", "pagina12.com.ar"}
)
_MAX_PAGE_BYTES = 2_000_000


def _article_host(url: str) -> str:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").removeprefix("www.")
    if (
        parsed.scheme != "https"
        or host not in _ARTICLE_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in {None, 443}
    ):
        return ""
    return host


class _SamePublisherRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _article_host(newurl) or _article_host(newurl) != _article_host(req.full_url):
            raise URLError("La redirección salió del sitio del medio")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _read_page(url: str, timeout: float) -> str:
    if not _article_host(url):
        return ""
    request = Request(url, headers={"User-Agent": "ROBY-XI.2 (personal assistant)"})
    with build_opener(_SamePublisherRedirect()).open(request, timeout=timeout) as response:
        data = response.read(_MAX_PAGE_BYTES + 1)
        if len(data) > _MAX_PAGE_BYTES:
            return ""
        return data.decode(response.headers.get_content_charset() or "utf-8", errors="replace")


class _ArticlePage(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.paragraphs: list[str] = []
        self.title = ""
        self.description = ""
        self._article_depth = 0
        self._href = ""
        self._anchor_text: list[str] = []
        self._paragraph: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "article":
            self._article_depth += 1
        elif tag == "p" and self._article_depth:
            self._paragraph = []
        elif tag == "a":
            self._href = attrs.get("href") or ""
            self._anchor_text = []
        elif tag == "meta":
            if attrs.get("property") == "og:title":
                self.title = attrs.get("content") or ""
            elif attrs.get("property") == "og:description":
                self.description = attrs.get("content") or ""

    def handle_data(self, data):
        if self._href:
            self._anchor_text.append(data)
        if self._paragraph is not None:
            self._paragraph.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            self.links.append((self._href, " ".join("".join(self._anchor_text).split())))
            self._href = ""
        elif tag == "p" and self._paragraph is not None:
            self.paragraphs.append(" ".join("".join(self._paragraph).split()))
            self._paragraph = None
        elif tag == "article" and self._article_depth:
            self._article_depth -= 1
            self._paragraph = None


def _title_key(title: str) -> tuple[str, ...]:
    return tuple(re.findall(r"\w+", title.casefold()))


def read_public_article(
    title: str, source: str, url: str, *, timeout: float
) -> tuple[str, tuple[str, ...]] | None:
    """Read identifiable public article text from a supported publisher."""
    try:
        if not _article_host(url):
            if source.strip().casefold() != "chequeado":
                return None
            # Resolve a Google News wrapper through the publisher's public search.
            query = " ".join(word for word in _title_key(title) if len(word) >= 5)
            search_url = "https://chequeado.com/?" + urlencode({"s": query})
            candidates = _ArticlePage()
            candidates.feed(_read_page(search_url, timeout))
            url = next(
                (
                    urljoin(search_url, href)
                    for href, label in candidates.links
                    if _title_key(label) == _title_key(title)
                    and _article_host(urljoin(search_url, href)) == "chequeado.com"
                ),
                "",
            )
        if not url:
            return None
        article = _ArticlePage()
        article.feed(_read_page(url, timeout))
    except (OSError, ValueError, LookupError):
        return None
    page_title = article.title.removesuffix(f" - {source}").removesuffix(f" | {source}")
    if _title_key(page_title) != _title_key(title):
        return None
    sentences = (
        sentence
        for paragraph in (*article.paragraphs, article.description)
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph)
        if len(sentence.split()) >= 8 and not re.search(r"https?://", sentence)
    )
    excerpts = []
    remaining_words = 25
    for sentence in dict.fromkeys(sentences):
        words = sentence.split()
        if len(words) <= remaining_words:
            excerpts.append(sentence)
            remaining_words -= len(words)
        if len(excerpts) == 2 or remaining_words < 8:
            break
    if not excerpts and article.description:
        words = article.description.split()
        if len(words) >= 8 and not re.search(r"https?://", article.description):
            excerpts.append(" ".join(words[:25]) + ("…" if len(words) > 25 else ""))
    return (url, tuple(excerpts)) if excerpts else None
