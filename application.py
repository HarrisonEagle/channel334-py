# -*- coding: utf-8 -*-
from flask import *
from flask import session
import pickle
import os,os.path
import sys
import datetime
import boto3
import pickle
import cloudpickle
from werkzeug.utils import secure_filename

class Reply:
    def __init__(self,username,userid,replyid,comment,userip,time,imageurl,repnum):
        self.username = username
        self.comment = comment
        self.userip = userip
        self.time = time
        self.replyid = replyid
        self.userid = userid
        self.imageurl = imageurl
        self.repnum = repnum

class Thre:
    def __init__(self,title,replylist):
        self.title = title
        self.replylist = replylist

class Tag:
    def __init__(self,tagname,taglist):
        self.tagname = tagname
        self.taglist = taglist


class UserInf:
    def __init__(self,username,userid,password,favorite,notification,mypost):
        self.username = username
        self.userid = userid
        self.password = password
        self.favorite = favorite
        self.notification = notification
        self.mypost = mypost

class IndexNum:
    def __init__(self):
        self.ntagindex = -1
        self.nthreadindex = -1
        self.threaderr = ""

class Notificationclass:
    def __init__(self,time,tagindex,threadindex,replycontent):
        self.time = time
        self.tagindex = tagindex
        self.threadindex = threadindex
        self.replycontent = replycontent

class Myposts:
     def __init__(self,time,tagindex,threadindex,replyindex,replyuserid,replycontent):
        self.time = time
        self.tagindex = tagindex
        self.threadindex = threadindex
        self.replyindex = replyindex 
        self.replyuserid = replyuserid
        self.replycontent = replycontent

class FavoriteThread:
    def __init__(self,tagindex,threadindex):
        self.tagindex= tagindex
        self.threadindex = threadindex

class Search:
    def __init__(self,tagindex,threadindex):
        self.tagindex= tagindex
        self.threadindex = threadindex

class Datasystem:
    def __init__(self,database,userdata):
        self.database = database
        self.userdata = userdata


indexnum = IndexNum()
datasystem = Datasystem([],[])

def loadfile():
    class Reply:
        def __init__(self,username,userid,replyid,comment,userip,time,imageurl,repnum):
            self.username = username
            self.comment = comment
            self.userip = userip
            self.time = time
            self.replyid = replyid
            self.userid = userid
            self.imageurl = imageurl
            self.repnum = repnum

    class Thre:
        def __init__(self,title,replylist):
            self.title = title
            self.replylist = replylist

    class Tag:
        def __init__(self,tagname,taglist):
            self.tagname = tagname
            self.taglist = taglist


    class UserInf:
        def __init__(self,username,userid,password,favorite,notification,mypost):
            self.username = username
            self.userid = userid
            self.password = password
            self.favorite = favorite
            self.notification = notification
            self.mypost = mypost

    class IndexNum:
        def __init__(self):
            self.ntagindex = -1
            self.nthreadindex = -1
            self.threaderr = ""

    class Notificationclass:
        def __init__(self,time,tagindex,threadindex,replycontent):
            self.time = time
            self.tagindex = tagindex
            self.threadindex = threadindex
            self.replycontent = replycontent

    class Myposts:
        def __init__(self,time,tagindex,threadindex,replyindex,replyuserid,replycontent):
            self.time = time
            self.tagindex = tagindex
            self.threadindex = threadindex
            self.replyindex = replyindex 
            self.replyuserid = replyuserid
            self.replycontent = replycontent

    class FavoriteThread:
        def __init__(self,tagindex,threadindex):
            self.tagindex= tagindex
            self.threadindex = threadindex
    
    with open('datas.hbase','rb') as db:
        datasystem.database = cloudpickle.load(db)


    with open('userdata.hbase','rb') as db2:
        datasystem.userdata = cloudpickle.load(db2)




app = Flask(__name__,static_url_path = "/static", static_folder = "static")
UPLOAD_FOLDER = '/static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','jpeg'])
app.config['SECRET_KEY'] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['SECRET_KEY'] = 'The secret key which ciphers the cookie'
app.config.from_object("config")
threaderr = ""
username = None
userid = -1

