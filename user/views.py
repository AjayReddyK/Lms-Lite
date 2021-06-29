from datetime import datetime
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
			  print("entering requests")
			  headers={'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'}
			  #print(headers)
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
			  a=soup.body.find(text=re.compile(username[1:]))
			  if(a!=None):
			  	print('credentials are correct')
			  	time=str(datetime.now()).split(" ")[1].split(":")[:2]
			  	for i in range(2):
			  		time[i]=int(time[i])
			  	time[0]=time[0]+5
			  	time[1]=time[1]+30
			  	if(time[1]>=60):
			  		dif=time[1]-60
			  		time[1]=dif
			  		time[0]+=1
			  	print("current time=",time)
			  	cal=s.get("http://lms.rgukt.ac.in/calendar/view.php?view=day",headers=headers).text
			  	soup=BeautifulSoup(cal,'lxml')
			  	date=soup.find('div',class_="calendar-controls").h2.text.split(" ")
			  	date[2]=date[2][0:3]
			  	date=" ".join(date[1:])
			  	print(date)
			  	list=soup.find('body')
			  	l2=list.find('div',{"class":"calendarwrapper"})
			  	l3=l2.find("div",class_="eventlist my-1")
			  	events=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_attendance'})
			  	for i in events:
			  		timet=i.find("div",class_="row").find("div",class_="col-11").text
			  		updated_time=timet.split(",")[1]
			  		attendance_timings.append(updated_time)
			  		#print(updated_time)
			  		temp_time=updated_time[1:].split(" ")[:2]
			  		#print(temp_time)
			  		tt=temp_time[0].split(":")
			  		tt.append(temp_time[1])
			  		#print(tt)
			  		for j in range(2):
			  			tt[j]=int(tt[j])
			  		if(tt[2]=="PM" and tt[0]<12):
			  			tt[0]=tt[0]+12
			  		tt[1]=tt[1]+3
			  		event=i.find_all('div',class_='row mt-1')[-1]
			  		subject_name=event.find('div',class_='col-11').a.text
			  		#print(subject_name)
			  		print("time=",tt[:2])
			  		attendance_subjects.append(subject_name)
			  		if(time[0]<tt[0]):
			  			attendance_status.append("Not active yet")
			  		elif(time[0]==tt[0] and time[1]<tt[1]):
			  			attendance_status.append("Not active yet")
			  		else:
				  		link=i.find('a',class_='card-link')['href']
				  		link=s.get(link,headers=headers).text
				  		soup=BeautifulSoup(link,'lxml')
				  		a_link=soup.find('td',class_="statuscol cell c2 lastcol")
				  		if(a_link!=None):
				  			a_link=a_link.a['href']
				  			b=a_link.split("?")[1].split("&")
				  			sessid=b[0].split("=")[1]
				  			sesskey=b[1].split("=")[1]
				  			print(sessid)
				  			print(sesskey)
				  			link="http://lms.rgukt.ac.in/mod/attendance/attendance.php"
				  			final_page=s.get(a_link,headers=headers).text
				  			soup=BeautifulSoup(final_page,'lxml')
				  			status=soup.find('input',{"class":"form-check-input","name":"status"})['value']
				  			print("status code=",status)
				  			at_data={
				  				"sessid":sessid,
				  				"sesskey":sesskey,
				  				"sesskey":sesskey,
				  				"_qf__mod_attendance_form_studentattendance":1,
				  				"mform_isexpanded_id_session":1,
				  				"status":status,
				  				"submitbutton":"Save+changes"
				  			}
				  			#print(at_data)
				  			headers['referer']=a_link
				  			#print(headers)
				  			submission=s.post(link,data=at_data,headers=headers,allow_redirects=True)
				  			attendance_status.append("Attendance Marked... [^_^]")
				  			print("attendance marked")
				  		else:
				  			m=soup.find(text=re.compile(date)).parent.parent.parent
				  			#print(m)
				  			att_status=m.find('td',class_="statuscol cell c2").text
				  			if(att_status=="?"):
				  				attendance_status.append("absent")
				  			elif(att_status=="Present"):
				  			 	attendance_status.append("present")
				  			else:
				  				attendance_status.append("status_unknown")
			  	for i in range(len(attendance_subjects)):
			  		dik={}
			  		dik['subject']=attendance_subjects[i]
			  		dik['time']=attendance_timings[i]
			  		dik['status']=attendance_status[i]
			  		content.append(dik)
			  	context['attendance']=content
			  	events=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_assign'})
			  	bevents=l3.find_all('div',{'class':'event mt-3','data-event-component':'mod_quiz'})
			  	for day in range(5):
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
			  		if(day==4):
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
