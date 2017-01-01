#!/bin/env python
# -*- encoding: utf-8 -*-

import re
import sys
import logging
import argparse
from socket import gethostname

from lxml.html import fromstring

import config
from mdb.film import Film
from mdb.db import Database
from mdb.http import Downloader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

db = Database.Instance()


class App():

    base = 'https://www.kinopoisk.ru'
    total_count = None

    def __init__(self):
        parser = argparse.ArgumentParser(description='Generate SQL statemets to create '
                                                     'attribute tables.')
        parser.add_argument('--year', type=int, help='Year to process')
        parser.add_argument('--hostname', type=str, help='Hostname', required=False,
                            default=gethostname())
        parser.add_argument('--film-id', type=int, help='Film ID')
        parser.add_argument('--sleep-time', type=int, help='Max sleep time between requests',
                            default=20)
        self.args = parser.parse_args()
        # Initialization of the cache
        Downloader.init_cache()
        # Initialization of database connection
        db.connect(config.dsn)
        config.sleep_time = self.args.sleep_time
        if self.args.year is not None:
            self.set_year(self.args.year)

    def set_year(self, year):
        config.year = year

    def get_rating_history(self, film_id):
        """
        /graph_data/variation_data_film/243/variation_data_film_810243.xml? + Math.random(0,10000)
        """
        return

    def get_pages_count(self, year):
        logger.info('Getting pages count for year %s' % year)
        page = Downloader.get(self.get_url_for_year(year))
        html = fromstring(page)
        a = html.xpath('//ul[@class="list"]//li[@class="arr"][last()]//a')
        if a is None or len(a) == 0:
            pages_count = 1
        else:
            m = re.search('/page/(\d+)/', a[0].get('href'))
            pages_count = int(m.group(1))

        h1 = html.xpath('//h1[@class="level2"]//span[@style="color: #777"]')
        if h1 is not None and len(h1) > 0:
            self.total_count = int(re.sub('[^\d]', '', h1[0].text_content()))
        else:
            raise Exception('Could not get total records count!')

        logger.info('Got total_count = %s' % self.total_count)
        return pages_count

    def get_url_for_year(self, year, page=1):
        return '%s/lists/ord/name/m_act[year]/%s/m_act[all]/ok/page/%s/' % (self.base, year, page,)

    def extract_id_from_url(self, url):
        m = re.search('/(\d+)/$', url)
        return int(m.group(1))

    def get_films_from_page(self, url):
        page = Downloader.get(url)
        html = fromstring(page)
        for item in html.xpath('//div[contains(@class, "item")]//div[@class="name"]//a'):
            title = item.text_content()
            href = item.get('href')
            id = self.extract_id_from_url(href)
            yield (id, title, href)

    def get_film_url(self, film_id):
        return '%s/film/%s/' % (self.base, film_id,)

    def get_film(self, film_id):
        """
        Extracts all informarion about film
        """
        page = Downloader.get(self.get_film_url(film_id))
        film = Film(film_id, page)

        logger.warning('%s (%s) | %s' % (film.title, film.alternative_title, film.year,))
        return film

    def get_current_count(self):
        return db.query_value('select count(*) from mdb.movie where year = %s' % config.year)

    def update_stat(self, last_movie_id):
        id = db.query_value('select id from mdb.stat where year = %s', [config.year])
        if id is None:
            db.execute('insert into mdb.stat (year, done_count, total_count, hostname, '
                       'last_movie_id) '
                       'values (%s, %s, %s, %s, %s)',
                       [config.year, self.get_current_count(), self.total_count,
                        self.args.hostname, last_movie_id])
        else:
            db.execute('update mdb.stat set done_count = %s, total_count = %s, hostname = %s, '
                       'last_update_time = current_timestamp, last_movie_id = %s '
                       'where year = %s',
                       [self.get_current_count(), self.total_count, self.args.hostname,
                        last_movie_id, config.year])

    def log_error(self, movie_id, message):
        logger.error('Could not parse movie %s: "%s"' % (movie_id, message,))
        db.execute('insert into mdb.error(hostname, movie_id, message) '
                   'values (%s, %s, %s)', [self.args.hostname, movie_id, message])

    def get_year(self, year):
        logger.info('======= Processing year %s =======' % year)
        for page_number in range(1, self.get_pages_count(year) + 1):
            logger.info("Processing page %s" % page_number)
            for id, title, href in self.get_films_from_page(self.get_url_for_year(year, page_number)):
                logger.info('%s | %s | %s' % (id, title, href,))
                try:
                    f = self.get_film(id)
                    f.save()
                except Exception as e:
                    self.log_error(id, str(e))
                logger.warning('%s from %s' % (self.get_current_count(), self.total_count,))
                self.update_stat(id)

    def run(self):
        if self.args.film_id is not None:
            logger.warning('======= Processing film %s =======' % self.args.film_id)
            f = self.get_film(self.args.film_id)
            f.save()
            sys.exit(0)
        while config.year <= 2016:
            self.get_year(config.year)
            self.set_year(config.year + 1)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO, stream=sys.stdout)
    app = App()
    app.run()
