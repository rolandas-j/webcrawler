# webcrawler
Simple webcrawler


# requirements:

* python 3.10
* python virtual environemnt(https://docs.python.org/3/library/venv.html)
* docker

# setup

1. Run setup.sh to install python venv and required dependencies
1. Run start_db.sh to start cassandra container and run data.cql to setup initial database structure
1. Run main.py --help to figure out what you need 
    * Example: `python main.py -U 'https://www.delfi.lt'`
