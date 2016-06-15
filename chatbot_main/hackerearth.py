import requests,re
from bs4 import BeautifulSoup
import logging
import traceback,datetime

logger = logging.getLogger('django')

userAgent = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:46.0) Gecko/20100101 Firefox/46.0"
referer = "https://www.hackerearth.com/challenges/"
home_url = "https://www.hackerearth.com"
ajax_url = "https://www.hackerearth.com/AJAX/filter-challenges/?modern=true"

def getContestData(data):
	headers = {'User-Agent': userAgent,'X-Requested-With': 'XMLHttpRequest', "referer": referer}
	live_contests = []
	contest_url = []
	contest_end_time = []
	try:
		with requests.Session() as s:
			s.get(home_url)
			headers["X-CSRFToken"] = s.cookies["csrftoken"]
			r = s.post(ajax_url, headers=headers)
			post_data=r.json()['data'].replace('\n','')
			soup = BeautifulSoup(post_data,"html.parser")

			for contests in soup.find('div',{'class':'ongoing challenge-list'}).findAll('div',{'class':'challenge-card-modern'}):
				live_contests.append(contests.find('h1').span.contents[0])
				url = contests.find('div',{'class':'challenge-button'}).a['modal-redirect']
				if 'http' not in url:
					url = home_url + url
				contest_url.append(url)				
				
			for contests in soup.find('div',{'class':'ongoing challenge-list'}).findAll('script'):
				time_string = re.search(r'(\d+-\d+-\d+ \d+:\d+:\d+)',contests.text).group(0)
				contest_end_time.append(datetime.datetime.strptime(time_string,'%Y-%m-%d %H:%M:%S'))

		if not len(live_contests)==len(contest_url)==len(contest_end_time):
			return False

		data.append(live_contests)
		data.append(contest_url)
		data.append(contest_end_time)

		return True
	except Exception as e:
		logger.error(e)
		traceback.print_exc()
		return False