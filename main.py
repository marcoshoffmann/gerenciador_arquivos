from resources.FilesManager import FilesManager
from time import sleep

if __name__ == '__main__':
    filesmanager: FilesManager = FilesManager()

    filesmanager.manage_all_files()
