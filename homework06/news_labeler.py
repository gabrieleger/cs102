from db import News, session

INTERESTING_WORDS = ['programming', 'python', 'C++', 'web', 'database', 'api', 'robot', 'ai', 'ml', 'windows', 'linux', 'apple']
INTERESTING_COLLOCATIONS = ['data science', 'machine learning']

CHANGE_DB = True

if __name__ == '__main__':
    s = session()
    news_table = s.query(News).filter(News.label == None).all()

    labeled, total = 0, 0

    for headline in news_table:
        title: str = headline.title.lower()
        title_splitted = title.split()

        if any([topic in title_splitted for topic in INTERESTING_WORDS]) or any([topic in title for topic in INTERESTING_COLLOCATIONS]):
            labeled += 1
            headline.label = 'good'
            print(title)
        else:
            headline.label = 'never'
        total += 1

    print(f'== Labeled as interesting {labeled}/{total}')
    if CHANGE_DB:
        s.commit()
        print('Changes commited')

