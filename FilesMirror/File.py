import os


class File:
    def __init__(self, path):
        self.path = path
        # get creation
        self.creation_time = os.path.getctime(path)
        # get last modification time
        self.last_modification_time = os.path.getmtime(path)

    def update_instance(self):
        # it's possible that the file get deleted while we run and don't update data
        if os.path.exists(self.path) is False:
            return 0

        modification_time = os.path.getmtime(self.path)
        if modification_time == self.last_modification_time:
            return 0
        else:
            self.last_modification_time = modification_time
            return 1
