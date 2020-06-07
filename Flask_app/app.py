from flask import Flask, render_template,request,redirect, url_for,session,flash
import sqlite3
import os
app = Flask(__name__)
app.secret_key = 'shourya'

status = False

@app.route('/')
def index():
    if 'loggedin' in session:
        status = True
        username = session['name']
        return render_template("new.html",status = status,username = username) 
    else:
        status = False
        return render_template("new.html",status = status) 


@app.route('/',methods = ["POST","GET"])
def login():
    msg = ''
    lg = True
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if email == 'admin' and password == 'admin':
            return redirect(url_for('admin'))
        with sqlite3.connect("fantasy league.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * from Players where email = (?) AND password = (?)",(email,password))
            user = cur.fetchone()
            if user:
                session['loggedin'] = True
                session['name'] = user[1]
                session['email'] = user[2]
                status = True
                username = user[1]
                return render_template("new.html",username = username,status = status)
            else:
                msg = 'incorrect password'
                status = False
                lg = False
                return render_template("new.html",msg = msg,status = status, lg = lg)
    return render_template("new.html",msg = msg,status = status)

@app.route('/logout/home')  
def logout():
    status = False
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('name',None)
        session.pop('email',None)
        return render_template("new.html",status = status)
    else:
        status = False
        return render_template("new.html",status = status)          

@app.route('/register/')
def register():
	return render_template("login.html")

@app.route("/savedetails",methods = ["POST","GET"])  
def saveDetails():  
    msg = "msg"  
    if request.method == "POST":  
        try:  
            name = request.form["name"]  
            email = request.form["email"]  
            password = request.form["password"]  
            with sqlite3.connect("fantasy league.db") as con:  
                cur = con.cursor()  
                cur.execute("INSERT into Players (name, email, password) values (?,?,?)",(name,email,password))  
                con.commit()  
                msg = "SignUp Successful"  
        except:  
            con.rollback()  
            msg = "Error while Signing up. Try Again"  
        finally:  
            status = False
            return render_template("new.html",msg = msg,status=status)  
            con.close()  
            
@app.route('/matches/<username>')
def selectmatch(username):
    con = sqlite3.connect("fantasy league.db")
    con.row_factory = sqlite3.Row 
    cur = con.cursor() 
    cur.execute("select * from MATCHES")
    rows = cur.fetchall()
    cur.execute("SELECT * FROM RANKS ORDER BY POINTS DESC")
    r1 = cur.fetchall()
    #usr = session['name']
    usrm = session['email']
    return render_template("page2.html",rows = rows, username = username, usrm = usrm, r1 = r1) 

@app.route("/play/<team1>/<team2>/<username>")  
def play(team1,team2,username):  
    con = sqlite3.connect("fantasy league.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT BS.NAME,K.TYPE,K.TEAM,K.CREDITS,BS.INNINGS,BS.MATCHES,BS.AVG,BS.RUNS,BS.NOT_OUT,BS.SR,BS.HUNDREDS,BS.FIFTIES,BS.FOUR,BS.SIX,BS.HS,BS.id FROM BATTING_STATISTICS as BS INNER JOIN (SELECT * FROM " +team1+" UNION SELECT * FROM "+team2+")  AS K ON K.NAME=BS.NAME")
    rows = cur.fetchall()
    cur.execute("SELECT BS.NAME,K.TYPE,K.TEAM,K.CREDITS,BS.MATCHES,BS.AVG,BS.WICKETS,BS.ER,BS.BEST_BOWL,BS.id FROM BOWLING_STATISTICS as BS INNER JOIN (SELECT * FROM " +team1+" UNION SELECT * FROM "+team2+")  AS K ON K.NAME=BS.NAME")
    r1 = cur.fetchall()
    return render_template("play.html",rows = rows,team1=team1,team2 = team2, username = username,r1 = r1)   

@app.route("/play/<team1>/<team2>/<username>",methods = ["POST","GET"])  
def selectplayer(team1,team2,username):
    if request.method == 'POST':
        p1 = request.form.getlist("player")
        usr = session['name']
        with sqlite3.connect("fantasy league.db") as con:
            cur = con.cursor()
            if len(p1) == 11:
                for i in p1:
                    cur.execute("INSERT INTO MYTEAM (PLAYER,session) values (?,?)",(i,username))
                    con.commit()
                cur.execute("INSERT INTO RANKS (ID,team1,team2) VALUES (?,?,?)",(username,team1,team2))
                con.commit()
        con.close()
    return redirect(url_for('final', team1 = team1 , team2 = team2 , username = username)) 

@app.route('/final/<team1>/<team2>/<username>')
def final(team1,team2,username):
    con = sqlite3.connect("fantasy league.db")
    con.row_factory = sqlite3.Row 
    cur = con.cursor() 
    cur.execute("SELECT MT.PLAYER,MT.POINTS,K.TEAM,K.TYPE FROM MYTEAM as MT INNER JOIN (SELECT * FROM "+team1+" UNION SELECT * FROM "+team2+" ) AS K ON K.NAME=MT.PLAYER WHERE session = (?)",(username,))
    rows = cur.fetchall()
    cur.execute("SELECT * FROM RANKS ORDER BY POINTS DESC")
    r = cur.fetchall()
    return render_template("final_page.html", rows= rows, team1 = team1, team2 = team2, r = r,username = username)

