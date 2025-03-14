from os import getenv, path, mkdir, listdir
from dotenv import load_dotenv
load_dotenv()

class PathManager:
    def __init__(self):
        self.path_files: str = getenv("PATH_FILES")
        self.path_duo: str = getenv("PATH_DUO")
        self.path_not_mapped: str = getenv("PATH_NOT_MAPPED")
        self.path_clients: str = getenv("PATH_CLIENTS")
        self.path_move: str = getenv("PATH_MOVE")
        self.verify_paths()

    def verify_paths(self) -> None:
        if not path.exists(self.path_files): mkdir(self.path_files)

    def list_clients(self) -> list:
        return [path_client for path_client in listdir(self.path_clients) if path.isdir(f'{self.path_clients}\\{path_client}') and not path_client.__eq__('INATIVAS')]
    
    def dict_clients(self) -> dict:
        clients: list = self.list_clients()
        return {path_client.split(" - ")[0]: f'{self.path_clients}\\{path_client}' for path_client in clients}
