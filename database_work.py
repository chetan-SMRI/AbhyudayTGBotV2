import sqlite3
from datetime import datetime,timedelta

##Doesnt Approve User
def register_user_contact(user_id,contact):
    print(f'Registering user, Bot Private ID {user_id} ,Contact {contact}')
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("""
    INSERT INTO CLIENTLIST ("ClientID","Balance","Contact","ApproveStatus")
    VALUES ('"""+user_id+"""',0,'"""+contact+"""',0);
    """)
    con.commit()

##Approves User
def register_user(user_id,user_alias):
    print(f'Registering user, Bot Private ID {user_id} ,Alias {user_alias}')
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("""
    UPDATE CLIENTLIST SET 
    ClientName='"""+user_alias+"""',
    Balance=0,
    ApproveStatus=1
    WHERE ClientID='"""+user_id+"""';
    """)
    con.commit()


    
    
def checkUserRegistered(user_id):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM ClientList WHERE ClientID='"+user_id+"';")
    for i in res.fetchall():
        if list(i)[4] == 1:
            return True    
    return False


def returnClientAlias(ID):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    res = cur.execute("SELECT ClientID,ClientName FROM ClientList")
    for id in res.fetchall():
        if (ID in str(id)):
            return id[1]
    return ID


###We Consider OrderMessageID as OrderID, because its unique per chat,per client
def create_order(USERId,Filename,DocumentID,Media,Size,Quantity,OrderMessageID):
    print(f'Generating Order With User : '+USERId+" , Order No. : "+OrderMessageID)
    OrderId=1
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    now = datetime.now()
    dateTimeString = now.strftime("%d/%m/%Y %H:%M:%S")
    
    WIDTH = ""
    HEIGHT=""
    WIDTH=Size.split('x')[0]
    HEIGHT=Size.split('x')[1]
    cur.execute("""
    INSERT INTO JOBLIST ("ClientID","FileName","Width","Height","Quantity","OrderMessageID","Media","FileDocumentID","DateTime","JobBilledStatus")
    VALUES ('"""+USERId+"""','"""+Filename+"""','"""+WIDTH+"""','"""+
    HEIGHT+"""','"""+Quantity+"""','"""+OrderMessageID+"""','"""+Media+"""','"""+DocumentID+"""','"""+dateTimeString+"""',0);""")
    con.commit()
    
    
def GetOrderDetails(OrderID):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM JobList WHERE OrderMessageID='"+OrderID+"';")
    for i in res.fetchall():
        return list(i)
        
def EditOrderDetails(chatID,OrderID,EditType,Edit):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    if EditType=="Media":
        cur.execute("""UPDATE JOBLIST SET Media='"""+Edit+"""' WHERE OrderMessageID='"""+OrderID+"""' AND ClientID='"""+chatID+"""'""")
    elif EditType=="WidthHeight":
        cur.execute("""UPDATE JOBLIST SET Width="""+Edit.split('x')[0]+""" , Height="""+Edit.split('x')[1]+""" WHERE OrderMessageID='"""+OrderID+"""' AND ClientID='"""+chatID+"""'""")
    elif EditType=="Quantity":
        cur.execute("""UPDATE JOBLIST SET Quantity='"""+Edit+"""' WHERE OrderMessageID='"""+OrderID+"""' AND ClientID='"""+chatID+"""'""")
    con.commit()


def CanEditOrder(chatID,OrderID):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM JobList WHERE ClientID='"+chatID+"' AND OrderMessageID='"+OrderID+"';")
    date = ""
    now = datetime.now()
    for i in res.fetchall():
        date = str(list(i)[11])
    try:
        if  datetime.strptime(date, "%d/%m/%Y %H:%M:%S") > datetime.today()-timedelta(minutes=10):
            return True
        else:
            return False
    except Exception as e:
        return False
        
        
def UpdateJobStatus(OrderID,Status):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    res = cur.execute("UPDATE JOBLIST SET PrintStatus='"+Status+"' WHERE OrderMessageID='"+OrderID+"';")
    con.commit()


def GetOrderDetailsFromOrderID(OrderID):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM JobList WHERE OrderMessageID='"+OrderID+"';")
    for i in res.fetchall():
        return list(i)