@app.route('/admin',methods = ["POST","GET"])
def admin():
    if request.method == 'POST':
        name1 = request.form['name']
        pts = request.form['points']
        team1 = request.form['t1']
        team2 = request.form['t2']
        reset = request.form.get('reset')
        if reset == 'reset':
            con = sqlite3.connect("fantasy league.db")
            cur = con.cursor() 
            cur.execute("DELETE FROM MYTEAM")
            con.commit()
            cur.execute("DELETE FROM RANKS")
            con.commit()
            cur.execute("UPDATE CSK SET POINTS = 0;")
            con.commit()
            cur.execute("UPDATE KKR SET POINTS = 0;")
            con.commit()
            cur.execute("UPDATE RCB SET POINTS = 0;")
            con.commit()
            cur.execute("UPDATE MI SET POINTS = 0;")
            con.commit()
            return render_template("admin.html")
        con = sqlite3.connect("fantasy league.db")
        con.row_factory = sqlite3.Row 
        cur = con.cursor() 
        cur.execute("SELECT * FROM RANKS")
        rows = cur.fetchall()
        with sqlite3.connect("fantasy league.db") as con:
            cur = con.cursor()
            #RCB vs CSK
            if (team1 == 'CSK' or team1 == 'RCB') and (team2 == 'CSK' or team2 == 'RCB'):
                cur.execute("UPDATE RCB_CSK SET POINTS = (?), NAME = (?) WHERE NAME = (?)",(pts,name1,name1))
                con.commit()
                cur.execute("UPDATE MYTEAM SET POINTS = (SELECT POINTS FROM RCB_CSK WHERE RCB_CSK.NAME = (?)) WHERE PLAYER = (?)",(name1,name1))
                con.commit()
                for row in rows:
                    cur.execute("UPDATE RANKS SET  POINTS = (SELECT SUM(POINTS) FROM MYTEAM WHERE session = (?) ) WHERE ID = (?)",(row[0],row[0]))
                    con.commit()
            #CSK vs MI
            elif (team1 == 'CSK' or team1 == 'MI') and (team2 == 'CSK' or team2 == 'MI'):
                cur.execute("UPDATE CSK_MI SET POINTS = (?), NAME = (?) WHERE NAME = (?)",(pts,name1,name1))
                con.commit()
                cur.execute("UPDATE MYTEAM SET POINTS = (SELECT POINTS FROM CSK_MI WHERE CSK_MI.NAME = (?)) WHERE PLAYER = (?)",(name1,name1))
                con.commit()
                for row in rows:
                    cur.execute("UPDATE RANKS SET  POINTS = (SELECT SUM(POINTS) FROM MYTEAM WHERE session = (?) ) WHERE ID = (?)",(row[0],row[0]))
                    con.commit()
            #KKR vs CSK
            elif (team1 == 'CSK' or team1 == 'KKR') and (team2 == 'CSK' or team2 == 'KKR'):
                cur.execute("UPDATE KKR_CSK SET POINTS = (?), NAME = (?) WHERE NAME = (?)",(pts,name1,name1))
                con.commit()
                cur.execute("UPDATE MYTEAM SET POINTS = (SELECT POINTS FROM KKR_CSK WHERE KKR_CSK.NAME = (?)) WHERE PLAYER = (?)",(name1,name1))
                con.commit()
                for row in rows:
                    cur.execute("UPDATE RANKS SET  POINTS = (SELECT SUM(POINTS) FROM MYTEAM WHERE session = (?) ) WHERE ID = (?)",(row[0],row[0]))
                    con.commit() 
            #MI vs KKR
            elif (team1 == 'KKR' or team1 == 'MI') and (team2 == 'KKR' or team2 == 'MI'):
                cur.execute("UPDATE MI_KKR SET POINTS = (?), NAME = (?) WHERE NAME = (?)",(pts,name1,name1))
                con.commit()
                cur.execute("UPDATE MYTEAM SET POINTS = (SELECT POINTS FROM MI_KKR WHERE MI_KKR.NAME = (?)) WHERE PLAYER = (?)",(name1,name1))
                con.commit()
                for row in rows:
                    cur.execute("UPDATE RANKS SET  POINTS = (SELECT SUM(POINTS) FROM MYTEAM WHERE session = (?) ) WHERE ID = (?)",(row[0],row[0]))
                    con.commit()
            #RCB vs KKR
            elif (team1 == 'KKR' or team1 == 'RCB') and (team2 == 'KKR' or team2 == 'RCB'):
                cur.execute("UPDATE RCB_KKR SET POINTS = (?), NAME = (?) WHERE NAME = (?)",(pts,name1,name1))
                con.commit()
                cur.execute("UPDATE MYTEAM SET POINTS = (SELECT POINTS FROM RCB_KKR WHERE RCB_KKR.NAME = (?)) WHERE PLAYER = (?)",(name1,name1))
                con.commit()
                for row in rows:
                    cur.execute("UPDATE RANKS SET  POINTS = (SELECT SUM(POINTS) FROM MYTEAM WHERE session = (?) ) WHERE ID = (?)",(row[0],row[0]))
                    con.commit()
            #RCB vs MI
            elif (team1 == 'RCB' or team1 == 'MI') and (team2 == 'RCB' or team2 == 'MI'):
                cur.execute("UPDATE RCB_MI SET POINTS = (?), NAME = (?) WHERE NAME = (?)",(pts,name1,name1))
                con.commit()
                cur.execute("UPDATE MYTEAM SET POINTS = (SELECT POINTS FROM RCB_MI WHERE RCB_MI.NAME = (?)) WHERE PLAYER = (?)",(name1,name1))
                con.commit()
                for row in rows:
                    cur.execute("UPDATE RANKS SET  POINTS = (SELECT SUM(POINTS) FROM MYTEAM WHERE session = (?) ) WHERE ID = (?)",(row[0],row[0]))
                    con.commit()
        con.close()
    return render_template("admin.html")

if __name__ == '__main__':
	app.run(debug=True)
