import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from wiki_game_data.items import GameItem
from wiki_game_data.utilities import get_text, clean_data, clean_publisher, clean, clean_merge, clean_release_date, format_dates

class WikiGameSpider(CrawlSpider):
    name = 'Games_Scraper'
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 1000,
    }
    allowed_domains = ['wikipedia.org']
    start_urls = [
        'https://en.wikipedia.org/wiki/Category:Articles_using_Infobox_video_game_using_locally_defined_parameters'
    ]
    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//*[@id="mw-pages"]/a[2]', )), callback='parse_start_url', follow=True), )

    def parse_start_url(self, response):
        for link in response.xpath('//*[@id="mw-pages"]/div/div//div/ul/li'):
            item = GameItem()
            mainPageUrl = 'https://en.wikipedia.org'+str(link.xpath('a/@href').extract()[0])
            request = scrapy.Request(mainPageUrl, callback=self.parseGameDetails)
            request.meta['item'] = item
            yield request

    def parseGameDetails(self, response):
        item = response.meta['item']
        item = self.getGameInfo(item, response)
        return item

    def getGameInfo(self, item, response):
        # Obtención de las rutas a los datos necesarios
        table = response.xpath('//table[@class="infobox hproduct"]')
        name = response.xpath('//*[@id="firstHeading"]//text()')
        image = table.xpath('.//a[@class="image"]/@href').extract_first()
        publisher = table.xpath('.//a[@title="Video game publisher"]')
        developer = table.xpath('.//a[@title="Video game developer"]')
        artist = table.xpath('.//a[@title="Video game artist"]')
        composer = table.xpath('.//a[@title="Video game music"]')
        platform = table.xpath('.//a[@title="Computing platform"]')
        genre = table.xpath('.//a[@title="Video game genre"]')
        mode = table.xpath('.//th[contains(text(), "Mode")]')
        release_date = table.xpath('.//th[contains(text(), "Release")]').xpath('following-sibling::*')
        # Listas auxiliares
        data = [name, image, publisher, developer, artist, composer, platform, genre, mode, release_date]
        keys = ['Nombre', 'Img_URL', 'Distribuidoras', 'Desarrolladores', 'Artistas', 'Compositores', 'Plataformas', 'Generos', 'Modos', 'Lanzamiento']
        no_value = ["N/A"]

        # Función de obtención de datos
        def get_data(arg):
            if arg == name:
                raw_data = [name.extract_first()]
            elif arg == image:
                raw_data = ['https://en.wikipedia.org' + str(image)]
            elif arg == publisher:
                raw_data = get_text(publisher)
            elif arg == developer:
                raw_data = get_text(developer)
            elif arg == artist:
                raw_data = get_text(artist)
            elif arg == composer:
                raw_data = get_text(composer)
            elif arg == platform:
                raw_data = get_text(platform)
            elif arg == genre:
                raw_data = get_text(genre)
            elif arg == mode:
                raw_data = mode.xpath('following-sibling::*').xpath('.//text()').extract()
            elif arg == release_date:
                raw_data = release_date
            return raw_data

        def get_release_date(date):
            if date.xpath('.//b'):
                platforms = release_date.xpath('.//b').xpath('.//text()').extract()
                plainlists = release_date.xpath('.//div[@class="plainlist"]')
                region_date = []
                for p in plainlists:
                    if p.xpath('.//abbr'):
                        regions = p.xpath('.//abbr').xpath('.//text()').extract()
                    else:
                        regions = p.xpath('.//a[contains(@href, "/wiki")]').xpath('.//text()').extract()
                    data = p.xpath('.//li').xpath('.//text()').extract()
                    index = []
                    for i in data:
                        if re.search(r'[0-9]{4}', i):
                            n = data.index(i)
                            index.append(n)
                        else:
                            continue
                    ind = list(map(int, index))
                    dates = []
                    for i in ind:
                        dates.append(data[i])
                    try:
                        fixed_dates = format_dates(dates)
                        merged_dates = dict(zip(regions, fixed_dates))
                        region_date.append(merged_dates)
                    except:
                        merged_dates = dict(zip(regions, dates))
                        region_date.append(merged_dates)
                release_dates = dict(zip(platforms, region_date))
                return release_dates
            elif date.xpath('.//div[@class="plainlist"]'):
                plainlists = release_date.xpath('.//div[@class="plainlist"]')
                if plainlists.xpath('.//abbr'):
                    regions = plainlists.xpath('.//abbr').xpath('.//text()').extract()
                else:
                    regions = plainlists.xpath('.//a[contains(@href, "/wiki")]').xpath('.//text()').extract()
                data = plainlists.xpath('.//li').xpath('.//text()').extract()
                index = []
                for i in data:
                    if re.search(r'[0-9]{4}', i):
                        n = data.index(i)
                        index.append(n)
                    else:
                        continue
                ind = list(map(int, index))
                dates = []
                for i in ind:
                    dates.append(data[i])
                try:
                    fixed_dates = format_dates(dates)
                    merged_dates = dict(zip(regions, fixed_dates))
                except:
                    merged_dates = dict(zip(regions, dates))
                return merged_dates
            elif date.xpath('.//a'):
                date_list = release_date.xpath('.//text()').extract()
                joined = ''.join(date_list)
                text = re.findall('\(.*?\)', joined)
                clean_text = []
                for t in text:
                    ct = t.strip('()')
                    clean_text.append(ct)
                joined_dates = re.sub(r"[\(\[].*?[\)\]]", ",", joined)
                splt_dates = joined_dates.split(",")
                splt_dates = [x for x in splt_dates if x]
                try:
                    fixed_dates = format_dates(splt_dates)
                    merged_dates = dict(zip(clean_text, fixed_dates))
                    return merged_dates
                except:
                    return no_value
            elif date.xpath('.//br'):
                date_list = date.xpath('.//text()').extract()
                joined = ''.join(date_list)
                if "(" in joined:
                    text = []
                    for d in date_list:
                        t = d[d.find("(") + 1:d.find(")")]
                        text.append(t)
                    dates = []
                    for d in date_list:
                        date = re.sub(r" ?\([^)]+\)", "", d)
                        dates.append(date)
                    try:
                        fixed_dates = format_dates(dates)
                        merged_dates = dict(zip(text, fixed_dates))
                    except:
                        merged_dates = dict(zip(text, dates))
                    return merged_dates
                elif ":" in joined:
                    dates = []
                    text = []
                    for d in date_list:
                        splitted = d.split(":")
                        dates.append(splitted[0])
                        text.append(splitted[1])
                    try:
                        fixed_dates = format_dates(dates)
                        merged_dates = dict(zip(text, fixed_dates))
                        return merged_dates
                    except:
                        return no_value
                else:
                    try:
                        fixed_dates = format_dates(date_list)
                        return fixed_dates
                    except:
                        return no_value
            else:
                date_list = date.xpath('.//text()').extract()
                try:
                    fixed_dates = format_dates(date_list)
                    return fixed_dates
                except:
                    return date_list

        for d in range(len(data)):
            if data[d]:
                if d == 1:
                    info = get_data(data[d])
                    if info:
                        item[keys[d]] = info
                    else:
                        item[keys[d]] = no_value
                elif d == 2:
                    info = clean_publisher(get_data(data[d]))
                    if info:
                        item[keys[d]] = info
                    else:
                        item[keys[d]] = no_value
                elif d == 9:
                    info = get_release_date(get_data(data[d]))
                    if info:
                        item[keys[d]] = info
                    else:
                        item[keys[d]] = no_value
                else:
                    info = clean_data(get_data(data[d]))
                    if info:
                        item[keys[d]] = info
                    else:
                        item[keys[d]] = no_value
            else:
                item[keys[d]] = no_value
        return item