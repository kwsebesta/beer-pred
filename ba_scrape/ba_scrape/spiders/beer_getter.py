# -*- coding: utf-8 -*-
import scrapy


class BeerSpider(scrapy.Spider):
    name = "beer_getter"
    download_delay = 1.0
    # allowed_domains = ["https://www.beeradvocate.com/beer/profile/1/"]
    # start_urls = ["www.beeradvocate.com/beer/profile/1//"]

    def start_requests(self):
        urls = ["https://www.beeradvocate.com/beer/profile/1/?view=beers&show=all"]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        beer_names = response.xpath("//tr[1]/td[1]/a/b/text()").getall()
        beer_styles = response.xpath("//tr[1]/td[2]/a/text()").getall()
        beer_abv = response.xpath("//tr[1]/td[3]/span/text()").getall()
        beer_ratings = response.xpath("//tr[1]/td[4]/b/text()").getall()
        beer_score = response.xpath("//tr[1]/td[5]/b/text()").getall()
        print(beer_names, beer_styles, beer_abv, beer_ratings, beer_score)
        # filename = "beer_response.html"
        # with open(filename, "wb") as f:
        # All we'll do is save the whole response as a huge text file.
        # f.write(response.body)
        # self.log("Saved file %s" % filename)
