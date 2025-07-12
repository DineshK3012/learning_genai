import scrapy
from urllib.parse import urljoin
import re

class OpenRewriteAuthoringRecipesSpider(scrapy.Spider):
    name = "authoring_recipes"
    allowed_domains = ["docs.openrewrite.org"]
    start_urls = ["https://docs.openrewrite.org/authoring-recipes"]

    visited = set()

    def parse(self, response):
        for href in response.css("a::attr(href)").getall():
            full_url = urljoin(response.url, href)

            if (
                full_url.startswith("https://docs.openrewrite.org/authoring-recipes")
                and full_url not in self.visited
            ):
                self.visited.add(full_url)
                yield response.follow(full_url, self.parse_page)

    def parse_page(self, response):
        title = response.css("h1::text, h2::text").get()
        if not title or self.should_skip_title(title):
            return

        elements = response.css("main p, main li, main pre, main code")
        content_lines = []

        for el in elements:
            tag = el.root.tag
            if tag in ['pre', 'code']:
                cleaned = re.sub(r"<.*?>", "", el.get()).strip()
                if cleaned:
                    content_lines.append(f"```\n{cleaned}\n```")
            else:
                text = el.css("::text").get()
                if text:
                    content_lines.append(text.strip())

        content = "\n".join([line for line in content_lines if line])
        content = self.clean_content(content)

        if len(content) < 100:
            return

        yield {
            "url": response.url,
            "title": title.strip(),
            "content": content.strip()
        }

    def should_skip_title(self, title):
        title = title.lower().strip()
        return any(kw in title for kw in [
            "edit this page", "contributors", "next", "previous", "license"
        ])

    def clean_content(self, text):
        removal_patterns = [
            r"Run this recipe on OSS repos.*",
            r"The community edition of the Moderne platform.*",
            r"Please\s+contact Moderne.*",
            r"Edit this page.*",
            r"Contributors.*",
            r"This page is licensed under.*",
            r"© .* OpenRewrite.*",
            r"Next steps:.*",
            r"To learn more.*",
            r"Run this recipe here.*"
        ]
        for pattern in removal_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'\n{2,}', '\n', text)
        return text.strip()
