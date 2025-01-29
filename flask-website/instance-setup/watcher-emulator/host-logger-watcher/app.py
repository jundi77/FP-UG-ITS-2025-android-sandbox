from flask import Flask, request, jsonify, abort
import queue
import argparse
import os

task_id_file = open(
    os.path.join(
        os.path.expanduser('~'),
        'dynamic_analysis',
        'task_id'
    )
)

task_id = None
for line in task_id_file:
    task_id = int(line.strip())

if task_id is None or task_id == '':
    exit(2) # No task id, gimmee task id!

task_id_data = {'id': task_id}

app = Flask(__name__)
log_queue = queue.Queue()

def localhost_only(func):
    def wrapper(*args, **kwargs):
        if request.remote_addr != '127.0.0.1':
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@localhost_only
@app.route('/api/android_watcher_log', methods=['POST'])
def receive_log():
    data = request.json
    if data is not None: # idk weird thing happens, i don't want to deal with it
        log_queue.put(data)

    return "Log received", 200

@app.route('/api/android_watcher_log', methods=['GET'])
def forward_log():
    """
    response will look like this, if there is log on queue:
    {
        id: <task_id>,
        timestamp: <timestamp in miliseconds>,
        type: <type>,
        action: <action>,
        msg: <msg>,
        data: {
            ...<extended data>
        }
    }
    """
    if log_queue.empty():
        return jsonify({})
    log = log_queue.get(block=False)
    log_queue.task_done()
    return jsonify({**task_id_data, **log}) # log is request.json ! merge task id and log

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Queue any log received and send to Watcher web ui log management if it wants it.")
    forwarder_port = 9999
    parser.add_argument(
        "--forwarder-port",
        type=int,
        default=forwarder_port,
        help=f"This log forwarder port (default: {forwarder_port})"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable log forwarder debug mode"
    )

    args = parser.parse_args()
    forwarder_port = args.forwarder_port
    debug = True if args.debug else False

    app.run(debug=debug, port=forwarder_port, host='0.0.0.0')
