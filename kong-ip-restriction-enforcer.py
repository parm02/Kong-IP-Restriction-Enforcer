import requests
import argparse

from mail import email
from chat import slack

parser = argparse.ArgumentParser(description='Kong IP-Restriction Enforcer')

parser.add_argument('-u','--url', help='Kong Server Location starting with http...',required=True)
parser.add_argument('-e','--email', help='Email From Address',required=True)
parser.add_argument('-t','--to', help='Email To Address',required=True)
parser.add_argument('-s','--smtp', help='SMTP Server',required=True)
parser.add_argument('-st','--token', help='SLACK Token',required=True)
parser.add_argument('-sc','--channel', help='SLACK Channel Id',required=True)

args = parser.parse_args()

try:
    
    response = requests.get(args.url,timeout=5)
    response.raise_for_status()

except requests.exceptions.HTTPError as e:
        print ('Http Error:', e)
        email (args.url,'Http Error',args.email,args.to,str(e),args.smtp)
        slack (args.token, args.channel, str(e))
except requests.exceptions.Timeout as e:
        print ('Timeout Error:', e)
        email (args.url,'Timeout Error',args.email,args.to,str(e),args.smtp)
        slack (args.token, args.channel, str(e))
except requests.exceptions.ConnectionError as e:
        print ('Error Connecting:', e)
        email (args.url,'Error Connecting',args.email,args.to,str(e),args.smtp)
        slack (args.token, args.channel, str(e))
except requests.exceptions.RequestException  as e:
        print('Something went wrong trying to fulfill the request -->', e)
        email (args.url,'Something went wrong trying to fulfill the request -->',args.email,args.to,str(e),args.smtp)
        slack (args.token, args.channel, str(e))
   
else:

       apis_json_object = response.json()
       apis_count = len(apis_json_object['data'])
       count_apis = 0
       while (count_apis < apis_count):
               print(apis_json_object['data'][count_apis]['id'])
               api_plugins_url = args.url + apis_json_object['data'][count_apis]['id'] + '/plugins/'
               response = requests.get(api_plugins_url)
               api_plugins_json_object = response.json()
               api_plugins_count = len(api_plugins_json_object['data'])
               count_plugins = 0
               ip_restriction_plugin_present = False
               while (count_plugins < api_plugins_count):
                   if api_plugins_json_object['data'][count_plugins]['name'] == 'ip-restriction':
                                 ip_restriction_plugin_present = True
                                 break
                   count_plugins = count_plugins + 1
               if ip_restriction_plugin_present == False:
                             try:
                                 payload = (('name','ip-restriction'),('config.whitelist','10.0.0.0/8,172.16.0.0/12,192.168.0.0/16'))
                                 response = requests.post(api_plugins_url, data = payload)
                                 print(response.text)
                                 response.raise_for_status()
                             except requests.exceptions.HTTPError as e:
                                 print ('Http Error:', e)
                             except requests.exceptions.Timeout as e:
                                 print ('Timeout Error:', e)
                             except requests.exceptions.ConnectionError as e:
                                 print ('Error Connecting:', e)
                             except requests.exceptions.RequestException  as e:
                                 print('Something went wrong trying to fulfill the request -->', e)
                             
               count_apis = count_apis + 1



	
