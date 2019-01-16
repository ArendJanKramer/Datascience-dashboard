from flask import Flask, send_from_directory, request
from drivers.CentroidnetDriver import CentroidnetDriver
import json

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
    return datasetprovider.get_loss_data()


@app.route('/api/summary')
def get_summary():
    summary = datasetprovider.get_summary()
    summary['dataprovider'] = datasetprovider.driverName
    return json.dumps(summary)


@app.route('/api/get_datasets')
def get_datasets():
    all_datasets = []
    for driver in drivers:
        all_datasets.append(driver.get_datasets())

    return json.dumps(all_datasets)


@app.route('/api/set_dataset', methods=["POST"])
def set_dataset():
    data = request.get_data().decode('ascii')
    data = json.loads(data)

    if "dataprovider" in data:
        for driver in drivers:
            if driver.driverName == data["dataprovider"]:
                print("Updating dataprovider to {}".format(driver.driverName))
                datasetprovider = driver

    if "dataset" in data:
        datasetprovider.set_dataset(data['dataset'])
    return json.dumps(data)


if __name__ == "__main__":
    centroidnetDriver = CentroidnetDriver()
    drivers = [centroidnetDriver]
    datasetprovider = drivers[0]

    app.run(port=int("8181"), host='0.0.0.0')
