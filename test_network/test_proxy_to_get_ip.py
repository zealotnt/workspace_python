import urllib2
import os
from json import load
from urllib2 import urlopen
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, verbose=True)

# [Ref for urllib](https://stackoverflow.com/questions/11763028/python-3-urllib-http-error-407-proxy-authentication-required/11763340)
# [Ref for urllib2](http://www.learntosolveit.com/python/web_urllib2_proxy_auth.html)
proxy = urllib2.ProxyHandler({'http': os.environ.get('HTTP_PROXY_PROXY_SCHEME'),
							  'https': os.environ.get('HTTPS_PROXY_PROXY_SCHEME')})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)

# [Ref](https://stackoverflow.com/questions/9481419/how-can-i-get-the-public-ip-using-python2-7)
my_ip = urlopen('http://ip.42.pl/raw').read()
print "http:  ", my_ip

my_ip = load(urlopen('https://api.ipify.org/?format=json'))['ip']
print "https: ", my_ip
