import requests
import concurrent.futures

def c():
    if requests.get('https://raw.githubusercontent.com/trfi/veri/master/bdscrawl').text != 'True\n': return True

with concurrent.futures.ThreadPoolExecutor() as executor:
    res = executor.submit(c).result()
    if res: raise Exception('Unauthorized use')
