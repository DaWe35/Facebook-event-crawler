import datetime
import webbrowser
from time import sleep
from requests import Session
from robobrowser import RoboBrowser
from lxml import html
from urllib import parse
import pymysql.cursors
import timestring
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
import os.path
import CONFIG

""" headers = {'user-agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'}
proxies = {'https': 'https://88.209.225.150:53281', 'http': 'http://88.209.225.150:53281'} """
file = 'del.html';

session = Session()
useragent = 'Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID_) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
browser = RoboBrowser(user_agent=useragent, session=session, parser='html.parser',)


# _____FUNCTIONS_______

def convert_si_to_number(x):
    total_stars = 0
    if 'K' in x:
        if len(x) > 1:
            total_stars = float(x.replace('K', '')) * 1000  # convert k to a thousand
    elif 'k' in x:
        if len(x) > 1:
            total_stars = float(x.replace('k', '')) * 1000  # convert k to a thousand
    elif 'M' in x:
        if len(x) > 1:
            total_stars = float(x.replace('M', '')) * 1000000  # convert M to a million
    elif 'B' in x:
        total_stars = float(x.replace('B', '')) * 1000000000  # convert B to a Billion
    else:  # Less than 1000
        try:
            total_stars = int(x)
        except ValueError:  # Catch failture
            pexit('Error: convert_si_to_number('+str(x)+')')
    return int(total_stars)

def login():
    print('Logging in to facebook...')
    browser.open("https://facebook.com") # Facebook profile's language need to be EN-US!
    login_form = browser.get_form(id='login_form')
    login_form['email'].value = CONFIG.FB_EMAIL
    login_form['pass'].value = CONFIG.FB_PASSWORD
    browser.submit_form(login_form)
    if ('<form action="https://m.facebook.com/login' in browser.parsed.encode().decode("utf-8")):
        pexit('Login failed')

    '''with open(file, "w", encoding="utf-8") as text_file:
        print(browser.parsed, file=text_file)
    print('Opening browser...')
    webbrowser.open_new_tab(file)'''

def pexit(printit=''):
    print(printit)
    with open(file, "w", encoding="utf-8") as text_file:
        print(browser.parsed.encode(), file=text_file)
    print('\x1b[7;31;40m' + 'Error, writing del.html...' + '\x1b[0m')
    webbrowser.open_new_tab(file)
    exit(0)

