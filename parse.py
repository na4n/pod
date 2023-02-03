from bs4 import BeautifulSoup
import requests

XML = '''<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" version="2.0">

	<channel>
		<title>Rice Lake Bible Chapel Sermons</title>
		<link>https://ricelakebiblechapel.com/</link>
		<description>Preach the word; be diligent in season, out of season; reprove, rebuke, exhort, with all longsuffering and doctrine. -1 Tim. 2:9</description>
		<atom:link href="https://ricelakebiblechapel.com/speakers" rel="self" type="application/rss+xml"> </atom:link>
		
		<itunes:owner>
			<itunes:name>RLBC</itunes:name>
			<itunes:email>na.th.an@icloud.com</itunes:email>
		</itunes:owner>
		<itunes:author>RLBC</itunes:author>
		<itunes:image href="https://images.squarespace-cdn.com/content/v1/55fc09f2e4b06df8abd1ba1d/1524265114635-R3NIHTYOVHZ7TBEY93J2/Church%2BOutline.png"> </itunes:image>

		<googleplay:block>yes</googleplay:block>
		<itunes:block>Yes</itunes:block>
		<language>en-US</language>

		<pubDate>Fri, 03 Feb 2023 18:00:03 GMT</pubDate>
		<lastBuildDate>Fri, 03 Feb 2023 18:00:03 GMT</lastBuildDate>
		<image>
			<url>https://images.squarespace-cdn.com/content/v1/55fc09f2e4b06df8abd1ba1d/1524265114635-R3NIHTYOVHZ7TBEY93J2/Church%2BOutline.png</url>
			<title>Rice Lake Bible Chapel Sermons</title>
			<link>https://ricelakebiblechapel.com/</link>
		</image>
'''

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

    formatted_date = day_lst[day_of_week-1] + ", " + date_lst[1] + " " + month_lst[month-1] + " 20" + str(raw_year) + " 01:00:00 GMT"
    
    return formatted_date

def guid_creation(date):
    out_string = ""
    
    for i in range(len(date)-1, -1, -1):
        out_string += str(ord(date[i]))
   
    return out_string
    
def find_first_digit(input_str):
    while(not input_str[0].isdigit()):
        input_str = input_str[1:]
    
    return input_str

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

def main():
    global XML

    site = requests.get('https://www.ricelakebiblechapel.com/speakers')
    soup = BeautifulSoup(site.text, 'lxml')
    result_set = soup.find_all('div')
    
    file = open("feed.rss", "w+")
    file.write(XML)
    for i in range(len(result_set)): #for element in result_set:
        element = result_set[i]        
       
        if 'class' in element.attrs and 'sqs-audio-embed' in element['class']:
            date = find_date(str(element['data-title'])[-10:])
            title = element['data-title'].split(" - ")[0] + "&#8211;" + element['data-author']
            
            if("(" in title or ")" in title):
                title = title.replace("(", "&#40;")  
                title = title.replace(")", "&#41;")
                title = title.replace("&", "&#38;")
#                print(title)

            if(title[0] == " "):
                title = title[1:]

            url = element['data-url']
            length = element['data-duration-in-ms'] 
            formatted_date = day_of_week(date)
            
            item = "\n\t\t<item>\n\t\t\t<title>" + title + "</title>\n\t\t\t<link>https://ricelakebiblechapel.com/speakers</link>\n\t\t\t<enclosure type=\"audio/mpeg\" length=\"" + length + "\" url=\"" + url + "\" />\n\t\t\t<guid isPermaLink=\"false\">" + guid_creation(date) + "</guid>\n\t\t\t<pubDate>" + formatted_date + "</pubDate>\n\t\t</item>\n" 
            
            file.write(item)
    file.write("\n\t</channel>\n</rss>")
        
if __name__ == '__main__':
    main()

