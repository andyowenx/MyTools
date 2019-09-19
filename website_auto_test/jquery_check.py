from selenium import webdriver
import argparse

def check_version(args, url_hash):
    #start Firefox
    driver = webdriver.Firefox()
    #print "jquery version: "+str(driver.execute_script("return jQuery().jquery"))
    for url,value in url_hash.iteritems():
	driver.get(url)
	value = {}
	"""
	try:
	    result = str(driver.execute_script("return jQuery.get('http://174.138.28.11/jquery_tester.html')"))
	except:
	    print "NOOOOOOOOOOOOOOOOOOOOOOO"
	"""
	if args.jquery == True:
	    try:
		value['jquery'] = str(driver.execute_script("return jQuery().jquery"))
	    except:
		value['jquery'] = "not implement"
	if args.jquery_ui == True:
	    try:
		version = str(driver.execute_script("return $.ui"))
	    except:
		value['jquery_ui'] = "not implement"

	    if version == "None":
		value['jquery_ui'] = "not implement"
		url_hash[url]=value
		continue

	    try:
		version = str(driver.execute_script("return $.ui.version"))
		value['jquery_ui'] = version
	    except:
		value['jquery_ui'] = "pre 1.6"
	
	url_hash[url]=value


def read_url_hash(args, url_hash):
    fd = open(args.url_filename, 'r')
    for content in fd:
	content=content[:-1]
	if "<url>" in content:
	    content = content.replace(']','[')
	    content = content.split('[')
	    url_hash[content[2]]=-1
    fd.close()

def read_config(args):
    fd = open(args.config_filename,'r')
    for content in fd:
	if content[0]=='#' or content == "":
	    continue
	content = content.split("=")
	if content[0] == 'url_filename':
	    args.url_filename=content[1][:-1]
	elif content[0] == 'no-jquery':
	    args.jquery=False
	elif content[0] == 'no-jquery-ui':
	    args.jquery_ui=False
	elif content[0] == 'max-pages':
	    args.max_pages=int(content[1][:-1])
	elif content[0] == 'task':
	    args.task=int(content[1][:-1])
	else:
	    print "[read_config] error configure arguments, "+str(content[0])
	

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursive check jQuery, jQuery-ui verion for website")
    parser.add_argument('--no-jquery', dest='jquery', action='store_false', help='Do not check jQuery version')
    parser.add_argument('--no-jquery-ui', dest='jquery_ui', action='store_false', help='Do not check jQuery ui version')
    parser.add_argument('-p', '--max-pages', type=int, nargs=1, default=500, help='Maximum page number, default is 500')
    parser.add_argument('-t', '--task', type=int, nargs=1, default=4, help='Task/Thread number, default is 4')
    parser.add_argument('-c', '--config-filename', type=str, nargs=1, default='config', help='Read the configuration in this file')
    parser.add_argument('-f', '--url_filename', type=str, default=None, help='Burp suite scan result')
    parser.set_defaults(jquery=True)
    parser.set_defaults(jquery_ui=True)
    parser.set_defaults(recursive=True)
    parser.set_defaults(boundary=True)
    args = parser.parse_args()
    
    fd = read_config(args)

    url_hash = {}

    read_url_hash(args, url_hash)
    check_version(args, url_hash)
    
    for url, version in url_hash.iteritems():
	print url
	if args.jquery == True:
	    print "\tjQuery version\t\t:\t"+str(version['jquery'])
	if args.jquery_ui == True:
	    print "\tjQuery ui version\t:\t"+str(version['jquery_ui'])
