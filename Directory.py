import os


class Directory:
    def __init__(self, path):
        self.path = path
        # get creation time
        self.creation_time = os.path.getctime(path)