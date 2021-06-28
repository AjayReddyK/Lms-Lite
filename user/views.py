from django.shortcuts import render,redirect
import requests
from bs4 import BeautifulSoup
import re
import lxml
from django.contrib import messages

def loginhome(request):
	if request.method=='POST':
		form=request.POST
		username=form.get('Username')
		password=form.get('Password')
		login_data={
    		'anchor':'',
   			'username': username,
   			'password': password,
   			'rememberusername':'1'
		}
		print("credentials received")
		with requests.Session() as s:
			  attendance_subjects=[]
			  attendance_timings=[]
			  attendance_status=[]
			  quiz_subjects=[]
			  quiz_timings=[]
			  quiz_titles=[]
			  quiz_link=[]
			  assignment_subjects=[]
			  assignment_timings=[]
			  assignment_titles=[]
			  assignment_link=[]
			  attendences=[]
			  content=[]
			  context={}
			  print("entering request")
			  headers={'user-agent':request.META['HTTP_USER_AGENT']}
			  print(headers)
			  url="http://lms.rgukt.ac.in/login/index.php"
			  r=s.get(url,headers=headers)
			  print("got data, appling soup")
			  soup=BeautifulSoup(r.content,'html5lib')
			  print("soup applied , next finding logintoken")
			  login_data['logintoken']=soup.find('input',attrs={'name':'logintoken'})['value']
			  print("found token , next posting request")
			  r=s.post(url,data=login_data,headers=headers).text
			  print("request posted")
			  soup=BeautifulSoup(r,'lxml')
			  a=soup.body.find(text=re.compile(username))
			  if(a!=None):
			  	print('credentials are correct')
			  	messages.success(request,f'Welcome {a} !!')
			  	cal=s.get("http://lms.rgukt.ac.in/calendar/view.php?view=day",headers=headers).text
			  	soup=BeautifulSoup(cal,'lxml')
			  	list=soup.find('body')
			  	l2=list.find('div',{"class":"calendarwrapper"})
			  	l3=l2.find("div",class_="eventlist my-1")
			  	events=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_attendance'})
			  	for i in events:
			  		time=i.find("div",class_="row").find("div",class_="col-11").text
			  		updated_time=time.split(",")[1]
			  		attendance_timings.append(updated_time)
			  		event=i.find_all('div',class_='row mt-1')[-1]
			  		subject_name=event.find('div',class_='col-11').a.text
			  		link=i.find('a',class_='card-link')['href']
			  		attendance_subjects.append(subject_name)
			  		link=s.get(link,headers=headers).text
			  		soup=BeautifulSoup(link,'lxml')
			  		a_link=soup.find('td',class_="statuscol cell c2 lastcol")
			  		if(a_link!=None):
			  			a_link=a_link.a['href']
			  			b=a_link.split("?")[1].split("&")
			  			sessid=b[0].split("=")[1]
			  			sesskey=b[1].split("=")[1]
			  			print(sessid,",",sesskey)
			  			link="http://lms.rgukt.ac.in/mod/attendance/attendance.php"
			  			final_page=s.get(a_link,headers=headers).text
			  			soup=BeautifulSoup(final_page,'lxml')
			  			status=soup.find('input',{"class":"form-check-input","name":"status"})['value']
			  			at_data={
			  				"sessid":sessid,
			  				"sesskey":{
			  					"0":sesskey,
			  					"1":sesskey
			  				},
			  				"_qf__mod_attendance_form_studentattendance":"1",
			  				"mform_isexpanded_id_session":"1",
			  				"status":status,
			  				"submitbutton":"Save+changes"
			  			}
			  			submission=s.post(link,data=at_data,headers=headers).text
			  			soup=BeautifulSoup(submission,'lxml')
			  			b_link=soup.find('td',class_="statuscol cell c2 lastcol")
			  			if(b_link==None):
			  				attendance_status.append("successfully Marked Now")
			  			else:
			  				attendance_status.append("Not active now")
			  		else:
			  			attendance_status.append("Not active now")


			  	for i in range(len(attendance_subjects)):
			  		dik={}
			  		dik['subject']=attendance_subjects[i]
			  		dik['time']=attendance_timings[i]
			  		dik['status']=attendance_status[i]
			  		content.append(dik)
			  	context['attendance']=content
			  	events=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_assign'})
			  	bevents=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_quiz'})
			  	for day in range(7):
			  		for i in events:
			  			assignment_titles.append(i['data-event-title'])
			  			time=i.find("div",class_="row").find("div",class_="col-11").text
			  			assignment_timings.append(time)
			  			event=i.find_all('div',class_='row mt-1')[-1]
			  			subject_name=event.find('div',class_='col-11').a.text
			  			link=i.find('a',class_='card-link')['href']
			  			assignment_subjects.append(subject_name)
			  			assignment_link.append(link)
			  		for i in bevents:
			  			quiz_titles.append(i['data-event-title'])
			  			time=i.find("div",class_="row").find("div",class_="col-11").text
			  			quiz_timings.append(time)
			  			bevent=i.find_all('div',class_='row mt-1')[-1]
			  			subject_name=bevent.find('div',class_='col-11').a.text
			  			link=i.find('a',class_='card-link')['href']
			  			quiz_subjects.append(subject_name)
			  			quiz_link.append(link)
			  		if(day==6):
			  			break
			  		else:
			  			link=l2.find('div',class_='calendar-controls').find('a',class_='arrow_link next')['href']
			  			cal=s.get(link,headers=headers).text
			  			soup=BeautifulSoup(cal,'lxml')
			  			list=soup.find('body')
			  			l2=list.find('div',{"class":"calendarwrapper"})
			  			l3=l2.find("div",class_="eventlist my-1")
			  			events=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_assign'})
			  			bevents=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_quiz'})
			  	content=[]
			  	for i in range(len(assignment_subjects)):
			  		dik={}
			  		dik['subject']=assignment_subjects[i]
			  		dik['time']=assignment_timings[i]
			  		dik['title']=assignment_titles[i]
			  		dik['link']=assignment_link[i]
			  		content.append(dik)
			  	context['assignment']=content
			  	bevents=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_quiz'})
			  	content=[]
			  	for i in range(len(quiz_subjects)):
			  		dik={}
			  		dik['subject']=quiz_subjects[i]
			  		dik['time']=quiz_timings[i]
			  		dik['title']=quiz_titles[i]
			  		dik['link']=quiz_link[i]
			  		content.append(dik)
			  	context['quiz']=content
			  	context['title']='Lms-Lite'
			  	messages.success(request,f'Welcome {a} !!')
			  	return render(request,'user/success_message.html',context)
			  print("something went wrong")

	return render(request,'user/login.html',{"title":"Lms-Lite"})
def success(request):
	return render(request,'user/success_message.html')
# Create your views here.
