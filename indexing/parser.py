import xml.etree.ElementTree as etree
import os
from inverted_index import inverted_index
import pickle
import functools
import heapq
import ast
import shutil

class parser ():
	def __init__ (self, output_folder, stemmer, stopwords):		
		self.etree = etree
		self.stemmer = stemmer
		self.stopwords = stopwords
		self.output_folder = output_folder
		self.document_number = 0
		self.total_number_of_documents = 0
		self.index_number = 0
		self.titles = {}
		self.current_file = None
		# self.inverted_index_backup = inverted_index

		if not os.path.exists(str("./" + self.output_folder)): 
			os.makedirs(str("./" + self.output_folder))

		self.inverted_index = inverted_index ()
		self.kinds = {"title":1, "infobox":2, "references":3, "category":4, "links":5, "body":6}

	def is_digit_in_string (self, element):
		return any(i.isdigit() for i in element)

	def remove_value (self, element):
		if "=" in element:
			return element[element.find("=")+1:]
		return element

	def remove_extra_ref_in_links (self, element):
		if "<ref" in element:
			return element[:element.find('<ref')-4]
		return element

	def get_infobox (self, entireText):
		count = 2
		for idx, letter in enumerate (entireText):
			if letter == '{':
				count += 1
			if letter == '}':
				count -= 1
				if count == 0:
					return entireText[:idx]


	def parse (self, filename):
		for event, element in self.etree.iterparse (filename, events=('start', 'end')):
			tag_name = element.tag[43:]
			if event == "start":
				if tag_name == "title":
					self.document_number += 1
					self.total_number_of_documents += 1
			if event == "end": 
				if tag_name == "title":
					self.titles[self.total_number_of_documents] = element.text
					title = element.text.lower()
					to_replace = [('!', ' '), ('module:', ''), ('category:', ''), ('file:', ''), ('wikipedia:', ''), ('template:', ''), ('.png', ''), ('.jpeg', ''), ('.com', ''), ('.', ' '),('|', ' '), ('"', ''), ('\"', ''), ('=', ' '), ('#', ' '), (',', ''), ('\'', ''), ('/', ''), ('&', ''), ('*', ''), (':', ' '), ('<', ' '), ('>', ''), ('_', ' '), ('[', ''), (']', ''), ('(', ''), (')', ''), ('-', ' ')]
					title = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, title)
					terms_in_title = title.split(' ')
					terms_in_title = [x for x in terms_in_title if not self.stopwords.check_stopword (x)]
					for term in terms_in_title:
						term = self.stemmer.stem (term)
						if self.inverted_index.check_word_in_main_index (term) is True:
							self.inverted_index.add_word_to_main_index (term, self.total_number_of_documents, self.kinds["title"])
						else:
							self.inverted_index.add_new_word_to_main_index (term, self.total_number_of_documents, self.kinds["title"])
				
				if tag_name == "text":
					try:
						body = element.text.split ('\n')
						infobox_before_processing = ""
						references_before_processing = ""

						categories = [x for x in body if "[[Category" in x]
						links = [x for x in body if "== External" in x or "==External" in x or "== Links" in x]
												
						if "Infobox" in element.text:
							infobox_onwards = element.text[element.text.find("Infobox") + len("Infobox"):]
							infobox = self.get_infobox (infobox_onwards)

							if infobox is None:
								continue							

							infobox = infobox.lower()[1:].split('\n')

							infobox = "".join([x[x.find("=")+1:] for x in infobox if "=" in x and "coordinates" not in x and "{{" not in x and "http" not in x and "/" not in x and ".com" not in x and ".pdf" not in x and "www" not in x and ".org" not in x and ".net" not in x and "px" not in x])

							to_replace = [('!', ' '), ('.', ' '),('&ndash;', ' '), ('|', ' '), ('"', ''), ('=', ' '), ('#', ' '), ('{{', ' '), ('}}', ' '), (',', ''), ('\'', ''), ('/', ''), ('*', ''), (':', ''), ('<', ' '), ('>', ''), ('br', ''), ('small', ''), ('ref', ''), ('_', ' '), ('[', ''), (']', ''), ('(', ''), (')', ''), ('-', ' ')]
							
							infobox = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, infobox)
							infobox.replace ('-', ' ')
							infobox = infobox.split(' ')
							infobox = list(filter(None, infobox)) 
							infobox_before_processing = infobox

							infobox = [self.stemmer.stem (x) for x in infobox if not self.stopwords.check_stopword(x)]

							for term in infobox:
								if self.inverted_index.check_word_in_main_index (term) is True:
									self.inverted_index.add_word_to_main_index (term, self.total_number_of_documents, self.kinds["infobox"])
								else:
									self.inverted_index.add_new_word_to_main_index (term, self.total_number_of_documents, self.kinds["infobox"])

						if "References" in element.text:
							if "==References" in element.text:
								references = element.text[element.text.find("==References")+12:].lower()
								references = references[2:references[2:].find("==")]

								references = references[references.find("\n")+1:references.find("[[")]
								references_before_processing = references
								references = references[:references.find("==")]

								references = references.split ('|')
								references = "".join([x[x.find("=")+1:] for x in references])
								to_replace = [('{', ' '),('=', ' '),('>', ' '), ('<', ' '), ('"', ' '),('\'', ' '),('defaultsort', ' '),(':', ' '),('DEFAULTSORT', ' '), ('-', ' '), ('!', ' '), ('|', ' '), ('Reflist', ' '), ('reflist', ' '), ('}', ' ', ), ('Just', ''), ('without', ''), ('changing', ''), ('anything', ''), ('Doing', ''), ('will', ''), ('submit', ''), ('article', ''), ('submission', ''), ('review.', ''), ('Once', ''), ('saved', ''), ('this', ''), ('find', ''), ('new', ''), ('yellow', ''), ('"Review"', ''), ('"waiting"', ''), ('bottom', ''), ('submitted', ''), ('previously', ''), ('either', ''), ('old', ''), ('pink', ''), ('"Submission"', ''), ('"declined"', ''), ('grey', ''), ('"Draft"', ''), ('template', ''), ('still', ''), ('appear', ''), ('should', ''), ('ignore', ''), ('Again', ''), ('please', ''), ('"dont"', ''), ('change', ''), ('anything', ''), ('text', ''), ('box.', ''), ('Just', ''), ('press', ''), ('"Save', ''), ('page"', ''), ('button', ''), ('below.', '')]                                                                
								references = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, references)
								if "Taxonbar" in references:
										references = references[:references.find("Taxonbar")-2]
								references = "".join(references.split('\n')).split(' ')
								references_before_processing = references                                                                
								references = [x for x in references if "title" not in x and "=" not in x and "http" not in x and "/" not in x and ".com" not in x and ".pdf" not in x and "www" not in x and ".org" not in x and ".net" not in x and "html" not in x and "ref" not in x and "taxonbar" not in x and "from=" not in x]

								references = list(filter(None, references)) 

								references = [self.stemmer.stem (x) for x in references if not self.stopwords.check_stopword(x)]

								for term in references:
										if self.inverted_index.check_word_in_main_index (term) is True:
												self.inverted_index.add_word_to_main_index (term, self.total_number_of_documents, self.kinds["references"])
										else:
												self.inverted_index.add_new_word_to_main_index (term, self.total_number_of_documents, self.kinds["references"])

							elif "== References" in element.text:
									references = element.text[element.text.find("== References")+13:].lower()
									references = references[2:references[2:].find("==")]

									references = references[references.find("\n")+1:references.find("[[")]
									references = references[:references.find("==")]
									references = references.split ('|')
									references = "".join([x[x.find("=")+1:] for x in references if "=" in x])
									to_replace = [('{', ' '), ('>', ' '),('<', ' '), ('"', ' '),('\'', ' '),('defaultsort', ' '),(':', ' '),('DEFAULTSORT', ' '), ('-', ' '), ('!', ' '), ('|', ' '), ('Reflist', ' '), ('reflist', ' '), ('}', ' ', ), ('Just', ''), ('without', ''), ('changing', ''), ('anything', ''), ('Doing', ''), ('will', ''), ('submit', ''), ('article', ''), ('submission', ''), ('review.', ''), ('Once', ''), ('saved', ''), ('this', ''), ('find', ''), ('new', ''), ('yellow', ''), ('"Review"', ''), ('"waiting"', ''), ('bottom', ''), ('submitted', ''), ('previously', ''), ('either', ''), ('old', ''), ('pink', ''), ('"Submission"', ''), ('"declined"', ''), ('grey', ''), ('"Draft"', ''), ('template', ''), ('still', ''), ('appear', ''), ('should', ''), ('ignore', ''), ('Again', ''), ('please', ''), ('"dont"', ''), ('change', ''), ('anything', ''), ('text', ''), ('box.', ''), ('Just', ''), ('press', ''), ('"Save', ''), ('page"', ''), ('button', ''), ('below.', '')]
									references = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, references)
									
									if "Taxonbar" in references:
											references = references[:references.find("Taxonbar")-2]
									
									references = "".join(references.split('\n')).split(' ')
									references_before_processing = references                                                                
									
									references = [x for x in references if "title" not in x and "=" not in x and "http" not in x and "/" not in x and ".com" not in x and ".pdf" not in x and "www" not in x and ".org" not in x and ".net" not in x and "html" not in x and "ref" not in x and "taxonbar" not in x and "from=" not in x]
									references = list(filter(None, references)) 
									references = [x for x in references if not self.is_digit_in_string(x) ]

									references = [self.stemmer.stem (x) for x in references if not self.stopwords.check_stopword(x)]

									for term in references:
											if self.inverted_index.check_word_in_main_index (term) is True:
													self.inverted_index.add_word_to_main_index (term, self.total_number_of_documents, self.kinds["references"])
											else:
													self.inverted_index.add_new_word_to_main_index (term, self.total_number_of_documents, self.kinds["references"])
					
						infobox_before_processing = infobox_before_processing
						references_before_processing = references_before_processing
						body = list(set(body) - set(categories))
						body = list(set(body) - set(links))
						body = list(set(body) - set(infobox_before_processing))
						body = list(set(body) - set(references_before_processing))
						body = " ".join(body).lower()
						import re
						body = re.sub (r'\{{[^}}]*\}}', '', body)
						body = body.split('|')
						body = list(map(self.remove_value, body))
						body = [x for x in body if "=" not in x and "/" not in x and "align" not in x and "wikitable" not in x and "sortable" not in x]
						to_replace = [('[', ' '), ('\'', ' '), ('\'\'', ' '), ('\"', ' '), ('redirect', ' '),('br', ' '), ('*', ' '), ('.', ' '), ('?', ' '), (':', ' '), ('#', ' '), ('!', ' '), ('&nbsp;', ' '), (']', ' '), (',', ' '), ('|', ' '), ('(', ' '), (')', ' '), ('{', ' '), ('}', ' '), ('-', ' '), ('<', ' '), ('>', ' '), ('<ref', ''), ('<style', ''), ('Reflist', ''), ('reflist', ''), ('.jpg', ''), ('DEFAULTSORT', ' '), ('defaultsort', ' '), ]
						body = " ".join(body)
						body = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, body)
						body = body.split(' ')
						body = [x for x in body if not self.is_digit_in_string(x)]

						body = list(filter(None, body))
						body = [x for x in body if not self.stopwords.check_stopword(x)]
						body = [self.stemmer.stem (x) for x in body] 
						body = [self.inverted_index.add_word_to_main_index (x, self.total_number_of_documents, self.kinds["body"]) for x in body if self.inverted_index.check_word_in_main_index (x)]
						body = [self.inverted_index.add_new_word_to_main_index (x, self.total_number_of_documents, self.kinds["body"]) for x in body if not self.inverted_index.check_word_in_main_index (x)]

						if "[[Category" in element.text:
							location_of_category = element.text.find("[[Category")
							categories = element.text[location_of_category:location_of_category+100].split('\n') 
						categories = "".join(categories)
						to_replace = [('[', ' '),('*', ' '), ('&nbsp;', ' '), (']', ' '), ('|', ' '), ('Category:', ' '), ('(', ' '), (')', ' '), ]
						categories = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, categories)
						categories = categories.split ('<')
						categories = "".join([x for x in categories if "style=" not in x and "noinclude" not in x])
						categories = categories.split (' ')
						categories = list(filter(None, categories))
						categories = [x for x in categories if not self.is_digit_in_string(x) ]
						categories = [self.stemmer.stem (x) for x in categories if not self.stopwords.check_stopword(x)]
						for term in categories:
								if self.inverted_index.check_word_in_main_index (term) is True:
										self.inverted_index.add_word_to_main_index (term, self.total_number_of_documents, self.kinds["category"])
								else:
										self.inverted_index.add_new_word_to_main_index (term, self.total_number_of_documents, self.kinds["category"])

						if "External" or "external" in element.text:
							if "== External" in element.text:
								links = element.text[element.text.find("== External"):]
							elif "==External" in element.text:
								links = element.text[element.text.find("==External"):]
							elif "== Links" in element.text:
								links = element.text[element.text.find("== Links"):]
						links = links[:10]
						links = [x for x in links if "*" in x]
						links = list (map (self.remove_extra_ref_in_links, links))
						links = "".join(links)
						to_replace = [('[', ' '), ('{', ' '), ('}', ' '), ('*', ' '), ('"', ' '), ('&nbsp;', ' '), (']', ' '), (';', ' '), ('|', ' '), ('-', ' '), ('(', ' '), (')', ' '), ]
						links = functools.reduce (lambda a, kv: a.replace(*kv), to_replace, links)
						links = links.split(' ')
						links = [x for x in links if not x.isdigit() and "http" not in x and "/" not in x and ".com" not in x and ".gov" not in x and ".ca" not in x and ".in" not in x and ".pdf" not in x and "www" not in x and ".org" not in x and ".net" not in x]
						links = [x for x in links if not self.is_digit_in_string(x) ]
						links = list(map(self.remove_value, links))
						links = list(filter(None, links)) 
						links = [self.stemmer.stem (x) for x in links if not self.stopwords.check_stopword(x)]
						for term in links:
							if self.inverted_index.check_word_in_main_index (term) is True:
								self.inverted_index.add_word_to_main_index (term, self.total_number_of_documents, self.kinds["links"])
							else:
								self.inverted_index.add_new_word_to_main_index (term, self.total_number_of_documents, self.kinds["links"])
													
					except Exception as e:
						# print ("error")
						print (e)
						continue

				if tag_name == "page":
					element.clear ()
					# if (self.document_number % 100 == 0):
						# print ("indexed", self.document_number, "documents for index", self.index_number)


			if (self.document_number > 2000):
				self.document_number = 0
				index_file_name = os.path.join (str("./" + self.output_folder + "/index_" + str (self.index_number)))
				index_file = open (index_file_name, 'ab')
				self.inverted_index.main_index = dict (sorted (self.inverted_index.main_index.items()))
				print ("making index", self.index_number)
				# m = [(x, self.inverted_index.main_index[x]) for x in self.inverted_index.main_index]
				pickle.dump (self.inverted_index.main_index, index_file)
				index_file.close ()
				self.index_number += 1
				self.inverted_index = inverted_index ()

			
		
		if (self.document_number > 0):
			self.document_number = 0
			index_file_name = os.path.join (str("./" + self.output_folder + "/index_" + str (self.index_number)))
			index_file = open (index_file_name, 'ab')
			self.inverted_index.main_index = dict (sorted (self.inverted_index.main_index.items()))
			print ("making index", self.index_number)
			# m = [(x, self.inverted_index.main_index[x]) for x in self.inverted_index.main_index]
			pickle.dump (self.inverted_index.main_index, index_file)
			index_file.close ()
			self.index_number += 1
			self.inverted_index = inverted_index ()

		f = open("titles.txt", 'wb')
		pickle.dump (self.titles, f, -1)
		f.close()



		print ("there were", self.total_number_of_documents, "documents")

	def final(self):
		initials = "starting"
		for count in range (self.index_number+1):
			current_index_file =  open ("output/index_"+str(count), 'rb')
			current_index = {}
			try:
				current_index = pickle.load (current_index_file)
			except:
				continue

			for key in current_index:
				if not key.isalnum() or len(key) < 2:
					continue
				initials = key[0:2]

				index_file_name = os.path.join("output/" + "index_" + str(initials))
				try:
					index_file = open (index_file_name, 'rb')
					index = pickle.load (index_file)
				except:
					index_file_name = os.path.join("output/" + "index_" + str(initials))
					index_file = open (index_file_name, 'wb+')
					index = {}
				
				try:
					index[key].extend (current_index[key])
				except:
					index[key] = current_index[key]
				index_file = open (index_file_name, 'wb+')
				pickle.dump (index, index_file)

			current_index_file.close()

	def final (self):
		initials = "starting"
		# for count in range (self.index_number+1):
		for count in range (1):
			current_index_file_name = "output/index_"+str(count)
			current_index_file = open (current_index_file_name, 'rb')
			current_index = {}
			current_index = pickle.load (current_index_file)
			current_index_file.close ()

			for key in current_index:
				if not key.isalnum() or len(key) < 2:
					continue

				if initials != key[0:2]:
					if initials != "starting":
						try:
							index_file.close()
						except:
							pass
						index_file = open (index_file_name, 'wb')
						pickle.dump (index, index_file)
						index_file.close()
					initials = key[0:2]
					index_file_name = os.path.join ("output/" + "index_" + str(initials))

					try:
						index_file = open (index_file_name, 'rb')
					except:
						index_file = open (index_file_name, 'wb+')

					try:
						index = {}
						index = pickle.load (index_file)
					except:
						index = {}

				if key in index:
					print (index[key])
					print (current_index[key])
					print ()
					print ()
					print ()

				else:
					index[key] = current_index[key]
					
						






	# def merge_files (self):
		# a_file = open ("output/index_0", 'rb')
		# a = []
		# a = pickle.load (a_file)
		# a_file.close()

	# 	merged_file = open ('merged_file', "w")

	# 	number_of_indexes = 14

	# 	heapq.heapify (a)
	# 	for count in range(len(a)):
	# 		temp = heapq.heappop(a)
	# 		merged_file.write (str(temp) + '\n')

	# 	a.clear ()

	# 	flag = 1
	# 	existing_file = None
	# 	merged_file = None

	# 	for count in range (1, number_of_indexes+1):

	# 		print (count)

	# 		break_flag = 0
	# 		item_flag = 0
	# 		if flag == 1:
	# 			existing_file = open ('merged_file', 'r')
	# 			merged_file = open ('merged_file_2', 'w')
	# 			flag = 0
	# 		else:
	# 			existing_file = open ('merged_file_2', 'r')
	# 			merged_file = open ('merged_file', 'w')
	# 			flag = 1
	# 		# print ("output/index_" + str(count))
	# 		index_file_path = open ("output/index_" + str(count), 'rb')
	# 		index = []
	# 		index = pickle.load (index_file_path)
	# 		heapq.heapify (index)
	# 		index_file_path.close ()
	# 		temp1 = heapq.heappop(index)
	# 		temp2 = existing_file.readline()

	# 		while True:
	# 			if len(index) == 0:
	# 				break_flag = 1
	# 				break
	# 			if item_flag == 0:
	# 				temp1 = heapq.heappop(index)
	# 				temp2 = existing_file.readline()
	# 			elif item_flag == 1:
	# 				temp1 = heapq.heappop(index)
	# 			elif item_flag == 2:
	# 				temp2 = existing_file.readline()
	# 			if not temp2:
	# 				break_flag = 2
	# 				break
	# 			j = temp2[2:temp2.find('[')]
	# 			j = j[:j.find('\'')]
	# 			temp2 = temp2.strip()

	# 			if temp1[0] == j:
	# 				item_flag = 0
	# 				k = ast.literal_eval (temp2[temp2.find(", [[")+2:temp2.find("]])")+2])
	# 				temp1[1].extend (k)
	# 				merged_file.write (str(temp1) + '\n')
	# 			elif temp1[0] < j:
	# 				item_flag = 1
	# 				merged_file.write (str(temp1) + '\n')
	# 			elif temp1[0] > j:
	# 				item_flag = 2
	# 				merged_file.write ((temp2) + '\n')

	# 		if break_flag == 1:
	# 			while True:
	# 				temp2 = existing_file.readline()
	# 				if not temp2:
	# 					break
	# 				merged_file.write ((temp2) + '\n')
	# 		elif break_flag == 2:
	# 			while (len(index) > 0):
	# 				temp1 = heapq.heappop(index)
	# 				merged_file.write (str(temp1) + '\n')
			
	# 		existing_file.close()
	# 		merged_file.close()
	# 		os.remove (existing_file.name)

	# 	os.rename (merged_file.name, "inverted_index")
	# 	shutil.rmtree ("output")
	# 	os.mkdir ("output")

	# def apply_divide (self, lines):
	# 	lines = [x.strip() for x in lines]
	# 	lines = [x for x in lines if not x == ""]
	# 	if self.current_file is None:
	# 		self.current_file = str(lines[0][2]) + str(lines[0][3])
	# 	current_file_pointer = open (str("output/index_"+str(self.current_file)), 'ab')		
	# 	current_file_pointer.close()
	# 	if self.current_file is None:
	# 		self.current_file = str(lines[0][2]) + str(lines[0][3])
	# 	temp_index = {}
	# 	if os.path.getsize(str("output/index_"+str(self.current_file))) > 0:
	# 		temp_file_read = open(self.current_file, 'rb')
	# 		temp_index = pickle.load (temp_file_read)
	# 		temp_file_read.close()
	# 	current_file_pointer = open (str("output/index_"+self.current_file), 'ab')		
	# 	dict_words = {}
	# 	for line in lines:
	# 		if len(line) < 2:
	# 			continue
	# 		if '/' in str(line[2]) + str(line[3]):
	# 			continue
	# 		if str(line[2]) + str(line[3]) == current_file:
	# 			j = line[2:line.find('[')]
	# 			j = j[:j.find('\'')]
	# 			k = line.strip()
	# 			k = ast.literal_eval (k[k.find(", [[")+2:k.find("]])")+2])
	# 			dict_words[j] = k
	# 		else:
	# 			temp_index.update (dict_words)
	# 			pickle.dump (temp_index, current_file_pointer)
	# 			dict_words = {}
	# 			self.current_file = str(line[2]) + str(line[3])
	# 			if '/' in self.current_file:
	# 				continue
	# 			current_file_pointer.close()
	# 			current_file_pointer = open (str("output/index_"+self.current_file), 'ab')		

		# temp_index = {}
		# if os.path.getsize(current_file_pointer.name) > 0:
			# temp_file_read = open(current_file_pointer.name, 'rb')
			# temp_index = pickle.load (temp_file_read)
		# temp_index.update (dict_words)
		# if "war" in temp_index:
			# print ("actually in index", current_file_pointer)
		# pickle.dump (temp_index, current_file_pointer)	



	# def apply_divide (self, lines):
	# 	lines = [x.strip() for x in lines]
	# 	lines = [x for x in lines if not x == ""]
	# 	current_file = str(lines[0][2]) + str(lines[0][3])
	# 	current_file_pointer = open (str("output/index_"+current_file), 'ab')
	# 	temp_index = {}
	# 	if os.path.getsize(current_file_pointer.name) > 0:
	# 		temp_file_read = open(current_file_pointer.name, 'rb')
	# 		temp_index = pickle.load (temp_file_read)
	# 	# temp_index.update (dict_words)
	# 	dict_words = {}
	# 	for line in lines:
	# 		if len(line) < 2:
	# 			continue
	# 		if '/' in str(line[2]) + str(line[3]):
	# 			continue
	# 		if str(line[2]) + str(line[3]) == current_file:
	# 			j = line[2:line.find('[')]
	# 			j = j[:j.find('\'')]
	# 			k = line.strip()
	# 			k = ast.literal_eval (k[k.find(", [[")+2:k.find("]])")+2])
	# 			dict_words[j] = k
	# 		else:
	# 			# if "gandhi" in dict_words:
	# 				# print ("in index", current_file_pointer)
	# 			temp_index.update (dict_words)
	# 			if "war" in temp_index:
	# 				print ("in index", current_file_pointer)
	# 			pickle.dump (temp_index, current_file_pointer)
	# 			dict_words = {}
	# 			current_file = str(line[2]) + str(line[3])
	# 			if '/' in str(line[2]) + str(line[3]):
	# 				continue
	# 			current_file_pointer = open (str("output/index_"+current_file), 'ab')
	# 	temp_index = {}
	# 	if os.path.getsize(current_file_pointer.name) > 0:
	# 		temp_file_read = open(current_file_pointer.name, 'rb')
	# 		temp_index = pickle.load (temp_file_read)
	# 	temp_index.update (dict_words)
	# 	if "war" in temp_index:
	# 		print ("actually in index", current_file_pointer)
	# 	pickle.dump (temp_index, current_file_pointer)		

	# def divide_files (self):
	# 	merged_file = open ('inverted_index', "r")
	# 	BUFFER_SIZE = 20000
	# 	temp_lines = merged_file.readlines (BUFFER_SIZE)
	# 	while temp_lines:
	# 		self.apply_divide ([line for line in temp_lines])
	# 		temp_lines = merged_file.readlines (BUFFER_SIZE)
	# 	os.remove ('inverted_index')		
		
			





		


				
				
				




