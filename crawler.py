
from __future__ import annotations
import re
import requests
from logger import setup_logger
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class WebNode:

    def __init__(self, rootUrl: str, content: str, urls: list[str]):
        self.rootUrl = rootUrl
        self.content = content
        self.urls = urls

class Config:
    def __init__(self, crawl_http = False, ignored_html_tags = ['script'], crawl_ads = True, scan_content_for_links = False) -> WebNode:
        self.crawl_http = crawl_http
        self.ignored_html_tags = ignored_html_tags
        self.crawl_ads = crawl_ads
        self.scan_content_for_links = scan_content_for_links

class WebCrawler:
    #Ignore <link> if their 'rel' is one of the following type
    link_tag_rel_blacklist = ['stylesheet', 'preload']
    known_add_links = ['adclick.g', 'track.adform.net']
    html_file_types = ['.txt', '.js', '.css']

    def __init__(self, logger) -> None:
        self.logger = logger
        

    def crawl(self, start_url: str, config: Config):
        html = self.request_content(start_url)
        urls = self.parse_urls(html, config)

        protocol, root_domain = self.extract_domain(start_url)
        final_urls = self.postprocess_urls(protocol, root_domain, urls, config)

        return WebNode(start_url, html, final_urls)

    def extract_domain(self, url: str) -> str:
        parsed_url = urlparse(url)
        protocol = parsed_url.scheme;
        domain = parsed_url.netloc
        return protocol, domain
    
    def request_content(self, url: str) -> str:
        response = requests.get(url)
        self.logger.debug(f'Response: {response.status_code}, Content:{response.text}')
        if response.ok:
            return response.text
        elif response.status_code > 300 or response.status_code < 400:
            #TODO handle redirects
            pass
        else:
            #TODO handle 4xx and retry on 5xx
            self.logger.error(f'Error while requesting to URL: {url}')
            self.logger.error(f'Error response: {response.text}')
        return ""
    
    def parse_urls(self, html: str, config: Config):
        if len(config.ignored_html_tags) == 0:
            return html
        
        soup = BeautifulSoup(html, 'lxml')
        
        for tag in soup.find_all(config.ignored_html_tags):
            tag.decompose()

        links = []
        for tag in soup.find_all(href=True):
            if tag.get('rel') in self.link_tag_rel_blacklist:
                continue
            links.append(tag['href'])

        content_links = []
        if config.scan_content_for_links:
            content_links = self.scan_content_for_urls(soup.get_text())

        return links + content_links;

    
    
    def scan_content_for_urls(self, content: str):
        pattern = '\bhttps?://\S+'
    
        return re.findall(pattern, content)
       

    def postprocess_urls(self, protocol: str, root_domain: str, urls: list[str], config: Config):
        full_domain = protocol + '://' + root_domain

        final_urls = set()
        for url in urls:
            if not config.crawl_ads and self.is_add_page(url):
                self.logger.debug(f'Removed add page:{url}')
                continue
            if self.is_a_file(url):
                self.logger.debug((f'Removed file:{url}'))
                continue
            if url.startswith('//'):
                final_urls.add(protocol + ':' + url)
                continue;
            if url.startswith('/'):
                final_urls.add(full_domain+url)
                continue;

        return final_urls
    
    #Extremely naive filter, in reality its much much harder to detect add pages
    def is_add_page(self, url):
        for add_pages in self.known_add_links:
            if url in add_pages:
                return True
        return False
    
    #TODO fix on the links where they dont actually end with .something, they have query params, etc.
    def is_a_file(self, url):
        for type in self.html_file_types:
            if url.endswith(type):
                return True
        return False