@app.before_first_request
def execute_this():
    
    
    s3 = boto3.resource('s3') 
    bucket = s3.Bucket('channel334storage')
    bucket.download_file('datas.hbase', 'datas.hbase')
    bucket.download_file('userdata.hbase', 'userdata.hbase')

    loadfile()



@app.route('/register', methods=['GET','POST'])
def regiter():
    if is_user_exist()==False:
        return render_template('regiter.html',error = "User Exists!")
    else:
        username = request.form['username']
        password = request.form['password']
        newuser = UserInf(username,len(datasystem.userdata),password,[],[],[])
        datasystem.userdata.append(newuser)
        with open('userdata.hbase','wb') as db:
            pickle.dump(datasystem.userdata,db)
        s3 = boto3.resource('s3') 
        bucket = s3.Bucket('channel334storage')
        bucket.upload_file('userdata.hbase', 'userdata.hbase')
        return redirect('/login')

@app.route('/goregiter', methods=['GET','POST'])
def goregiter():
    return render_template('regiter.html')

@app.route('/trylogin', methods=['GET','POST'])
def trylogin():
    strs = ""

    err = _is_account_valid()
    if err == 1:
        session['username'] = request.form['username']
        return redirect('/')
    elif err == 2:
        return render_template('login.html',error = "Password Incorrect!")
    return render_template('login.html',error = "User Does Not Exist!")

@app.route('/login', methods=['GET', 'POST'])
def login():

    loadfile()
        

    if request.method == 'POST' and _is_account_valid():
            
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    
    session.pop('username', None)
    session.pop('userid',None)
    
    return redirect('/login')



#1 Logined #2 Password Incorrect # User Not exist!
def _is_account_valid():
    for users in datasystem.userdata:
        if users.username ==  request.form['username']:
            if users.password == request.form['password']:
                session['userid']=users.userid
                userid = users.userid
                return 1
            else:
                return 2
    return 3

def is_user_exist():
    for users in datasystem.userdata:
        if users.username ==  request.form['username']:
            return False
    return True

@app.route('/opentag',methods = ['POST','GET'])
def opentag():
    loadfile()
    ttls = []
    times = []
    i = 0
    tagindex = int(request.form['action']) - 1
    while i != len(datasystem.database[tagindex].taglist):
        ttls.append(datasystem.database[tagindex].taglist[i].title)
        times.append(datasystem.database[tagindex].taglist[i].replylist[0].time)
        i+=1
    return render_template('tag.html',titles=zip(ttls,times),tagname = datasystem.database[tagindex].tagname,tagindex = tagindex,username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/newthread',methods = ['POST','GET'])
def newthread():
    tagindex = int(request.form['tagindex'])
    savefile()
    return render_template("newthread.html",tagindex = tagindex,username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/makenewtag',methods = ['POST','GET'])
def makenewttag():
    tagname = request.form['tagname']
    newtag = Tag(tagname,[])
    datasystem.database.append(newtag)
    savefile()
    return redirect('/')

@app.route('/sendfirstcomment',methods = ['POST','GET'])
def sendfirstcomment():
    title = request.form['title']
    tagindex = int(request.form['tagindex'])
    for tags in datasystem.database:
        for thread in tags.taglist:
            if title == thread.title:
                return render_template('newthread.html',error = "This Title has posted yet!",tagindex = tagindex)
    
    firstcomment = request.form['firstcomment']
    isanonymous = request.form.get("anonymous")
    usrname = ""
    if isanonymous:
        usrname = "風吹けば名無し"
    else:
        usrname = session['username']
    userip = request.remote_addr
    timenow = str(datetime.datetime.now())
    img_file = request.files['img_file']
    imgfilename = ""
    userid = session['userid']
    if img_file:
        imgfilename = secure_filename(img_file.filename)
        savedir = os.path.abspath(os.path.dirname(__file__)) + app.config['UPLOAD_FOLDER'] + img_file.filename
        file_name=savedir
        img_file.save(savedir)
    firstcomment = Reply(usrname,userid,-1,firstcomment,userip,timenow,imgfilename,0)
    mypost = Myposts(timenow,tagindex,0,0,0,firstcomment.comment)
    datasystem.userdata[int(session['userid'])].mypost.insert(0,mypost)
    commentlist = []
    commentlist.append(firstcomment)
    newtr = Thre(title,commentlist)
    datasystem.database[tagindex].taglist.insert(0,newtr)
    savefile()
    username = []
    comments = []
    times = []
    filenames = []
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[0].replylist):
        username.append(datasystem.database[tagindex].taglist[0].replylist[i].username)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[0].replylist):
        comments.append(datasystem.database[tagindex].taglist[0].replylist[i].comment)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[0].replylist):
        times.append(datasystem.database[tagindex].taglist[0].replylist[i].time)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[0].replylist):
        filenames.append(datasystem.database[tagindex].taglist[0].replylist[i].imageurl)
        i+=1
    
    indexnum.ntagindex = tagindex
    indexnum.nthreadindex = 0

    indexnum.threaderr = ""
    

    #return render_template('thread.html',title = datasystem.database[tagindex].taglist[0].title,comment_products=zip(username,times, comments,filenames),threadindex = 0,tagindex = tagindex)
    return redirect('/jump2')

