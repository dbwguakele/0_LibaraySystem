#!/usr/bin/python
#encoding=gbk
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import MySQLdb
import sys
import urllib
import time
import datetime
import os

reload(sys)
sys.setdefaultencoding( "gbk" )

def searchDataBase(sql):
        db = MySQLdb.connect("localhost","root","950609","bookmis",charset='gbk') 
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            if sql[0:6]!="SELECT" and sql[0:6]!="select":
                db.commit()
            db.close()
            return results
        except Exception,e:
            print "Error: unable to fecth data"
            print e
            return 'error'

def checkAuthority():
        try:
            userInfo=open('user.txt','r').read()
            if userInfo[0]=='m':
                return 'm'
            elif userInfo[0]=='a':
                return 'a'
            else:
                return None
        except:
            return None
            

class MyHandler(BaseHTTPRequestHandler):
#    '''Definition of the request handler.'''

    def doAdminRecord(self,action):
        try:
            if checkAuthority()!='a':
                return ''' <!DOCTYPE html><script>alert("��û�д˲�����Ȩ��,���ٴε�¼����.");history.go(-1);</script>'''
            if len(action)==2 or action[2]=="search":
                if len(action)==2:
                    sql='''select borrow.reader_id,reader_name,borrow.book_id,book_name,date_borrow,date_return,loss,days from borrow,readers,books,member_level where books.book_id=borrow.book_id and readers.reader_id=borrow.reader_id and member_level.level=readers.level'''
                else:
                    cmd=action[3][1:].split("&")
                    searchWord=str(cmd[0].split('=')[1])
                    searchBy="borrow."+str(cmd[1].split('=')[1])
                    sql='''select borrow.reader_id,reader_name,borrow.book_id,book_name,date_borrow,date_return,loss,days from borrow,readers,books,member_level where books.book_id=borrow.book_id and readers.reader_id=borrow.reader_id and member_level.level=readers.level and %s="%s"''' % (searchBy,searchWord)

                print "sql���Ϊ:"+sql
                result=searchDataBase(sql)
                print "result:"+str(result)
                if result=='error':
                    return ''' <!DOCTYPE html><script>alert("���ݿ����ʧ��!");history.go(-1);</script>'''
                else:
                    
                    resultCode=''
                    if len(result)==0:
                        resultCode="<td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td>"
                    else:
                        for row in result:
                            rowCode=''
                            i=0
                            hasReturn="yes"
            
                            for item in row:
                                i+=1
                                if i==8:
                                    daysDelta=datetime.timedelta(days=item)
                                    itemCode="<td>%s</td>" % str(row[4]+daysDelta)
                                elif i==6:
                                    if str(item)!="None":
                                        itemCode="<td>%s</td>" % str(item)
                                    elif str(row[6])=="��":
                                        itemCode="<td>%s</td>" % "�Ѷ�ʧ"
                                    else:
                                        itemCode="<td>%s</td>" % "δ�黹"
                                        hasReturn="no"
                                else:
                                    itemCode='<td>%s</td>' % str(item)
                                rowCode+=itemCode
                            if hasReturn=="no":
                                rowCode+=('''<td><a href="|admin|record|return|?reader_id=%s&book_id=%s">����</a>|<a href="|admin|record|loss|?reader_id=%s&book_id=%s">��ʧ</a></td>''' % (row[0],row[2],row[0],row[2]))
                            else:
                                rowCode+="<td> </td>"
                            resultCode+=("<tr>%s</tr>" % rowCode)
                            

                    searchModelFile=open("admin/adminRecord.html","r")
                    searchModel=searchModelFile.read()
                    searchModelFile.close()
                    webPage=searchModel % resultCode
                    return webPage
            elif action[2]=="borrow":
                cmd=action[3][1:].split('&')
                sql='''select quantity_in from books where %s="%s"''' % (str(cmd[1].split('=')[0]),str(cmd[1].split('=')[1]))
                print "sql���Ϊ:"+sql
                checkQuantity=searchDataBase(sql)
                print "CQT:"+str(checkQuantity)
                if checkQuantity=='error':
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''
                elif len(checkQuantity)==0:
                    return ''' <!DOCTYPE html><script>alert("����ͼ����,δ��⵽����!");history.go(-1);</script>'''
                elif int(checkQuantity[0][0])==0:
                    return ''' <!DOCTYPE html><script>alert("�Բ���,�����Ѿ���������!");history.go(-1);</script>'''

                sql='''select numbers,borrow.reader_id,borrow.book_id,date_return from borrow,readers,member_level where borrow.reader_id=readers.reader_id and readers.level=member_level.level and date_return is null and readers.reader_id="%s"''' % (str(cmd[0].split('=')[1]))
                print "sql���Ϊ:"+sql
                checkNumber=searchDataBase(sql)
                print "CNB:"+str(checkNumber)
                if checkNumber=='error':
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''
                elif len(checkNumber)!=0 and len(checkNumber)==int(checkNumber[0][0]):
                    return ''' <!DOCTYPE html><script>alert("�û�Ա���ֻ��ͬʱ��%d����!");history.go(-1);</script>''' % int(checkNumber[0][0])

                reader_id=str(cmd[0].split('=')[1])
                book_id=str(cmd[1].split('=')[1])
                curDate=time.strftime("%Y-%m-%d")
                sql='''select * from loss_card where reader_id="%s"''' % reader_id
                if len(searchDataBase(sql))!=0:
                    return ''' <!DOCTYPE html><script>alert("���û��Ѿ���ʧ,����ʧ��!");history.go(-1);</script>''' 
                
                sql='''insert into borrow (reader_id,book_id,date_borrow,loss) values ("%s","%s","%s","��")''' % (reader_id,book_id,curDate)
                print "sql���Ϊ:"+sql
                if searchDataBase(sql)=='error':
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''

                sql='''update books set quantity_in=quantity_in-1,quantity_out=quantity_out+1 where book_id="%s"''' % (book_id)
                print "sql���Ϊ:"+sql
                if searchDataBase(sql)=='error':
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''
                return ''' <!DOCTYPE html><script>alert("����ɹ�!");window.location.assign("|admin|record");</script>'''

            elif action[2]=="return":
                cmd=action[3][1:].split('&')
                reader_id=str(cmd[0].split("=")[1])
                book_id=str(cmd[1].split("=")[1])

                sql='''select * from borrow where reader_id="%s" and book_id="%s"''' % (reader_id,book_id)
                print "sql���Ϊ:"+sql
                result=searchDataBase(sql)
                if result=="error":
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''

                if len(result)==0:
                    return ''' <!DOCTYPE html><script>alert("���ݿ��в�û�������Ľ����¼,����ʧ��!");history.go(-1);</script>'''
                curDate=time.strftime("%Y-%m-%d")
                sql='''update borrow set date_return="%s" where book_id="%s" and reader_id="%s";''' % (curDate,book_id,reader_id)
                print "sql���Ϊ:"+sql
                if searchDataBase(sql)=="error":
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''
                sql='''update books set quantity_in=quantity_in+1,quantity_out=quantity_out-1 where book_id="%s"''' % (book_id)
                print "sql���Ϊ:"+sql
                if searchDataBase(sql)=="error":
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''

                return ''' <!DOCTYPE html><script>alert("����ɹ�!");window.location.assign("|admin|record");</script>'''

            elif action[2]=="loss":
                cmd=action[3][1:].split('&')
                reader_id=str(cmd[0].split("=")[1])
                book_id=str(cmd[1].split("=")[1])

                sql='''select * from borrow where reader_id="%s" and book_id="%s"''' % (reader_id,book_id)
                print "sql���Ϊ:"+sql
                result=searchDataBase(sql)
                if result=="error":
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''

                if len(result)==0:
                    return ''' <!DOCTYPE html><script>alert("���ݿ��в�û�������Ľ����¼,��ʧʧ��!");history.go(-1);</script>'''
                curDate=time.strftime("%Y-%m-%d")
                sql='''update borrow set loss="��",date_return="%s" where reader_id="%s" and book_id="%s"''' % (curDate,reader_id,book_id)
                print "sql���Ϊ:"+sql
                if searchDataBase(sql)=="error":
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''
                sql='''update books set quantity_out=quantity_out-1,quantity_loss=quantity_loss+1 where book_id="%s"''' % book_id
                print "sql���Ϊ:"+sql
                if searchDataBase(sql)=="error":
                    return ''' <!DOCTYPE html><script>alert("�������ݿ�ʧ��!");history.go(-1);</script>'''
                return ''' <!DOCTYPE html><script>alert("��ʧ�ɹ�!");window.location.assign("|admin|record");</script>'''
        except Exception,e:
            print "Error in doAdminRecord:"
            print e
            return ''' <!DOCTYPE html><script>alert("failed");history.go(-1);</script>'''
    
    def doAdminReader(self,action):
        try:
            if checkAuthority()!='a':
                return ''' <!DOCTYPE html><script>alert("��û�д˲�����Ȩ��,���ٴε�¼����.");history.go(-1);</script>'''
            if len(action)==2 or action[2]=="search":
                if len(action)==2:
                    #|admin|reader
                    sql='''select reader_id,reader_name,sex,birthday,phone,mobile,card_name,card_id,level,day from readers'''
                else:
                    #|admin|reader|?cmd
                    cmd=action[3][1:].split("&")
                    print "������ѯ��������:"+str(cmd)
                    searchName=cmd[0].split("=")[1]
                    searchBy=cmd[1].split("=")[1]
                    sql='''select reader_id,reader_name,sex,birthday,phone,mobile,card_name,card_id,level,day from readers where %s like "%%%s%%"''' % (searchBy,searchName)

                result=searchDataBase(sql)

                if result=="error":
                    return ''' <!DOCTYPE html>
                            <script>alert("���ݿ����ʧ��!");    history.go(-1);</script>
                            '''
                
                resultCode=""
                editCode='''<td align="center"><a href="|admin|reader|edit|%s"><img src="img/edit.png" alt="�༭">��<a href="|admin|reader|delete|%s"><img src="img/delete.png" alt="��ʧ" onClick="return confirmDelete()"></a></td>'''
                if len(result)!=0:
                    for row in result:
                        rowCode=""
                        for item in row:
                            itemCode="<td>%s</td>" % str(item)
                            rowCode+=itemCode
                        rowCode="<tr>%s%s</tr>" % (rowCode,(editCode % (row[0],row[0])))
                        resultCode+=rowCode
                else:
                    resultCode='''<tr><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td></tr>'''

                sql='''select reader_id,reader_name from loss_card'''
                result=searchDataBase(sql)
                resultCode2=''
                if result=="error":
                    return ''' <!DOCTYPE html>
                            <script>alert("���ݿ����ʧ��!");    history.go(-1);</script>
                            '''
                else:
                    if len(result)!=0:
                        for row in result:
                            rowCode='''<tr><td>%s</td><td>%s</td></tr>''' %(str(row[0]),str(row[1]))
                            resultCode2+=rowCode
                    else:
                        resultCode2='''<tr><td>��</td><td>��</td><td>��</td></tr>'''
                readerModelFile=open("admin/adminReader.html","r")
                readerModel=readerModelFile.read()
                readerModelFile.close()

                webPage=readerModel % (resultCode,resultCode2)
                return webPage
            elif action[2]=="edit":
                if action[3][0]!='?':
                    #��ʾ�༭����
                    print '��ʼ��ȥ"%s"�༭����:' % str(action[3])
                    reader_id=str(action[3])
                    sql='''select * from readers where reader_id="%s"''' % reader_id
                    result=searchDataBase(sql)
                    print "result:"+str(result)
                    if result=='error':
                        return '''
                                <!DOCTYPE html>
                                <script>alert(�������ݿ����!");    history.go(-1);</script>
                                '''
                    else:
                        editModelFile=open("admin/adminReaderEdit.html",'r')
                        editModel=editModelFile.read()
                        editModelFile.close()

                        row=result[0]
                        reader_id=str(row[0])
                        reader_name=str(row[1])
                        sex=str(row[2])
                        birthday=str(row[3])
                        phone=str(row[4])
                        mobile=str(row[5])
                        card_name=str(row[6])
                        card_id=str(row[7])
                        level=str(row[8])
                        day=str(row[9])
                        password=str(row[10])
                        
                        if sex=="��":
                            rsex=("selected"," ")
                        else:
                            rsex=(" ","selected")

                        if card_name=="���֤":
                            rcard_name=("selected"," ")
                        else:
                            rcard_name=(" ","selected")

                        if level=="��ͨ":
                            rlevel=("selected"," "," ")
                        elif level=="����":
                            rlevel=(" " , "selected" , " ")
                        else:
                            rlevel=(" " , " " , "selected")
                        print (reader_id+reader_name+rsex[0]+rsex[1]+birthday+phone+mobile+rcard_name[0]+rcard_name[1]+card_id+rlevel[0]+rlevel[1]+rlevel[2]+day+password)
                        
                        webPage = editModel % (reader_id,reader_name,rsex[0],rsex[1],birthday,phone,mobile,rcard_name[0],rcard_name[1],card_id,rlevel[0],rlevel[1],rlevel[2],day,password)
                        return webPage
                else:
                    #?reader_id=%25s&reader_name=%25s&sex=%C4%D0&birthday=%25s&phone=%25s&mobile=%25s&
                    #card_name=%C9%ED%B7%DD%D6%A4&card_id=%25s&level=%C6%D5%CD%A8&day=%25s&password=%25s
                    cmd=action[3][1:].split("&")
                    print "cmd:"+str(cmd)

                    setCode=''
                    for item in cmd:
                        setCode+=''',%s="%s"''' % (str(item.split('=')[0]),str(item.split('=')[1]))

                    setCode=setCode[1:]

                    sql='''update readers set %s where reader_id="%s"''' % (setCode,str(cmd[0].split('=')[1]))
                    print "sql���Ϊ:"+sql

                    result=searchDataBase(sql)
                    print result
                    if result=='error':
                        return '''
                                <!DOCTYPE html>
                                <script>alert(�������ݿ����!");    history.go(-1);</script>
                                '''

                    return  '''
                                <!DOCTYPE html>
                                <script>alert("�޸ĳɹ�!");    window.location.assign("|admin|reader");</script>
                            '''
            elif action[2]=="delete":
                reader_id=str(action[3])
                sql='''insert into loss_card (select * from readers where reader_id="%s")''' % reader_id
                print "sql���Ϊ:"+sql
                result=searchDataBase(sql)
                sql='''delete from readers where reader_id="%s"''' % reader_id
                print "sql���Ϊ:"+sql
                result=searchDataBase(sql)
                if result=='error':
                    return '''
                                <!DOCTYPE html>
                                <script>alert(�������ݿ����!");    history.go(-1);</script>
                           '''
                else:
                    return '''  <!DOCTYPE html>
                                <script>alert("��ʧ��Ա�ɹ�!");    window.location.assign("|admin|reader");</script>
                           '''
                
            elif action[2]=="new":
                if len(action)==3:
                #|admin|reader|new
                    curDate=time.strftime("%Y-%m-%d")
                    newModelFile=open("admin/adminReaderNew.html","r")
                    newModel=str(newModelFile.read())
                    newModelFile.close()
                    webPage=newModel % curDate
                    return webPage
                else:
                #|admin|reader|new|?cmd
                #%7Cadmin%7Creader%7Cnew%7C?reader_id=&sex=%C5%AE&birthday=1900-01-01&
                #phone=&mobile=&card_name=%C9%ED%B7%DD%D6%A4&card_id=&level=&day=%25s&password=d
                    cmd=action[3][1:].split("&")

                    last_id=str(int(str(searchDataBase("select max(reader_id) from readers")[0][0])[1:])+1)
                    l=len(last_id)
                    if l>3:
                        return '''
                                <!DOCTYPE html>
                                <script>alert("��Ա���Ѿ���������");    history.go(-1);</script>
                                '''
                    elif l==3:
                        last_id="r"+last_id
                    elif l==2:
                        last_id="r0"+last_id
                    elif l==1:
                        last_id="r00"+last_id

                    
                    field="reader_id"
                    value='''"%s"''' % last_id
                    for item in cmd:
                        field+=(","+str(item.split("=")[0]))
                        value+=(''',"%s"''' % str(item.split("=")[1]))
                    
                    sql='''insert into readers (%s) values (%s)''' % (field,value)
                    print "��ӻ�Ա��sql���Ϊ:"+sql

                    if searchDataBase(sql)=="error":
                        return '''
                                <!DOCTYPE html>
                                <script>alert("���ʧ��:�������ݿ����!");    history.go(-1);</script>
                                '''
                    return '''
                                <!DOCTYPE html>
                                <script>alert("��ӳɹ�:���߱��Ϊ%s!");    window.location.assign("|admin|reader");</script>
                            ''' % last_id
                
        except Exception,e:
            print "Error in doAdminReader..."
            print e
            return ''' <!DOCTYPE html>
                    <script>alert("failed!");    history.go(-1);</script>
                    '''

            
    
    def memberInfo(self):
        try:
            if checkAuthority()!='m':
                return ''' <!DOCTYPE html><script>alert("��û�д��û��������Ȩ��,������Ѿ���¼�����µ�¼����.");history.go(-1);</script>'''
            else:
                userStr=open("user.txt",'r').read()
                userID=userStr[2:]
                sql='''select * from readers where reader_id="%s"''' % (userID)
                result=searchDataBase(sql)
                reader_id=result[0][0]
                reader_name=result[0][1]
                sex=result[0][2]
                birthday=str(result[0][3])
                phone=result[0][4]
                mobile=result[0][5]
                card_name=result[0][6]
                card_id=result[0][7]
                level=result[0][8]
                createDay=str(result[0][9])
                memberInfoModelFile=open("member/memberInfo.html","r")
                webpage=memberInfoModelFile.read()
                return webpage % (reader_id,level,reader_name,sex,birthday,createDay,card_name,card_id,mobile,phone)
                
                
        except Exception,e:
            print "Error in memberinfo fuction:"
            print e
            return ''' <!DOCTYPE html>
                    <script>alert("Please first login!");    window.location.assign("/");</script>
                    '''

    def doLogin(self,method,userID,password):
        print "start doLogin(%s-%s-%s)"%(method,userID,password)
        if method=="member":
            userFile=open("user.txt","w")
            try:
                result=searchDataBase('''select password from readers where reader_id="%s"''' % (userID))
                print result
                if password==result[0][0]:
                    userFile.write("m:"+userID)
                    userFile.close()
                    print "Login Succeeded!"
                    webpage=self.memberInfo()
                    return webpage
                else:
                    raise "LoginError"
            except Exception,e:
                print "Exception e in doLogin:"
                print e
                print "Login Failed!"
                raise "LoginError"
        elif method=="admin":
            userFile=open("user.txt","w")
            try:
                result=searchDataBase('''select password from admin where userID="%s"''' % (userID))
                print result
                if password==result[0][0]:
                    userFile.write("a:"+userID)
                    userFile.close()
                    print "Login Succeeded!"
                    href="admin|book"
                    action=href.split('|')
                    webPage=self.doAdminBook(action)
                    return webPage
                else:
                    print "Wrong Password or UserID!"
                    raise "LoginError"
            except:
                print "Login Failed!"
                raise "LoginError"
        else:
            print "Wrong Method!"
            return '''
                    <!DOCTYPE html>
                    <script>alert("����ĵ�½ģʽ��!");    history.back(-1);</script>
                    '''

    def doBorrow(self,searchWord,searchBy,category="all"):
        sql='''select * from book_category'''
        try:
            if checkAuthority()!='m':
                return ''' <!DOCTYPE html><script>alert("��û�д��û��������Ȩ��,������Ѿ���¼�����µ�¼����.");history.go(-1);</script>'''
            allCategory=searchDataBase(sql)
            caSelectCode=""
            for row in allCategory:
                appendStr='''<option value="%s">%s</option>''' % (row[0],row[1])
                caSelectCode+=appendStr
            print "caSelectCode:"+caSelectCode
            
            if searchWord!='':
                if category == "all":
                    sql='''select * from books where %s like "%%%s%%"''' % (searchBy,searchWord)
                else:
                    sql='''select * from books where %s like "%%%s%%" and category_id="%s"''' % (searchBy,searchWord,category)
            else:
                if category == "all":
                    sql='''select * from books'''
                else:
                    sql='''select * from books where category_id="%s"''' % (category)
            result=searchDataBase(sql)
            resultTableCode=""
            if len(result)==0:
                resultTableCode='''<tr><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td></tr>'''
            else:
                for row in result:
                    rowTableCode=''
                    for item in row:
                        item=str(item)
                        itemTableCode='''<td>%s</td>'''
                        if item[0:2]=="ca" and len(item)==4:
                            for ca in allCategory:
                                if ca[0]==item:
                                    item=ca[1]      
                        itemTableCode=itemTableCode%item
                        rowTableCode+=itemTableCode
                    rowTableCode="<tr>"+rowTableCode+"</tr>"
                    resultTableCode+=rowTableCode
            memberBorrowModelFile=open("member/memberBorrow.html","r")
            memberBorrowModel=memberBorrowModelFile.read()
            print "test"
            webPage=memberBorrowModel % (caSelectCode,resultTableCode)
            print webPage
            return webPage
        except Exception,e:
            print "Exception in doBorrow:"
            print e
            return '''
                    <!DOCTYPE html>
                    <script>alert("Show borrow page failed!");    history.back(-1);</script>
                    '''

    def doHistory(self):
        try:
            if checkAuthority()!='m':
                return ''' <!DOCTYPE html><script>alert("��û�д��û��������Ȩ��,������Ѿ���¼�����µ�¼����.");history.go(-1);</script>'''


            userFile=open("user.txt","r")
            userFileStr=userFile.read()
            userID=userFileStr[2:]
            userFile.close()

            sql='''select borrow.book_id,book_name,date_borrow,date_return,loss from books,borrow where books.book_id=borrow.book_id and reader_id="%s"''' % (userID)
            result = searchDataBase(sql)
            print result
            sql='''select days from readers,member_level where member_level.level=readers.level and reader_id="%s"''' % (userID)
            daysResult=searchDataBase(sql)
            print daysResult
            daysDelta=datetime.timedelta(days=daysResult[0][0])

            resultTableCode=''
            if len(result)==0:
                resultTableCode='''<tr><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td></tr>'''
            else:
                for row in result:
                    rowTableCode=''
                    book_id=str(row[0])
                    book_name=str(row[1])
                    date_borrow=str(row[2])
                    date_return=str(row[3])
                    loss=str(row[4])
                    date_limit=str(row[2]+daysDelta)
                    if date_return=='None':
                        date_return="δ�黹"
                    rowTableCode='''<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>''' % (book_id,book_name,date_borrow,date_return,loss,date_limit)
                    resultTableCode+=rowTableCode

            memberHistoryModelFile=open("member/memberHistory.html","r")
            memberHistoryModel=memberHistoryModelFile.read()
            memberHistoryModelFile.close()
            webPage=memberHistoryModel % resultTableCode
            return webPage
        except Exception ,e:
            print "Exception in doHistory:"
            print e
            return '''
                    <!DOCTYPE html>
                    <script>alert("Show history page failed!");    history.back(-1);</script>
                    '''
    def doAdminBook(self,action):
        #href=admin|book
        #href=admin|book|search/delete/edit/new|...
        print "doAdminBook"
        try:
            if checkAuthority()!='a':
                return ''' <!DOCTYPE html><script>alert("��û�д��û��������Ȩ��,������Ѿ���¼�����µ�¼����.");history.go(-1);</script>'''

            sql='''select * from book_category'''
            allCategory=searchDataBase(sql)
            caSelectCode=""
            for row in allCategory:
                appendStr='''<option value="%s">%s</option>''' % (row[0],row[1])
                caSelectCode+=appendStr
            print "caSelectCode:"+caSelectCode
            result=()
            if len(action)==2 or action[2]=="search":
                if len(action)==2:
                    sql='''select * from books'''
                    result=searchDataBase(sql)
                else:
                    searchWord=str(action[3]).decode("utf-8","ignore")
                    searchBy=str(action[4])
                    category=str(action[5])
                    if category!="all" and category!="ALL":
                        sql='''select * from books where %s like "%%%s%%" and category_id="%s"''' % (searchBy,searchWord,category)
                    else:
                        sql='''select * from books where %s like "%%%s%%"''' % (searchBy,searchWord)
                    print "sql:"+sql
                    result=searchDataBase(sql)
                print result
                resultCode=""
                for row in result:
                    rowCode="<tr>"
                    for itemm in row:
                        item=str(itemm)
                        itemCode=""
                        if item[0:2]=="ca" and len(item)==4:
                            for ca in allCategory:
                                if item==ca[0]:
                                    item=ca[1]
                        itemCode="<td>%s</td>" % (item)
                        rowCode+=itemCode
                    rowCode+=('''<td align="center"><a href="|admin|book|edit|%s"><img src="img/edit.png" alt="�༭"></a>||<a href="|admin|book|delete|%s"><img src="img/delete.png" alt="ɾ��"></td></tr>''' % (str(row[0]),str(row[0])))
                    resultCode+=rowCode

                if len(result)==0:
                    resultCode='''<tr><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td><td>��</td></tr>'''
                adminModelFile=open("admin/adminBook.html","r")
                adminModel=adminModelFile.read()
                adminModelFile.close()
                webPage=adminModel % (caSelectCode,resultCode)
                print webPage
                return webPage
            elif action[2]=="delete":
                delBookID=str(action[3])
                sql='''select * from books where book_id="%s"''' % delBookID
                judge=searchDataBase(sql)
                print result
                if len(judge)!=1:
                    return '''
                                <!DOCTYPE html>
                                <script>alert("û�����ͼ��");    window.location.assign(|admin|book);</script>
                                '''
                else:
                    sql='''delete from books where book_id="%s"''' % delBookID
                    if searchDataBase(sql)=='error':
                        return '''
                                <!DOCTYPE html>
                                <script>alert("ɾ������");    window.location.assign("|admin|book");</script>
                                '''
                    return '''
                                <!DOCTYPE html>
                                <script>alert("ɾ���ɹ�");    window.location.assign("|admin|book");</script>
                                '''
            elif action[2]=="new":
                if len(action)==3:
                    #�����Ǵ�new����ҳ
                    newModelFile=open("admin/adminBookNew.html")
                    sql='''select * from book_category'''
                    allCategory=searchDataBase(sql)
                    caSelectCode=""
                    for row in allCategory:
                        appendStr='''<option value="%s">%s</option>''' % (row[0],row[1])
                        caSelectCode+=appendStr
                    print "caSelectCode:"+caSelectCode

                    last_id=str(int(str(searchDataBase("select max(book_id) from books")[0][0])[1:])+1)
                    l=len(last_id)
                    if l>3:
                        return '''
                                <!DOCTYPE html>
                                <script>alert("ͼ�����Ѿ���������");    history.go(-1);</script>
                                '''
                    elif l==3:
                        last_id="b"+last_id
                    elif l==2:
                        last_id="b0"+last_id
                    elif l==1:
                        last_id="b00"+last_id
                    
                    
                    webPage=str(newModelFile.read()) % (last_id,caSelectCode,time.strftime("%Y-%m-%d"))
                    newModelFile.close()
                    return webPage
                else:
                    #�������������Ĺ���
                    cmd=action[3][1:].split("&")
                    field=""
                    value=""
                    for item in cmd:
                        field+='''%s,''' % str(item.split('=')[0])
                        value+='''"%s",''' % str(item.split('=')[1])
                    field=field[0:len(field)-1]
                    value=value[0:len(value)-1]
                    sql='''insert into books (%s) values (%s)''' % (field,value)
                    if searchDataBase(sql)=="error":
                        return '''
                                <!DOCTYPE html>
                                <script>alert("����,���������Ƿ�������ȷ!");    history.go(-1);</script>
                                '''
                    
                    return '''
                                <!DOCTYPE html>
                                <script>alert("��ӳɹ�!");    window.location.assign("|admin|book");</script>
                            '''
            elif action[2]=="edit":
                if action[3][0]!='?':
                    cur=action[3]
                    sql='''select * from books where book_id="%s"''' % cur
                    result=searchDataBase(sql)
                    print result

                    
                    editModelFile=open("admin/adminBookEdit.html","r")
                    editModel=editModelFile.read()
                    editModelFile.close()
                    webPage=editModel % (cur,str(result[0][0]),str(result[0][1]),caSelectCode,str(result[0][2]),str(result[0][3]),str(result[0][5]),str(result[0][6]),str(result[0][7]),str(result[0][8]),str(result[0][9]))
                    return webPage
                else:
		    #�޸Ĳ���ʾ��:
		    #?ori=b001&book_id=b001&book_name=%CD%BC%CF%F1%B4%A6%C0%ED&category=all&author=%CD%F5%D2%BB&publishing=%B1%B1%BE%A9%B4%F3%D1%A7%B3%F6%B0%E6%C9%E7&price=21.0&date_in=2010-03-07&quantity_in=10&quantity_out=3&quantity_loss=0
                    print "�޸�ͼ�鿪ʼ...�޸�����Ϊ:%s" % str(action[3])
                    cmd=action[3][1:].split('&')
                    #print "cmd:"+str(cmd)
                    setCode=""
                    whereCode=""
                    for item in cmd:
                            if item[0:3]=="ori":
                                whereCode=str(item.split('=')[1])
                            elif item.split('=')[1]=="all":
                                print "category keep original."
                            else:
                                setCode+=str(item.split('=')[0])
                                setCode+='''="'''
                                setCode+=str(item.split('=')[1])
                                setCode+='''",'''
                    setCode=setCode[0:len(setCode)-1]
                    sql='''UPDATE books SET %s WHERE book_id="%s"''' % (setCode,whereCode)
                    print "�޸�ͼ���sql���Ϊ:%s" % sql
                    if searchDataBase(sql)=="error":
                        raise BaseException("Error: unable to fecth data")
                    
                    return '''
                            <!DOCTYPE html>
                            <script>alert("�޸ĳɹ�!");    window.location.assign("|admin|book");</script>
                            '''

        except Exception,e:
            print "Error in doAdminBook:"
            print e
            return '''
                    <!DOCTYPE html>
                    <script>alert("Failed!");    history.back(-1);</script>
                    '''
    def _writeheaders(self,doc):
 
        if doc is None:
            self.send_response(404)
        else:
            self.send_response(200)
     
     
        self.send_header("Content-type","text/html")
        self.end_headers()
     
    def _getdoc(self,filename):
        '''Handle a request for a document,returning one of two different page as as appropriate.'''
        print "1:"+filename
        filename=urllib.unquote(filename)
        print "2:"+filename
        if filename == '/':
            try:
                path="member.html"
                tmpFile=open(path,"rb")
                return tmpFile.read()
            except Exception,e:
                print "ERROR PATH:"
                print path
                return None
        elif filename[1] == '|':
            ##action
            action = filename[2:].split('|')
            print action
            if action[0] == "login":
                ##action=login
                try:
                    webPage=self.doLogin(action[1],action[2],action[3])
                except Exception,e:
                    print "Exception e in docfuntion:"
                    print e
                    print "Login Failed!"
                    print "Method:%s,UserID:%s,Password:%s" % (action[1],action[2],action[3])
                    webPage='''
                    <!DOCTYPE html>
                    <script>alert("Login Failed!");    history.back(-1);</script>
                    '''
                finally:
                    return webPage
                
            elif action[0] == "borrow":
                ##action=borrow
                if len(action)==1:
                    searchWord=""
                    searchBy="book_id"
                    category="all"
                else:
                    searchWord=action[1].decode("utf-8")
                    searchBy=action[2]
                    category=action[3]
                webPage=self.doBorrow(searchWord,searchBy,category)
                return webPage
            
            elif action[0] == "history":
                webPage=self.doHistory()
                return webPage
            
            elif action[0] == "memberinfo":
                webPage=self.memberInfo()
                return webPage

            elif action[0] == "logout":
                os.remove("user.txt")
                f=open("member.html","r")
                webPage=f.read()
                return webPage
            #�����￪ʼ���ǹ���Ա��������
            elif action[0] == "admin":
                try:
                    userFile=open("user.txt","r")
                    if str(userFile.read())[0]!='a':
                        return '''<!DOCTYPE html><script>alert("���¼!");    history.back(-1);</script>'''
                except Exception,e:
                    print e
                    return '''<!DOCTYPE html><script>alert("���¼!");    history.back(-1);</script>'''
                if action[1]=="book":
                    webPage=self.doAdminBook(action)
                    return webPage
                elif action[1] == "record":
                    webPage=self.doAdminRecord(action)
                    return webPage
                elif action[1] == "reader":
                    webPage=self.doAdminReader(action)
                    return webPage
        else:
            try:
                path=filename[1:]
                tmpFile=open(path,"rb")
                return tmpFile.read()
            except IOError:
                print "ERROR"
                return None
         
    def do_HEAD(self):
        '''Handle a request for headers only'''
        doc=self._getdoc(self.path)
        self._writeheaders(doc)
 
    def do_GET(self):
        '''Handle a request for headers and body'''
        print "Get path is:%s"%self.path
        doc=self._getdoc(self.path)
        self._writeheaders(doc)
        if doc is None:
            self.wfile.write('''
                                <html>
                                    <head>
                                        <title>Not Found</title>
                                        <body>
                                            �Ҳ���������� '%s'!
                                        </body>
                                    </head>
                                </html>
                                '''%(self.path))
 
        else:
            self.wfile.write(doc)
 
#Create the pbject and server requests
serveaddr=('',8000)
httpd=HTTPServer(serveaddr,MyHandler)
print "Base serve is start add is %s port is %d"%(serveaddr[0],serveaddr[1])
httpd.serve_forever()
