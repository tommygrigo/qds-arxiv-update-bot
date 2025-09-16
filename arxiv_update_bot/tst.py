import smtplib
from datetime import datetime
import os

import configparser
from typing import List 
from os import linesep
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import feedparser


DEFAULT_CONFIGURATION_PATH = "./config.ini"


def load_config(path: str):
    """Load the configuration from the path.
    It will try to load the token from the [bot] section.
    Then it will iterate over the other sections to find the updates to verify.

    Args:
        path (string): path of the config file.

    Raises:
        Exception: if the bot section is not found.
        Exception: if there is no token value in the bot section.
        Exception: if an update section is not complete.

    Returns:
        (string, list): the token and the list of updates.
    """
    config = configparser.ConfigParser()
    config.read(path)

    categories = config.sections()
    categories.remove('general')
    
    buzzwords = dict()
    authors = dict()
    
    general_buzzwords = config['general']['buzzwords'].split(',')
    general_authors = config['general']['authors'].split(',')
    categories_clean = []
    for category in categories:
        temp_buzzwords = config[category]["buzzwords"].split(",")
        temp_buzzwords.extend(general_buzzwords)
        temp_buzzwords = list(set(temp_buzzwords))
        if '' in temp_buzzwords:
            temp_buzzwords.remove('')
        buzzwords.update({category:temp_buzzwords})
        temp_authors = config[category]["authors"].split(",")
        temp_authors.extend(general_authors)
        temp_authors= list(set(temp_authors))
        if '' in temp_authors:
            temp_authors.remove('')
        authors.update({category:temp_authors})


    return categories, buzzwords, authors


def get_articles(category: str, buzzwords: List[str]) -> List:
    """Get the articles from arXiv.

    It get the RSS flux re;ated to the category of the update,
    then filter the entries with the buzzwords.

    Args:
        category (str): the name of the category.
        buzzwords (List[str]): a list of buzzwords.

    Returns:
        List: list of entries.
    """
    news_feed = feedparser.parse(f"http://export.arxiv.org/rss/{category}")
    res = []
    for entry in news_feed.entries:
        for buzzword in buzzwords:
            if buzzword.lower() in entry.title.lower():
                if not 'announce type: replace' in entry.summary.lower():
                    if entry not in res:
                        res.append(entry)
            if buzzword.lower() in entry.summary.lower():
                if not 'announce type: replace' in entry.summary.lower():
                    if entry not in res:
                        res.append(entry)
    return res

def get_favourite_authors_articles(category: str, authors: List[str]) -> List:

    news_feed = feedparser.parse(f"http://export.arxiv.org/rss/{category}")
    res = []
    for entry in news_feed.entries:
        for author in authors:
            if author.lower() in entry.author.lower():
                if entry not in res:
                    res.append(entry)
    return res


def send_articles(
    category: str,
    buzzwords: List[str],
    authors: List[str],
):
    """Send the articles to telegram.

    Args:
        bot (telebot.Telebot): telebot instance.
        chat_id (int): the chat id to send the message. Either a group or individual.
        category (str): the category for arXiv.
        buzzwords (List[str]): list of buzzwords.
        quiet (bool, optional): whether to send a messae when no article is found. Defaults to False.
    """
    message = f'<h1>{category}</h1>'

    message += '<h2>Favourite authors </h2>'

    author_articles = get_favourite_authors_articles(category, authors)
    
    if not author_articles:
        message += f"No new articles from your favourite authors in section {category} today.<br>"
    else:
        for article in author_articles:
            try:
                message +=f"<h3>{article.title}</h3>"
                message += f"<b>Authors:</b> {article.authors[0]['name']}<br>"
                message += f"<b>Link:</b> {article.link}<br>"
                message += f"<b>Abstract:</b> {article.summary.replace(linesep,' ').replace('<p>', '').replace('</p>', '')}<br><br>"
            except:
                message+=f"<h3>{article.title}</h3>"
                message+=f"<b>Authors:</b> {article.authors[0]['name']}<br>"
                message+=f"<b>Link:</b> {article.link}<br><br>"    
    
    articles = get_articles(category, buzzwords)

    message += '<h2>Keywords </h2>'

    if not articles:
        message+=f"I scraped the arXiv RSS but found nothing of interest for you in the section {category}. Sorry.<br>"
    else:
        message+=f"You are going to be happy. I found {len(articles)} article(s) of potential interest in the section {category}.<br><br>"
        for article in articles:
            try:
                message +=f"<h3>{article.title}</h3>"
                message += f"<b>Authors:</b> {article.authors[0]['name']}<br>"
                message += f"<b>Link:</b> {article.link}<br>"
                message += f"<b>Abstract:</b> {article.summary.replace(linesep,' ').replace('<p>', '').replace('</p>', '')}<br><br>"
            except:
                print('Error sending a message regarding the paper', article.title)
    
    return message


def main():
    email = 'tommygrigoletto@gmail.com'
    reciever_email = 'tommaso.grigoletto@unipd.it'

    subject = 'QDS ArXiv update ' + datetime.today().strftime('%d-%m-%Y')
    

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()

    mail_pw = os.environ['MAIL_PW']

    server.login(email,mail_pw)

    

    categories, buzzwords, authors = load_config(DEFAULT_CONFIGURATION_PATH)

    article_lst = []

    for category in categories:
        article_lst.append(send_articles(
                category,
                buzzwords[category],
                authors[category]
            ))
        
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email
    msg['To'] = reciever_email

    msg.attach(MIMEText('Good morning you!\n\n','plain'))
    message = 'Good morning you!\n\n'
    html_msg = ''
    for m in article_lst:
        message += m
        html_msg += m
    msg.attach(MIMEText(html_msg,'html'))

    text = f'Subject: {subject}\n\n{message}'
    
    server.sendmail(email,reciever_email, msg.as_string())
    
    print('Email sent')
    server.quit()

if __name__ == "__main__":
    main()