def savefile():
    s3 = boto3.resource('s3') 
    bucket = s3.Bucket('channel334storage')
    with open('datas.hbase','wb') as db:
        pickle.dump(datasystem.database,db)
    with open('userdata.hbase','wb') as db:
        pickle.dump(datasystem.userdata,db)
    bucket.upload_file('datas.hbase', 'datas.hbase')
    bucket.upload_file('userdata.hbase', 'userdata.hbase')



@app.route('/gomypage',methods = ['POST','GET'])
def gomypage():
    loadfile()
    tagname = []
    threadname = []
    time = [] 
    replyindex = []
    threadindex = []
    tagindex = []
    replyuserid = []
    replycontent = []
    for posts in datasystem.userdata[int(session['userid'])].mypost:
        tagname.append(datasystem.database[int(posts.tagindex)].tagname)
        threadname.append(datasystem.database[int(posts.tagindex)].taglist[int(posts.threadindex)].title)
        time.append(posts.time)
        replyindex.append(posts.replyindex)
        threadindex.append(posts.threadindex)
        tagindex.append(posts.tagindex)
        replyuserid.append(posts.replyuserid)
        replycontent.append(posts.replycontent)

    favoritetagindex = []
    favoritetagtitle = []
    favoritethreadindex = []
    favoritethreadtitle = []

    for favorite in datasystem.userdata[int(session['userid'])].favorite:
        favoritetagindex.append(int(favorite.tagindex))
        favoritetagtitle.append(datasystem.database[int(favorite.tagindex)].tagname)
        favoritethreadindex.append(int(favorite.threadindex))
        favoritethreadtitle.append(datasystem.database[int(favorite.tagindex)].taglist[int(favorite.threadindex)].title)
    return render_template('mypage.html',username=session['username'],userid=session['userid'],postnum=len(time),myposts=zip(tagname,threadname,time,replycontent),favoritenum = len(favoritetagindex),myfavorites = zip(favoritetagindex,favoritetagtitle,favoritethreadindex,favoritethreadtitle),notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/sendnewcomment',methods = ['POST','GET'])
def sendnewcomment():
    threadindex = int(request.form['threadindex']) 
    tagindex = int(request.form['tagindex']) 
    newcomment = request.form['newcomment']
    usrname = ""
    isanonymous = request.form.get("anonymous")
    usrname = ""
    if isanonymous:
        usrname = "風吹けば名無し"
    else:
        usrname = session['username']
    userip = request.remote_addr
    timenow = str(datetime.datetime.now())
    mypost = Myposts(timenow,tagindex,threadindex,len(datasystem.database[tagindex].taglist[threadindex].replylist),0,newcomment)
    userindex = int(session['userid'])
    datasystem.userdata[userindex].mypost.append(mypost)
    
    
    img_file = request.files['img_file']
    imgfilename = ""
    if img_file:
        imgfilename = secure_filename(img_file.filename)
        savedir = os.path.abspath(os.path.dirname(__file__)) + app.config['UPLOAD_FOLDER'] + img_file.filename
        file_name=savedir
        img_file.save(savedir)
            

    NewReply = Reply(usrname,userindex,-1,newcomment,userip,timenow,imgfilename,0)
    datasystem.database[tagindex].taglist[threadindex].replylist.append(NewReply)
    savefile()

    username = []
    comments = []
    times = []
    filenames = []
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        username.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].username)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        comments.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].comment)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        times.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].time)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        filenames.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].imageurl)
        i+=1
    #return render_template('thread.html',title = datasystem.database[tagindex].taglist[threadindex].title,comment_products=zip(username, times,comments,filenames),threadindex = threadindex,tagindex=tagindex)
    indexnum.ntagindex = tagindex
    indexnum.nthreadindex = threadindex
    indexnum.threaderr = ""
    return redirect('/jump2')

