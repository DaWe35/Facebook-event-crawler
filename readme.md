# Facebook event crawler

While facebook removed his events API, retrieving data became difficult. This library is crawling Facebook, and parsing all data from the UI. Sometimes that fails, so you need to be fault tolerant :)

![Picture about the database](https://github.com/DaWe35/Facebook-event-crawler/raw/master/database.jpg "Facebook event crawler events table")

### Install:

1) Create a new non-used facebook account
2) Change the language to English/US! (That's important!) (https://www.facebook.com/settings?tab=language)
3) Create a new mysql database
4) Import the database.sql file
5) Add some page ids to the pages database table (the page id is on the link, for example facebook.com/PageId)

### Config:

1) Copy CONFIG_DEFAULT.py to CONFIG.py ```cp CONFIG_DEFAULT.py CONFIG.py```
2) Fill the empty fields below
3) Run! All records will be inserted to the 'events' table!

### Setup geocode (optional):

If you need latitude and longitude codes for event places, use my [Geo Cache](https://github.com/DaWe35/Geo-cache) library.
This library is included as a submodule, so you just need to pull it [(more)](https://stackoverflow.com/questions/1030169/easy-way-to-pull-latest-of-all-git-submodules):
```
cd Facebook-event-crawler
git submodule update --init --recursive
```
1) Setup the local or remote server
2) Setup Geo-cache/CONFIG.php
2) Edit Facebook-event-crawler/CONFIG.py

Enjoy!

### Development

Want to contribute? Great!
Please test a lot, before sending your pull request :)

### Alternatives

This crawler is not too universal, so if you need to crawl anything else, I would recommend these:

| Crawler                                        | No coding required | Login feature | Open source & self hosted |
|------------------------------------------------|--------------------|---------------|---------------------------|
| [Scrapy](https://scrapy\.org)                  |                    | ✓             | ✓                         |
| [ParseHub](https://www\.parsehub\.com)         | ✓                  | ✓             |                           |
| [Simple Scaper](https://simplescraper\.io)     | ✓                  | ?             |                           |
