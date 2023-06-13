from flask import Flask, render_template
app = Flask(__name__) 
@app.route('/') 

def EC_top():
 return render_template("top.html")


if __name__ == "__main__":
 app.run(debug = True) 