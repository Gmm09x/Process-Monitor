from flask import Flask, render_template, request, jsonify
import psutil

app = Flask(__name__)

@app.route('/')
def index():
    processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            process_info = {
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'username': proc.info['username'],
                'cpu_percent': proc.info['cpu_percent'],
                'memory_percent': proc.info['memory_percent'],
                'create_time': proc.info['create_time']
            }
            processes.append(process_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return render_template('index.html', processes=processes)

@app.route('/action/<action>/<int:pid>')
def perform_action(action, pid):
    try:
        process = psutil.Process(pid)
        if action == 'kill':
            process.terminate()
            return jsonify({'message': f'Process with PID {pid} has been terminated.'}), 200
        elif action == 'stop':
            process.suspend()
            return jsonify({'message': f'Process with PID {pid} has been stopped.'}), 200
        elif action == 'restart':
            process.resume()
            return jsonify({'message': f'Process with PID {pid} has been restarted.'}), 200
        elif action == 'details':
            process_info = {
                'pid': pid,
                'name': process.name(),
                'username': process.username(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'create_time': process.create_time(),
                'status': process.status(),
                'threads': process.num_threads()
            }
            return jsonify(process_info), 200
    except psutil.NoSuchProcess:
        return jsonify({'error': f'Process with PID {pid} does not exist.'}), 404
    except psutil.AccessDenied:
        return jsonify({'error': f'Access denied to perform action on process with PID {pid}.'}), 403

if __name__ == '__main__':
    app.run(debug=True)

