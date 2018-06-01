import requests
import argparse
import threading
from bs4 import BeautifulSoup
import datetime
import time

#debug level:
# 1=> basic message
# 2=> ALL message (include HTML source code)
debug=0

mutex = threading.Lock()

def scan_data(url, timeout, account_list):
    try:
	data = requests.get(url, timeout = timeout, cookies={'over18': '1'}, verify=True)
    except requests.Timeout as e:
        print "scan_data request timeout, error : " + str(e) +" , url = "+str(url)
	return

    if 'text/' not in data.headers['Content-Type']: #Content-Type
	if debug > 0:
	    print "Content-Type is not text/html, "+ data.headers['Content-Type'] +" ,scan_data return"
	return

    soup=BeautifulSoup(data.text.encode('utf-8'),'html.parser')
    if debug > 1:
	print soup.prettify()  

    #author
    author_data = soup.find('span', class_='article-meta-value')
    author_data=str(author_data)
    tmp_ptr=author_data.find('>')
    author=author_data[tmp_ptr+1:author_data.find(' ',tmp_ptr)]
    if author not in account_list:
	account_list[author]=0
    account_list[author]+=1

    #reply
    for content in soup.find_all('span', class_= 'f3 hl push-userid'):
	username = content.get_text()
	if username not in account_list:
	    account_list[username]=0
	account_list[username]+=1
	

def crawl(myitem):

    time.sleep(3) #sleep 3 second first to let url_scan find some website
    sleep_count=0
    crawl_count=0

    while True:
	if crawl_count % 50 == 0 and crawl_count != 0:
	    print "Still "+str(len(myitem['url']))+" in Thread "+str(myitem['index'])

	target_url = ""
	mutex.acquire()
	try:
	    if myitem['url'] != []:
		target_url = myitem['url'].pop(0)
	    else:
		if debug > 0:
		    print "Thread "+str(myitem['index'])+ " have nothing to do, sleep for "\
		    +str(myitem['sleep_time'])+" second"
		sleep_count+=1
	finally:
	    mutex.release()

	# too many idle for this thread
	if sleep_count > myitem['sleep_limit'] and myitem['sleep_limit'] != 0:
	    print "Thread "+str(myitem['index'])+" already sleep "+str(myitem['sleep_limit']) \
	    +" times, end this thread"
	    return

	if target_url == "":
	    time.sleep(myitem['sleep_time'])
	    continue
	elif debug > 0:
	    print "Thread "+str(myitem['index'])+" : " + target_url

	#start to scan the data we need
	scan_data(target_url, myitem['timeout'], myitem['account_list'])

	crawl_count +=1
    

def url_scan(argument):

    scanned_list={}
    url=[]
    url.append(argument['add_url'])
    try:
	tmp_data = requests.get(argument['add_url'], timeout = argument['timeout'], cookies={'over18': '1'}, verify=True)
    except requests.Timeout as e:
        print "First request timeout, error : " +str(e)+" , url = "+str(url)
	return

    tmp_string=tmp_data.url.split('/')
    root_url = tmp_string[2]
    basic_url = tmp_data.url[:tmp_data.url.find('/',8)]


    if debug > 0:
	print "root_url : "+root_url

    page_count=0
    timeout = argument['timeout']
    thread_number = argument['thread_number']

    max_pages=argument['max_pages']

    #initial each thread
    thread=[]
    thread_item=[]
    for i in range(0,thread_number):
	thread_item.append({})
	thread_item[i]['index']=i
	thread_item[i]['url']=[]
	thread_item[i]['timeout']=argument['timeout']
	thread_item[i]['sleep_limit']=argument['sleep_limit']
	thread_item[i]['sleep_time']=argument['sleep_time']
	thread_item[i]['account_list']={}
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

	if page_count % 50 ==0 and page_count != 0:
	    print "Already scan "+str(page_count)+" pages."
	
	#scan if there any other url we can find in this website
	try:
	    data = requests.get(target_url, timeout = timeout, cookies={'over18': '1'}, verify=True)
	except requests.Timeout as e:
	    print "url_scan request timeout, error : "+str(e) + " , url = "+str(target_url)
	    continue

	if 'text/' not in data.headers['Content-Type']: #Content-Type
	    if debug > 0:
		print "Content-Type is not text/html, "+ data.headers['Content-Type'] +" ,url_scan shift to next url"
	    continue
	else:
	    soup=BeautifulSoup(data.text.encode('utf-8'),'html.parser')
	    domain_name = str(data.url)[:str(data.url).rfind('/')]
	    if debug > 0:
		print "domain_name : "+domain_name
	    if debug > 1:
		print soup.prettify()
	

	page_list={}
	for link in soup.find_all('a'):
	    another_page=link.get('href')
	    if another_page is None: #Cannot find href in <a>
		continue

	    if "search" in another_page:
		continue

	    if 'http://' not in another_page and 'https://' not in another_page:
		if another_page[0] == '/':
		    another_page = basic_url + another_page
		elif another_page[0] == '.':
		    another_page = domain_name+"/"+another_page
		else:
		    "Unexcept url find, "+another_page
		    continue
	    elif root_url not in another_page:
		continue
	    
	    if another_page not in scanned_list:
		scanned_list[another_page]=1
		page_list[another_page]=1
		if debug > 0:
		    print "add url : "+str(another_page)
	
	mutex.acquire()
	try:
	    for link in page_list.keys():
		url.append(link)
		thread_item[thread_loop]['url'].append(link)
		thread_loop+=1
		if thread_loop >= thread_number:
		    thread_loop = 0
	finally:
	    mutex.release()

	page_count+=1
    
    #write url list to file
    urllist_file=open(argument['urllist_filename'],'w')
    sorted_url=sorted(url)
    for content in sorted_url:
	urllist_file.write(content+"\n")
    urllist_file.close()

    print "url scan finish, it scans "+str(page_count)+" urls"

    #wait for all thread end
    for i in range(0,thread_number):
	thread[i].join()

    #merge the account list in every threads
    account_merge={}
    for i in range(0, thread_number):
	for key,value in thread_item[i]['account_list'].iteritems():
	    if key not in account_merge:
		account_merge[key]=0
	    account_merge[key]+=value
	#release the memory
	thread_item[i]['account_list']={}

    #write account to file
    account_file=open(argument['account_filename'],'w')
    for key,value in account_merge.iteritems():
	account_file.write(str(key)+" : "+str(value)+"\n")

    account_file.close()

if __name__ == "__main__":
    date=str(datetime.datetime.now())
    default_account_filename=date[:19]+"-account"
    default_scan_url_filename=date[:19]+"-urllist"

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--add-url', required=True, help='The website url you want to crawler.')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Timeout for a url (second)')
    parser.add_argument('-n', '--thread-number', type=int, default=1, help='How many threads you need')
    parser.add_argument('-p', '--max-pages', type=int, default=500, help='The max webpages number')
    parser.add_argument('-l', '--sleep-limit', type=int, default=3, help='Thread idle limits, \
    if set to 0 means limitless')
    parser.add_argument('-s', '--sleep-time', type=int, default=3, help='Thread sleep time')
    parser.add_argument('--account-filename', default=default_account_filename, help='Filename to save account')
    parser.add_argument('--urllist-filename', default=default_scan_url_filename, help='Filename to save url list')
    args = vars(parser.parse_args())

    if debug > 0:
	print args   
    
    url_scan(args)
