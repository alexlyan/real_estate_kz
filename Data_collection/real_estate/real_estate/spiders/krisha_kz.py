import scrapy
from scrapy import Spider
import re
from datetime import datetime
import time
import re
from scrapy_splash import SplashRequest

class RealEstateKz(Spider):
    
    # Unique name
    name = 'RealEstateKz'

    page_number = 60

    def start_requests(self):
        self.index = 0
        

        web = 'https://krisha.kz/arenda/kvartiry/almaty/?das[rent.period][0]=2'
    
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
        # Binary object. if apartments are checked 1, othrerwise 0
        checked_by = []
                        
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
            z = 0
            # we need z+1 value to get price, where xpath is different from normal
            if index % 2 == 1:
                z = 1
                yield scrapy.Request(link, callback=self.parse_data, 

                cb_kwargs=dict(header = headers[index],
                            price = prices[index+z].strip().replace('\xa0', ''),
                            address = addresses[index].strip() + ', ' + cities[index],
                            owner = owners[index],))
            else:
                yield scrapy.Request(link, callback=self.parse_data, 

                cb_kwargs={"header": headers[index],
                            "price": prices[index].strip().replace('\xa0', ''),
                            "address": addresses[index].strip() + ', ' + cities[index],
                            "owner": owners[index],
                            })
        time.sleep(2)
        
    def parse_data(self, response, header, price, address, owner):
        other_params = {'house_type': None,
                        'area': None, 
                        'condition': None, 
                        'bathroom': None}
        
        # timestampf

        # house type
        house_type = response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[3]/text()').get()

       
        # district
        def get_district(xpath):
            try:
                return xpath.get().split(',')[1].strip()
            except IndexError:
                return None
        
        district = get_district(response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[3]/span/text()'))

        # Area
        area = re.findall('(\d+)', response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[4]/div[3]/text()').get())[0]
        
        # Condition
        condition = response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[5]/div[3]/text()').get() 
        
        # Bathroom
        bathroom = response.xpath('/html/body/main/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[6]/div[3]/text()').get()
        
        # Other params
        params_xpath = response.xpath('/html/body/main/div[2]/div/div[2]/div[2]/div[6]/div[1]/dl')

        for x_path in params_xpath:
            
            key = x_path.xpath('.//dt/text()').get()
            value = x_path.xpath('.//dd/text()').get()
            if key == 'Балкон остеклён':
                other_params['Балкон остеклён'] = value
            elif key == 'Парковка':
                other_params['Парковка'] = value
            elif key == 'Интернет':
                other_params['Интернет'] = value
            elif key == 'Мебель':
                other_params['Мебель'] = value

        if owner == None:
            owner = 'Хозяин'

        time.sleep(3)

        yield {
            'url': response.url,
            'datetime': time.mktime(datetime.now().timetuple()),
            'header': header,
            # parsing monthly renting of flats
            'rent_type': 'квартира',
            'price': price,
            'district': district,
            'address': address,
            'owner' : owner,
            'house_type': house_type,
            'area': area,
            'condition': condition,
            'bathroom': bathroom,
        }


        # multiple pages option

        home_page = 'https://krisha.kz/arenda/kvartiry/almaty/?das[rent.period][0]=2&das[rent.period][1]=3&page={}'

        # If next_page have value
        for page in range(2, RealEstateKz.page_number):
            
            # we use += operator to limit number of pages
            next_page = home_page.format(page)

            yield scrapy.Request(url=next_page, callback=self.get_links)

