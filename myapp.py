from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
import datetime

####################################################################################

#creating app
app = Flask(__name__)
#configuring Databases
app.config['SECRET_KEY'] = 'blogger'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mydbpassword'
app.config['MYSQL_DB'] = 'blogger'

#initializing mysql
mysql = MySQL(app)

###################################################################################

userstatus = 0

###################################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    global userstatus
    if userstatus <= 0 :
        form = request.form
        if request.method == 'POST' and form['action'] == 'Login' :
            enteredemail = form['emailid']
            enteredpassword = form['password']
            cur = mysql.connection.cursor()
            result = cur.execute("Select * From users where email = %s and password = PASSWORD(%s);",[enteredemail,enteredpassword])
            user = cur.fetchone()
            cur.close()
            if result > 0:
                userstatus = user[0]
                return redirect(url_for('dashboard'))
        elif request.method == 'POST' and form['action'] == 'Confirm and Signup':
            fullname = form['fullname']
            emailid = form['emailid']
            password1 = form['password1'] 
            password2 = form['password2']
            if password1 == password2 :
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO users(fullname,email,password) VALUES (%s,%s,PASSWORD(%s));",[fullname,emailid,password1])
                mysql.connection.commit()
                result = cur.execute("SELECT * FROM users WHERE email = %s;",[emailid])
                user = cur.fetchone()
                cur.close()
                if result > 0 :
                    userstatus = user[0]
                    return redirect(url_for('dashboard'))
        return render_template('home.html')
    else:
        return redirect(url_for('dashboard'))

#-------------------------------------------------------------------------------

@app.route('/dashboard',methods=['GET', 'POST'] )
def dashboard():
    global userstatus
    id = userstatus
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        form = request.form
        cur = mysql.connection.cursor()
        if request.method == 'POST' and form['action'] == 'Update Profile' :
            fullname = form['fullname']
            password1 = form['password1'] 
            password2 = form['password2']
            if password1 == password2: 
                query = cur.execute("UPDATE users SET fullname = %s, password = PASSWORD(%s) WHERE id = %s;",[fullname,password1,id])
                mysql.connection.commit()
                return redirect(url_for('dashboard'))
        if request.method == 'POST' and form['action'] == 'Publish' :
            title = form['title']
            description = form['description']
            dated = datetime.date.today()
            query = cur.execute("INSERT INTO articles (title,post,userid,postdate) values (%s,%s,%s,%s);",[title,description,id,dated])
            mysql.connection.commit()
            return redirect(url_for('dashboard'))
        result1 = cur.execute("SELECT * FROM users WHERE id = %s;",[id])
        userdetails = cur.fetchall()
        result2 = cur.execute("SELECT * FROM articles WHERE userid = %s order by articles.id DESC;",[id])
        postdetails = cur.fetchall()        
        result3 = cur.execute("Select count(fid) from friends where id1 = %s;",[id])
        following = cur.fetchone()
        result4 = cur.execute("select count(fid) from friends where fid = %s;",[id])
        followers = cur.fetchone()
        result5 = cur.execute("select sum(likes) from articles where userid = %s;",[id])
        likes = cur.fetchone()
        result6 = cur.execute("select sum(dislikes) from articles where userid = %s;",[id])
        dislike = cur.fetchone()
        cur.close()
        return render_template('dashboard.html', userdetails = userdetails, postdetails = postdetails, following = following, followers = followers, likes = likes, dislike = dislike)

#-----------------------------------------------------------

@app.route('/friends')
def friends():
    global userstatus
    id = userstatus
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        result = cur.execute("select * from friends,users where users.id = friends.fid and friends.id1 = %s;",[id])
        following = cur.fetchall()
        result = cur.execute("select * from users where users.id != %s and users.id not in (select fid from friends where users.id = friends.fid and friends.id1 = %s);",[id,id])
        explore = cur.fetchall()
        cur.close()
        return render_template('friends.html', following = following, explore = explore)

#-----------------------------------------------------------

@app.route('/logout')
def logout():
    global userstatus
    userstatus = False
    return redirect(url_for('index'))

#-----------------------------------------------------------

