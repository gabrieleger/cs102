from scraputils import get_news
from db import session, News

PAGES_TO_COLLECT = 35

if __name__ == '__main__':
    print('== Stage #1 - Collecting database...')
    print(f'\tPAGES_TO_COLLECT = {PAGES_TO_COLLECT}')
    news = get_news('https://news.ycombinator.com/newest', PAGES_TO_COLLECT)
    print(f'\tNews collected, total {len(news)}')
    print(f'== Stage #2 - Adding news to database...')
    s = session()
    news = [s.add(News(**n)) for n in news]
    print('\tNews list converted to ORM')
    s.commit()
    print('\tSession commited')
