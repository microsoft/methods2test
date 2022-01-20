import os
import csv
import json
import argparse
import subprocess
import difflib
import shutil
import multiprocessing
import tqdm
import copy
from TestParser import TestParser



def analyze_project(repo_git, repo_id, grammar_file, tmp, output):
	"""
	Analyze a single project
	"""
	repo = {}
	repo["url"] = repo_git
	repo["repo_id"] = repo_id

	#Create folders
	os.makedirs(tmp, exist_ok=True)
	#os.chdir(tmp)
	repo_path = os.path.join(tmp, str(repo_id))
	repo_out = os.path.join(output, str(repo_id))
	os.makedirs(repo_out, exist_ok=True)

	#Clone repo
	print("Cloning repository...")
	subprocess.call(['git', 'clone', repo_git, repo_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	#Run analysis
	language = 'java'
	print("Extracting and mapping tests...")
	tot_mtc = find_map_test_cases(repo_path, grammar_file, language, repo_out, repo)
	(tot_tclass, tot_tc, tot_tclass_fclass, tot_mtc) = tot_mtc
	
	#Delete
	shutil.rmtree(repo_path, ignore_errors=True)

	#Print Stats
	print("---- Results ----")
	print("Test Classes: " + str(tot_tclass))
	print("Mapped Test Classes: " + str(tot_tclass_fclass))
	print("Test Cases: " + str(tot_tc))
	print("Mapped Test Cases: " + str(tot_mtc))



def find_map_test_cases(root, grammar_file, language, output, repo):
	"""
	Finds test cases using @Test annotation
	Maps Test Classes -> Focal Class
	Maps Test Case -> Focal Method
	"""
	#Logging
	log_path = os.path.join(output, "log.txt")
	log = open(log_path, "w")

	#Move to folder
	if os.path.exists(root):
		os.chdir(root)
	else:
		return 0, 0, 0, 0

	#Test Classes
	try:
		result = subprocess.check_output(r'grep -l -r @Test --include \*.java', shell=True)
		tests = result.decode('ascii').splitlines()
	except:
		log.write("Error during grep" + '\n')
		return 0, 0, 0, 0
	
	#Java Files
	try:
		result = subprocess.check_output(['find', '-name', '*.java'])
		java = result.decode('ascii').splitlines()
		java = [j.replace("./", "") for j in java]
	except:
		log.write("Error during find" + '\n')
		return 0, 0, 0, 0

	#Potential Focal Classes
	focals = list(set(java) - set(tests))
	focals = [f for f in focals if not "src/test" in f]
	focals_norm = [f.lower() for f in focals]
	
	log.write("Java Files: " + str(len(java)) + '\n')
	log.write("Test Classes: " + str(len(tests)) + '\n')
	log.write("Potential Focal Classes: " + str(len(focals)) + '\n')
	log.flush()

	#Matched tests
	mapped_tests = {}

	#Map Test Class -> Focal Class
	log.write("Perfect name matching analysis" '\n')
	for test in tests:
		tests_norm = test.lower().replace("/src/test/", "/src/main/")
		tests_norm = tests_norm.replace("test", "")
		
		if tests_norm in focals_norm:
			index = focals_norm.index(tests_norm)
			focal = focals[index]
			mapped_tests[test] = focal

	log.write("Perfect Matches Found: " + str(len(mapped_tests)) + '\n')

	#Stats
	tot_tclass = len(tests)
	tot_tclass_fclass = len(mapped_tests)
	tot_tc = 0
	tot_mtc = 0

	#Map Test Case -> Focal Method
	log.write("Mapping test cases" '\n')
	mtc_list = list()
	parser = TestParser(grammar_file, language)
	for test, focal in mapped_tests.items():
		log.write("----------" + '\n')
		log.write("Test: " + test + '\n')
		log.write("Focal: " + focal + '\n')

		test_cases = parse_test_cases(parser, test)
		focal_methods = parse_potential_focal_methods(parser, focal)
		tot_tc += len(test_cases)

		mtc = match_test_cases(test, focal, test_cases, focal_methods, log)
		
		mtc_size = len(mtc)
		tot_mtc += mtc_size
		if mtc_size > 0:
			mtc_list.append(mtc)
	

	#Export Mapped Test Cases
	if len(mtc_list) > 0:
		export_mtc(repo, mtc_list, output)

	#Print Stats
	log.write("==============" + '\n')
	log.write("Test Classes: " + str(tot_tclass) + '\n')
	log.write("Mapped Test Classes: " + str(tot_tclass_fclass) + '\n')
	log.write("Test Cases: " + str(tot_tc) + '\n')
	log.write("Mapped Test Cases: " + str(tot_mtc) + '\n')

	log.close()
	return tot_tclass, tot_tc, tot_tclass_fclass, tot_mtc


def parse_test_cases(parser, test_file):
	"""
	Parse source file and extracts test cases
	"""
	parsed_classes = parser.parse_file(test_file)

	test_cases = list()

	for parsed_class in parsed_classes:
		for method in parsed_class['methods']:
			if method['testcase']:

				#Test Class Info
				test_case_class = dict(parsed_class)
				test_case_class.pop('methods')
				test_case_class.pop('argument_list')
				test_case_class['file'] = test_file
				method['class'] = test_case_class

				test_cases.append(method)
	
	return test_cases


def parse_potential_focal_methods(parser, focal_file):
	"""
	Parse source file and extracts potential focal methods (non test cases)
	"""
	parsed_classes = parser.parse_file(focal_file)

	potential_focal_methods = list()

	for parsed_class in parsed_classes:
		for parsed_method in parsed_class['methods']:
			method = dict(parsed_method)
			if not method['testcase']: #and not method['constructor']:

				#Class Info
				focal_class = dict(parsed_class)
				focal_class.pop('argument_list')

				focal_class['file'] = focal_file
				method['class'] = focal_class

				potential_focal_methods.append(method)
	
	return potential_focal_methods



def match_test_cases(test_class, focal_class, test_cases, focal_methods, log):
	"""
	Map Test Case -> Focal Method
	It relies on two heuristics:
	- Name: Focal Method name is equal to Test Case name, except for "test"
	- Unique Method Call: Test Case invokes a single method call within the Focal Class
	"""
	#Mapped Test Cases
	mapped_test_cases = list()

	focals_norm = [f['identifier'].lower() for f in focal_methods]
	for test_case in test_cases:
		test_case_norm = test_case['identifier'].lower().replace("test", "")
		log.write("Test-Case: " + test_case['identifier'] + '\n')

		#Matching Strategies
		if test_case_norm in focals_norm:
			#Name Matching
			index = focals_norm.index(test_case_norm)
			focal = focal_methods[index]
			
			mapped_test_case = {}
			mapped_test_case['test_class'] = test_class
			mapped_test_case['test_case'] = test_case
			mapped_test_case['focal_class'] = focal_class
			mapped_test_case['focal_method'] = focal

			mapped_test_cases.append(mapped_test_case)
			log.write("> Found Focal-Method:" + focal['identifier'] + '\n')
		
		else:
			#Single method invoked that is in the focal class
			invoc_norm = [i.lower() for i in test_case['invocations']]
			overlap_invoc = list(set(invoc_norm).intersection(set(focals_norm)))
			if len(overlap_invoc) == 1:

				index = focals_norm.index(overlap_invoc[0])
				focal = focal_methods[index]

				mapped_test_case = {}
				mapped_test_case['test_class'] = test_class
				mapped_test_case['test_case'] = test_case
				mapped_test_case['focal_class'] = focal_class
				mapped_test_case['focal_method'] = focal

				mapped_test_cases.append(mapped_test_case)
				log.write("> [Single-Invocation] Found Focal-Method:" + focal['identifier'] + '\n')
	
	log.write("+++++++++" + '\n')
	log.write("Test-Cases: " + str(len(test_cases)) + '\n')
	log.write("Focal Methods: " + str(len(focals_norm)) + '\n')
	log.write("Mapped Test Cases: " + str(len(mapped_test_cases)) + '\n')
	return mapped_test_cases


def read_repositories(json_file_path):
	"""
	Read the repository java file
	"""
	if os.path.isfile(json_file_path):
		data = json.loads(open(json_file_path).read())
	return data


def export_mtc(repo, mtc_list, output):
	"""
	Export a JSON file representing the Mapped Test Case (mtc)
	It contains info on the Test and Focal Class, and Test and Focal method
	"""

	mtc_id = 0
	for mtc_file in mtc_list:
		for mtc_p in mtc_file:
			mtc = copy.deepcopy(mtc_p)
			mtc['test_class'] = mtc['test_case'].pop('class')
			mtc['focal_class'] = mtc['focal_method'].pop('class')
			mtc['repository'] = repo

			#Clean Focal Class data
			for fmethod in mtc['focal_class']['methods']:
				fmethod.pop('body')
				fmethod.pop('class')
				fmethod.pop('invocations')

			mtc_file = str(repo["repo_id"]) + "_" + str(mtc_id) + ".json"
			json_path = os.path.join(output, mtc_file)
			export(mtc, json_path)
			mtc_id += 1

def export(data, out):
	"""
	Exports data as json file
	"""
	with open(out, "w") as text_file:
		data_json = json.dumps(data)
		text_file.write(data_json)	



def parse_args():
	"""
	Parse the args passed from the command line
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--repo_url", 
		type=str, 
		default="https://github.com/apache/hadoop",
		help="GitHub URL of the repo to analyze",
	)
	parser.add_argument(
		"--repo_id",
		type=str,
		default="23418517",
		help="ID used to refer to the repo",
	)
	parser.add_argument(
		"--grammar",
		type=str,
		default="java-grammar.so",
		help="Filepath of the tree-sitter grammar",
	)
	parser.add_argument(
		"--tmp",
		type=str,
		default="/tmp/tmp/",
		help="Path to a temporary folder used for processing",
	)
	parser.add_argument(
		"--output",
		type=str,
		default="/tmp/output/",
		help="Path to the output folder",
	)

	return vars(parser.parse_args())


def main():
	args = parse_args()
	repo_git = args['repo_url']
	repo_id = args['repo_id']
	grammar_file = args['grammar']
	tmp = args['tmp']
	output = args['output']
	
	analyze_project(repo_git, repo_id, grammar_file, tmp, output)

if __name__ == '__main__':
	main()