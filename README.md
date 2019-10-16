# Search Engine for Wikipedia
A search engine indexed on the latest corpus of English Wikipedia, with full support for field queries. Python 3.7.

Latest dumps can be found at - https://dumps.wikimedia.org/backup-index.html


## GUI
A simple, clean GUI made in flask to ease interaction with the search engine.
![Homepage](/screenshots/homepage.png)
![A search result](/screenshots/search.png)

## Installation
In a new virtual environment, run 
`pip install -r requirements`

## Building the Index
You can either collect the index from the link (indexed on October 1st 2019), or run the indexer code

`bash index.sh <path to corpus> <path to output directory>`

The sequences and locations for storing the page titles can be found inside `parser.py` (placed there due to specific title storing format)

## Search through Terminal
Field queries are written as 

`title:title_text infobox:infobox_text category:category_text ref:references_text body:body_text`

Store queries inside queries.txt. An example - 

> life of pi

> hogwarts

> pink city of india

> title:gandhi infobox:mohandas

Run the search as

`bash search.sh <anypath> <path to queries.txt> <path to output file>`

The results would be present inside output file.

## To Do:
1. Multiprocess the indexing portion, to speed up indexing time.
2. Cache the results of the stemmer (say upto 500,000 words and then clear cache) to significantly improve indexing performance)
3. Repair some field query code.
4. Improve ranking methods
