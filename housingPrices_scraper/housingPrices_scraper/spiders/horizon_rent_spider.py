import scrapy

class HorizonSpider(scrapy.Spider):
    name = "horizon"
    allowed_domains = ["thehorizonproperties.com"]

    # Start from page 1
    base_url = "https://thehorizonproperties.com/status/for-rent/page/{}/"
    current_page = 1
    max_pages = 50  # You can change this to crawl more/less

    start_urls = [base_url.format(current_page)]

    def parse(self, response):

        # Scrape all properties on the page
        for prop in response.css("h2.item-title a::attr(href)").getall():
            yield response.follow(prop, callback=self.parse_property)

        # Move to the next page automatically
        if self.current_page < self.max_pages:
            self.current_page += 1
            next_page_url = self.base_url.format(self.current_page)
            self.logger.info(f"Going to next page: {next_page_url}")
            yield response.follow(next_page_url, callback=self.parse)

    def parse_property(self, response):
        # Extract title
        title = response.css("div.page-title h1::text").get()
        if title:
            title = title.strip()
        else:
            title = ""

        # Key normalization mapping
        key_map = {
            "Property Type": "Property Type",
            "Property Status": "Property Status",
            "Bedroom": "Bedrooms",
            "Bedrooms": "Bedrooms",
            "Room": "Rooms",
            "Rooms": "Rooms",
            "Bathroom": "Bathrooms",
            "Bathrooms": "Bathrooms",
            "Garage": "Garage",
            "sqft": "Property Size",
            "Year Built": "Year Built",
            "Property ID": "Property ID",
            "Price": "Price",
            "Land Area": "Land Area",
        }

        # Extract details list
        details = {}
        for li in response.css("div.detail-wrap li"):
            key = li.css("strong::text").get()
            value = li.css("span::text").get()
            if key and value:
                norm_key = key_map.get(key.replace(":", "").strip(), key.replace(":", "").strip())
                details[norm_key] = value.strip()

        # Add title + URL
        details["Title"] = title
        details["URL"] = response.url

        yield details

