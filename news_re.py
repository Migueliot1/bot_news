import re
import urllib.request, urllib.parse, urllib.error
import ssl
import sqlite3
from hidden import get_db_name

# Temp file path
temp_path = 'files/temp.html'
temp_db_path = 'files/temp.db'

urls = ['https://www.pcgamer.com/news/', 'https://kotaku.com/culture/news/']

def get_searchables(db_name):
    '''Get searchables from the database in a format of tuple 
    (article, name, link, synopsis, image, time).
    '''

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('SELECT article, name, link, synopsis, image, time FROM Searchables')
    searchables = list()

    for row in cur:
        searchables.append(row)

    cur.close()
    conn.close()

    return searchables


def download_image(url):
    '''Downloads image from given URL and returns its filepath.'''

    filepath = 'files/' + 'image.' + url[-3:]
    urllib.request.urlretrieve(url, filepath)

    return filepath


def check():
    '''Main function which performes articles search on websites 
    and adds them into the final database.
    '''

    searchables = get_searchables(get_db_name())
    count = 0

    for i in range(2):

        download_data(urls[i])
        find_contents(searchables[i])

        added = get_arts()
        count += added

    print('Check is succesful. Added', count, 'articles.')


def download_data(url):
    '''Getting published articles from the given website'''

    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    html = urllib.request.urlopen(url, context=ctx) # Save page contents
    data = html.read().decode() # Decode contents
    print('Retrieved', len(data), 'characters from URL', url)

    # Save html contents to a temp file
    file = open(temp_path, 'r+')
    file.truncate(0)
    data = data.replace("\u017b", "")
    data = data.replace("\u0142", "")
    file.write(data)
    file.close()


def find_contents(searchables):
    '''Finding in HTML file articles' contents and saving them 
    to SQL database.
    
    Gets searchables terms as a tuple to extract way to find each article, name, link, etc.
    Searchables tuple should be (article, name, link, synopsis, image, time)'''

    # Getting raw HTML contents from the saved temp file
    file = open(temp_path, 'r')
    data = file.read()
    file.close()

    # Browsing through articles
    # Condition allows correct work on Kotaku website
    if 'div' in searchables[0]:
        arts_list = re.findall(searchables[0], data, re.DOTALL)
    else:
        arts_list = re.findall(searchables[0], data)

    conn = sqlite3.connect(temp_db_path)
    cur = conn.cursor()
    
    cur.executescript('DROP TABLE TempArticles')
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS TempArticles (
        name TEXT UNIQUE,
        link TEXT UNIQUE,
        image TEXT UNIQUE,
        synopsis TEXT,
        time TEXT
    );
    ''')

    # Extracting PC Gamer news articles
    for item in arts_list:

        # Checking if it's news or deals article on PC Gamer and skipping if it's not news
        check = re.search('<a class="category-link" href="javascript:void(0)">(.+?)</a>', item)
        if check:
            if check.lower() != 'news':
                continue

        # Searching for article's name
        mn = re.search(searchables[1], item)
        if mn:
            name = mn.group(1)
        else:
            name = None

        # Searching for articles' link
        ml = re.search(searchables[2], item)
        if ml:
            # for some reason link to the next page is also added to the list so I have to do this workaround
            link = ml.group(1)
            if link == 'https://www.pcgamer.com/news/page/2/':
                link = None
        else:
            link = None

        # Searching for synopsis
        ms = re.search(searchables[3], item, re.DOTALL)
        if ms:
            synopsis = ms.group(1)
        else:
            synopsis = None

        # Searching for image's link
        mi = re.search(searchables[4], item)
        if mi:
            img_link = mi.group(1)
        else:
            img_link = None

        # Searching for time
        mt = re.search(searchables[5], item)
        if mt:
            time = mt.group(1)
        else:
            time = None
    
        if name and link and synopsis and img_link and time:
            cur.execute('''INSERT INTO TempArticles 
                (name, link, image, synopsis, time) VALUES 
                (?, ?, ?, ?, ?)''', (name, link, img_link, synopsis, time))
            conn.commit()

    cur.close()
    conn.close()


def get_arts():
    '''Saves clean articles' data into SQL database 
    and returns number of added articles.'''

    # Final database to fill
    conn = sqlite3.connect(get_db_name())
    cur = conn.cursor()

    # Create table if it doesn't exist
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS Articles (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        name TEXT UNIQUE,
        link_id  INTEGER,
        link TEXT UNIQUE,
        image_id INTEGER,
        image TEXT UNIQUE,
        synopsis TEXT,
        time TEXT,
        was_published INTEGER
    );
    ''')

    # Open temp database
    temp_conn = sqlite3.connect(temp_db_path)
    temp_cur = temp_conn.cursor()
    temp_cur.execute('SELECT * FROM TempArticles')

    arts = list()
    # Add (name, link, image, synopsis, time) into list
    for row in temp_cur:
        arts.append(row)

    temp_cur.close()
    temp_conn.close()
    
    length = len(arts)
    if length != 0:
        for i in range(length):

            name = arts[i][0]
            link = arts[i][1]
            image = arts[i][2]
            syn = arts[i][3]
            time = arts[i][4]

            if name is None or link is None or image is None or syn is None or time is None: 
                continue
            
            # Preparing links to be stored
            # First, article's link
            if 'pcgamer' in link:
                cur.execute('SELECT id FROM Links WHERE name = ? ', ('PC Gamer', ))
                link_id = cur.fetchone()[0]
                link = link.split('/')[3] # Getting link piece after 'pcgamer.com/'

            if 'kotaku' in link:
                cur.execute('SELECT id FROM Links WHERE name = ? ', ('Kotaku', ))
                link_id = cur.fetchone()[0]
                link = link.split('/')[3] # Getting link piece after 'kotaku.com/'
        
            # Second, image's link
            if 'cdn.mos.cms.futurecdn.net' in image:
                cur.execute('SELECT id FROM Images WHERE name = ? ', ('CDN', ))
                image_id = cur.fetchone()[0]
                image = image.split('/')[3]
            else:
                cur.execute('SELECT id FROM Images where name = ? ', ('KINJA', ))
                image_id = cur.fetchone()[0]
                image += '.jpg'

            # Adding all of stuff into the database
            cur.execute('''INSERT OR IGNORE INTO Articles
                (name, link_id, link, image, image_id, synopsis, time, was_published) 
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ? )''', 
                (name, link_id, link, image, image_id, syn, time, 0))
            conn.commit()

    cur.close()
    conn.close()
    return length