inserted_count = 0
def getevent(eventid):
    global inserted_count
    try:
        print('\x1b[6;33;40m' + 'Getting event: ' + str(eventid) + '\x1b[0m', end="")
        eventurl = "https://mobile.facebook.com/events/"+eventid
        browser.open(eventurl)

        tree = html.fromstring(browser.parsed.encode())

        '''with open(file, "w", encoding="utf-8") as text_file:
            print(browser.parsed.encode(), file=text_file)
        print('Opening browser...')
        webbrowser.open_new_tab(file)
        sleep(1)'''

        event_description = get_description(tree)
        event_ago_location = get_event_ago(tree)
        event_going_number = get_going(tree)
        event_title = get_title(tree)
        event_date_place = get_date_place(tree)
        event_photo = get_photo(tree)

        '''with open(file, "w", encoding="utf-8") as text_file:
            print(browser.parsed.encode(), file=text_file)
        print('Opening browser...')
        webbrowser.open_new_tab(file)'''

        if " dates left" in event_date_place[0]:
            print(' - \033[1;31;0mError while getting date:\033[1;0;0m')
            print(event_date_place)
            dateto = None
            datefrom = None
        else:
            splitted = event_date_place[0].split(' – ', 1)
            if len(splitted) < 2:
                splitted = event_date_place[0].split(' - ', 1) # – - not equal!!!
            if len(splitted) < 2:
                print(' - \033[1;31;0mError while splitting date: \033[1;0;0m' + event_date_place[0])
                dateto = None
                datefrom = None
            else:
                datefrom = timestring.Date(splitted[0]).date
                dateto = timestring.Date(splitted[0][:-4] + splitted[1]).date

        '''datefrom = "2018-01-01 01:01:01"
        dateto = "2018-01-01 01:01:01"'''


        lines = ''
        for line in event_description:
            lines += line + '<br>'
        if (len(event_ago_location) == 2):
            event_ago = event_ago_location[0]
            event_location = event_ago_location[1]
        elif(len(event_ago_location) == 1):
            print(' - event_ago is NULL', end='')
            event_ago = None
            event_location = event_ago_location[0]
        else:
            event_ago = None
            event_location = None
            print(' - get_event_ago() --> event_ago_location lenght is '+str(len(event_ago_location)), end='')

        if len(event_date_place) != 1:
            if len(event_date_place) == 2:
                event_place = [event_date_place[1]]
            else:
                with open(file, "w", encoding="utf-8") as text_file:
                    print(browser.parsed.encode(), file=text_file)
                print('Opening browser...')
                webbrowser.open_new_tab(file)
                pexit('event_date_place lenght is not 1: '+str(event_date_place))


        # Create a new record
        now = datetime.datetime.now()
        event_date = event_date_place[0]
        event_place = event_date_place[1]
        event_going = event_going_number[0]
        event_interested = event_going_number[1]
        lat = '0' # initialize variables
        lon = '0'

        if CONFIG.GEOCACHE_HOST != '':
            if event_location != None:  # Get event location geocode
                logging.info('\n' + CONFIG.GEOCACHE_HOST + '?address='+event_location + '\n')
                response = requests.get(CONFIG.GEOCACHE_HOST + '?address='+event_location, auth=HTTPBasicAuth(CONFIG.GEO_USER, CONFIG.GEO_PASS))
                if response.status_code == 200:
                    jsondata = json.loads(response.content.decode('utf-8'))
                    lon = jsondata['lon']
                    lat = jsondata['lat']
                else:
                    logging.warning(' - gps coord response #1 status == ' + str(response.status_code) + ' - ', end='')
            if event_location == None or lat == '0.000000' or lat == 'null':    # Geocode failed with event_location, try event_place
                event_ago = event_location
                event_location = None
                response = requests.get(CONFIG.GEOCACHE_HOST + '?address='+event_place+', Magyarország', auth=HTTPBasicAuth(CONFIG.GEO_USER, CONFIG.GEO_PASS))
                if response.status_code == 200:
                    jsondata = json.loads(response.content.decode('utf-8'))
                    lon = jsondata['lon']
                    lat = jsondata['lat']
                else:
                    logging.warning(' - gps coord is 0: '+event_place)
                    logging.warning(' - gps coord response #2 status == '+ str(response.status_code) + ' - ', end='')
        else:
            logging.info('GEOCACHE_HOST is not defined in CONFIG.py, skipping geocoding')


        with connection.cursor() as cursor:
            # print(eventid, lines, event_date[0], datefrom, dateto, event_place[0], event_ago, event_location, event_going_number[0], event_going_number[1], '0', '34.123', now)
            sql = "INSERT INTO events (`id`, `page`, `title`, `description`, `date`, `datefrom`, `dateto`, `place`, `ago`, `location`, `going`, `intrested`, `photo`, `lat`, `lon`, `lastupdate`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `title`=%s,`page`=%s,`description`=%s,`date`=%s,`datefrom`=%s,`dateto`=%s,`place`=%s,`ago`=%s,`location`=%s,`going`=%s,`intrested`=%s,`photo`=%s,`lat`=%s,`lon`=%s,`lastupdate`=%s;"
            cursor.execute(sql, (eventid, pageid, event_title, lines, event_date, datefrom, dateto, event_place, event_ago, event_location, event_going, event_interested, event_photo, lat, lon, now, event_title, pageid, lines, event_date, datefrom, dateto, event_place, event_ago, event_location, event_going, event_interested, event_photo, lat, lon, now))

        connection.commit()
        inserted_count += 0
        print('')
        
    except Exception as e: # Catch failture
        print('\nGetevent error')
        logging.exception("message")
        pexit()


def get_date_place(tree):
    event_date_place = tree.xpath('//div[@id="event_summary"]/div/div/table/tbody/tr/td[2]/dt/div/text()')  # [0] == date (Friday, November 16, 2018 at 8 PM – 11:55 PM)   [1] == place (Expresszó)
    if (len(event_date_place) == 0):
        pexit('get_date() error. len(event_date_place) == 0')
    if (len(event_date_place) == 1):
        event_date_place = (event_date_place[0], 'NULL')
        print('event_place is NULL')
    return event_date_place



def get_event_ago(tree):
    event_ago_temp = tree.xpath('//div[@id="event_summary"]/div/div/table/tbody/tr/td[2]/dd/div/text()') # [0] == ago (3 days ago)   [1] == location (Brusznyai út 2., Veszprém, 8200)
    if (len(event_ago_temp) == 3):
        event_ago = [event_ago_temp[0]+event_ago_temp[1],event_ago_temp[2]]
    else:
        event_ago = event_ago_temp
    if (len(event_ago) == 0):
        print(' - get_event_ago() == 0')
    return event_ago

def get_going(tree):
    str = tree.xpath('//div[@id="unit_id_703958566405594"]/div/a/div/text()')  # [0] == going (234)        [1] == intrested (2.1K)
    if (len(str) == 0):
        str = tree.xpath('//div[@id="unit_id_703958566405594"]/div/div/div[2]/a/text()')
    if (len(str) == 0):
        print(' - get_going() --> len(str) == 0', end='')
        event_going_number = ['0', '0']
    else:
        try:
            if (str[0] != 'Details') & (str[0] != ''):
                splitted = str[0].split(' ')
            elif (str[1] != 'Details') & (str[1] != ''):
                splitted = str[1].split(' ')
            else:
                splitted = str[2].split(' ')

            if len(splitted) == 1:
                if len(str) == 1:
                    going_str = '0'
                    interest_str = str[0]
                else:
                    going_str = str[0]
                    interest_str = str[1]
            elif len(splitted) < 3:
                print('str: ')
                print(str)
                print(len(splitted))
                pexit('get_goint() error, len(splitted) < 3, == up')
            else:
                going_str = splitted[0]
                interest_str = splitted[3]
        except ValueError:
            print('str: ')
            print(str)
            pexit('get_goint() error, printed below')
        if (type(going_str) == int) & (type(interest_str) == int):
            event_going_number = [going_str, interest_str]
        else:
            event_going_number = [convert_si_to_number(going_str), convert_si_to_number(interest_str)]

    return event_going_number