@app.route('/jump',methods = ['POST','GET'])
def jump():
    loadfile()
    index = int(request.form['action']) - 1
    tagindex = int(request.form['tagindex']) 
    username = []
    comments = []
    times = []
    filenames = []
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        username.append(datasystem.database[tagindex].taglist[index].replylist[i].username)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        comments.append(datasystem.database[tagindex].taglist[index].replylist[i].comment)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        times.append(datasystem.database[tagindex].taglist[index].replylist[i].time)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        filenames.append(datasystem.database[tagindex].taglist[index].replylist[i].imageurl)
        i+=1
    i = 0
    return render_template('thread.html',title = datasystem.database[tagindex].taglist[index].title,comment_products=zip(username,times,comments,filenames),threadindex=index,tagindex = tagindex,threadindex2=index,tagindex2=tagindex,threadindex3=index,tagindex3=tagindex,username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/jump2',methods = ['POST','GET'])
def jump2():
    loadfile()
    tagindex = int(indexnum.ntagindex)
    index = int(indexnum.nthreadindex)
    print(tagindex)
    print(index)
    username = []
    comments = []
    times = []
    filenames = []
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        username.append(datasystem.database[tagindex].taglist[index].replylist[i].username)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        comments.append(datasystem.database[tagindex].taglist[index].replylist[i].comment)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        times.append(datasystem.database[tagindex].taglist[index].replylist[i].time)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[index].replylist):
        filenames.append(datasystem.database[tagindex].taglist[index].replylist[i].imageurl)
        i+=1
    i = 0
    return render_template('thread.html',title = datasystem.database[tagindex].taglist[index].title,comment_products=zip(username,times,comments,filenames),threadindex=index,tagindex = tagindex,threadindex2=index,tagindex2=tagindex,tagindex3=tagindex,threadindex3=index,error = indexnum.threaderr,username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/jump3',methods = ['POST','GET'])
def jump3():
    index = int(request.form['action']) - 1
    
    indexnum.ntagindex = datasystem.userdata[int(session['userid'])].mypost[index].tagindex
    indexnum.nthreadindex =  datasystem.userdata[int(session['userid'])].mypost[index].threadindex
    indexnum.threaderr = ""
    return redirect('/jump2')

@app.route('/jump4',methods = ['POST','GET'])
def jump4():
    index = int(request.form['action']) - 1
  
    indexnum.ntagindex = datasystem.userdata[int(session['userid'])].favorite[index].tagindex
    indexnum.nthreadindex =  datasystem.userdata[int(session['userid'])].favorite[index].threadindex
    indexnum.threaderr = ""
    return redirect('/jump2')

@app.route('/addtofavorite',methods = ['POST','GET'])
def addtofavorite():
    
    tagindex = request.form['tagindex2']
    threadindex = request.form['threadindex2']
    fav = FavoriteThread(tagindex,threadindex)
    datasystem.userdata[int(session['userid'])].favorite.insert(0,fav)
    indexnum.threaderr="Added to Favorite"
    indexnum.ntagindex = int(request.form['tagindex2'])
    indexnum.nthreadindex = int(request.form['threadindex2'])
    savefile()

    return redirect('/jump2')
    


@app.route('/')
def index():
    if session.get('username') is None:
        return redirect('/login')
    tags = []
    i = 0
    username=session.get('username')
    while i != len(datasystem.database):
        tags.append(datasystem.database[i].tagname)
        i+=1

    return render_template('index.html',titles=tags,username=username,notifynum = len(datasystem.userdata[int(session['userid'])].notification))
    
@app.route('/',methods = ['POST','GET'])
def index2():
    if session['username']==None or len(datasystem.userdata) == 0:
        return redirect('/login')
    tags = []
    i = 0
    username=session.get('username')
    while i != len(datasystem.database):
        tags.append(datasystem.database[i].tagname)
        i+=1

    return render_template('index.html',titles=tags,username=username,notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/newtag',methods = ['POST','GET'])
def newtag():
    return render_template("newtag.html",username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/gousersettings',methods = ['POST','GET'])
def gousersettings():
    return render_template("usersettings.html",username=session['username'],password=datasystem.userdata[int(session['userid'])].password,notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/changeusersettings',methods = ['POST','GET'])
def updateuserprofile():
    username = request.form["username"]
    password = request.form["password"]
    i = 0
    for user in datasystem.userdata:
        if username == user.username and i != int(session['userid']):
            return render_template("usersettings.html",username=session['username'],error="User Name Exists!")
        i+=1
    
    session['username'] = username
    userindex = int(session['userid'])
    datasystem.userdata[userindex].username = username
    datasystem.userdata[userindex].password = password
    savefile()
    return redirect('/gomypage')

@app.route('/reply',methods = ['POST','GET'])
def goreply():
    tagindex = request.form['tagindex3']
    threadindex = request.form['threadindex3']
    replyindex = int(request.form['action'])
    userindex = session['userid']
    replyuserindex = datasystem.database[int(tagindex)].taglist[int(threadindex)].replylist[replyindex-1].userid
    

    return render_template("reply.html",tagindex = tagindex , threadindex = threadindex,replyindex = replyindex,userindex = userindex,replyuserindex = replyuserindex,repindex = replyindex,username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))


@app.route('/sendreply',methods = ['POST','GET'])
def sendreply():
    threadindex = int(request.form['threadindex']) 
    tagindex = int(request.form['tagindex']) 
    replyindex = int(request.form['repindex'])
    newcomment = '>>>'+str(replyindex)+' '+request.form['newcomment']
    
    usrname = ""
    isanonymous = request.form.get("anonymous")
    usrname = ""
    if isanonymous:
        usrname = "風吹けば名無し"
    else:
        usrname = session['username']
    userip = request.remote_addr
    timenow = str(datetime.datetime.now())
    userindex = int(session['userid'])
    replyuserindex = int(request.form['replyuserindex'])
    mypost = Myposts(timenow,tagindex,threadindex,len(datasystem.database[tagindex].taglist[threadindex].replylist),replyuserindex,newcomment)
   
    datasystem.userdata[userindex].mypost.append(mypost)
    #print("User:"+str(userindex),file=sys.stdout)
    #print("Reply:"+str(replyuserindex),file=sys.stdout)
    img_file = request.files['img_file']
    imgfilename = ""
    if img_file:
        imgfilename = secure_filename(img_file.filename)
        savedir = os.path.abspath(os.path.dirname(__file__)) + app.config['UPLOAD_FOLDER'] + img_file.filename
        file_name=savedir
        img_file.save(savedir)
            

    NewReply = Reply(usrname,userid,replyuserindex,newcomment,userip,timenow,imgfilename,0)
    datasystem.database[tagindex].taglist[threadindex].replylist.append(NewReply)
    #add Notification to replied user
    notifycontent = timenow+' '+usrname+'さんが返信しました:'+newcomment
   
    notification = Notificationclass(timenow,tagindex,threadindex,notifycontent)
    datasystem.userdata[replyuserindex].notification.insert(0,notification)
    
    savefile()

    username = []
    comments = []
    times = []
    filenames = []
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        username.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].username)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        comments.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].comment)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        times.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].time)
        i+=1
    i = 0
    while i!= len(datasystem.database[tagindex].taglist[threadindex].replylist):
        filenames.append(datasystem.database[tagindex].taglist[threadindex].replylist[i].imageurl)
        i+=1
    #return render_template('thread.html',title = datasystem.database[tagindex].taglist[threadindex].title,comment_products=zip(username, times,comments,filenames),threadindex = threadindex,tagindex=tagindex)
    indexnum.ntagindex = tagindex
    indexnum.nthreadindex = threadindex
    indexnum.threaderr = "Replied"
    return redirect('/jump2')

