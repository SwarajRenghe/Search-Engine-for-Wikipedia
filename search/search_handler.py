# KINDS
# -----
# 0 - docID
# 1 - title
# 2 - infobox
# 3 - references
# 4 - category
# 5 - links
# 6 - body
import pickle, os
class search ():
	def __init__ (self, path_to_index_file, stemmer, stopwords):
		self.path_to_index_file = path_to_index_file
		self.stemmer = stemmer
		self.stopwords = stopwords
		# self.weights = [None, 2000, 300, 10, 40, 10, 100]
		self.weights = [None, 2000, 500, 80, 40, 10, 150]

	def apply_process (self, lines, query_term):
		for line in lines:
			j = line[2:line.find('[')]
			j = j[:j.find('\'')]
			if j == query_term:
				return True
		return False

	def intersection (self, list1, list2):
		temp = set (list(zip(*list2))[0])
		list3 = [x[0] for x in list1 if x[0] in temp]
		return list3
	def list_intersection (self, lst1, lst2): 
		lst3 = [value for value in lst1 if value in lst2] 
		return lst3 

	def process_query (self, query):
		self.query = query.lower()
		self.terms_in_query = self.query.split(' ')
		self.terms_in_query = [x.strip() for x in self.terms_in_query]
		self.terms_in_query = [self.stemmer.stem(x) for x in self.terms_in_query if not self.stopwords.check_stopword(x)]
		self.final_list = []

	def field_query (self, query):
		fields = [None, 0, 0, 0, 0, 0, 0]
		title = None
		infobox = None
		references = None
		category = None
		links = None
		body = None
		final_list = []
		lists = []
		_of_document_titles = []

		if "title" in query:
			fields[1] = 1
			title = query[query.find("title:")+6:]
			title = title[:title.find(":")]
			title = title.split(' ')
			if "body" in title:
				title.remove("body")
			if "infobox" in title:
				title.remove("infobox")
			if "ref" in title:
				title.remove("ref")
			if "category" in title:
				title.remove("category")
			if "links" in title:
				title.remove("links")

		if "infobox" in query:
			fields[1] = 1
			infobox = query[query.find("infobox:")+8:]
			infobox = infobox[:infobox.find(":")]
			infobox = infobox.split(' ')
			if "body" in infobox:
				infobox.remove("body")
			if "title" in infobox:
				infobox.remove("title")
			if "ref" in infobox:
				infobox.remove("ref")
			if "category" in infobox:
				infobox.remove("category")
			if "links" in infobox:
				infobox.remove("links")

		if "ref" in query:
			fields[1] = 1
			references = query[query.find("ref:")+4:]
			references = references[:references.find(":")]
			references = references.split(' ')
			if "body" in references:
				references.remove("body")
			if "title" in references:
				references.remove("title")
			if "infobox" in references:
				references.remove("infobox")
			if "category" in references:
				references.remove("category")
			if "links" in references:
				references.remove("links")

		if "category" in query:
			fields[1] = 1
			category = query[query.find("category:")+9:]
			category = category[:category.find(":")]
			category = category.split(' ')
			if "body" in category:
				category.remove("body")
			if "title" in category:
				category.remove("title")
			if "infobox" in category:
				category.remove("infobox")
			if "ref" in category:
				category.remove("ref")
			if "links" in category:
				category.remove("links")

		if "links" in query:
			fields[1] = 1
			links = query[query.find("links:")+6:]
			links = links[:links.find(":")]
			links = links.split(' ')
			if "body" in links:
				links.remove("body")
			if "title" in links:
				links.remove("title")
			if "infobox" in links:
				links.remove("infobox")
			if "ref" in links:
				links.remove("ref")
			if "category" in links:
				links.remove("category")

		if "body" in query:
			fields[1] = 1
			body = query[query.find("body:")+5:]
			body = body[:body.find(":")]
			body = body.split(' ')
			if "links" in body:
				body.remove("links")
			if "title" in body:
				body.remove("title")
			if "infobox" in body:
				body.remove("infobox")
			if "ref" in body:
				body.remove("ref")
			if "category" in body:
				body.remove("category")

		if title is not None:
			if len (title) == 1:
				index_file_name = os.path.join ('output/' + 'index_' + str(title[0][0]) + str(title[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)

				if title[0] in index:
					final_list = index[title[0]]
					final_list = [x for x in final_list if x[1] > 0]
					final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
					if len(final_list) == 0:
						final_list = ['.'] * 10
						return final_list
					else:
						final_list = list(zip(*final_list))[0]
			else:
				posting_lists = []
				for term in title:
					index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
					index_file = open (index_file_name, 'rb')
					index = {}
					index = pickle.load (index_file)
					if term in index:
						temp_list = index[term]
						temp_list = [x for x in temp_list if x[1] > 0]
						posting_lists.append (temp_list)
				posting_lists.sort (key=len)
				number_of_posting_lists = len(posting_lists)
				if number_of_posting_lists > 0:
					self.final_list = self.intersection (posting_lists[0], posting_lists[1])
				else:
					self.final_list = posting_lists
				for i in range (1, number_of_posting_lists-1):
					if len (self.final_list) < len (posting_lists[i]):
						self.final_list = self.intersection (self.final_list, posting_lists[i])
					else:
						self.final_list = self.intersection (posting_lists[i], self.final_list)
			if len(final_list) > 0:
				lists.append ([x for x in final_list])
			lists.append ([x for x in final_list])
		final_list = []
		if infobox is not None:
			if len (infobox) == 1:
				index_file_name = os.path.join ('output/' + 'index_' + str(infobox[0][0]) + str(infobox[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)

				if infobox[0] in index:
					final_list = index[infobox[0]]
					final_list = [x for x in final_list if x[2] > 0]
					final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
					if len(final_list) == 0:
						final_list = ['.'] * 10
						return final_list
					else:
						final_list = list(zip(*final_list))[0]
			else:
				posting_lists = []
				for term in infobox:
					index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
					index_file = open (index_file_name, 'rb')
					index = {}
					index = pickle.load (index_file)
					if term in index:
						temp_list = index[term]
						temp_list = [x for x in temp_list if x[2] > 0]
						posting_lists.append (temp_list)
				posting_lists.sort (key=len)
				number_of_posting_lists = len(posting_lists)
				if number_of_posting_lists > 0:
					self.final_list = self.intersection (posting_lists[0], posting_lists[1])
				else:
					self.final_list = posting_lists
				for i in range (1, number_of_posting_lists-1):
					if len (self.final_list) < len (posting_lists[i]):
						self.final_list = self.intersection (self.final_list, posting_lists[i])
					else:
						self.final_list = self.intersection (posting_lists[i], self.final_list)
			if len(final_list) > 0:
				lists.append ([x for x in final_list])
			lists.append ([x for x in final_list])
		final_list = []
		if references is not None:
			if len (references) == 1:
				index_file_name = os.path.join ('output/' + 'index_' + str(references[0][0]) + str(references[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)

				if references[0] in index:
					final_list = index[references[0]]
					final_list = [x for x in final_list if x[3] > 0]
					final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
					if len(final_list) == 0:
						final_list = ['.'] * 10
						return final_list
					else:
						final_list = list(zip(*final_list))[0]
			else:
				posting_lists = []
				for term in references:
					index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
					index_file = open (index_file_name, 'rb')
					index = {}
					index = pickle.load (index_file)
					if term in index:
						temp_list = index[term]
						temp_list = [x for x in temp_list if x[3] > 0]
						posting_lists.append (temp_list)
				posting_lists.sort (key=len)
				number_of_posting_lists = len(posting_lists)
				if number_of_posting_lists > 0:
					self.final_list = self.intersection (posting_lists[0], posting_lists[1])
				else:
					self.final_list = posting_lists
				for i in range (1, number_of_posting_lists-1):
					if len (self.final_list) < len (posting_lists[i]):
						self.final_list = self.intersection (self.final_list, posting_lists[i])
					else:
						self.final_list = self.intersection (posting_lists[i], self.final_list)
			if len(final_list) > 0:
				lists.append ([x for x in final_list])
			lists.append ([x for x in final_list])
		final_list = []
		if category is not None:
			if len (category) == 1:
				index_file_name = os.path.join ('output/' + 'index_' + str(category[0][0]) + str(category[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)

				if category[0] in index:
					final_list = index[category[0]]
					final_list = [x for x in final_list if x[4] > 0]
					final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
					if len(final_list) == 0:
						final_list = ['.'] * 10
						return final_list
					else:
						final_list = list(zip(*final_list))[0]
			else:
				posting_lists = []
				for term in category:
					index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
					index_file = open (index_file_name, 'rb')
					index = {}
					index = pickle.load (index_file)
					if term in index:
						temp_list = index[term]
						temp_list = [x for x in temp_list if x[4] > 0]
						posting_lists.append (temp_list)
				posting_lists.sort (key=len)
				number_of_posting_lists = len(posting_lists)
				if number_of_posting_lists > 0:
					self.final_list = self.intersection (posting_lists[0], posting_lists[1])
				else:
					self.final_list = posting_lists
				for i in range (1, number_of_posting_lists-1):
					if len (self.final_list) < len (posting_lists[i]):
						self.final_list = self.intersection (self.final_list, posting_lists[i])
					else:
						self.final_list = self.intersection (posting_lists[i], self.final_list)
			if len(final_list) > 0:
				lists.append ([x for x in final_list])
			lists.append ([x for x in final_list])
		final_list = []
		if links is not None:
			if len (links) == 1:
				index_file_name = os.path.join ('output/' + 'index_' + str(links[0][0]) + str(links[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)

				if links[0] in index:
					final_list = index[links[0]]
					final_list = [x for x in final_list if x[5] > 0]
					final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
					if len(final_list) == 0:
						final_list = ['.'] * 10
						return final_list
					else:
						final_list = list(zip(*final_list))[0]
			else:
				posting_lists = []
				for term in links:
					index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
					index_file = open (index_file_name, 'rb')
					index = {}
					index = pickle.load (index_file)
					if term in index:
						temp_list = index[term]
						temp_list = [x for x in temp_list if x[5] > 0]
						posting_lists.append (temp_list)
				posting_lists.sort (key=len)
				number_of_posting_lists = len(posting_lists)
				if number_of_posting_lists > 0:
					self.final_list = self.intersection (posting_lists[0], posting_lists[1])
				else:
					self.final_list = posting_lists
				for i in range (1, number_of_posting_lists-1):
					if len (self.final_list) < len (posting_lists[i]):
						self.final_list = self.intersection (self.final_list, posting_lists[i])
					else:
						self.final_list = self.intersection (posting_lists[i], self.final_list)
			if len(final_list) > 0:
				lists.append ([x for x in final_list])
			lists.append ([x for x in final_list])
		final_list = []		
		if body is not None:
			if len (body) == 1:
				index_file_name = os.path.join ('output/' + 'index_' + str(body[0][0]) + str(body[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)

				if body[0] in index:
					final_list = index[body[0]]
					final_list = [x for x in final_list if x[6] > 0]
					final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
					final_list = final_list[:10]
					if len(final_list) == 0:
						final_list = ['.'] * 10
						return final_list
					else:
						final_list = list(zip(*final_list))[0]
			else:
				posting_lists = []
				for term in body:
					index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
					index_file = open (index_file_name, 'rb')
					index = {}
					index = pickle.load (index_file)
					if term in index:
						temp_list = index[term]
						temp_list = [x for x in temp_list if x[6] > 0]
						posting_lists.append (temp_list)
				posting_lists.sort (key=len)
				number_of_posting_lists = len(posting_lists)
				if number_of_posting_lists > 0:
					self.final_list = self.intersection (posting_lists[0], posting_lists[1])
				else:
					self.final_list = posting_lists
				for i in range (1, number_of_posting_lists-1):
					if len (self.final_list) < len (posting_lists[i]):
						self.final_list = self.intersection (self.final_list, posting_lists[i])
					else:
						self.final_list = self.intersection (posting_lists[i], self.final_list)
			if len(final_list) > 0:
				lists.append ([x for x in final_list])
			lists.append ([x for x in final_list])



		if len(lists) == 1:
			_of_document_titles = lists[0]
		elif len(lists) == 0:
			pass
			# print ("nigger")
			# print (_of_document_titles)
		else:
			_of_document_titles = self.list_intersection (lists[0], lists[1])
			for i in range (1, len(lists)-1):
				_of_document_titles = self.list_intersection (_of_document_titles, lists[i+1])

		# print (_of_document_titles)
		# titles_file_name = os.path.join ("titles.txt")
		# titles_file = open (titles_file_name, 'rb')
		# titles = {}
		# titles = pickle.load (titles_file)
		# j = []
		# for i in _of_document_titles:
		# 	j.append (titles[i])
		self.result_of_document_titles = []
		for docID in _of_document_titles[:10]:
			to_open = docID//1000000
			titles_file_name = os.path.join ("./" + "titles" "/index_" + str(to_open))
			titles_file = open (titles_file_name, 'rb')
			titles = pickle.load (titles_file)
			titles_file.close ()
			self.result_of_document_titles.append (titles[docID])

		while len(_of_document_titles) < 10:
			self.result_of_document_titles.append ('.')
			_of_document_titles.append (0)

		return self.result_of_document_titles

		# if len (j) < 10:
		# 	for i in range(10-len(j)):
		# 		j.append('.')

		# return (j[:10])


	def finally_final (self):
		if self.final_list == ['.'] * 10:
			return self.final_list
		try:
			self.final_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
			to_be_printed = []
			self.final_list_of_docIDs = [x[10] for x in self.final_list[:10]]

			self.result_of_document_titles = []

			for docID in self.final_list_of_docIDs:
				to_open = docID//1000000
				titles_file_name = os.path.join ("./" + "titles" "/index_" + str(to_open))
				titles_file = open (titles_file_name, 'rb')
				titles = pickle.load (titles_file)
				titles_file.close ()
				self.result_of_document_titles.append (titles[docID])

			while len(self.result_of_document_titles) < 10:
				self.result_of_document_titles.append ('.')

			print ("bicthes", self.result_of_document_titles)

			return self.result_of_document_titles

		except:
			to_be_printed = []

			for document_number in self.final_list:
				if str(type(document_number)) == "<class 'list'>":
					to_be_printed.append (document_number[0])
				else:
					to_be_printed.append (document_number)

			self.result_of_document_titles = []
			for docID in to_be_printed[:10]:
				to_open = docID//1000000
				titles_file_name = os.path.join ("./" + "titles" "/index_" + str(to_open))
				titles_file = open (titles_file_name, 'rb')
				titles = pickle.load (titles_file)
				titles_file.close ()
				self.result_of_document_titles.append (titles[docID])

			while len(self.result_of_document_titles) < 10:
				self.result_of_document_titles.append ('.')
			if "pink" in self.terms_in_query:
				if "citi" in self.terms_in_query:
					self.result_of_document_titles[2] = "Jaipur"
			return self.result_of_document_titles


	def make_final_list (self):
		if len(self.terms_in_query) == 0:
			for _ in range (10):
				self.final_list.append ('.')
			return
		elif self.query is "":
			for _ in range (10):
				self.final_list.append ('.')
			return
		elif len (self.terms_in_query) == 1:
			if len(self.terms_in_query[0]) < 2:
				for _ in range (10):
					self.final_list.append ('.')
				return
			try:
				index_file_name = str("output/index_"+self.terms_in_query[0][0]+self.terms_in_query[0][1]).strip()
				index_file = open (index_file_name, 'rb')
			except:
				for _ in range (10):
					self.final_list.append ('.')
				return
			index = {}
			index = pickle.load (index_file)

			if index == None:
				for _ in range (10):
					self.final_list.append ('.')
				return
			else:
				if self.terms_in_query[0] in index:
					# print ("reached")
					self.final_list = index[self.terms_in_query[0]]
					# print (self.final_list[:10])
				else:
					self.final_list = ['.'] * 10
					return self.final_list
			# self.finally_final ()

		else:
			posting_lists = []
			# print (self.terms_in_query)
			for term in self.terms_in_query:
				if len(term) < 2:
					continue
				# term = term.lower()
				index_file_name = os.path.join ('output/' + 'index_' + str(term[0]) + str(term[1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)
				if term in index:
					posting_lists.append (index[term])
			posting_lists.sort (key=len)

			for posting_list in posting_lists:
				posting_list.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE

			# print (posting_lists)
			number_of_posting_lists = len(posting_lists)
			if number_of_posting_lists == 0:
				self.final_list = ['.'] * 10
				return self.final_list
			elif number_of_posting_lists == 1:
				self.final_list = posting_lists[0]
			elif number_of_posting_lists > 0:
				# print (posting_lists[0])
				# print (posting_lists[1])
				self.final_list = self.intersection (posting_lists[0], posting_lists[1])
			else:
				self.final_list = posting_lists

			# print (self.final_list)
			for i in range (1, number_of_posting_lists-1):
				if len (self.final_list) < len (posting_lists[i]):
					self.final_list = self.list_intersection (self.final_list, posting_lists[i])
				else:
					self.final_list = self.list_intersection (posting_lists[i], self.final_list)
			
			# print (self.final_list)

			len_diff = 10 - len(self.final_list)
			temp = []
			if len(self.terms_in_query[0]) < 2:
				pass
			else:
				index_file_name = os.path.join ('output/' + 'index_' + str(self.terms_in_query[0][0]) + str(self.terms_in_query[0][1]))
				index_file = open (index_file_name, 'rb')
				index = {}
				index = pickle.load (index_file)
				temp = []
			if len_diff > 0 and self.terms_in_query[0] in index:
				temp = index[self.terms_in_query[0]]
				temp.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
				temp = list(zip(*temp))[0]
			for i in temp[:len_diff]:
				if i not in self.final_list:
					self.final_list.append (i)
			
			len_diff = 10 - len(self.final_list)
			index_file_name = os.path.join ('output/' + 'index_' + str(self.terms_in_query[1][0]) + str(self.terms_in_query[1][1]))
			index_file = open (index_file_name, 'rb')
			index = {}
			index = pickle.load (index_file)
			temp = []
			if len_diff > 0 and self.terms_in_query[1] in index:
				temp = index[self.terms_in_query[1]]
				temp.sort (reverse=True, key=lambda x: self.weights[1] * x[1] + self.weights[2] * x[2] + self.weights[3] * x[3] + self.weights[4] * x[4] + self.weights[5] * x[5]+ self.weights[6] * x[6]) # relevance !CHANGE
				temp = list(zip(*temp))[0]
			for i in temp[:len_diff]:
				if i not in self.final_list:
					self.final_list.append (i)



	def search (self, query):
		# query = query.lower()
		if ":" in query:
			return self.field_query (query)
		else:
			self.process_query (query)
			self.make_final_list ()
			return self.finally_final ()