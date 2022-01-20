from tree_sitter import Language, Parser
from typing import List, Dict, Any, Set, Optional

class TestParser():
	
	def __init__(self, grammar_file, language):
		JAVA_LANGUAGE = Language(grammar_file, language)
		self.parser = Parser()
		self.parser.set_language(JAVA_LANGUAGE)


	def parse_file(self, file):
		"""
		Parses a java file and extract metadata of all the classes and methods defined
		"""

		#Build Tree
		with open(file, 'r') as content_file:
			try: 
				content = content_file.read()
				self.content = content
			except:
				return list()
		tree = self.parser.parse(bytes(content, "utf8"))
		classes = (node for node in tree.root_node.children if node.type == 'class_declaration')
		#print(tree.root_node.sexp())
		
		#Parsed Classes
		parsed_classes = list()

		#Classes
		for _class in classes:

			#Class metadata
			class_identifier = self.match_from_span([child for child in _class.children if child.type == 'identifier'][0], content).strip()
			class_metadata = self.get_class_metadata(_class, content)

			methods = list()

			#Parse methods
			for child in (child for child in _class.children if child.type == 'class_body'):
				for _, node in enumerate(child.children):
					if node.type == 'method_declaration' or node.type == 'constructor_declaration':	
						
						#Read Method metadata
						method_metadata = TestParser.get_function_metadata(class_identifier, node, content)
						methods.append(method_metadata)

			class_metadata['methods'] = methods
			parsed_classes.append(class_metadata)

		return parsed_classes



	@staticmethod
	def get_class_metadata(class_node, blob: str):
		"""
		Extract class-level metadata 
		"""
		metadata = {
			'identifier': '',
			'superclass': '',
			'interfaces': '',
			'fields': '',
			'argument_list': '',
			'methods':'',
		}

		#Superclass
		superclass = class_node.child_by_field_name('superclass')
		if superclass:
			metadata['superclass'] = TestParser.match_from_span(superclass, blob)
		
		#Interfaces
		interfaces = class_node.child_by_field_name('interfaces')
		if interfaces:
			metadata['interfaces'] = TestParser.match_from_span(interfaces, blob)
		
		#Fields
		fields = TestParser.get_class_fields(class_node, blob)
		metadata['fields'] = fields

		#Identifier and Arguments
		is_header = False
		for n in class_node.children:
			if is_header:
				if n.type == 'identifier':
					metadata['identifier'] = TestParser.match_from_span(n, blob).strip('(:')
				elif n.type == 'argument_list':
					metadata['argument_list'] = TestParser.match_from_span(n, blob)
			if n.type == 'class':
				is_header = True
			elif n.type == ':':
				break
		return metadata



	@staticmethod
	def get_class_fields(class_node, blob: str):
		"""
		Extract metadata for all the fields defined in the class
		"""
		
		body_node = class_node.child_by_field_name("body")
		fields = []
		
		for f in TestParser.children_of_type(body_node, "field_declaration"):
			field_dict = {}

			#Complete field
			field_dict["original_string"] = TestParser.match_from_span(f, blob)

			#Modifier
			modifiers_node_list = TestParser.children_of_type(f, "modifiers")
			if len(modifiers_node_list) > 0:
				modifiers_node = modifiers_node_list[0]
				field_dict["modifier"] = TestParser.match_from_span(modifiers_node, blob)
			else:
				field_dict["modifier"] = ""

			#Type
			type_node = f.child_by_field_name("type")
			field_dict["type"] = TestParser.match_from_span(type_node, blob)

			#Declarator
			declarator_node = f.child_by_field_name("declarator")
			field_dict["declarator"] = TestParser.match_from_span(declarator_node, blob)
			
			#Var name
			var_node = declarator_node.child_by_field_name("name")
			field_dict["var_name"] = TestParser.match_from_span(var_node, blob)

			fields.append(field_dict)

		return fields



	@staticmethod
	def get_function_metadata(class_identifier, function_node, blob: str):
		"""
		Extract method-level metadata 
		"""		
		metadata = {
			'identifier': '',
			'parameters': '',
			'modifiers': '',
			'return' : '',
			'body': '',
			'class': '',
			'signature': '',
			'full_signature': '',
			'class_method_signature': '',
			'testcase': '',
			'constructor': '',
		}

		# Parameters
		declarators = []
		TestParser.traverse_type(function_node, declarators, '{}_declaration'.format(function_node.type.split('_')[0]))
		parameters = []
		for n in declarators[0].children:
			if n.type == 'identifier':
				metadata['identifier'] = TestParser.match_from_span(n, blob).strip('(')
			elif n.type == 'formal_parameters':
				parameters.append(TestParser.match_from_span(n, blob))
		metadata['parameters'] = ' '.join(parameters)

		#Body
		metadata['body'] = TestParser.match_from_span(function_node, blob)
		metadata['class'] = class_identifier

		#Constructor
		metadata['constructor'] = False
		if "constructor" in function_node.type:
			metadata['constructor'] = True

		#Test Case
		modifiers_node_list = TestParser.children_of_type(function_node, "modifiers")
		metadata['testcase'] = False
		for m in modifiers_node_list:
			modifier = TestParser.match_from_span(m, blob)
			if '@Test' in modifier:
				metadata['testcase'] = True

		#Method Invocations
		invocation = []
		method_invocations = list()
		TestParser.traverse_type(function_node, invocation, '{}_invocation'.format(function_node.type.split('_')[0]))
		for inv in invocation:
			name = inv.child_by_field_name('name')
			method_invocation = TestParser.match_from_span(name, blob)
			method_invocations.append(method_invocation)
		metadata['invocations'] = method_invocations

		#Modifiers and Return Value
		for child in function_node.children:
			if child.type == "modifiers":
				metadata['modifiers']  = ' '.join(TestParser.match_from_span(child, blob).split())
			if("type" in child.type):
				metadata['return'] = TestParser.match_from_span(child, blob)
		
		#Signature
		metadata['signature'] = '{} {}{}'.format(metadata['return'], metadata['identifier'], metadata['parameters'])
		metadata['full_signature'] = '{} {} {}{}'.format(metadata['modifiers'], metadata['return'], metadata['identifier'], metadata['parameters'])
		metadata['class_method_signature'] = '{}.{}{}'.format(class_identifier, metadata['identifier'], metadata['parameters'])

		return metadata


	def get_method_names(self, file):
		"""
		Extract the list of method names defined in a file
		"""

		#Build Tree
		with open(file, 'r') as content_file: 
			content = content_file.read()
			self.content = content
		tree = self.parser.parse(bytes(content, "utf8"))
		classes = (node for node in tree.root_node.children if node.type == 'class_declaration')

		#Method names
		method_names = list()

		#Class
		for _class in classes:		
			#Iterate methods
			for child in (child for child in _class.children if child.type == 'class_body'):
				for _, node in enumerate(child.children):
					if node.type == 'method_declaration':
						if not TestParser.is_method_body_empty(node):
							
							#Method Name
							method_name = TestParser.get_function_name(node, content)
							method_names.append(method_name)

		return method_names


	@staticmethod
	def get_function_name(function_node, blob: str):
		"""
		Extract method name
		"""
		declarators = []
		TestParser.traverse_type(function_node, declarators, '{}_declaration'.format(function_node.type.split('_')[0]))
		for n in declarators[0].children:
			if n.type == 'identifier':
				return TestParser.match_from_span(n, blob).strip('(')


	@staticmethod
	def match_from_span(node, blob: str) -> str:
		"""
		Extract the source code associated with a node of the tree
		"""
		line_start = node.start_point[0]
		line_end = node.end_point[0]
		char_start = node.start_point[1]
		char_end = node.end_point[1]
		lines = blob.split('\n')
		if line_start != line_end:
			return '\n'.join([lines[line_start][char_start:]] + lines[line_start+1:line_end] + [lines[line_end][:char_end]])
		else:
			return lines[line_start][char_start:char_end]


	@staticmethod
	def traverse_type(node, results: List, kind: str) -> None:
		"""
		Traverses nodes of given type and save in results
		"""
		if node.type == kind:
			results.append(node)
		if not node.children:
			return
		for n in node.children:
			TestParser.traverse_type(n, results, kind)


	@staticmethod
	def is_method_body_empty(node):
		"""
		Check if the body of a method is empty
		"""
		for c in node.children:
			if c.type in {'method_body', 'constructor_body'}:
				if c.start_point[0] == c.end_point[0]:
					return True

	
	@staticmethod
	def children_of_type(node, types):
		"""
		Return children of node of type belonging to types

		Parameters
		----------
		node : tree_sitter.Node
			node whose children are to be searched
		types : str/tuple
			single or tuple of node types to filter

		Return
		------
		result : list[Node]
			list of nodes of type in types
		"""
		if isinstance(types, str):
			return TestParser.children_of_type(node, (types,))
		return [child for child in node.children if child.type in types]
