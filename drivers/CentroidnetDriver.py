import datetime
import json
import logging
import os

from natsort import natsorted

from .Driver import Driver

logger = logging.getLogger('centroidnetDriver')
import platform


class CentroidnetDriver(Driver):
    driverName = "centroidnet"
    data_dirs = {}
    current_data_dir = ""
    root_folder = "../centroidnet"

    def __init__(self):
        self.find_datasets()
        if platform.node().startswith("n550jv"):
            self.root_folder = "/extern/centroidnet"

    def txt_to_dict(self, file):
        result = {}
        if not os.path.exists(file):
            return {}
        with open(file, 'r') as f:
            for i, line in enumerate(f):
                components = line.split(' ')
                if i > 0 and len(components) >= 3:
                    epoch = components[0]
                    loss = float(components[1])
                    if (loss > 100):
                        loss = 0.0
                    result[epoch] = loss
        return result

    def find_datasets(self):
        result = []
        data_dirs_new = {}
        # Sometimes, this fails so the global list is updated when everything went well
        for root, dirs, files in os.walk(self.root_folder, topdown=False):
            for file in files:
                if "_training.txt" in file:
                    name = os.path.basename(os.path.abspath(os.path.join(root, os.pardir))) + "/" + os.path.basename(root)
                    result.append(name)
                    data_dirs_new[name] = root
        if len(list(data_dirs_new.keys())) > 0:
            self.data_dirs = data_dirs_new
        return result

    def get_datafiles_paths(self):
        self.find_datasets()

        if len(list(self.data_dirs.keys())) == 0:
            return "", ""

        if self.current_data_dir == "" or self.current_data_dir not in self.data_dirs:
            self.current_data_dir = list(self.data_dirs.keys())[0]
            logger.error("Updating data directory to in get_data_dir_files " + self.current_data_dir)

        current_data_path = self.data_dirs[self.current_data_dir]

        training_file = ""
        validation_file = ""
        for file in os.listdir(current_data_path):
            if "_training.txt" in file:
                training_file = os.path.join(current_data_path, file)
            elif "_validation.txt" in file:
                validation_file = os.path.join(current_data_path, file)

        return training_file, validation_file

    ''' Implementations of driver class '''

    def get_loss_data(self):
        result = {}

        training_file, validation_file = self.get_datafiles_paths()

        result["training_loss"] = self.txt_to_dict(training_file)
        result["validation_loss"] = self.txt_to_dict(validation_file)

        return json.dumps(result)

    def get_summary(self):
        result = ""
        training_file, validation_file = self.get_datafiles_paths()
        last_epoch_time = ""

        if os.path.exists(training_file):
            with open(training_file, 'r') as f:
                for i, line in enumerate(f):
                    components = line.split(' ')
                    if i > 0 and len(components) >= 3:
                        result = components[2]
                        break
            last_epoch_time = datetime.datetime.utcfromtimestamp(os.path.getmtime(training_file)).strftime("%d-%b %H:%M")

        return {"loss_function": result.strip(), "dataset": self.current_data_dir, "last_epoch": last_epoch_time}

    def get_datasets(self):
        datasets = natsorted(self.find_datasets())
        return {"centroidnet": datasets}

    def set_dataset(self, folder):
        self.current_data_dir = folder
        self.get_datafiles_paths()

        logger.error("Updating data directory to in set_folder " + self.current_data_dir)
