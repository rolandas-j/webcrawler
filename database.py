from cassandra.cluster import Cluster

class Database:
    def __init__(self, ip, port, keyspace) -> None:
        cluster = Cluster([ip], port = port);
        self.cluster = cluster
        self.session = cluster.connect(keyspace)

    def insert_html(self, url: str, html: str):
        statement = self.session.prepare(f'INSERT INTO pages (url, content) VALUES (?, ?)')
        self.session.execute(statement, [url, html])

    def check_if_page_exists(self, url: str):
        statement = self.session.prepare(f'SELECT count(*) FROM pages WHERE url = ?')
        result = self.session.execute(statement, [url])[0]
        return result.count == 1;