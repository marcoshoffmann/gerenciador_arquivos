from os import getenv, listdir, rename, path, remove
from shutil import move, copy2
from dotenv import load_dotenv
load_dotenv()
from resources.PathManager import PathManager
from resources.PdfData import PdfData
from use_cases.MySQLDB import MySQLDB
from queries.queries import consulta_responsavel
from resources.EmailsManager import EmailsManager
import json
from time import sleep
from loguru import logger

class FilesManager:
    def __init__(self):
        self.pathmanager: PathManager = PathManager()
        self.pdfdata: PdfData = PdfData()
        self.emailsmanager: EmailsManager = EmailsManager()
        self.mysqldb: MySQLDB = MySQLDB(host=getenv("HOST"), user=getenv("USER"), password=getenv("PWD"), database=getenv("DATABASE"))
        self.responsaveis: dict = json.loads(getenv("RESPONSAVEIS"))

    def list_files(self, ext: str) -> list:
        return [f'{self.pathmanager.path_files}\\{file}' for file in listdir(self.pathmanager.path_files) if file.lower().endswith(ext.lower())]

    def rename_file(self, file: str, attributes_file: dict) -> str:
        id_dominio: str = attributes_file['ID_DOMINIO']
        tipo: str = attributes_file['TIPO']
        status: str = attributes_file['STATUS']
        mes: str = attributes_file['MES']
        ano: str = attributes_file['ANO']
        finalidade: str = attributes_file['FINALIDADE']
        if tipo.__contains__('SPED'): file_renamed: str = '\\'.join(file.split("\\")[:-1]) + '\\' + f'{int(id_dominio):03}' + f' - {tipo} - {mes}.{ano} ({finalidade}).pdf'
        elif tipo.__contains__('CND'): file_renamed: str = '\\'.join(file.split("\\")[:-1]) + '\\' + f'{int(id_dominio):03}' + f' - {tipo} - {mes}.{ano}.pdf'
        elif tipo.__contains__('GIA') or tipo.__contains__('DESTDA'): file_renamed: str = '\\'.join(file.split("\\")[:-1]) + '\\' + f'{int(id_dominio):03}' + f' - {tipo} - {mes}.{ano} ({status} {finalidade}).pdf'
        else: file_renamed: str = '\\'.join(file.split("\\")[:-1]) + '\\' + f'{int(id_dominio):03}' + f' - {tipo} - {mes}.{ano}.pdf'
        logger.info(f'FILE_RENAMED: {file_renamed}')
        if not path.exists(file_renamed): rename(file, file_renamed)
        return file_renamed
    
    def move_file(self, file: str, id_dominio: str, mes: str, ano: str) -> None:
        clients = self.pathmanager.dict_clients()
        if not path.exists(self.pathmanager.path_move.format(clients[id_dominio], ano, mes, ano) + "\\" + file.split("\\")[-1]):
            logger.info('MOVER NORMALMENTE')
            logger.info(f'MOVE: {file} -> {self.pathmanager.path_move.format(clients[id_dominio], ano, mes, ano)}' + " \\" + file.split("\\")[-1])
            move(file, self.pathmanager.path_move.format(clients[id_dominio], ano, mes, ano) + "\\" + file.split("\\")[-1])
        else:
            logger.info('MOVER DUPLICADO')
            logger.info(f'MOVE: {file} -> {self.pathmanager.path_duo}' + " \\" + file.split("\\")[-1])
            self.responsavel = self.mysqldb.ler_dados(query=consulta_responsavel.format(int(id_dominio)))[0][0]
            copy2(file, self.pathmanager.path_duo + "\\" + file.split("\\")[-1])
            remove(file)
            # self.emailsmanager.send_email(destiny=[self.responsaveis[self.responsavel]], usuario=self.responsavel, arquivo=self.pathmanager.path_move.format(clients[id_dominio], ano, mes, ano) + '\\' + file.split("\\")[-1])
            self.emailsmanager.send_email(destiny=[self.responsaveis['TESTE']], usuario=self.responsavel, arquivo=self.pathmanager.path_move.format(clients[id_dominio], ano, mes, ano) + '\\' + file.split("\\")[-1])  
    
    def move_not_mapped(self, file: str) -> None:
        copy2(file, self.pathmanager.path_not_mapped)
        remove(file)

    def manage_file(self, file: str) -> None:
        attributes = self.pdfdata.verify_infos(file=file)
        if attributes['TIPO'] is None: self.move_not_mapped(file)
        elif all(value is not None for value in attributes.values()):
            new_file: str = self.rename_file(file, attributes_file=attributes)
            self.move_file(new_file, attributes['ID_DOMINIO'], attributes['MES'], attributes['ANO'])

    def manage_all_files(self) -> None:
        while True:
            files: list = self.list_files(ext='.pdf')
            for file in files:
                print(f'FILE: {file}')
                self.manage_file(file=file)
            logger.info('AGUARDANDO 30 SEGUNDOS PARA CARREGAR NOVOS DOCUMENTOS...')
            sleep(30)