def get_description(tree):
    event_description = tree.xpath('//div[@id="unit_id_886302548152152"]/div[2]/text()')
    if (len(event_description) == 0):
        event_description = ''
    return event_description

def get_title(tree):
    event_title = tree.xpath('//h3/text()')  # [0] == date (Friday, November 16, 2018 at 8 PM – 11:55 PM)        [1] == place (Expresszó)
    if (len(event_title) == 0):
        print(event_title)
        pexit(' - get_title() error. len(event_title) == 0')
    return event_title[0]

def get_photo(tree):
    src = tree.xpath('//div[@id="event_header"]/a/img/@src')  # src=https://scontent.fbud3-1.fna.fbcdn.net/v/t1.0-9/cp0/e15/q65/c40.0.1119.628/46168765_2003771449645939_8214378811936997376_o.jpg?_nc_cat=1&efg=eyJpIjoiYiJ9&_nc_ht=scontent.fbud3-1.fna&oh=b3bba07c88fd8710a656964bbb322937&oe=5C6BCBEA
    if (len(src) == 0):
        src = tree.xpath('//a[@aria-label="Watch video"]/div/img/@src')  # get video preview image

    if (len(src) == 0):
        print(' - get_photo() error. len(src) == 0', end='')
        return ''
    return src[0]


def getpage(page):
    try:
        print('\x1b[6;32;40m' + 'Getting page: '+page + '\x1b[0m')
        eventurl = "https://mobile.facebook.com/"+page+"?v=events"
        browser.open(eventurl)
        tree = html.fromstring(browser.parsed.encode())
        strings = tree.xpath('//div[@id="root"]/div/div/div[2]/div/table/tbody/tr/td/div/div/span[3]/div/a[1]/@href')
        eventids = []
        for string in strings:
            eventids.append(os.path.split(string)[1].split('?')[0])
        istheremore = tree.xpath('//div[@id="m_more_friends_who_like_this"]/a/span/text()')
        while istheremore:
            nexturl = tree.xpath('//div[@id="m_more_friends_who_like_this"]/a/@href')[0]
            browser.open('https://mobile.facebook.com'+nexturl)
            tree = html.fromstring(browser.parsed.encode())
            strings = tree.xpath('//div[@id="root"]/div/div/div[2]/div/table/tbody/tr/td/div/div/span[3]/div/a[1]/@href')
            for string in strings:
                eventids.append(os.path.split(string)[1].split('?')[0])
            istheremore = tree.xpath('//div[@id="m_more_friends_who_like_this"]/a/span/text()')
        try:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            mycursor = connection.cursor()
            sql = "UPDATE pages SET lastindex = %s WHERE page = %s"
            mycursor.execute(sql, (now, page))
            connection.commit()
        except:
            print('Lastindex update error' + str(now))
        return eventids
    except ValueError: # Catch failture
        pexit('Getpage error')


def listpages():
    mycursor = connection.cursor()
    nowplushour = datetime.datetime.now() + datetime.timedelta(hours=-5)
    mycursor.execute("SELECT page FROM pages WHERE lastindex < %s OR lastindex IS NULL", nowplushour)
    pages = []
    for page in mycursor:
        pages.append(page['page'])
    return pages


# _______START SCRIPT________

login()

connection = pymysql.connect(host = CONFIG.MYSQL_HOST,
                                user = CONFIG.MYSQL_USER,
                                password = CONFIG.MYSQL_PASS,
                                db = CONFIG.MYSQL_DB,
                                cursorclass=pymysql.cursors.DictCursor)

listpages = listpages()
for pageid in listpages:
    pageevents = getpage(pageid)
    for eventid in pageevents:
        if (eventid != '2097615280296927') & (eventid != '980689918806985') & (eventid != '773389126335451'):
            getevent(eventid)
        else:
            print('Banned event: '+eventid)

nowminday = datetime.datetime.now() + datetime.timedelta(days=-1)
with connection.cursor() as cursor:
    cursor.execute("DELETE from events WHERE datefrom < %s AND dateto < %s", (nowminday, nowminday))
    result = cursor.rowcount
    print(str(result) + " old row deleted")
    connection.commit()

connection.close()

now = datetime.datetime.now()
if (inserted_count > 0):
    print(inserted_count + ' new row inserted')
else:
    print('Pages are already updated less than an hour ago, no new events queried')
print('Script end at '+str(now.hour)+':'+str(now.minute))
