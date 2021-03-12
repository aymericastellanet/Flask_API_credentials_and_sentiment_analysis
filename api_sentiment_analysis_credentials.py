import pandas as pd
import numpy as np
from flask import Flask, request, abort, make_response, jsonify
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#by Aymeric Castellanet

app = Flask(import_name = "api_sentiment_analysis_credentials")

df = pd.read_csv("credentials.csv")

analyzer = SentimentIntensityAnalyzer()

## At the endpoint status, you can see the API status:
## Return '1' if the API is running.
@app.route("/status", methods = ["GET"])
def return_status():
    return """
    	<h2>Status: {}</h2>
    	""".format(1)

## At the permissions endpoint, return the rights for v1 and v2 endpoints
## for a user when entering its username and its password.
@app.route("/permissions", methods = ["GET"])
def return_permissions():
	username = request.args["username"]
	password = request.args.get("password")
	df_user = df[df["username"] == username]
	if df_user.empty == False: #the user exists in the dataframe
		if df_user["password"].item() == int(password): #password is OK!
			perm_v1 = df_user["v1"].item()
			perm_v2 = df_user["v2"].item()
		#The password doesn't match the username
		else:
			abort(403)
	#The user doesn't exist
	else:
		abort(404)
	return """
		<h2>For user {}</h2>
		<ul>
			<li>Permission for v1: {}</li>
			<li>Permission for v2: {}</li>
		</ul>""".format(username, perm_v1, perm_v2)

## If the user (logged in with its username and password) have permission to access the v1 endpoint,
## the API returns a random number between -1.00 and 1.00.
@app.route("/v1/sentiment", methods = ["GET"])
def return_random_number():
	username = request.args["username"]
	password = request.args.get("password")
	sentence = request.args.get("sentence")
	df_user = df[df["username"] == username]
	if df_user.empty == False: #the user exists in the dataframe
		if df_user["password"].item() == int(password): #password is OK!
			perm_v1 = df_user["v1"].item()
			if perm_v1 == 1: #the user has the permission
				#Return random float with two decimals between -1.00 and 1.00
				rand_float = np.random.randint(low = -100, high = 101)/100 
			#The user does not have the permission: perm_v1 == 0
			else:
				abort(400)
		#The password doesn't match the username
		else:
			abort(403)
	#The user doesn't exist
	else:
		abort(404)
	return """
		<h2>Random number: {}</h2>
		""".format(rand_float)

## If the user (logged in with its username and password) have permission to access the v2 endpoint,
## the API returns the sentiment analysis of the sentence entered.
@app.route("/v2/sentiment", methods = ["GET"])
def return_sentiment():
	username = request.args["username"]
	password = request.args.get("password")
	sentence = request.args.get("sentence")
	df_user = df[df["username"] == username]
	if df_user.empty == False: #the user exists in the dataframe
		if df_user["password"].item() == int(password): #password is OK!
			perm_v2 = df_user["v2"].item()
			if perm_v2 == 1: #the user has the permission
				#Return the compound part of the sentiment analyzer
				compound_score = analyzer.polarity_scores(sentence)["compound"]
			#The user does not have the permission: perm_v2 == 0
			else:
				abort(400)
		#The password doesn't match the username
		else:
			abort(403)
	#The user doesn't exist
	else:
		abort(404)
	return """
		<h2>Sentiment score: {}</h2>
		""".format(compound_score)


@app.errorhandler(400)
def access_denied(error):
	return make_response("""<h2>Error 403:</h2> 
		<p>You don't have the rights to access!</p>""", 403)

@app.errorhandler(403)
def wrong_password(error):
	return make_response("""<h2>Error 403:</h2> 
		<p>The password does not match the username!</p>""", 403)

@app.errorhandler(404)
def resource_not_found(error):
	return make_response("""<h2>Error 404:</h2> 
		<p>Resource not found</p>""", 404)


if __name__ == "__main__":
	app.run(host = "0.0.0.0", port = 5000)
