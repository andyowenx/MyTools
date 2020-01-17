########################################################
# Normalize the result xlsx files from beSOURCE        #
# Author : Owen					       #
# Email	 : owen@onwardsecurity.com		       #
########################################################

import os
import inspect
import openpyxl
import argparse
import anytree

#DEBUG = 0, Quiet Mode
#DEBUG = 1, only print error
#DEBUG = 2, print error and information
#DEBUG = 3, print error, information, and debug messages
DEBUG = 3 
log_file=None

def normalize_path(buf):
    buf['output']=[]

    item_number = 1
    root = anytree.Node('root')
    level = {}
    level[0] = root

    #skip the first line
    iter_input = iter(buf['input'].rows)
    next(iter_input)

    # A Tree struct to handle this part
    for row in iter_input:
	none_count=0
	for data in row:
	    if data.value == None:
		none_count+=1
	    else:
		value = str(data.value)
		if value.rfind('(') > 0:
		    value = value[:value.rfind('(')-1]
		node = anytree.Node(value, parent=level[none_count-1])
		level[none_count]=node
		break
    for content in root.leaves:
	output = []
	output.append(item_number)
	output.append(str(content)[12:-2])
	buf['output'].append(output)
	item_number+=1

def normalize_vuln(buf, rule_buf):
    buf['output']=[]

    item_number=1
    target_vuln = ""
    target_level = ""
    target_file = ""

    #skip the first line
    iter_input = iter(buf['input'].rows)
    next(iter_input)

    for row in iter_input:
	none_count = 0
	for data in row:
	    if data.value == None:
		none_count += 1
	    elif none_count == 0: #VulnName
		cut_position = data.value.rfind('(')
		if cut_position != 0:
		    target_vuln = data.value[:cut_position-1]
		else:
		    target_vuln = data.value
		break
	    elif none_count == 1: #Vuln Level
		target_level = data.value.split(' ')[0]
		break
	    elif none_count == 2: #Vuln Filename
		target_file = data.value.split(' ')[0]
		none_count = 0
		break
	    elif none_count == 3: #Vuln path and Vuln line
		#Ignore Info
		if target_level == "Info.":
		    break
		#Ignore exclude rule
		elif "exclude_list" in rule_buf and target_vuln in rule_buf['exclude_list']:
		    break

		output = []

		if len(buf['output']) >= 1 and buf['output'][len(buf['output'])-1][1] != target_vuln:
		    item_number=1
		output.append(item_number)
		output.append(target_vuln)
		output.append(target_level)
		if row[4].value != None:
		    output.append(row[4].value+"/"+target_file)
		else:
		    output.append(target_file)
		output.append(row[5].value)
		buf['output'].append(output)

		item_number+=1

		break
	    else: # Unexcept
		func_info = inspect.stack()
		debug_log(func_info[0][3], func_info[0][2], 2, "Meet a unexcept row, None="+str(none_count)+", "+str(row))

def write_xlsx(filename, buf):
    wb = openpyxl.Workbook()
    ws = wb.active
    
    for content in buf['output']:
	ws.append(content)

    wb.save(filename)

def read_xlsx(filename, buf):
    try:
	wb = openpyxl.load_workbook(filename)
    except IOError:
	func_info = inspect.stack()
	debug_log(func_info[0][3], func_info[0][2], 1, "An IOError happened for "+filename)
	return False

    buf['input'] = wb['Sheet']
    wb.close()

    return True


def debug_log(func_name, line, level, message):

    if DEBUG == 0:
	return

    output = ""
    if level == 1 and DEBUG >=1:
	output += "[Error]"
    elif level == 2 and DEBUG >=2:
	output += "[Info]"
    elif level == 3 and DEBUG >=3:
	output += "[DEBUG]"
    else: #DEBUG is lower than level, skip this message
	return

    output += "[" + str(func_name) + "][" + str(line)+"]: "+str(message)
    if log_file is not None:
	log_file.write(output+"\n")
    else:
	print output


def main():
    parser = argparse.ArgumentParser(description="Normalize the result xlsx files from beSOURCE")
    parser.add_argument('-l', '--log_file', type=str, default=None, help='The file to save log messages, default configuration is STDOUT')
    parser.add_argument('-d','--debug_level', type=int, default=3, help='The Debug level, 0 is quite, 1 is error, 2 is information, 3 is debug')
    parser.add_argument('-v', '--vuln_xlsx', type=str, default=None, help='The xlsx file with vulnerabilities from beSOURCE' )
    parser.add_argument('-p', '--path_xlsx', type=str, default=None, help='The xlsx file with path data from beSOURCE')
    parser.add_argument('-r', '--rule_xlsx', type=str, default=None, help='The xlsx file with exclude vulnerable rules inside')
    parser.add_argument('--rewrite', dest='rewrite', action='store_true', help='If you set this, this program will output the result to the same file name. You will LOSE your original data. CAREFUL')
    parser.set_defaults(rewrite=False)
    parser.add_argument('--vuln_output', type=str, default='vuln_output.xlsx', help='The file name of the result of vulnerabilites, default is vuln_output.xlsx')
    parser.add_argument('--path_output', type=str, default='path_output.xlsx', help='The file name of the result of path data, default is path_output.xlsx')
    args = parser.parse_args()

    global DEBUG
    global log_file

    log_filename = args.log_file
    if log_filename is not None:
	log_file = open(log_filename, 'w')

    DEBUG = args.debug_level
    func_info = inspect.stack()
    debug_log(func_info[0][3], func_info[0][2], 2, "Debug level is "+str(DEBUG))

    if args.vuln_xlsx == None and args.path_xlsx == None:
	func_info = inspect.stack()
	debug_log(func_info[0][3], func_info[0][2], 1, "You did not provide either vuln_xlsx or path_xlsx, program quits")
	exit(0)


    if args.rewrite == True:
	args.vuln_output = args.vuln_xlsx
	args.path_output = args.path_xlsx
	func_info = inspect.stack()
	debug_log(func_info[0][3], func_info[0][2], 2, "Rewrite is enable, set output result to original filename")

    vuln_buf={}
    path_buf={}
    rule_buf={}

    #read the exclude rules
    if args.rule_xlsx != None and read_xlsx(args.rule_xlsx, rule_buf) != False:
	rule_buf['exclude_list']={}
	for row in rule_buf['input'].rows:
	    exclude_vuln = str(row[0].value).rstrip() #remove the space in the end of string
	    rule_buf['exclude_list'][exclude_vuln]=1

    #handle vulnerabilities
    if args.vuln_xlsx !=None and read_xlsx(args.vuln_xlsx, vuln_buf) != False:
	normalize_vuln(vuln_buf, rule_buf)
	write_xlsx(args.vuln_output, vuln_buf)
    #handle path
    if args.path_xlsx != None and read_xlsx(args.path_xlsx, path_buf) != False:
	normalize_path(path_buf)
	write_xlsx(args.path_output, path_buf)
    
if __name__ == '__main__':
    main()
