import os
from flask import Flask, render_template, request

from foogle.engine.controller import Controller

controller = Controller()
server = Flask(__name__, root_path=os.path.join(os.getcwd(), 'resources'))


@server.route('/')
def main():
    return render_template('engine.html')


@server.route('/build_index', methods=['POST'])
def build_index():
    res = ''
    if request.method == 'POST':
        form = request.form
        root_dir = form['root_dir']
        robot_txt = form['robot_txt']
        res = controller.execute('build_index', root_dir, robot_txt)
    return render_template('engine.html', index_status=res)


@server.route('/load_index', methods=['GET'])
def load_index():
    res = ''
    if request.method == 'GET':
        res = controller.execute('load_index')
    return render_template('engine.html', index_status=res)


@server.route('/save_index', methods=['GET'])
def save_index():
    res = ''
    if request.method == 'GET':
        res = controller.execute('save_index')
    return render_template('engine.html', index_status=res)


@server.route('/search', methods=['POST'])
def search():
    res = ''
    if request.method == 'POST':
        query = request.form['query']
        res = controller.execute('search', query)
        if isinstance(res, str) and res.startswith('error'):
            return render_template('engine.html', search_status=res)
    return render_template('search_results.html', search_results=res)


@server.route('/about')
def about():
    return render_template('about.html')


def run_server(host: str, port: str, debug: bool):
    server.run(host, port, debug)
