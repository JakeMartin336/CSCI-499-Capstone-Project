from flask import Flask, request, render_template
import pandas as pd
app = Flask(__name__, static_folder='static')

@app.route("/")
def home():
    columns=["Account ID","Name","Age","Location","Music Genre 1","Music Genre 2","Music Genre 3","Budget","Travel Time","Contacts","Description"]
    df = pd.read_csv("data.csv", names=columns, header= 0)
    account_id = request.args.get('account_id')

    user_info = None
    
    if account_id:
        df["Account ID"] = df["Account ID"].astype(str)
        user_data = df[df["Account ID"] == account_id]

        if not user_data.empty:
            user_info = user_data.iloc[0].to_dict()

    return render_template("index.html", user=user_info)

# @app.route("/mysite")
# def get_user_info():
#     # print(request.args)
#     return "Hello World"