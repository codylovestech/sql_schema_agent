import itertools
import json
import time
from queue import Queue

import flask
from flask import Flask, render_template, Response, request, stream_with_context

from reactflow_converter import validateReactFlow, ReactFlowToSQLConverter

app = Flask(__name__)


@app.route("/create", methods=["POST"])
def create_sql_schem():
    content = None
    try:
        content = request.json
    except Exception as e:
        return flask.jsonify(status=400, error="Can not parse your posted data, please send a JSON"+str(e)), 400

    try:
        if "data" not in content:
            raise Exception("Missing data key in posted JSON")

        if "technology" not in content:
            raise Exception("Missing technology key in posted JSON")

    except Exception as e:
        return flask.jsonify(status=400, error="Your json needs to contain 'data' and 'technology' attributes, "+str(e)), 400

    try:
        if not validateReactFlow(content["data"]):
            raise Exception("Invalid ReactFlow diagram")

    except Exception as e:
        return flask.jsonify(status=400, error="Your posted data does not look like a ReactFlow diagram, "+str(e)), 400

    def stream():
        q = Queue()  # fmin produces, the generator consumes
        job_done = object()  # signals the processing is done

        def producer():
            converter = ReactFlowToSQLConverter(content["data"], content["technology"])
            converter.convert(q.put)
            q.put(job_done)

        # start the producer in a separate thread
        import threading
        threading.Thread(target=producer).start()

        # consume the output
        for item in iter(q.get, job_done):
            yield json.dumps(item)+"\n"
            time.sleep(0.5)




    return Response(stream_with_context(stream()), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True)