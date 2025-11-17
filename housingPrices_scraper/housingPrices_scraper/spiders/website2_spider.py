import scrapy

class SakilaHomesSpider(scrapy.Spider):
    name = "sakila"
    allowed_domains = ["sakilahomes.com"]

    # Start from page 1
    base_url = "https://sakilahomes.com/index.php?page={}"
    current_page = 1
    max_pages = 60  # adjust as needed
    start_urls = [base_url.format(current_page)]

    def parse(self, response):
        # Follow each property link
        for prop in response.css("h3.title a::attr(href)").getall():
            yield response.follow(prop, callback=self.parse_property)

        # Go to next page
        if self.current_page < self.max_pages:
            self.current_page += 1
            next_page_url = self.base_url.format(self.current_page)
            self.logger.info(f"Going to next page: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)

    def parse_property(self, response):
        # Extract title
        title = response.css("h3.title a::text").get(default="").strip()

        # Extract the info you care about
        details = {

            "Type": response.css("div.info_wrapper > div:contains('Type')::text").get(default="").replace("Type:", "").strip(),
            "Price": response.css("div.info_wrapper > div:contains('Price')::text").get(default="").replace("Price:", "").strip(),
            "Bedrooms": response.css("div.info_wrapper > div:contains('Bedrooms')::text").get(default="").replace("Bedrooms:", "").strip(),
            "Location": response.css("div.info_wrapper > div:contains('Location')::text").get(default="").replace("Location:", "").strip(),
            "Area": response.css("div.info_wrapper > div:contains('Area')::text").get(default="").replace("Area:", "").strip(),
            "URL": response.url,
        }

        yield details
