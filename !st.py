from flask import Flask, render_template

app=Flask(__name__)


@app.route("/")
def hello2():
    return render_template('index.html')

@app.route("/about")
def hello():
    name="Raamchandra"
    return render_template('about.html',namep=name)

@app.route("/webt")
def web_1():
    return render_template("web1.html")




app.run(debug=True)