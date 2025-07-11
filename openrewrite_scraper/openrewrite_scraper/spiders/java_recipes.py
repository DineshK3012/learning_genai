import scrapy
from urllib.parse import urljoin
import re

class JavaRecipesSpider(scrapy.Spider):
    name = "java_recipes"
    allowed_domains = ["docs.openrewrite.org"]
    start_urls = ["https://docs.openrewrite.org/recipes/java"]
    visited = set()

    def parse(self, response):
        if response.url in self.visited:
            return
        self.visited.add(response.url)

        title = response.css("h1::text, h2::text").get()
        content_list = response.css("main *::text").getall()
        content_raw = " ".join(content_list).strip()

        # Remove unwanted sections
        cleaned_content = self.clean_content(content_raw)

        yield {
            "url": response.url,
            "title": title,
            "content": cleaned_content,
        }

        for href in response.css("a::attr(href)").getall():
            full_url = urljoin(response.url, href)
            if (
                "recipes/java" in full_url
                and full_url.startswith("https://docs.openrewrite.org/recipes/java")
                and full_url not in self.visited
            ):
                yield response.follow(full_url, self.parse)

    def clean_content(self, text):
        # Remove Contributors and everything after
        text = re.split(r"Contributors\s+", text)[0]

        # Remove Data Tables section if present
        text = re.sub(r"Data Tables\s+.*?(?=Recipe source|Usage|Options|$)", "", text, flags=re.DOTALL)

        # Remove navigation hints
        text = re.sub(r"(Previous\s+.+?\s+Next\s+.+?)", "", text)

        # Optional: Remove recipe stats
        text = re.sub(r"Recipe performance\s+.*", "", text, flags=re.DOTALL)

        # Clean up whitespace
        text = re.sub(r"\s{2,}", " ", text)

        return text.strip()
