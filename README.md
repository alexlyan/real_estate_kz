Predictions of apartment prices
===============================

This is project to predict monthly renting prices of apartments in Almaty, Kazakhstan.

### Objectives:
1. To find out what apartments are worth renting
2. Prediction of renting price of apartments 

Notebook of renting price prediction [kz_analysis.ipynb](/kz_analysis.ipynb) was writter in readable form to share knowledge.

In README, you will find only explanation to data collection, other stages are explained in notebook.

## Data Collection:

- Notes before scrapping
- The process will take 3.47 hours to scrape 130 pages, in total you will get 2488 items

In order to repeat scrapping of data, you should:

1. Clone repository into your local directory
2. Create virtual environment (optional, but preferable) and install scrapy
```
# In order to create virtual environment input command in terminal
python3 -m venv <directory>

# In order to activate virtual environment input command
source <directory>/bin/activate
```
  ```
  # Input in terminal 
  pip install scrapy
  ```
3. In terminal move to "Data_Collection/real_estate"
```
# Input command
scrapy crawl <spidername> -o <outputname>.<format>
scrapy crawl RealEstateKz -o  <name_of_file>.json
```

4. Process of scrapping is explained in [scrapper file](/Data_collection/real_estate/real_estate/spiders/krisha_kz.py)
