from resources.PathManager import PathManager
from use_cases.Email import Email

class EmailsManager:
    def __init__(self):
        self.pathmanager: PathManager = PathManager()
        self.mensagem: str = ""
        self.mensagem = """<html>
        <head>
            <style>
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <p>Olá, {user}</p>
            <p>O seguinte arquivo já existe: {file}, caso realmente queira substitui-lo, por favor remova o arquivo do local de destino e coloque o novo arquivo no local indicado da automação: {path_automation}</p>
        <tbody>"""
        self.mensagem += '<br><br>Atenciosamente:<br>Equipe de TI'

    def send_email(self, destiny: list, usuario: str, arquivo: str) -> None:
        email: Email = Email(destiny=destiny, mensagem=self.mensagem.format(user=usuario, file=arquivo, path_automation=self.pathmanager.path_files)).send_email()
