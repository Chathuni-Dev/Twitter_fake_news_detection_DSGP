from flask import Flask,request, render_template
import pandas as pd
import tweepy
import configparser
import pandas
import numpy as np
import pickle
import pymongo
import json

# Twitter API
# read configs
config = configparser.ConfigParser()
config.read('config.ini')

api_key= config['twitter']['api_key']
api_key_secret= config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret=config['twitter']['access_token_secret']

auth = tweepy.OAuthHandler(api_key,api_key_secret)
auth.set_access_token(access_token,access_token_secret)

api = tweepy.API(auth)

public_tweets = api.home_timeline()

print(public_tweets[0].text)

columns = ['User', 'Tweets']
data=[]

for tweet in public_tweets:
    data.append([tweet.user.screen_name, tweet.text])

df = pd.DataFrame(data,columns=columns)

# print(df)

df.to_csv('tweets.csv')


# Using the Model
with open('model.pkl', 'rb') as f:
    lr = pickle.load(f)


x = pandas.read_csv('tweets.csv', usecols= ['Tweets'])

# print(lr.predict(pd.Series(np.array(["If a study concludes that Ivermectin is effective for COVID and that "
#                                            "makes you angry, you are not an objective scientist looking for the "
#                                            "truth; you’re an emotional, selfish person who cares more about personal "
#                                            "image and protecting your ego than helping others and saving lives."]))))
result = lr.predict(x.iloc[:,0])
# print(result)
# print(x)

x = pandas.read_csv('tweets.csv', usecols= ['User', 'Tweets'])
df1 = x.assign(label=pd.Series(result))
df1.to_csv('tweets_withlabes.csv')

# print(df1)

y = pandas.read_csv('tweets.csv', usecols= ['Tweets'])
df2 = y.assign(label=pd.Series(result))

# print(df2)


# Auto update to MongoDB

client = pymongo.MongoClient("mongodb+srv://DSGP-G9:WGjKPaRuQfhWTO1K@group9dsgp.bn0yz.mongodb.net/?retryWrites=true&w=majority")

post_with_result = df1          # Here I have directly taken the dataframe from the above function. If there is a need to read from csv file, replace "df1" with "pd.read_csv("<-Path of csv file->")"
upload_data = post_with_result.to_dict(orient='records')

mongoDatabase = client["tweets"]
mongoDatabase.tweet_data.insert_many(upload_data)

# Rest API

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("popup.html",x=x)

@app.route('/results', methods= ['POST',"GET"])
def results():
    # output = request.form.to_dict()
    #Y = output["name"]


    return render_template("popup.html", df1 = df1, tables=[df1.to_html(classes='data')], titles=df1.columns.values)

@app.route('/resultuser', methods=['POST', "GET"])
def resultuser():
    output = request.form.to_dict()
    tst = output["tst"]
    print(tst)
    df = pd.read_csv('tweets_withlabes.csv')
    df.set_index("User", inplace=True)
    z = df.loc[[tst]]
    print(df.loc[[tst]])

    return render_template("popup.html", z=z, tables=[z.to_html(classes='data')], titles=z.columns.values)

    #for i in range(len(z.User)):
        #if tst == x.user[i]:

            #return render_template("popup.html", z=z, tables=[z.to_html(classes='data')], titles=z.columns.values)
        #else:
            #return render_template("popup.html",error_msg="User not found!")


if __name__ == "__main__":
    app.run()
