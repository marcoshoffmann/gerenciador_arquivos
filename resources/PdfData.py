from os import getenv
import pdfplumber as plb
from re import sub
from use_cases.MySQLDB import MySQLDB
from queries.queries import consulta_empresa_by_cpf_cnpj
import json

class PdfData:
    def __init__(self):
        self.mysqldb: MySQLDB = MySQLDB(host=getenv("HOST"), user=getenv("USER"), password=getenv("PWD"), database=getenv("DATABASE"))
        self.meses: dict = json.loads(getenv("MESES"))
        self.meses_simples_nacional: dict = json.loads(getenv("MESES_SIMPLES_NACIONAL"))

    def read_pdf(self, file: str) -> list:
        lines: list = []
        with plb.open(path_or_fp=file) as pdf_open:
            for page in range(len(pdf_open.pages)):
                extracted_data = pdf_open.pages[page].extract_text()
                lines.extend(extracted_data.split("\n"))
        return lines
    
    def verify_pdf(self, file: str) -> str:
        data: str = self.read_pdf(file=file)
        for line in data:
            if line.__eq__(getenv('PATTERN_SPED_ICMS_IPI')): return 'SPED ICMS IPI', data
            if line.__eq__(getenv('PATTERN_SPED_PIS_COFINS')): return 'SPED PIS COFINS', data
            if line.__contains__(getenv('PATTERN_GIA')): return 'GIA', data
            if line.__contains__(getenv('PATTERN_DESTDA')): return 'DESTDA', data

    def verify_infos(self, file: str) -> dict:
        dict_infos: dict = {'ID_DOMINIO': None, 'TIPO': None, 'STATUS': 'ACEITA', 'CNPJ_CPF': None, 'FINALIDADE': None, 'MES': None, 'ANO': None}
        status: str = 'ACEITA'
        full_data: tuple = self.verify_pdf(file=file)
        if full_data:
            tipo: str = full_data[0]
            data: list = full_data[1]
            if tipo.__eq__('SPED ICMS IPI'):
                for line in data:
                    if line.__contains__('CNPJ/CPF: '):
                        cnpj_cpf: str = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf: str = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Finalidade do Arquivo: Remessa de arquivo original'): finalidade = 'ORIGINAL'
                    if line.__contains__('Finalidade do Arquivo: Remessa de arquivo substituto'): finalidade = 'RETIFICADORA'
                    if line.__contains__('Período: '):
                        competencia: str = line.split(" ")[1]
                        mes: str = competencia.split("/")[1]                    
                        ano: str = competencia.split("/")[-1]
            if tipo.__eq__('SPED PIS COFINS'):
                for line in data:
                    if line.__contains__('CNPJ: '):
                        cnpj_cpf: str = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf: str = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Tipo: Original'): finalidade: str = 'ORIGINAL'
                    if line.__contains__('Tipo: Substituto'): finalidade: str = 'RETIFICADORA'
                    if line.__contains__('Período de apuração: '):
                        competencia: str = line.split(" ")[3]
                        mes: str = competencia.split("/")[1]                    
                        ano: str = competencia.split("/")[-1]
            if tipo.__eq__('GIA'):
                for line in data:
                    if line.__contains__('CNPJ: '):
                        cnpj_cpf: str = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf: str = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Tipo: ORIGINAL'): finalidade: str = 'ORIGINAL'
                    else: finalidade: str = 'RETIFICADORA'
                    if line.__eq__('Situação da GIA: GIA ACEITA'): status_recebimento: str = 'ACEITA'
                    if line.__eq__('Situação da GIA: GIA ACEITA - INCONSISTENTE'): status_recebimento: str = 'ACEITA INCONSISTENTE'
                    if line.__eq__('Situação da GIA: GIA NÃO ACEITA'): status_recebimento: str = 'NÃO ACEITA'
                    if line.__contains__('Mês de Referência: '):
                        competencia: str = line.split("Mês de Referência: ")[-1]
                        mes: str = competencia.split("/")[0]
                        ano: str = competencia.split("/")[-1]   
            if tipo.__eq__('DESTDA'):
                for line in data:
                    if line.__contains__('CNPJ '):
                        cnpj_cpf: str = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf: str = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Finalidade do Arquivo DeStda Original'): finalidade = 'ORIGINAL'                    
                    if line.__contains__('Finalidade do Arquivo DeStda Substituta'): finalidade = 'RETIFICADORA'
                    if line.__contains__('DeSTDA - ACEITA'): status = 'ACEITA'
                    if line.__contains__('DeSTDA - ACEITA INCONSISTENTE'): status = 'ACEITA INCONSISTENTE'
                    if line.__contains__('DeSTDA - NÃO ACEITA'): status = 'NÃO ACEITA'
                    if line.__contains__(' Mês Referência '):
                        competencia: str = line.split(" ")[-1]
                        mes: str = competencia.split("/")[0]
                        ano: str = competencia.split("/")[-1]
            id_dominio: str = self.mysqldb.ler_dados(query=consulta_empresa_by_cpf_cnpj.format(cnpj_cpf))[0][0]
            id_dominio: str = f'{id_dominio:03}'
            dict_infos: dict = {'ID_DOMINIO': id_dominio, 'TIPO': tipo, 'STATUS': status, 'CNPJ_CPF': cnpj_cpf, 'FINALIDADE': finalidade, 'MES': mes, 'ANO': ano}
        return dict_infos