@app.route('/gonotifications',methods = ['POST','GET'])
def gonotifications():
    loadfile()
    notifications =  []
    for noti in datasystem.userdata[int(session['userid'])].notification:
        notifications.insert(0,noti.replycontent)
        
    
    return render_template('notification.html',Notifications = zip(notifications),username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))


@app.route('/opennotification',methods = ['POST','GET'])
def opennotifications():
    notifyindex = int(request.form['action']) - 1


    indexnum.ntagindex = int(datasystem.userdata[int(session['userid'])].notification[notifyindex].tagindex)
    indexnum.nthreadindex = int(datasystem.userdata[int(session['userid'])].notification[notifyindex].threadindex)
    datasystem.userdata[int(session['userid'])].notification.pop(notifyindex)
    

    return redirect('/jump2')


@app.route('/searchintag',methods = ['POST','GET'])
def searchintag():
    word = request.form['search']
    results = []
    resulttagindex = []
    resultthreadindex = []

    tagindex = int(request.form['tagindex'])
    threadindex = 0
    for thread in datasystem.database[tagindex].taglist:
        if word in thread.title:
            results.append(thread.title)
            resulttagindex.append(str(tagindex))
            resultthreadindex.append(str(threadindex))
                
            
        threadindex+=1
    


    return render_template('search.html',word=word,tagname='all',results=zip(results,resulttagindex,resultthreadindex))

