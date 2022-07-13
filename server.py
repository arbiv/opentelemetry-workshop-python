from flask import Flask, request
import requests
import sys
import os

app = Flask(__name__)

@app.route("/")
def root():
  sys.stdout.write('\n')
  return "Click [Logs] to see spans!"

@app.route("/fib")
@app.route("/fibInternal")
def fibHandler():
  value = int(request.args.get('i'))
  
  returnValue = 0
  if value == 1:
    returnValue = 0
  elif value == 2:
    returnValue = 1
  else:
    minusOnePayload = {'i': value - 1}
    minusTwoPayload = {'i': value - 2 }
    
    respOne = requests.get('http://127.0.0.1:5000/fibInternal', minusOnePayload)
    respTwo = requests.get('http://127.0.0.1:5000/fibInternal', minusTwoPayload)
    
    returnValue = int(respOne.content) + int(respTwo.content)
    
  # this is a workaround for a glitch logging issue
  sys.stdout.write('\n')
  return str(returnValue)

if __name__ == "__main__":
  app.run(debug=True)
