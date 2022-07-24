from flask import Flask, request
import requests
import sys
import os

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)

provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "yosef-workshop-test-attr"}))
otlpExporter = OTLPSpanExporter(endpoint="http://3.210.98.245:4317")
processor = BatchSpanProcessor(otlpExporter)
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def root():
  with tracer.start_as_current_span("span-name") as span:
    sys.stdout.write('\n')
  return "Click [Logs] to see spans!"

@app.route("/fib")
@app.route("/fibInternal")
def fibHandler():
  value = int(request.args.get('i'))
  current_span = trace.get_current_span()
  current_span.set_attribute("parameter", value)
  
  returnValue = 0
  if value <= 1:
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
