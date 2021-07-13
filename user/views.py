from datetime import datetime
from django.shortcuts import render,redirect
import requests
from bs4 import BeautifulSoup
import re
import lxml
from .models import Profile 
from django.contrib import messages

context={}
hubcontent={}
s=requests.Session()
def loginhome(request):
    headers={'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'}
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
        global s
        s=requests.Session()
        with s:
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
              global context
              print("entering requests")
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
                dev=request.META['HTTP_USER_AGENT']
                log_instance=Profile.objects.create(b_id=username,device=dev)
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
                    print("updated_time=",updated_time)
                    start_t=updated_time[1:].split(" ")[:2]
                    end_t=updated_time[1:].split(" ")[3:]
                    print("start_time=",start_t)
                    print("end_time=",end_t)
                    start_time=start_t[0].split(":")
                    start_time.append(start_t[1])
                    end_time=end_t[0].split(":")
                    end_time.append(end_t[1])
                    for j in range(2):
                        start_time[j]=int(start_time[j])
                        end_time[j]=int(end_time[j])
                    if(start_time[2]=="PM" and start_time[0]<12):
                        start_time[0]=start_time[0]+12
                    if(end_time[2]=="PM" and end_time[0]<12):
                        end_time[0]=end_time[0]+12
                    event=i.find_all('div',class_='row mt-1')[-1]
                    subject_name=event.find('div',class_='col-11').a.text
                    print("total start time=",start_time)
                    print("start time=",start_time[:2])
                    print("total end time=",end_time)
                    print("end time=",end_time[:2])
                    attendance_subjects.append(subject_name)
                    if(time[0]<start_time[0]):
                        attendance_status.append("Not active yet")
                    elif(time[0]==start_time[0] and time[1]<start_time[1]):
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
                            headers['referer']=a_link
                            submission=s.post(link,data=at_data,headers=headers,allow_redirects=True)
                            attendance_status.append("Attendance Marked... [^_^]")
                            print("attendance marked")
                        else:
                            m=soup.find(text=re.compile(date)).parent.parent.parent
                            att_status=m.find('td',class_="statuscol cell c2").text
                            if(att_status=="?"):
                                if(time[0]<end_time[0] or (time[0]==end_time[0] and time[1]<end_time[1])):
                                    attendance_status.append("Not active yet(server time lag-reload after sometime)")
                                else:
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
                context['title']='LmsLite'
                context['login']="true"
                messages.success(request,f'Welcome {a} !!')
                return render(request,'user/success_message.html',context)
              print("something went wrong")
    global hubcontent
    hub=requests.get("https://hub.rgukt.ac.in/hub/notice/index",headers=headers,verify=False).text
    print("connected hub")
    hubdata=BeautifulSoup(hub,'lxml')
    cards=hubdata.find('div',class_="card-body text-success").find_all('div',class_="card")[:15]
    card_time=[]
    card_header=[]
    card_description=[]
    card_url=[]
    card_attachment=[]
    card_published_by=[]
    for i in range(15):
          header=cards[i].find('div',class_="card-header").a.text
          header=header.split(":")
          card_time.append(header[0].strip())
          card_header.append(":".join(header[1:]).strip())
          body=cards[i].find('div',class_="card-body")
          if(body.pre==None):
            p_tag=body.find_all("p")
            text=""
            for i in range(len(p_tag)-3):
                text=text+p_tag[i].text.strip()
            tex=p_tag[-3].find(text=re.compile("URL"))
            if(tex!=None):
                a=p_tag[-3].a['href']
                a=a.replace(" ","%20")
                card_url.append(a)
                b=p_tag[-2].a['href']
                b=b.replace(" ","%20")
                if(b.find("/hub/notice")!=-1):
                    b="https://hub.rgukt.ac.in"+b
                card_attachment.append(b)
                card_published_by.append(p_tag[-1].a.text)
            else:
                text=text+p_tag[-3].text.strip()
                tex=p_tag[-2].find(text=re.compile("URL"))
                if(tex!=None):
                    a=p_tag[-2].a['href']
                    a=a.replace(" ","%20")
                    card_url.append(a)
                    card_attachment.append("false")
                    card_published_by.append(p_tag[-1].a.text)
                elif(p_tag[-2].find(text=re.compile("Download"))!=None):
                    b=p_tag[-2].a['href']
                    b=b.replace(" ","%20")
                    if(b.find("/hub/notice")!=-1):
                      b="https://hub.rgukt.ac.in"+b
                    card_attachment.append(b)
                    card_published_by.append(p_tag[-1].a.text)
                    card_url.append("false")
                else:
                    text=text+p_tag[-2].text.strip()    
                    card_url.append("false")    
                    card_attachment.append("false")
                    card_published_by(p_tag[-1].a.text)
            card_description.append(text)
            continue
          card_description.append(body.pre.code.text.strip())
          p_tag=body.find_all("p")
          if(len(p_tag)==3):
            a=p_tag[0].a['href']
            a=a.replace(" ","%20")
            card_url.append(a)
            b=p_tag[1].a['href']
            b=b.replace(" ","%20")
            if(b.find("/hub/notice")!=-1):
              b="https://hub.rgukt.ac.in"+b
            card_attachment.append(b)
            card_published_by.append(p_tag[2].a.text)
          elif(len(p_tag)==2):
            b=p_tag[0].a['href']
            tex=p_tag[0].find(text=re.compile("URL"))
            b=b.replace(" ","%20")
            if(b.find("/hub/notice")!=-1):
              b="https://hub.rgukt.ac.in"+b
            if(tex!=None):
              card_url.append(b)
              card_attachment.append("false")
            else:
              card_attachment.append(b)
              card_url.append("false")
            card_published_by.append(p_tag[1].a.text)
          else:
            card_published_by.append(p_tag[0].a.text)
            card_url.append("false")
            card_attachment.append("false")
    l=[]
    for  i in range(15):
          dictionary={}
          dictionary['time']=card_time[i]
          dictionary['header']=card_header[i]
          dictionary['content']=card_description[i]
          dictionary['url']=card_url[i]
          dictionary['download']=card_attachment[i]
          dictionary['published_by']=card_published_by[i]
          dictionary['no']=i
          l.append(dictionary)
    hubcontent['cards']=l
    hubcontent['title']='LmsLite'
    hubcontent['login']="false"
    #print(hubcontent)
    hubcards={}
    hubcards['cards']=l[:6]
    hubcards['title']='LmsLite'
    hubcards['login']='false'
    return render(request,'user/login.html',hubcards)
