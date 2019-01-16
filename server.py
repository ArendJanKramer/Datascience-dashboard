from flask import Flask, send_from_directory, request
from drivers.CentroidnetDriver import CentroidnetDriver

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')


@app.route('/scripts/<path:path>')
def send_js(path):
    return send_from_directory('scripts', path)


@app.route('/style/<path:path>')
def send_style(path):
    return send_from_directory('style', path)


@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)


@app.route('/')
def root():
    return send_from_directory('', 'index.html')


@app.route('/api/loss')
def api():
    return driver.get_loss_data()


@app.route('/api/summary')
def get_summary():
    return driver.get_summary()


@app.route('/api/get_datasets')
def get_datasets():
    return driver.get_datasets()


@app.route('/api/set_dataset', methods=["POST"])
def set_dataset():
    data = request.get_data().decode('ascii')
    if (len(data) > 1):
        driver.set_dataset(data)
    return data


if __name__ == "__main__":
    driver = CentroidnetDriver()
    app.run(port=int("8181"), host= '0.0.0.0')
