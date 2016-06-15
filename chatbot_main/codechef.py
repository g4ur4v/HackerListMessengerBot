import requests,re
from bs4 import BeautifulSoup
import logging
import traceback,datetime

logger = logging.getLogger('django')

home_url = "https://www.codechef.com"
get_url = "https://www.codechef.com/contests"

def getContestData(data):
	live_contests = []
	contest_url = []
	contest_end_time = []
	try:
		r = requests.get(get_url)
		get_data=r.text.replace('\n','')
		soup = BeautifulSoup(get_data,"html.parser")
		# TODO : /check for h3 tag for present contests
		for contest in soup.find('table').find('tbody').findAll('tr'):
			td=contest.findAll('td')
			live_contests.append(td[1].contents[0].contents[0])
			contest_url.append(home_url + td[1].contents[0]['href'])
			contest_end_time.append(datetime.datetime.strptime(td[3].contents[0],'%Y-%m-%d %H:%M:%S'))			

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