def home(request):
    global context
    global s
    attendance_subjects=[]
    attendance_timings=[]
    attendance_status=[]
    content=[]
    headers={'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'}
    with s:
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
            print("updated_time=",updated_time)
            start_t=updated_time[1:].split(" ")[:2]
            end_t=updated_time[1:].split(" ")[3:]
            print("start_time=",start_t)
            print("end_time=",end_t)
            start_time=start_t[0].split(":")
            start_time.append(start_t[1])
            end_time=end_t[0].split(":")
            end_time.append(end_t[1])
            for j in range(2):
                start_time[j]=int(start_time[j])
                end_time[j]=int(end_time[j])
            if(start_time[2]=="PM" and start_time[0]<12):
                start_time[0]=start_time[0]+12
            if(end_time[2]=="PM" and end_time[0]<12):
                end_time[0]=end_time[0]+12
            event=i.find_all('div',class_='row mt-1')[-1]
            subject_name=event.find('div',class_='col-11').a.text
            print("total start time=",start_time)
            print("start time=",start_time[:2])
            print("total end time=",end_time)
            print("end time=",end_time[:2])
            attendance_subjects.append(subject_name)
            if(time[0]<start_time[0]):
                attendance_status.append("Not active yet")
            elif(time[0]==start_time[0] and time[1]<start_time[1]):
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
                    headers['referer']=a_link
                    submission=s.post(link,data=at_data,headers=headers,allow_redirects=True)
                    attendance_status.append("Attendance Marked... [^_^]")
                    print("attendance marked")
                else:
                    m=soup.find(text=re.compile(date)).parent.parent.parent
                    att_status=m.find('td',class_="statuscol cell c2").text
                    if(att_status=="?"):
                        if(time[0]<end_time[0] or (time[0]==end_time[0] and time[1]<end_time[1])):
                            attendance_status.append("Not active yet(server time lag-reload after sometime)")
                        else:
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
        context['login']="true"
        context['title']="Lms-Lite"
    return render(request,'user/success_message.html',context)
def hub(request):
    global hubcontent
    hubcontent['login']="true"
    return render(request,'user/hub.html',hubcontent)
# Create your views here.
