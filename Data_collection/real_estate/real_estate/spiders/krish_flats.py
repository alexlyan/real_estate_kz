import scrapy
from scrapy import Spider
import re
from datetime import datetime
import time
import re
from scrapy_splash import SplashRequest

class RealEstateKz(Spider):
    
    # Unique name
    name = 'krisha_flats'

    page_number = 60

    def start_requests(self):
        self.index = 0
        

        web = 'https://krisha.kz/arenda/komnaty/almaty/'
    
        yield SplashRequest(web, callback=self.get_links, args={'wait': 5})
    
    # Get data from cards on page
    def get_links(self, response):
        
        home_page = 'https://krisha.kz{}'

        # links_to_parsedata.append('https://krisha.kz/arenda/kvartiry/almaty/?das[rent.period][0]=2&das[rent.period][1]=3&page=2')
        links = [home_page.format(x) for x in response.xpath('/html/body/main/section[3]/div/section[1]/div/div/a/@href').extract()]

        # Links of cards

        # for x in links:
        #    links_to_parsedata.append(home_page.format(x))

        # Header of card
        headers = response.xpath('/html/body/main/section[3]/div/section[1]/div/div/div/div/div/div/a/text()').getall()

        # Prices
        prices = response.xpath('/html/body/main/section[3]/div/section[1]/div/div/div/div[1]/div[1]/div[2]/text()').getall()

        # Address
        addresses = response.xpath('/html/body/main/section[3]/div/section[1]/div/div/div/div[1]/div[2]/div[1]/div/text()').getall()
        
        # City
        cities = response.xpath('/html/body/main/section[3]/div/section[1]/div/div/div/div[2]/div[2]/div[1]/div[1]/text()').getall()
        
        # Type of ownership
        owners = []
                        
        for index, owner in enumerate(response.xpath('/html/body/main/section[3]/div/section[1]/div/div/div/div[2]/div[1]')):
            checked_pro = owner.xpath('./@class').extract_first()
            try:
                if checked_pro == 'a-card__owner user-title-not-pro':
                    owner = owner.xpath('./text()').get().strip()
                    owners.append(owner)

                elif checked_pro == 'a-card__owner user-title-pro':
                    owner = owner.xpath('./a[2]/text()').get().strip()
                    owners.append(owner)

            except AttributeError:
                owner = owner.xpath('./a/text()').get()
                owners.append(owner)


        for index, link in enumerate(links):
            # we need index+1 value to get price, where xpath is different from normal

            yield scrapy.Request(link, callback=self.parse_data, 

            cb_kwargs=dict(header = headers[index],
                        address = addresses[index].strip() + ', ' + cities[index],
                        owner = owners[index]))

        time.sleep(2)
        
    def parse_data(self, response, header, address, owner):
        other_params = {'district': None,
                        'этаж': None,
                        'area': None, 
                        'condition': None, 
                        'bathroom': None,
                        'accommodations': None}
        
       
        # district
        def get_district(xpath):
            try:
                return xpath.get().split(',')[1].strip()
            except IndexError:
                return None
        
        district = get_district(response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]/span/text()'))

        price = response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/text()').get().strip().replace('\xa0', '')

        # Other params
        params_xpath = response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div')

        for x_path in params_xpath:
            
            key = x_path.xpath('./div[1]/text()').get()
            value = x_path.xpath('./div[3]/text()').get() 
            if key == 'Мебель':
                other_params['accommodations'] = value
            elif key == 'Этаж':
                other_params['этаж'] = value
            elif key == 'Площадь':
                other_params['area'] = value


        # if Owner is empty
        if owner == None:
            owner = 'Хозяин'

        time.sleep(3)

        yield {
            'url': response.url,
            'datetime': time.mktime(datetime.now().timetuple()),
            'header': header,
            'rent_type': 'комната',
            'price': price,
            'district': district,
            'floor': other_params['этаж'],
            'address': address,
            'owner' : owner,
            'house_type': None,
            'area': other_params['area'],
            'condition': None,
            'bathroom': None,
            'accommodations': other_params['accommodations'],
        }


        # multiple pages option

        home_page = 'https://krisha.kz/arenda/komnaty/almaty/?page={}'

        # If next_page have value
        for page in range(2, RealEstateKz.page_number):
            
            # we use += operator to limit number of pages
            next_page = home_page.format(page)

            yield scrapy.Request(url=next_page, callback=self.get_links)

