# ~/projects/beer-pred/venv/bin/ python
import scrapy
import sqlalchemy
import sqlcmds

conn = sqlcmds.create_connection("beers.sqlite3")

sql_create_beers_table = """CREATE TABLE IF NOT EXISTS Beers (
                                brewery varchar,
                                name varchar,
                                style varchar, 
                                abv float(3,2), 
                                ratings int(7), 
                                score float(3,2) 
                            );"""

if conn is not None:
    # Create team table
    sqlcmds.create_table(conn, sql_create_beers_table)
    print("created table")
else:
    print("Error! Cannot create database connection")


def create_beer(conn, beer_info):
    """
    Create a new beer into the beers table if it doesn't exist
    :param conn: Connection object
    :param beer_info: tuple of beer information
    :return: None  
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM Beers WHERE brewery = (?) and name = (?)",
        [beer_info[0], beer_info[1]],
    )
    if cur.fetchone() is None:
        sql = """INSERT INTO Beers(brewery, name, style, abv, ratings, score) VALUES(?,?,?,?,?,?)"""
        cur.execute(sql, beer_info)
        conn.commit()
    else:
        print("Beer", beer_info[1], "in database")
        return


class BeerSpider(scrapy.Spider):
    name = "beer_getter"
    download_delay = 1.0
    autothrottled_enabled = True

    def start_requests(self):
        # 55537 is id for the last webpage for a new place
        urls = [
            "https://www.beeradvocate.com/beer/profile/"
            + str(i)
            + "/?view=beers&show=all"
            for i in range(55538)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if "Brewery" not in response.xpath('//div[@id="info_box"]/text()').getall()[4]:
            print("Not a brewery")
            return None

        brewery = response.xpath('//div[@class="titleBar"]/h1/text()').get()

        beer_names = response.xpath("//tr/td[1]/a/b/text()").getall()
        beer_styles = response.xpath("//tr/td[2]/a/text()").getall()
        beer_abvs = response.xpath("//tr/td[3]/span/text()").getall()
        beer_ratings = response.xpath("//tr/td[4]/b/text()").getall()
        beer_scores = response.xpath("//tr/td[5]/b/text()").getall()

        # Strip beer ratings of commas for SQLite
        beer_ratings = [int(rating.replace(",", "")) for rating in beer_ratings]

        # Convert "?" abvs to None, so SQLite will read as Null
        beer_abvs = [None if abv == "?" else abv for abv in beer_abvs]

        if len(beer_names) == 0:
            print("Brewery", brewery, "has no beers")
        else:
            for i in range(len(beer_names)):
                create_beer(
                    conn,
                    (
                        brewery,
                        beer_names[i],
                        beer_styles[i],
                        beer_abvs[i],
                        beer_ratings[i],
                        beer_scores[i],
                    ),
                )
