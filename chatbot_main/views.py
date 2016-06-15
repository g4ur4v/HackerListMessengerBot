from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from chatbot_main.models import HackerEarth_DB,CodeChef_DB,LastFetch,Message_Log
import hackerearth,codechef
from django.utils import timezone
import requests,json,logging
from FileLock import FileLock
import traceback,time
from django.conf import settings

logger = logging.getLogger('django')

# Move this token to settings later
VERIFY_TOKEN = ''
PAGE_ACCESS_TOKEN = ''
FB_API = 'https://graph.facebook.com/v2.6/me/messages'

def gatherdatafromContestSite(contestName,contest_DB):
		logger.debug('Gather data from '+ contestName.__name__.split('.')[-1] +' sites')
		contest = []
		data = []
		contest_gather_time = timezone.now()
		if contestName.getContestData(contest):
			for i in range(len(contest[0])):
				data.append(contest_DB(contest_name=contest[0][i],contest_url=contest[1][i]\
					,contest_end_time=contest[2][i],contest_gather_time=contest_gather_time))
			contest_DB.objects.all().delete()			
			contest_DB.objects.bulk_create(data)
			return True
		else:
			logger.error('Could not fetch '+ contestName.__name__.split('.')[-1] +' live contests')
			return False

def gatherdata():
	logger.debug('gatherdata started')
	lock=FileLock('lock')
	result = []
	if lock.acquire():
		if gatherdatafromContestSite(hackerearth,HackerEarth_DB):
			result.append(True)
		else:
			result.append(False)
		if gatherdatafromContestSite(codechef,CodeChef_DB):
			result.append(True)
		else:
			result.append(False)
		
		lastf = LastFetch.objects.all()
		if(len(lastf)==0):
			LastFetch(update_date=timezone.now()).save()
		else:
			lastf[0].update_date=timezone.now()
			lastf[0].save()
		lock.release()
	else:
		lock.poll()

	return result

def POST_REQUEST_MSG(payload):
	r = requests.post(FB_API, params={'access_token': PAGE_ACCESS_TOKEN}, json=payload)
	if r.status_code!=200:
		logger.error('Call to FB API failed')
		logger.error(r.text)
		return False
	else:
		return True

def sendMessage(message_to,contestName,contest_DB):
	live_contests = contest_DB.objects.all()
	payload = {}
	buttons = []
	if len(live_contests) == 0: # No live contests running
		payload = { 'recipient': { 'id': message_to },
                    'message': { 'text': 'No Live contest running on' + contestName }
                   }
		r = requests.post(FB_API, params={'access_token': PAGE_ACCESS_TOKEN}, json=payload)
		if r.status_code!=200:
			logger.error('Call to FB API failed')
			logger.error(r.text)

	elif len(live_contests) <=3: # button limit is 3 - https://developers.facebook.com/docs/messenger-platform/send-api-reference#guidelines
		buttons=[{'type':'web_url','title':i.contest_name,'url':i.contest_url} for i in live_contests]
		payload = { "recipient":{ "id":message_to },
  				"message":{
    					"attachment":{
      									"type":"template",
      									"payload":{
        											"template_type":"button",
        											"text":"Live " + contestName + " contests",
        											"buttons":buttons
      												}
    									}
  							}
			  }

		POST_REQUEST_MSG(payload)
		
	else:
		buttons=[{'type':'web_url','title':i.contest_name,'url':i.contest_url} for i in live_contests]
		payload = { "recipient":{ "id":message_to },
  				"message":{
    					"attachment":{
      									"type":"template",
      									"payload":{
        											"template_type":"button",
        											"text":"Live " + contestName + " contests",
        											"buttons":buttons[0:3]
      												}
    									}
  							}
			  }
		if not POST_REQUEST_MSG(payload):
			return False

		n = len(live_contests)
		i=3
		while i<=n:
			if (i+3)>n:
				j=n
			else:
				j=i+3
			payload = { "recipient":{ "id":message_to },
  				"message":{
    					"attachment":{
      									"type":"template",
      									"payload":{
        											"template_type":"button",
        											"text":"Few more Live " + contestName + " contests",
        											"buttons":buttons[i:j]
      												}
    									}
  							}
			  }
			i = i+3
			if not POST_REQUEST_MSG(payload):
				return False

def initiate_sendMessage(user_id):
	result = []
	last_update = LastFetch.objects.all()

	# Gather new data from contest sites only if the current data is more than 2 hours old
	if len(last_update)!=0:
		timediff = timezone.now()-last_update[0].update_date
		if (timediff.seconds/3600)>2:
			result = gatherdata()
	else:
		result = gatherdata()
			
	sendMessage(user_id,'HackerEarth',HackerEarth_DB)
	sendMessage(user_id,'CodeChef',CodeChef_DB)


@csrf_exempt
def webhook(request):
	if request.method == 'GET':
		if request.GET.get('hub.verify_token',False) == VERIFY_TOKEN:
			return HttpResponse(request.GET['hub.challenge'])
		else:
			return HttpResponse("Nothing!")
	elif request.method == 'POST':
		logger.debug('Request body : ' + request.body)
		try:
			data = []
			received_json_data=json.loads(request.body)
			for entry in received_json_data['entry']:
				for msg in entry['messaging']:
					user_id = msg['sender']['id']
					if 'message' in msg:
						if 'text' in msg['message']:
							user_msg = msg['message']['text']
							msg_date = timezone.now()
							data.append(Message_Log(userid=user_id,msg_date=msg_date,msg=user_msg))
							if 'list' in user_msg.lower().split():
								initiate_sendMessage(user_id)
						else:
							logger.debug('Not a message callback')
					else:
						logger.debug('Not a message callback')
			
			if settings.LOG_ALL_MESSAGE:
				Message_Log.objects.bulk_create(data)
				
			return HttpResponse("")
		except Exception as e:
			logger.error(e)
			traceback.print_exc()
			return HttpResponse("some issue with the request")
