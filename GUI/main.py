from flask import Flask
from flask import request, render_template, redirect, request, abort, url_for

import subprocess
app = Flask (__name__)

@app.route('/')
def homePage():
	return render_template ('index.html')

@app.route('/result', methods=['POST'])
def loginFormHandling():
	from stemmer import stemmer
	from stopwords import stopwords
	from search_handler import search
	stemmer = stemmer()
	stopwords = stopwords()
	search = search ("path", stemmer, stopwords)
	data = request.form
	query = request.form ['query']
	flag = 0
	if data['title'] != '':
		flag = 1
		query += " title:"
		query += data['title']
	if data['infobox'] != '':
		flag = 1
		query += " infobox:"
		query += data['infobox']
	if data['references'] != '':
		flag = 1
		query += " ref:"
		query += data['references']
	if data['category'] != '':
		flag = 1
		query += " category:"
		query += data['category']
	if data['links'] != '':
		flag = 1
		query += " links:"
		query += data['links']
	if data['body'] != '':
		flag = 1
		query += " body:"
		query += data['body']
	# if (flag == 1):
	# 	r = len(request.form ['query'])
	# 	query = query[r:]
	print (query)
	the_result = search.search (query)
	return render_template ('results.html', query=query, results=the_result)

app.run (debug=True, threaded = True)
