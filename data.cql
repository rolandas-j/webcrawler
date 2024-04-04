-- Create a keyspace
CREATE KEYSPACE IF NOT EXISTS crawler WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : '1' };

-- Create a table
CREATE TABLE IF NOT EXISTS crawler.pages (
url text PRIMARY KEY,
content text
);