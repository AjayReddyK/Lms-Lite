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
			  print("entering request")
			  headers={'user-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}
			  url="http://lms.rgukt.ac.in/login/index.php"
			  r=s.get(url,headers=headers)
			  print("got data, appling soup")
			  soup=BeautifulSoup(r.content,'html5lib')
			  print("soup applied , next finding logintoken")
			  login_data['logintoken']=soup.find('input',attrs={'name':'logintoken'})['value']
			  print("found token , next posting request")
			  r=s.post(url,data=login_data,headers=headers)
			  print("request posted")
			  soup=BeautifulSoup(r.content,'html5lib')
			  a=soup.body.find(text=re.compile(username))
			  if(a!=None):
			  	print('credentials are correct')
			  	messages.success(request,f'Welcome {a} !!')
			  	return redirect('success')
			  print("something went wrong")

	return render(request,'user/login.html')
def success(request):
	return render(request,'user/success_message.html')
# Create your views here.
