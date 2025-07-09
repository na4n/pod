#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import math
import html

# Corrected XML declaration and itunes:image format
XML = '''<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     version="2.0">

  <channel>
    <title>Rice Lake Bible Chapel Sermons</title>
    <link>https://ricelakebiblechapel.com/</link>
    <description>Preach the word; be diligent in season, out of season; reprove, rebuke, exhort, with all longsuffering and doctrine. -1 Tim. 2:9</description>
    <atom:link href="https://ricelakebiblechapel.com/speakers" rel="self" type="application/rss+xml"/>
    <itunes:summary>Rice Lake Bible Chapel is an autonomous fellowship of believers responsible directly to Jesus Christ who is the Head of the universal church. We are non-denominational in that we seek not to be divided from any other individual who has put their trust in the Lord Jesus Christ and seeks to honor Him.</itunes:summary>
    <itunes:owner>
      <itunes:name>RLBC</itunes:name>
      <itunes:email>na.th.an@icloud.com</itunes:email>
    </itunes:owner>
    <itunes:author>RLBC</itunes:author>
    <itunes:image href="https://raw.githubusercontent.com/na4n/pod/main/scripts/resources/img.png"/>
    <googleplay:block>yes</googleplay:block>
    <itunes:block>Yes</itunes:block>
    <language>en-US</language>
    <pubDate>Fri, 03 Feb 2023 18:00:03 GMT</pubDate>
    <lastBuildDate>Fri, 03 Feb 2023 18:00:03 GMT</lastBuildDate>
    <image>
      <url>https://raw.githubusercontent.com/na4n/pod/main/scripts/resources/img.png</url>
      <title>Rice Lake Bible Chapel Sermons</title>
      <link>https://ricelakebiblechapel.com/</link>
    </image>
'''

def day_of_week(date):
    day, month, year = map(int, date.split("/")[1::-1] + [date.split("/")[2]])
    raw_year = int("20" + date.split("/")[2])

    t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
    year -= month < 3
    dow = (year + year//4 - year//100 + year//400 + t[month - 1] + day) % 7
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    return f"{days[dow]}, {day:02d} {months[month - 1]} {raw_year} 11:00:00 GMT"

def guid_creation(date):
    return ''.join(str(ord(c)) for c in reversed(date))

def find_first_digit(input_str):
    return next((input_str[i:] for i in range(len(input_str)) if input_str[i].isdigit()), input_str)

def find_date(input_str):
    input_str = find_first_digit(input_str).replace('-', '/')
    parts = input_str.split('/')
    if len(parts[2]) == 3:
        parts[2] = parts[2][:2]
    if len(parts[0]) == 4:
        return f"{parts[1]}/{parts[2]}/{parts[0][-2:]}"
    return f"{parts[0]}/{parts[1]}/{parts[2][-2:]}"

def create_output(divs):
    output = XML
    for element in divs:
        if 'class' in element.attrs and 'sqs-audio-embed' in element['class']:
            date = find_date(str(element['data-title'])[-10:])
            raw_title = element['data-title'].split(" - ")[0] + " – " + element['data-author']
            title = html.escape(raw_title.strip())
            url = element['data-url']
            length = str(math.ceil(int(element['data-duration-in-ms']) / 1000))
            pub_date = day_of_week(date)
            guid = guid_creation(date)

            item = f'''
    <item>
      <title>{title}</title>
      <link>https://ricelakebiblechapel.com/speakers</link>
      <enclosure url="{url}" type="audio/mpeg" length="{length}"/>
      <guid isPermaLink="false">{guid}</guid>
      <pubDate>{pub_date}</pubDate>
      <itunes:duration>{length}</itunes:duration>
    </item>'''
            output += item
    output += '\n  </channel>\n</rss>'
    return output

def main():
    site = requests.get('https://www.ricelakebiblechapel.com/speakers')
    soup = BeautifulSoup(site.text, 'lxml')
    divs = soup.find_all('div')
    out = create_output(divs)
    with open("feed.xml", "w", encoding="utf-8") as file:
        file.write(out)

if __name__ == '__main__':
    main()

