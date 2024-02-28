#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import math
import difflib

# String containing XML header information about podcast
XML = '''<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">

	<channel>
		<title>Rice Lake Bible Chapel Sermons</title>
		<link>https://ricelakebiblechapel.com/</link>
		<description>Preach the word; be diligent in season, out of season; reprove, rebuke, exhort, with all longsuffering and doctrine. -1 Tim. 2:9</description>
		<atom:link href="https://ricelakebiblechapel.com/speakers" rel="self" type="application/rss+xml"> </atom:link>
	    <itunes:summary>Rice Lake Bible Chapel is an autonomous fellowship of believers responsible directly to Jesus Christ who is the Head of the universal church. We are non-denominational in that we seek not to be divided from any other individual who has put their trust in the Lord Jesus Chrsit and seeks to honor Him.</itunes:summary>	
		<itunes:owner>
			<itunes:name>RLBC</itunes:name>
			<itunes:email>na.th.an@icloud.com</itunes:email>
		</itunes:owner>
		<itunes:author>RLBC</itunes:author>
		<itunes:image href="https://dl.dropboxusercontent.com/s/revi2cr9ilzany2/Church%2BOutline.jpg"> </itunes:image>

		<googleplay:block>yes</googleplay:block>
		<itunes:block>Yes</itunes:block>
		<language>en-US</language>

		<pubDate>Fri, 03 Feb 2023 18:00:03 GMT</pubDate>
		<lastBuildDate>Fri, 03 Feb 2023 18:00:03 GMT</lastBuildDate>
		<image>
			<url>https://raw.githubusercontent.com/na4n/pod/main/scripts/img.png</url>
			<title>Rice Lake Bible Chapel Sermons</title>
			<link>https://ricelakebiblechapel.com/</link>
		</image>
'''

# formats XML date and day of the week based on string input mm/dd/yyyy
# uses the doomsday algorithm to calculate day of the week based on date
def day_of_week(date):
    date_lst = date.split("/")
    day = int(date_lst[1])
    month = int(date_lst[0])
    year = int(date_lst[2])
    raw_year = int(date_lst[2])    
 
    t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    year -= month < 3
    
    day_of_week = (year + int(year/4) - int(year/100) + int(year/400) + t[month-1] + day) % 7
    
    day_lst = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] 
    month_lst = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    formatted_date = day_lst[day_of_week-1] + ", " + date_lst[1] + " " + month_lst[month-1] + " 20" + str(raw_year) + " 11:00:00 CST"
    
    return formatted_date

# creates a guid based on the date of a podcast, as far as I can tell
# this is meaningless
def guid_creation(date):
    out_string = ""
    
    for i in range(len(date)-1, -1, -1):
        out_string += str(ord(date[i]))
   
    return out_string

# finds the first occurrence of a digit in a string
# useful for retreiving the date out of differently formatted string titles
def find_first_digit(input_str):
    while(not input_str[0].isdigit()):
        input_str = input_str[1:]
    
    return input_str

# returns a standard mm/dd/yyyy formatting for variously formatted date strings
def find_date(input_str):
    input_str = find_first_digit(input_str) 
   
    input_str = input_str.replace('-', '/')    
    split_str = input_str.split("/")
    if(len(split_str[2]) == 3): 
       split_str[2] = split_str[2][:2]  

    if(len(split_str[0]) == 4):
        input_str = split_str[1] + "/" + split_str[2] + "/" + split_str[0][-2:]     
    else:
        input_str = split_str[0] + "/" + split_str[1] + "/" + split_str[2][-2:]   
    return input_str    

def create_output(divs):
    strng = XML
    
    for i in range(len(divs)): 
        element = divs[i]        
       
        if 'class' in element.attrs and 'sqs-audio-embed' in element['class']:
            date = find_date(str(element['data-title'])[-10:])
            title = element['data-title'].split(" - ")[0] + "&#8211;" + element['data-author']
            
            if("(" in title or ")" in title):
                title = title.replace("(", "&#40;")  
                title = title.replace(")", "&#41;")
                title = title.replace("&", "&#38;")

            if(title[0] == " "):
                title = title[1:]

            url = element['data-url']
            length = element['data-duration-in-ms'] 
            formatted_date = day_of_week(date)

            length = str(math.ceil(int(length) / 1000))
            
            item = "\n\t\t<item>\n\t\t\t<title>" + title + "</title>\n\t\t\t<link>https://ricelakebiblechapel.com/speakers</link>\n\t\t\t<enclosure type=\"audio/mpeg\" length=\"" + length + "\" url=\"" + url + "\" />\n\t\t\t<guid isPermaLink=\"false\">" + guid_creation(date) + "</guid>\n\t\t\t<pubDate>" + formatted_date + "</pubDate>\n\t\t\t<itunes:duration>" + length + "</itunes:duration>\n\t\t</item>\n" 
            
            strng += item
    strng += "\n\t</channel>\n</rss>"
    
    return strng

# the big boy, finds every audio file on the sermons site (searches for a 
# sqs-audio-embed class tag under every div) then uses sermon info to 
# format name, date, mp3 url, and length of sermon into RSS feed, adds
# to the global rss variable at the top and outputs everything to a 
# feed.rss file
def main():
    global XML

    site = requests.get('https://www.ricelakebiblechapel.com/speakers')
    soup = BeautifulSoup(site.text, 'lxml')
    divs = soup.find_all('div')

    out = create_output(divs)
 
    file = open("feed.rss", "w+")
    file.write(out)
    file.close()
   
if __name__ == '__main__': #supposedly standard
    main()

