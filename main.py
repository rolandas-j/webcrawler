import argparse
from collections import deque
from queue import Queue
import signal
import sys
import logging
from time import sleep
from database import Database
from logger import setup_logger
from concurrent.futures import TimeoutError, thread
from pebble import ProcessFuture, ProcessPool, ProcessExpired, sighandler
from crawler import Config, WebCrawler, WebNode
from urllib.parse import urlparse




@sighandler((signal.SIGINT, signal.SIGTERM))
def signal_handler(signum, frame):
    sys.exit(0)


def start_worker(): 
    parser = argparse.ArgumentParser(description='WebCrawler simple CLI')
    parser.add_argument('--url', '-U', type=str, help='Url to start crawling.', required=True)
    parser.add_argument('--crawl-http', '-ch', type=bool, help='Flag to allow crawling in http pages.', default=True)
    parser.add_argument('--ignored-html-tags', '-i', type=list[str], help='Specify tags(with its contents) to remove from html before parsing URLs.', default=['script'])
    parser.add_argument('--crawl-ads', '-ca', type=bool, help='Flag to allow crawling in advertesment pages.', default=True)
    parser.add_argument('--scan-content', '-sc', type=bool, help='Flag to enable for URL search in the contents of the page instead of only in html tags.', default=True)
    parser.add_argument('--cassandra-ip', '-cI', type=str, help='Cassandra DB IP, default: 0.0.0.0', default='0.0.0.0')
    parser.add_argument('--cassandra-port', '-cP', type=str, help='Cassandra DB port, default: 9042', default='9042')
    parser.add_argument('--cassandra-keyspace', '-cK', type=str, help='Cassandra DB keyspace name, default: crawler', default="crawler")
    parser.add_argument('--log-level', '-L', type=str, help='Log level, default: info', default="info")

    args = parser.parse_args()

   
    logger = setup_logger('worker', args.log_level)
    logger.info(args)
    config = Config(crawl_http=args.crawl_http, ignored_html_tags=args.ignored_html_tags, crawl_ads=args.crawl_ads, scan_content_for_links=args.scan_content)
    db = Database(args.cassandra_ip, args.cassandra_port, args.cassandra_keyspace)
    stuff  = db.check_if_page_exists(args.url)
    logger.info(stuff)

    webCrawler = WebCrawler(logger=setup_logger('crawler', args.log_level))
    pool = ProcessPool()
    tasks_queue = Queue()
    results_list = []

    tasks_queue.put_nowait(args.url)

    while not tasks_queue.empty() or len(results_list) != 0:
        logger.debug("Waiting for tasks")
        
        if not tasks_queue.empty():
            url_to_crawl = tasks_queue.get_nowait()
            
            task_result = pool.schedule(webCrawler.crawl, [url_to_crawl, config])

            results_list.append(task_result)
            
        current_tasks = results_list[:]
        results_list = []
        for idx, running_task in enumerate(current_tasks):
            if running_task.done():
                webnode: WebNode = running_task.result()
                db.insert_html(webnode.rootUrl, webnode.content)
                logger.debug(f'Finished crawling page: {webnode.rootUrl}')
                for url in webnode.urls:
                    logger.debug(f'Page exists: {db.check_if_page_exists(url)}, url: {url}')
                    if not db.check_if_page_exists(url):
                        tasks_queue.put_nowait(url)
                        pass
            else:
                results_list.append(running_task)

        #Slow everything down abit
        sleep(1)
    logger.info("Completed")


if __name__ == '__main__':
    start_worker()

