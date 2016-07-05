import re
import urllib2

html = urllib2.urlopen('http://steve-yegge.blogspot.com/2007/08/how-to-make-funny-talk-title-without.html').read()
pattern = r'\b(the\s+\w+)\s+'
regex = re.compile(pattern, re.IGNORECASE)
for match in regex.finditer(html):
    print "%s: %s" % (match.start(), match.group(1))