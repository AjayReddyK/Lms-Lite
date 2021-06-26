from django.shortcuts import render,redirect
import requests
from bs4 import BeautifulSoup
import re
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
			  subjects=[]
			  timings=[]
			  links=[]
			  attendences=[]
			  content=[]
			  print("entering request")
			  headers={'user-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}
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
			  		timings.append(updated_time)
			  		event=i.find_all('div',class_='row mt-1')[-1]
			  		subject_name=event.find('div',class_='col-11').a.text
			  		subject_link=event.find('div',class_='col-11').a['href']
			  		subjects.append(subject_name)
			  		'''links.append(subject_link)
			  		r=s.get(subject_link,headers=headers).text
			  		soup=BeautifulSoup(r,'lxml')
			  		k=soup.find_all('li',class_='activity attendance modtype_attendance ')[-1]
			  		attendence_link=k.find('a',class_="aalink")['href']
			  		attendences.append(attendence_link)
			  		sub=s.get(attendence_link,headers=headers).text
			  		soup=BeautifulSoup(sub,'lxml')
			  		if(soup.body.find(text=re.compile('Submit attendance'))!=None):
			  		  l=soup.body.find('div',id="page-content").find('tr',class_='lastrow')
			  		  print(l)
			  		  bl=l.find('td',class_='statuscol cell c2 lastcol').a['href']
			  		  if(bl!=None):
			  		  	print('link found')'''

			  	for i in range(len(subjects)):
			  		dik={}
			  		context={}
			  		dik['subject']=subjects[i]
			  		dik['time']=timings[i]
			  		content.append(dik)
			  		context['content']=content
			  	print(context)
			  	return render(request,'user/success_message.html',context)
			  print("something went wrong")

	return render(request,'user/login.html')
def success(request):
	return render(request,'user/success_message.html')
# Create your views here.
