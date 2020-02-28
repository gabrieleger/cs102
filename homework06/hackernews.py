from bottle import (
    route, run, template, request, redirect
)
from sqlalchemy.orm import load_only

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier
from sqlalchemy import and_


@route('/')
def route_page():
    redirect('/news')


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():
    s = session()
    label = request.query.label
    row_id = request.query.id
    row = s.query(News).filter(News.id == row_id).one()
    row.label = label
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    s = session()

    current_news = get_news('https://news.ycombinator.com/newest', 1)
    old_news = [n.id for n in s.query(News).options(load_only('id')).all()]

    for headline in current_news:
        if int(headline['id']) not in old_news:
            news_add = News(**headline)
            s.add(news_add)

    s.commit()
    redirect("/news")


@route("/classify")
def classify_news():
    new_labeled_news = s.query(News).filter(and_(News.label != None, News.title not in x_train)).all()
    x_new = [row.title for row in new_labeled_news]
    y_new = [row.label for row in new_labeled_news]
    classifier.fit(x_new, y_new)

    news_to_predict = s.query(News).filter(News.label == None).all()
    x_predict = [row.title for row in news_to_predict]
    y_predict = classifier.predict(x_predict)

    headlines_good = [news_to_predict[i] for i in range(len(news_to_predict)) if y_predict[i] == 'good']
    headlines_maybe = [news_to_predict[i] for i in range(len(news_to_predict)) if y_predict[i] == 'maybe']
    headlines_never = [news_to_predict[i] for i in range(len(news_to_predict)) if y_predict[i] == 'never']

    return template('recommendations', hgood=headlines_good, hmaybe=headlines_maybe, hnever=headlines_never)


if __name__ == "__main__":
    s = session()
    classifier = NaiveBayesClassifier()

    marked_news = s.query(News).filter(News.label != None).all()
    x_train = [row.title for row in marked_news]
    y_train = [row.label for row in marked_news]
    classifier.fit(x_train, y_train)
    run(host="localhost", port=8080)
