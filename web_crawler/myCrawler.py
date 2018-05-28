import HTMLParser
import urllib
import argparse
import threading

debug=1

mutex = threading.Lock()

def crawl(myitem):
    print "a"

def main_scan(argument):
    url=[]
    url.append(argument['add_url'])
    page_count=0
    max_pages=argument['max_pages']
    thread_loop=0

    #initial each thread
    thread=[]
    thread_item=[]
    for i in range(0,argument['thread_number']):
	thread_item[i]={}
	thread_item[i]['url']=[]
	thread_item[i]['timeout']=argument['timeout']
	t = threading.Thread(target=crawl, args=(thread_item[i]))
	thread[i]=t

	if debug > 0:
	    print "thread "+str(i)+" is ready"
	
	t.start()
	
    #start to scan website and distribute them to threads
    while page_count < max_pages:
	mutex.acquire()
	try:
	    target_url = url.pop(0)
	    thread_item[thread_loop]['url'].append(target_url)
	finally:
	    mutex.release()
	
	thread_loop+=1
	if thread_loop >= argument['thread_num']:
	    thread_loop = 0
	
	#scan if there any other url we can find in this website
    
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
