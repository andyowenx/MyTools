import os
import csv
import netaddr

MAXLINE=100000

def write_csv_file(csv_hash, csv_writer):
    csv_list=[]
    for row,value in csv_hash.iteritems():
	content_list=[]
	row = row.split(",")
	for content in row:
	    content_list.append(content)
	csv_list.append(content_list)
    csv_writer.writerows(csv_list)
    csv_hash.clear()
    print "write "+str(MAXLINE)

def in_subnet(ip_str, subnet):
    for net in subnet:
	if netaddr.IPAddress(ip_str) in netaddr.IPNetwork(net):
	    return True
    return False

def open_files(location, filetype):
    if filetype not in location:
	return
    csv_file = open(location, "r")
    csv_row = csv.reader(csv_file)
    return csv_row

def remove_dns_row(csv_row, csv_hash,subnet, csv_writer):
    for row in csv_row:
	if row[0] == "" or row[1]=="" or in_subnet(row[0], subnet) is False:
	   continue
	else:
	    final = str(row[0])+","+str(row[1])
	    if final not in csv_hash:
		csv_hash[final]=1

	if len(csv_hash) > MAXLINE:
	    write_csv_file(csv_hash, csv_writer)

def remove_ip_row(csv_row, csv_hash, subnet, csv_writer):
    for row in csv_row:
	#src_ip, dst_ip, protocol is empty or row[0] is not IP address, ignore this data
	if row[0] =="" or row[2] == "" or row[4] =="" or in_subnet(row[0], subnet) is False:
	    continue
	if row[4] == "17" and row[1] == "" and row[3] =="": #dns
	    row[1] = 53
	    row[3] = 53
	final = str(row[0])+","+str(row[1])+","+str(row[2])+","+str(row[3])+","+str(row[4])
	if final not in csv_hash:
	    csv_hash[final]=1
	if len(csv_hash) > MAXLINE:
	    write_csv_file(csv_hash,csv_writer)

if __name__ == '__main__':
    csv_hash={}
    col_max = 16000 #excel column max
    file_root = "/home/owen/Downloads/packet_analysis"
    filetype="dns"
    dns_filename = "dns.csv"
    ip_filename = "ip.csv"

    files = os.listdir(file_root)
    #keep the IP address in one of these subnet
    subnet = []
    subnet.append("150.242.101.0/24")
    subnet.append("210.201.136.0/27")
    subnet.append("210.201.138.48/28")
    subnet.append("211.72.210.0/23")

    if filetype == "dns": #dns
	csv_fd = open(dns_filename, "w")
    else: #ip
	csv_fd = open(ip_filename, "w")
    csv_writer = csv.writer(csv_fd)

    for location in files:
	csv_row = open_files(file_root+"/"+location, filetype)
	if filetype ==  "dns" and csv_row is not None:
	    remove_dns_row(csv_row, csv_hash,subnet, csv_writer)
	elif filetype=="ip" and csv_row is not None:
	    remove_ip_row(csv_row, csv_hash,subnet, csv_writer)

    #last write
    write_csv_file(csv_hash, csv_writer)
    
