import sqlite3
from news_re import check
from hidden import get_db_name

db_name = get_db_name()
months = {
    '01':'Jan',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Apr',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'Aug',
    '09': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dec'
}


def prepare_date_time(raw_time):
    '''Gets a string in yyyy-mm-ddThh:mm:ssZ format and returns 
    a string in 'dd mmmm yyyy | hh:mm UTC' format
    '''

    kotaku_check = False
    if "-04:00" in raw_time:
        kotaku_check = True
    
    full_date = raw_time.split('T')
    date_unedited = full_date[0].split('-') # Contains year, month, day
    time_unedited = full_date[1].split(':') # Contains hour, min, sec

    month = None
    month_num = date_unedited[1]

    # Check if it's the time from Konami website
    # if yes - add 4 hours cuz they have that weird time system
    if kotaku_check:
        hour_upd = int(time_unedited[0]) + 4
        time_unedited[0] = str(hour_upd)
    
    # Save month name from its number    
    if month_num in months:
        month = months[month_num]
    
    try:
        if month != None:
            result = date_unedited[2] + ' ' + month + ' ' + date_unedited[0] + ' | ' + time_unedited[0] + ':' + time_unedited[1] + ' UTC'
    except:
        result = None
    
    return result


def publish(name):
    '''Changes was_published of article with given name'''

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    cur.execute('SELECT * FROM Articles')
    cur.execute(
                'UPDATE Articles SET was_published = ? AND name = ? WHERE was_published = ?', 
                (1, name, 0))
    conn.commit()

    cur.close()
    conn.close()


# Getting articles data out of sql file
def get_news():
    '''Getting articles data out of sql file.
    
    Returns a list of tuples (article header, website, link to article, link to image, synopsis, time)
    '''
    # Perform a check on PC Gamer and Kotaku
    check()

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('''
    SELECT Articles.Name, Links.name, Links.link, Articles.link, Images.link, Articles.image, Articles.synopsis, Articles.time
    FROM Articles JOIN Links JOIN Images
    ON Articles.link_id = Links.id and Articles.image_id = Images.id and Articles.was_published = 0 
    ORDER BY Articles.time ASC
    ''')

    # Add everything about each article into a list
    articles = list()
    for row in cur:
        articles.append(row)

    cur.close()
    conn.close()

    links = list() # list of tuples; contains links to the website and image
    dates_times = list() # list of tuples; contains date and time

    if len(articles) != 0:
        for i in articles:

            links.append( ((i[2] + i[3]), (i[4] + i[5])) ) # Appending article link and image link
            dates_times.append(prepare_date_time(i[7])) # Appending time and date

    # Making a list of tuple with newly made links and dates/times and all of the articles stuff
    final_data = list()
    if len(articles) != 0:
        for i in range(len(articles)):
            final_data.append(
                (articles[i][0],
                articles[i][1],
                links[i][0],
                links[i][1],
                articles[i][6],
                dates_times[i])
                )

    # Getting data to the bot as a list
    return final_data
