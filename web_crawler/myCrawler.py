import urllib
import argparse
import threading
from bs4 import BeautifulSoup
import time

#debug level:
# 1=> basic message
# 2=> ALL message (include HTML source code)
debug=1

mutex = threading.Lock()

def crawl(myitem):
    while True:
	target_url = ""
	mutex.acquire()
	try:
	    if myitem['url'] != []:
		target_url = myitem['url'].pop(0)
	    else:
		print "Thread have nothing to do, sleep for 3 second"
	finally:
	    mutex.release()
	if target_url == "":
	    time.sleep(3)
	elif debug > 0:
	    print "Thread handle :" + target_url
    

def main_scan(argument):

    url=[]
    url.append(argument['add_url'])

    page_count=0
    thread_number = argument['thread_number']

    max_pages=argument['max_pages']

    #initial each thread
    thread=[]
    thread_item=[]
    for i in range(0,thread_number):
	thread_item.append({})
	thread_item[i]['url']=[]
	thread_item[i]['timeout']=argument['timeout']
	t = threading.Thread(target=crawl, args=(thread_item[i],))
	thread.append(t)

	if debug > 0:
	    print "thread "+str(i)+" is ready"
	
	t.start()
        
    #start to scan website and distribute them to threads
    #ignore the first website data
    thread_loop=0
    while page_count < max_pages:
	if url != []:
	    target_url = url.pop(0)
	else: 
	    break

	
	#scan if there any other url we can find in this website
	data=urllib.urlopen(target_url)
	if 'text/html' in data.info().headers[0]: #Content-Type
	    soup=BeautifulSoup(data.read(),'html.parser')
	    if debug > 1:
		print soup.prettify()
	    
	else: #not text, shift to next
	    continue
	
	domain_name = str(data.geturl())
	page_list={}
	for link in soup.find_all('a'):
	    another_page=link.get('href')
	    if 'http://' not in another_page and 'https://' not in another_page:
		if another_page[0] == '/':
		    another_page = another_page[1:]
		another_page = domain_name+another_page
	    page_list[another_page]=1
	
	mutex.acquire()
	try:
	    for link in page_list.keys():
		thread_item[thread_loop]['url'].append(link)
		thread_loop+=1
		if thread_loop >= thread_number:
		    thread_loop = 0
	finally:
	    mutex.release()
	
    for i in range(0,thread_number):
	thread[i].join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add-url', required=True, help='The website url you want to crawler.')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout for a url (second)')
    parser.add_argument('-n', '--thread-number', type=int, default=1, help='How many threads you need')
    parser.add_argument('-p', '--max-pages', type=int, default=500, help='The max webpages number')
    args = vars(parser.parse_args())

    if debug > 0:
	print args   
    
    main_scan(args)
