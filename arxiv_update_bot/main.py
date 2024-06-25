"""
Main file of the arxiv_update_bot module.

Contains the methods to read configuration,
fetch updates and send messages along with the cli.
"""

import argparse
import configparser
from typing import List, Tuple
from os import linesep
import os

import feedparser
import telebot

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
    bot: telebot.TeleBot,
    chat_id: int,
    category: str,
    buzzwords: List[str],
    authors: List[str],
) -> None:
    """Send the articles to telegram.

    Args:
        bot (telebot.Telebot): telebot instance.
        chat_id (int): the chat id to send the message. Either a group or individual.
        category (str): the category for arXiv.
        buzzwords (List[str]): list of buzzwords.
        quiet (bool, optional): whether to send a messae when no article is found. Defaults to False.
    """
    author_articles = get_favourite_authors_articles(category, authors)
    
    if not author_articles:
        bot.send_message(
            chat_id,
            text=f"No new articles from your favourite authors in section {category} today.",
        )
    else:
        for article in author_articles:
            try:
                bot.send_message(
                    chat_id,
                    text=f"I found a paper by one of your favourite authors!",
                    parse_mode="HTML",
                )
                bot.send_message(
                    chat_id,
                    text=f"<strong>Title:</strong> {article.title}\n<strong>Authors:</strong> {article.authors[0]['name']}\n<strong>Link:</strong> {article.link}\n<strong>Abstract:</strong> {article.summary.replace(linesep,' ').replace('<p>', '').replace('</p>', '')}",
                    parse_mode="HTML",
                )
            except:
                bot.send_message(
                    chat_id,
                    text=f"<strong>Title:</strong> {article.title}\n<strong>Authors:</strong> {article.authors[0]['name']}\n<strong>Link:</strong> {article.link}",
                    parse_mode="HTML",
                )
    
    
    articles = get_articles(category, buzzwords)

    if not articles:
        bot.send_message(
            chat_id,
            text=f"I scraped the arXiv RSS but found nothing of interest for you in the section {category}. Sorry.",
        )
    else:
        bot.send_message(
            chat_id,
            text=f"You are going to be happy. I found {len(articles)} article(s) of potential interest in the section {category}.",
        )
        for article in articles:
            try:
                #print(article.title)
                bot.send_message(
                    chat_id,
                    text=f"<strong>Title:</strong> {article.title}\n<strong>Authors:</strong> {article.authors[0]['name']}\n<strong>Link:</strong> {article.link}\n<strong>Abstract:</strong> {article.summary.replace(linesep,' ').replace('<p>', '').replace('</p>', '')}",
                    parse_mode="HTML",
                )
            except:
                print('Error sending a message regarding the paper', article.title)


def main():
    """
    The main function.
    """
    parser = argparse.ArgumentParser(description="Scrap the arXiv")
    # parser.add_argument('token', metavar='token', type=str,
    #                 help='Telegram token for sending the messages')
    # parser.add_argument('id', metavar='id', type=int,
    #                 help='Telegram chat id for sending the messages')

    parser.add_argument(
        "-c",
        "--config-path",
        help="Path for configuration path. Replace default of /etc/arxiv-update-bot/config.ini",
    )

    args = parser.parse_args()
    config_path = args.config_path or DEFAULT_CONFIGURATION_PATH
    # token = args.token
    # chat_id = args.id
    
    token = os.environ['TOKEN']
    chat_id = os.environ['CHATID']
    
    categories, buzzwords, authors = load_config(config_path)

    bot = telebot.TeleBot(token, parse_mode="HTML")
    
    bot.send_message(chat_id,'Good morning you!\n\n\n\n\n\n')

    for category in categories:
        #print(category)
        send_articles(
                bot,
                chat_id,
                category,
                buzzwords[category],
                authors[category]
            )


if __name__ == "__main__":
    main()