@app.route('/deletearticle/<postid>')
def deletearticle(postid):
    global userstatus
    id = userstatus
    postid = postid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("DELETE FROM articles WHERE id = %s;",[postid])
        mysql.connection.commit()
        return redirect(url_for('dashboard'))
        cur.close()
    return redirect(url_for('index'))


#-----------------------------------------------------------

@app.route('/editarticle/<postid>', methods=['GET', 'POST'])
def editarticle(postid):
    global userstatus
    id = userstatus
    postid = postid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        form = request.form
        cur = mysql.connection.cursor()
        query1 = cur.execute("SELECT * FROM articles WHERE id = %s;",[postid])
        details = cur.fetchall()
        if request.method == 'POST' and form['action'] == 'Update Blog' :
            title = form['title']
            post = form['description'] 
            dated = datetime.date.today()
            query = cur.execute("UPDATE articles SET title = %s, post = %s, postdate = %s WHERE id = %s AND userid = %s;",[title,post,dated,postid,id])
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('dashboard'))
        return render_template('editarticle.html', details = details)


#-----------------------------------------------------------

@app.route('/removefriend/<friendid>')
def removefriend(friendid):
    global userstatus
    id = userstatus
    friendid = friendid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("DELETE FROM friends WHERE id1 = %s and fid = %s;",[id,friendid])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('friends'))
    return redirect(url_for('index'))

#--------------------------------------------------------------------------------

@app.route('/addfriend/<friendid>')
def addfriend(friendid):
    global userstatus
    id = userstatus
    friendid = friendid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("INSERT INTO friends(id1,fid) values(%s,%s);",[id,friendid])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('friends'))
    return redirect(url_for('index'))

#--------------------------------------------------------------------------------

@app.route('/likearticle/<postid>')
def likearticle(postid):
    global userstatus
    id = userstatus
    postid = postid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("UPDATE articles SET likes = (likes + 1) where id = %s",[postid])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('read',postid = postid))

#--------------------------------------------------------------------------------

@app.route('/dislikearticle/<postid>')
def dislikearticle(postid):
    global userstatus
    id = userstatus
    postid = postid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("UPDATE articles SET dislikes = (dislikes + 1) where id = %s",[postid])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('read',postid = postid))

#-----------------------------------------------------------

@app.route('/read/<postid>')
def read(postid):
    global userstatus
    postid = postid
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("SELECT * FROM articles,users WHERE articles.id = %s and articles.userid = users.id;",[postid])
        details = cur.fetchall()
        print(details)
        cur.close()
        return render_template('read.html',details = details)

#-----------------------------------------------------------

@app.route('/myfriend/<id>')
def myfriend(id):
    global userstatus
    id = id
    if userstatus <= 0 :
        return redirect(url_for('index'))
    else:
        cur = mysql.connection.cursor()
        query = cur.execute("SELECT * FROM articles WHERE userid = %s;",[id])
        postdetails = cur.fetchall()
        print(postdetails)
        query = cur.execute("SELECT * FROM users WHERE id = %s;",[id])
        userdetails = cur.fetchall()
        result3 = cur.execute("Select count(fid) from friends where id1 = %s;",[id])
        following = cur.fetchone()
        result4 = cur.execute("select count(fid) from friends where fid = %s;",[id])
        followers = cur.fetchone()
        result5 = cur.execute("select sum(likes) from articles where userid = %s;",[id])
        likes = cur.fetchone()
        result6 = cur.execute("select sum(dislikes) from articles where userid = %s;",[id])
        dislike = cur.fetchone()
        cur.close()
        return render_template('myfriend.html',postdetails = postdetails, userdetails = userdetails, following = following, followers = followers, likes = likes, dislike = dislike)

#-----------------------------------------------------------

# All Articles
@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    result = cur.execute("Select * From articles,users where articles.userid = users.id order by articles.id desc;")
    allarticles = cur.fetchall()
    result = cur.execute("select * from articles,users where articles.userid = users.id order by articles.id desc limit 6;")
    latestarticles = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('articles.html', allarticles=allarticles, latestarticles=latestarticles)
    else:
        return redirect(url_for('dashboard'))    


###################################################################################

if __name__ == '__main__':
    app.run(debug = True)
