from flask import Flask, request
import os
app=Flask(__name__)


@app.route("/",methods=['GET'])
def hell():
    return "Hello, world!"

@app.route("/ask",methods=['GET'])
async def ask():
    prompt=request.args
    # result=model.invoke([prompt])
    # return({"response":result["content"]})
    return({"response":prompt})
