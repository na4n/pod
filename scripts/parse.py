#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import math
import html
import re

XML = '''<?xml version='1.0' encoding='utf-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     version="2.0">

  <channel>
    <title>Rice Lake Bible Chapel</title>
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

def find_date(input_str):
    # Match dates like 1/8/17, 05/08/2017, 2016-11-13, 2016/11/13, etc.
    match = re.search(r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b|\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', input_str)
    if not match:
        return None

    if match.group(1):  # YYYY-MM-DD or YYYY/MM/DD
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
    else:  # MM/DD/YY or MM/DD/YYYY
        month = match.group(4)
        day = match.group(5)
        year = match.group(6)

    # Normalize components
    month = month.zfill(2)
    day = day.zfill(2)
    if len(year) == 4:
        year = year[2:]

    return f"{month}/{day}/{year}"

def day_of_week(date):
    try:
        month, day, yy = map(int, date.split("/"))
        year = 2000 + yy
        t = [0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4]
        year -= month < 3
        dow = (year + year//4 - year//100 + year//400 + t[month - 1] + day) % 7
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return f"{days[dow]}, {day:02d} {months[month - 1]} {year} 11:00:00 GMT"
    except Exception as e:
        print(f"⚠️  Invalid date input to day_of_week(): {date} — {e}")
        return "Sun, 01 Jan 2000 00:00:00 GMT"

def guid_creation(date):
    return ''.join(str(ord(c)) for c in reversed(date))

def create_output(divs):
    output = XML
    for element in divs:
        if 'class' in element.attrs and 'sqs-audio-embed' in element['class']:
            raw_title = element.get('data-title', '').strip()
            date = find_date(raw_title)
            if not date:
                print(f"⚠️  Skipping entry due to missing date: {raw_title}")
                continue

            try:
                formatted_date = day_of_week(date)
                url = element['data-url']
                length = str(math.ceil(int(element['data-duration-in-ms']) / 1000))
                guid = guid_creation(date)

                # Parse title and author if present
                if ' - ' in raw_title:
                    title_part, author_part = raw_title.rsplit(' - ', 1)
                    title = html.escape(title_part.strip())
                    speaker = html.escape(author_part.strip())
                    summary = f"<itunes:summary>Spoken by {speaker}.</itunes:summary>"
                else:
                    title = html.escape(raw_title)
                    summary = ""

                item = f'''
    <item>
      <title>{title}</title>
      <link>https://ricelakebiblechapel.com/speakers</link>
      <enclosure url="{url}" type="audio/mpeg" length="{length}"/>
      <guid isPermaLink="false">{guid}</guid>
      <pubDate>{formatted_date}</pubDate>
      <itunes:duration>{length}</itunes:duration>{summary}
    </item>'''
                output += item
            except Exception as e:
                print(f"⚠️  Skipping malformed entry: {raw_title} — {e}")
                continue
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
