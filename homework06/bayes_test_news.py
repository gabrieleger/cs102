from bayes import NaiveBayesClassifier
from db import News, session

classifier = NaiveBayesClassifier()
s = session()

marked_news = s.query(News).filter(News.label != None).all()
x_train = [row.title for row in marked_news]
y_train = [row.label for row in marked_news]
classifier.fit(x_train, y_train)

predicts_test = [('good', 'Python'),
                 ('good', 'Python developers created new app'),
                 ('good', 'New python version 3.8.3 released'),
                 ('good', 'Windows subsystem for linux'),
                 ('never', 'Coronavirus deleted our world'),
                 ('never', 'Trump ordered a nuke bomb for his museum'),
                 ('never', 'Ask HN: How to find work while homeless?'),
                 ('never', 'Love Zombies? Thank the Public Domain')]

stop_index = 1

print('Status | Classifier | True | Title')
for correct, title in predicts_test:
    decision = classifier.predict([title])[0]
    status = 'OK' if decision == correct else '!!'
    print(f'{status} | {decision} | {correct} | {title}')
