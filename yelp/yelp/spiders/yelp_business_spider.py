import scrapy
from scrapy.contracts import Contract
from scrapy_selenium import SeleniumRequest


class YelpBusinessSpider(scrapy.Spider):
    name = 'yelp.com'
    url = "https://www.yelp.com/biz/fog-harbor-fish-house-san-francisco-2"

    parsed_fields = [
        {
            'field_name': 'name',
            'xpath': '//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div/div[1]/'
                     'h1/text()'
        },
        {
            'field_name': 'first_image',
            'xpath': '//*[@id="wrap"]/div[3]/div/div[3]/div[1]/div[1]/div[1]/a/img/@src'
        },
        {
            'field_name': 'phone',
            'xpath': '//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/section[2]/div'
                     '/div[2]/div/div[2]/p[2]/text()'
        },
        {
            'field_name': 'rating',
            'xpath': '//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div/div[2]'
                     '/div[1]/span/div/@aria-label'
        },
        {
            'field_name': 'reviews',
            'xpath': '//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div/div[2]'
                     '/div[2]/p/text()'
        },
        {
            'field_name': 'web_site',
            'xpath': '//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/section[2]/div'
                     '/div[1]/div/div[2]/p[2]/a/text()'
        }
    ]

    result = {}

    def start_requests(self):
        return [SeleniumRequest(url=self.url, callback=self.parse)]

    def parse(self, response, **kwargs):
        """
        @with_selenium
        """

        self.result['direct_link'] = self.url
        self.result['business_id'] = self.url.split('/')[-1]

        for field in self.parsed_fields:
            self.get_item(response, field['field_name'], field['xpath'])

        self.address(response)
        self.category_list(response)
        self.time_tible(response)

        return self.result

    def get_item(self, response, item, xpath):
        try:
            response_to_xpath = response.selector.xpath(xpath)
            self.result[item] = response_to_xpath.get()
        except Exception as e:
            self.log(item + ' ' + str(e))

    def address(self, response):
        address = []

        try:
            address_list = response.xpath('//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/'
                                          'section[4]/div[2]/div[1]/div/div/div/div[1]/address')

            for address_line in address_list.xpath('.//p'):
                address.append(address_line.xpath('.//text()').get())

            self.result['address'] = address

        except Exception as e:
            self.log('Address error' + str(e))

    def category_list(self, response):
        categories = []

        try:
            category_list = response.xpath('//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/'
                                           'div[1]/div/div/span[2]')

            for category in category_list.xpath('.//a'):
                categories.append(category.xpath('.//text()').get())

            self.result['categories'] = categories

        except Exception as e:
            self.log('Category error' + str(e))

    def time_tible(self, response):
        time_table = {}

        try:
            table = response.xpath('//*[@id="wrap"]/div[3]/div/div[4]/div/div/div[2]/div/div/div[1]/div/div[1]/'
                                   'section[4]/div[2]/div[2]/div/div/table/tbody')

            for time_table_item in table.xpath('.//tr'):
                date = time_table_item.xpath('.//th/p/text()').get()
                time = time_table_item.xpath('.//td/ul/li/p/text()').get()
                time_table[date] = time

            self.result['time_table'] = time_table

        except Exception as e:
            self.log('Time table error' + str(e))


class WithSelenium(Contract):
    """ Contract to set the request class to be SeleniumRequest for the current call back method to test
    @with_selenium
    """
    name = 'with_selenium'
    request_cls = SeleniumRequest
