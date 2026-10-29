"""wfx-firecrawl: Firecrawl bundle.

Distribution unit ``wfx-firecrawl``.  At runtime Primeagent's loader
discovers ``extension.json`` shipped alongside this ``__init__.py`` and
registers the bundle's components under the namespaced IDs
``ext:firecrawl:<Class>@official``.
"""

from wfx_firecrawl.components.firecrawl.firecrawl_crawl_api import FirecrawlCrawlApi
from wfx_firecrawl.components.firecrawl.firecrawl_map_api import FirecrawlMapApi
from wfx_firecrawl.components.firecrawl.firecrawl_scrape_api import FirecrawlScrapeApi
from wfx_firecrawl.components.firecrawl.firecrawl_search_api import FirecrawlSearchApi

__all__ = ["FirecrawlCrawlApi", "FirecrawlMapApi", "FirecrawlScrapeApi", "FirecrawlSearchApi"]
