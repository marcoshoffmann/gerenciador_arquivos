from os import getenv
import pdfplumber as plb
from re import sub
from use_cases.MySQLDB import MySQLDB
from queries.queries import consulta_empresa_by_cpf_cnpj, consulta_empresa_by_im, consulta_empresa_by_ie, consulta_empresa_by_base_cpf_cnpj
import json

class PdfData:
    def __init__(self):
        self.mysqldb = MySQLDB(host=getenv("HOST"), user=getenv("USER"), password=getenv("PWD"), database=getenv("DATABASE"))
        self.meses = json.loads(getenv("MESES"))
        self.meses_simples_nacional = json.loads(getenv("MESES_SIMPLES_NACIONAL"))

    def read_pdf(self, file: str) -> list:
        lines = []
        with plb.open(path_or_fp=file) as pdf_open:
            for page in range(len(pdf_open.pages)):
                extracted_data = pdf_open.pages[page].extract_text()
                lines.extend(extracted_data.split("\n"))
        return lines
    
    def verify_pdf(self, file: str) -> str:
        data = self.read_pdf(file=file)
        # for line in data:
        #     print(f'LINE: |{line}|')
        # input("ANALISAR AQUI!!!")
        for line in data:
            # print(f'LINE: |{line}|')
            if line.__eq__(getenv('PATTERN_SPED_ICMS_IPI')): return 'SPED ICMS IPI', data
            if line.__eq__(getenv('PATTERN_SPED_PIS_COFINS')): return 'SPED PIS COFINS', data
            if line.__contains__(getenv('PATTERN_GIA')): return 'GIA', data
            if line.__contains__(getenv('PATTERN_DESTDA')): return 'DESTDA', data
            if line.__eq__(getenv('PATTERN_RECIBO_ISSQN')):
                # input('ISSQN AQUI!!!')
                if data[1].__eq__('Secretaria Municipal da Fazenda') and data[2].__eq__('RECIBO DE ENTREGA - DECLARAÇÃO MENSAL'):
                    input('RECIBO ISSQN AQUI!!!!!')
                    return 'RECIBO ISSQN', data
                if data[1].__eq__('Secretaria Municipal da Fazenda') and data[11].__eq__('GUIA PARA PAGAMENTO DE ISSQN'):
                    input('GUIA ISSQN AQUI!!!!!')
                    return 'GUIA ISSQN', data
            if line.__eq__(getenv('PATTERN_CND_FEDERAL')):
                # input('ISSQN AQUI!!!')
                if data[3].__contains__('CERTIDÃO NEGATIVA DE DÉBITOS RELATIVOS AOS TRIBUTOS FEDERAIS'):
                    input('CND FEDERAL')
                    return 'CND FEDERAL', data
            if line.__eq__(getenv('PATTERN_CND_ESTADUAL')):
                # input('ISSQN AQUI!!!')
                if data[11].__eq__('CERTIDAO NEGATIVA'):
                    input('CND ESTADUAL')
                    return 'CND ESTADUAL', data
            if line.__eq__(getenv('PATTERN_CND_MUNICIPAL_PORTO_ALEGRE')):
                # input('ISSQN AQUI!!!')
                if data[2].__eq__('CERTIDÃO GERAL NEGATIVA DE DÉBITOS'):
                    input('CND MUNICIPAL')
                    return 'CND MUNICIPAL', data
            if line.__eq__(getenv('PATTERN_DEFIS')):
                # # input('ISSQN AQUI!!!')
                # if data[2].__eq__('CERTIDÃO GERAL NEGATIVA DE DÉBITOS'):
                input('RECIBO DEFIS')
                return 'RECIBO DEFIS', data
            if line.__eq__(getenv('PATTERN_CNPJ')):
                input('CNPJ')
                return 'CNPJ', data
            if line.__eq__(getenv('PATTERN_DAS')):
                input('DAS')
                return 'DAS', data
            if line.__eq__(getenv('PATTERN_EXTRATO_DAS')):
                input('EXTRATO DAS')
                return 'EXTRATO DAS', data
            if line.__eq__(getenv('PATTERN_RECIBO_DAS')):
                input('RECIBO DAS')
                return 'RECIBO DAS', data
            if line.__eq__(getenv('PATTERN_ACOMPANHAMENTO_DE_SAIDAS')):
                input('ACOMPANHAMENTO DE SAÍDAS')
                return 'ACOMPANHAMENTO DE SAÍDAS', data
            if line.__eq__(getenv('PATTERN_COMPRAS_E_VENDAS')):
                input('COMPRAS E VENDAS')
                return 'COMPRAS E VENDAS', data
            if line.__eq__(getenv('PATTERN_COMPENSACAO_SIMPLES_NACIONAL')):
                input('COMPENSAÇÃO SIMPLES NACIONAL')
                return 'COMPENSAÇÃO SIMPLES NACIONAL', data
            if line.__eq__(getenv('PATTERN_IE_RS')):
                input('IE')
                return 'IE', data
            if line.__eq__(getenv('PATTERN_IM_PORTO_ALEGRE')):
                input('IM')
                return 'IM', data
            if line.__eq__(getenv('PATTERN_AUTENTICACAO_LIVRO')):
                input('AUTENTICAÇÃO LIVRO')
                return 'AUTENTICAÇÃO LIVRO', data
        input("AGUARDAR AQUI!!!!")

    def verify_infos(self, file: str) -> dict:
        dict_infos = {'ID_DOMINIO': None, 'TIPO': None, 'STATUS': 'ACEITA', 'CNPJ_CPF': None, 'FINALIDADE': None, 'MES': None, 'ANO': None}
        status = 'ACEITA'
        full_data = self.verify_pdf(file=file)
        if full_data:
            tipo = full_data[0]
            input(f'TIPO: {tipo}')
            data = full_data[1]
            if tipo.__eq__('SPED ICMS IPI'):
                for line in data:
                    # print(f'LINE: {line}')
                    if line.__contains__('CNPJ/CPF: '):
                        cnpj_cpf = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Finalidade do Arquivo: Remessa de arquivo original'):
                        finalidade = 'ORIGINAL'                    
                    if line.__contains__('Finalidade do Arquivo: Remessa de arquivo substituto'):
                        finalidade = 'RETIFICADORA'                    
                    if line.__contains__('Período: '):
                        competencia = line.split(" ")[1]
                        mes = competencia.split("/")[1]                    
                        ano = competencia.split("/")[-1]
            if tipo.__eq__('SPED PIS COFINS'):
                for line in data:
                    # print(f'LINE: {line}')
                    if line.__contains__('CNPJ: '):
                        input(f"CNPJ AQUIIIII!!!!!!!: {line}")
                        cnpj_cpf = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                        input(f'CNPJ_CPF: {cnpj_cpf}')
                    if line.__contains__('Tipo: Original'):
                        finalidade = 'ORIGINAL'                    
                    if line.__contains__('Tipo: Substituto'):
                        finalidade = 'RETIFICADORA'                      
                    if line.__contains__('Período de apuração: '):
                        input(f'PERIODO AQUIIIIIIIIIII!!!!!!!!!: {line}')
                        competencia = line.split(" ")[3]
                        mes = competencia.split("/")[1]                    
                        ano = competencia.split("/")[-1]
            if tipo.__eq__('GIA'):
                for line in data:
                    # print(f'LINE: {line}')
                    if line.__contains__('CNPJ: '):
                        cnpj_cpf = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Tipo: ORIGINAL'):
                        finalidade = 'ORIGINAL'
                    if line.__contains__('Tipo: SUBSTITUTA'):
                        finalidade = 'RETIFICADORA'
                    if line.__eq__('Situação da GIA: GIA ACEITA'):
                        status_recebimento = 'ACEITA'
                    if line.__eq__('Situação da GIA: GIA ACEITA - INCONSISTENTE'):
                        status_recebimento = 'ACEITA INCONSISTENTE'
                    if line.__eq__('Situação da GIA: GIA NÃO ACEITA'):
                        status_recebimento = 'NÃO ACEITA'
                    if line.__contains__('Mês de Referência: '):
                        competencia = line.split("Mês de Referência: ")[-1]
                        mes = competencia.split("/")[0]
                        ano = competencia.split("/")[-1]   
            if tipo.__eq__('DESTDA'):
                # for line in data:
                #     print(f'LINE: {line}')
                    if line.__contains__('CNPJ '):
                        cnpj_cpf = sub('\D', '', line.split(" ")[1])
                        cnpj_cpf = f'{int(cnpj_cpf):014}'if len(cnpj_cpf).__gt__(11) else f'{int(cnpj_cpf):011}'
                    if line.__contains__('Finalidade do Arquivo DeStda Original'):
                        finalidade = 'ORIGINAL'                    
                    if line.__contains__('Finalidade do Arquivo DeStda Substituta'):
                        finalidade = 'RETIFICADORA'
                    if line.__contains__('DeSTDA - ACEITA'):
                        status = 'ACEITA'
                    if line.__contains__('DeSTDA - ACEITA INCONSISTENTE'):
                        status = 'ACEITA INCONSISTENTE'
                    if line.__contains__('DeSTDA - NÃO ACEITA'):
                        status = 'NÃO ACEITA'
                    if line.__contains__(' Mês Referência '):
                        competencia = line.split(" ")[-1]
                        mes = competencia.split("/")[0]
                        ano = competencia.split("/")[-1]
            if tipo.__eq__('RECIBO ISSQN'):
                # for line in data:
                #     print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                cnpj_cpf = self.mysqldb.ler_dados(query=consulta_empresa_by_im.format(sub("\D", "", data[4].split()[0])))[0][0]
                finalidade = 'ORIGINAL'
                status = 'ACEITA'
                competencia = data[4].split()[1]
                mes = self.meses[competencia.split("/")[0]]
                ano = competencia.split("/")[1]
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('GUIA ISSQN'):
                # for line in data:
                #     print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                cnpj_cpf = self.mysqldb.ler_dados(query=consulta_empresa_by_im.format(sub("\D", "", data[4].split()[0])))[0][0]
                finalidade = 'ORIGINAL'
                status = 'ACEITA'
                competencia = data[12].split()[1]
                mes = self.meses[competencia.split("/")[0]]
                ano = competencia.split("/")[1]
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('CND FEDERAL'):
                # for line in data:
                #     print(f'LINE: {line}')
                # input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                status = 'ACEITA'
                for line in data:
                    if line.__contains__('Emitida às '):
                        print(f'LINE: {line}')
                        competencia = line.split()[5]
                        # mes = competencia.split("/")[1]
                        mes = sub("\D", "", competencia.split("/")[1])
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                cnpj_cpf = sub("\D", "", data[6].split()[1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('CND ESTADUAL'):
                # for line in data:
                #     print(f'LINE: {line}')
                # input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                status = 'ACEITA'
                for line in data:
                    if line.__contains__('Esta certidão é válida até '):
                        print(f'LINE: {line}')
                        competencia = line.split()[5]
                        # mes = competencia.split("/")[1]
                        mes = sub("\D", "", competencia.split("/")[1])
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                cnpj_cpf = self.mysqldb.ler_dados(query=consulta_empresa_by_base_cpf_cnpj.format(sub("\D", "", data[4].split()[2])))[0][0]
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('CND MUNICIPAL'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                status = 'ACEITA'
                for line in data:
                    if line.__contains__('Certidão emitida em '):
                        print(f'LINE: {line}')
                        competencia = line.split()[3]
                        # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        # mes = competencia.split("/")[1]
                        mes = sub("\D", "", competencia.split("/")[1])
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[5].split()[1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('RECIBO DEFIS'):
                for line in data:
                    print(f'LINE: {line}')
                    # input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                if data[5].__eq__('DECLARAÇÃO ORIGINAL'):
                    finalidade = 'ORIGINAL'
                else:
                    finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                for line in data:
                    if line.__contains__('Período abrangido pela Declaração: '):
                        print(f'LINE: {line}')
                        competencia = line.split()[4]
                        # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        # mes = competencia.split("/")[1]
                        mes = sub("\D", "", competencia.split("/")[1])
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[10].split()[-1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('CNPJ'):
                for line in data:
                    print(f'LINE: {line}')
                    # input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[5].__eq__('DECLARAÇÃO ORIGINAL'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                for line in data:
                    if line.__contains__('Emitido no dia '):
                        print(f'LINE: {line}')
                        competencia = line.split()[3]
                        # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        mes = competencia.split("/")[1]
                        # mes = ".".join(competencia.split("/")[0:-1])
                        input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[4].split()[0])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('DAS'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[5].__eq__('DECLARAÇÃO ORIGINAL'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                competencia = data[5].split()[0]
                mes = self.meses_simples_nacional[competencia.split("/")[0]]
                ano = sub("\D", "", competencia.split("/")[-1])
                # for line in data:
                #     if line.__contains__('Emitido no dia '):
                #         print(f'LINE: {line}')
                #         competencia = line.split()[3]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                #         mes = competencia.split("/")[1]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                #         mes = f'{int(mes):02}'
                #         ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[3].split()[0])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('EXTRATO DAS'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                # finalidade = 'ORIGINAL'
                if data[3].__eq__('Apuração Original'):
                    finalidade = 'ORIGINAL'
                else:
                    finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                # competencia = data[5].split()[0]
                # mes = self.meses_simples_nacional[competencia.split("/")[0]]
                # ano = sub("\D", "", competencia.split("/")[-1])
                for line in data:
                    if line.__contains__('Período de Apuração (PA): '):
                        print(f'LINE: {line}')
                        competencia = line.split()[4]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        mes = competencia.split("/")[0]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = self.mysqldb.ler_dados(query=consulta_empresa_by_base_cpf_cnpj.format(sub("\D", "", data[6].split()[2])))[0][0]
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('RECIBO DAS'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                # finalidade = 'ORIGINAL'
                if data[3].__eq__('Declaração Original'):
                    finalidade = 'ORIGINAL'
                else:
                    finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                # competencia = data[5].split()[0]
                # mes = self.meses_simples_nacional[competencia.split("/")[0]]
                # ano = sub("\D", "", competencia.split("/")[-1])
                for line in data:
                    if line.__contains__(' R$ '):
                        print(f'LINE: {line}')
                        competencia = line.split()[0]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        mes = competencia.split("/")[0]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[4].split()[-1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('ACOMPANHAMENTO DE SAÍDAS'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[3].__eq__('Declaração Original'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                competencia = data[3].split()[1]
                mes = competencia.split("/")[1]
                mes = f'{int(mes):02}'
                ano = sub("\D", "", competencia.split("/")[-1])
                # for line in data:
                #     if line.__contains__(' R$ '):
                #         print(f'LINE: {line}')
                #         competencia = line.split()[0]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        # mes = competencia.split("/")[0]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        # mes = f'{int(mes):02}'
                        # ano = sub("\D", "", competencia.split("/")[1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[1].split()[1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('COMPRAS E VENDAS'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[3].__eq__('Declaração Original'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                competencia = data[4].split()[1]
                mes = competencia.split("/")[1]
                mes = f'{int(mes):02}'
                ano = sub("\D", "", competencia.split("/")[-1])
                # for line in data:
                #     if line.__contains__(' R$ '):
                #         print(f'LINE: {line}')
                #         competencia = line.split()[0]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        # mes = competencia.split("/")[0]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        # mes = f'{int(mes):02}'
                        # ano = sub("\D", "", competencia.split("/")[1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[2].split()[1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('COMPENSAÇÃO SIMPLES NACIONAL'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[3].__eq__('Declaração Original'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                competencia = data[16].split()[0]
                mes = competencia.split("/")[0]
                mes = f'{int(mes):02}'
                ano = sub("\D", "", competencia.split("/")[-1])
                # for line in data:
                #     if line.__contains__(' R$ '):
                #         print(f'LINE: {line}')
                #         competencia = line.split()[0]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        # mes = competencia.split("/")[0]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        # mes = f'{int(mes):02}'
                        # ano = sub("\D", "", competencia.split("/")[1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[1].split()[-1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('IE'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[3].__eq__('Declaração Original'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                competencia = data[1].split()[-1]
                mes = competencia.split("/")[1]
                mes = f'{int(mes):02}'
                ano = sub("\D", "", competencia.split("/")[-1])
                # for line in data:
                #     if line.__contains__(' R$ '):
                #         print(f'LINE: {line}')
                #         competencia = line.split()[0]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        # mes = competencia.split("/")[0]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        # mes = f'{int(mes):02}'
                        # ano = sub("\D", "", competencia.split("/")[1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[4].split()[-1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('IM'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                finalidade = 'ORIGINAL'
                # if data[3].__eq__('Declaração Original'):
                #     finalidade = 'ORIGINAL'
                # else:
                #     finalidade = 'RETIFICADORA'
                status = 'ACEITA'
                # competencia = data[1].split()[-1]
                # mes = competencia.split("/")[1]
                # mes = f'{int(mes):02}'
                # ano = sub("\D", "", competencia.split("/")[-1])
                for line in data:
                    if line.__contains__('Emitido na Internet, em '):
                        print(f'LINE: {line}')
                        competencia = line.split()[-3]
                        # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                        mes = competencia.split("/")[1]
                        # mes = ".".join(competencia.split("/")[0:-1])
                        input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                        mes = f'{int(mes):02}'
                        ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = sub("\D", "", data[10].split()[1])
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            if tipo.__eq__('AUTENTICAÇÃO LIVRO'):
                for line in data:
                    print(f'LINE: {line}')
                input(f'VERIFICAR O CNPJ_CPF AQUI!!!!!!')
                # finalidade = 'ORIGINAL'
                if data[5].__contains__('Livro nº '):
                    finalidade = f'N° {data[5].split()[-1]}'
                else:
                    finalidade = 'N° 0'
                status = 'ACEITA'
                competencia = data[7].split()[-1]
                mes = competencia.split("/")[1]
                mes = f'{int(mes):02}'
                ano = sub("\D", "", competencia.split("/")[-1])
                # for line in data:
                #     if line.__contains__('Emitido na Internet, em '):
                #         print(f'LINE: {line}')
                #         competencia = line.split()[-3]
                #         # input(f'VERIFICAR_COMPETENCIA_AQUI!!!!!!!!: {competencia}')
                #         mes = competencia.split("/")[1]
                #         # mes = ".".join(competencia.split("/")[0:-1])
                #         input(f'VERIFICAR_MES_AQUI!!!!!!: {mes}')
                #         mes = f'{int(mes):02}'
                #         ano = sub("\D", "", competencia.split("/")[-1])
                    # if line.__contains__("CNPJ base: "):
                    #     cnpj_cpf = sub("\D", "", line.split()[2])
                # input(f'DATA[5]: {data[5]}')
                cnpj_cpf = self.mysqldb.ler_dados(query=consulta_empresa_by_ie.format(sub("\D", "", data[3].split()[1])))[0][0]
                input(f'CNPJ_CPF: {cnpj_cpf}')
                input(f'FINALIDADE: {finalidade}')
                input(f'STATUS: {status}')
                input(f'COMPETENCIA: {competencia}')
                input(f'MES: {mes}')
                input(f'ANO: {ano}')
            id_dominio = self.mysqldb.ler_dados(query=consulta_empresa_by_cpf_cnpj.format(cnpj_cpf))[0][0]
            id_dominio = f'{id_dominio:03}'
            dict_infos = {'ID_DOMINIO': id_dominio, 'TIPO': tipo, 'STATUS': status, 'CNPJ_CPF': cnpj_cpf, 'FINALIDADE': finalidade, 'MES': mes, 'ANO': ano}
        return dict_infos
