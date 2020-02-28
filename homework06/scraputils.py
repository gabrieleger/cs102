import time

import requests
from bs4 import BeautifulSoup


def extract_news(parser: BeautifulSoup):
    """ Extract news from a given web page """
    news_list = []

    news_table = parser.find('table', {"class": "itemlist"})

    post_tr = news_table.findNext('tr', {'class': 'athing'})

    while post_tr is not None:
        post_id = post_tr.attrs['id']

        _post_href = post_tr.findNext('a', {'class': 'storylink'})
        post_url = _post_href.attrs['href']
        post_title = _post_href.text

        _post_subtext = post_tr.findNext('td', {'class': 'subtext'})
        post_points = int(_post_subtext.findNext('span').text.split(' ')[0])
        post_author = _post_subtext.findNext('a', {'class': 'hnuser'}).text

        _post_discussion = _post_subtext.findAllNext('a', {'href': f'item?id={post_id}'})[1]
        if _post_discussion.text == 'discuss':
            post_comments = 0
        else:
            post_comments = int(_post_discussion.text.split('\xa0')[0])

        post_dict = {
            'id':       post_id,
            'title':    post_title,
            'author':   post_author,
            'url':      post_url,
            'comments': post_comments,
            'points':   post_points
        }
        news_list.append(post_dict)

        post_tr = post_tr.findNext('tr', {'class': 'athing'})

    return news_list


def extract_next_page(parser: BeautifulSoup):
    """ Extract next page URL """
    more_href = parser.find('a', {'class': 'morelink'}).attrs['href']
    return more_href


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        if n_pages % 10 == 0:
            time.sleep(5)
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html5lib")
        try:
            news_list = extract_news(soup)
            next_page = extract_next_page(soup)
            url = "https://news.ycombinator.com/" + next_page
            news.extend(news_list)
            n_pages -= 1
        except Exception as e:
            print('Exception occured! Scraping stopped')
            n_pages = 0

    return news


if __name__ == '__main__':
    get_news('https://news.ycombinator.com/newest', 3)