@app.route('/searchall',methods = ['POST','GET'])
def searchall():
    word = request.form['search']
    results = []
    resulttagindex = []
    resultthreadindex = []

    tagindex = 0
    threadindex = 0
    for tags in datasystem.database:
        threadindex = 0
        for thread in tags.taglist:
            if word in thread.title:
                results.append(thread.title)
                resulttagindex.append(str(tagindex))
                resultthreadindex.append(str(threadindex))
                
            
            threadindex+=1
        tagindex+=1
    


    return render_template('search.html',word=word,tagname='all',results=zip(results,resulttagindex,resultthreadindex),username=session['username'],notifynum = len(datasystem.userdata[int(session['userid'])].notification))

@app.route('/openthread',methods = ['POST','GET'])
def openthread():
    loadfile()
    title = request.form['action']
    tagindex = 0
    threadindex = 0
    for tags in datasystem.database:
        threadindex = 0
        for thread in tags.taglist:
            if title == thread.title:
                indexnum.ntagindex = tagindex
                indexnum.nthreadindex = threadindex
            threadindex+=1
        tagindex+=1

                
    
    indexnum.threaderr = ""
    return redirect('/jump2')



if __name__ == "__main__":

    s3 = boto3.resource('s3') 
    bucket = s3.Bucket('channel334storage')
    bucket.download_file('datas.hbase', 'datas.hbase')
    bucket.download_file('userdata.hbase', 'userdata.hbase')

    
    app.debug = False
    app.run()

