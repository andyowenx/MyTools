import os
import csv
import netaddr

def in_subnet(ip_str, subnet):
    for net in subnet:
	if netaddr.IPAddress(ip_str) in netaddr.IPNetwork(net):
	    return True
    return False

def open_files(location, filetype):
    if filetype not in location:
	return
    csv_file = open(location)
    csv_row = csv.reader(csv_file)
    return csv_row

def read_dns_file(csv_row, hlist,subnet):
    for row in csv_row:
	if row[0] == "" or in_subnet(row[0], subnet) is False:
	   continue
	elif row[0] is not "" and row[1] is not "":
	    if row[0] not in hlist:
		hlist[row[0]]={}
		hlist[row[0]][row[1]]=1
	    elif row[1] not in hlist[row[0]]:
		hlist[row[0]][row[1]]=1

def read_ip_file(csv_row, hlist, subnet):
    for row in csv_row:
	#src_ip, dst_ip, protocol is empty or row[0] is not IP address, ignore this data
	if row[0] =="" or row[2] == "" or row[4] =="" or in_subnet(row[0], subnet) is False:
	    continue
	if row[4] == "17" and row[1] == "" and row[3] =="": #dns
	    row[1] = 53
	    row[3] = 53
	final = str(row[0])+","+str(row[1])+","+str(row[2])+","+str(row[3])+","+str(row[4])
	if final not in hlist:
	    hlist[final] = 1

if __name__ == '__main__':
    hlist={}
    col_max = 16000 #excel column max
    file_root = "/home/owen/Downloads/packet_analysis"
    filetype="ip"
    dns_filename = "dns.csv"
    ip_filename = "ip.csv"

    files = os.listdir(file_root)
    #keep the IP address in one of these subnet
    subnet = []
    subnet.append("150.242.101.0/24")
    subnet.append("210.201.136.0/27")
    subnet.append("210.201.138.48/28")
    subnet.append("211.72.210.0/23")

    for location in files:
	csv_row = open_files(file_root+"/"+location, filetype)
	if filetype ==  "dns" and csv_row is not None:
	    read_dns_file(csv_row, hlist,subnet)
	elif filetype=="ip" and csv_row is not None:
	    read_ip_file(csv_row,hlist,subnet)

    sort_hlist = sorted(hlist.items(), key=lambda k: k[0])
    #fix hash table to csv format
    csv_list=[]
    if filetype=="dns":
	for key,value in sort_hlist:
	    content_list = []
	    content_list.append(key)
	    for domain in value.keys():
		content_list.append(domain)
		#More than 16000 columns in a row, add one more row for it
		if len(content_list) > col_max:
		    new_content_list=[]
		    new_content_list.append(content_list[0]) #same key
		    csv_list.append(content_list)
		    content_list=new_content_list
	    csv_list.append(content_list)
    else:
	for key, v in sort_hlist:
	    content_list=[]
	    key=key.split(",")
	    for value in key:
		content_list.append(value)
	    csv_list.append(content_list)
    
    #write to csv file
    if filetype == "dns":
	csv_fd = open(dns_filename, "w")
	csv_writer = csv.writer(csv_fd)
	csv_writer.writerows(csv_list)
    else:
	csv_fd = open(ip_filename, "w")
	csv_writer = csv.writer(csv_fd)
	csv_writer.writerows(csv_list)
    
