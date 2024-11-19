from flask import Flask, render_template, request, url_for, redirect
from flask_uploads import UploadSet, configure_uploads, IMAGES, DATA, ALL
from werkzeug import secure_filename
import pandas as pd 
import pygal
import io
import os 

app = Flask(__name__)

# Configurações para o Upload de Arquivos
files = UploadSet('files', ALL)
app.config['UPLOADED_FILES_DEST'] = 'static/dados'
app.config['ALLOWED_EXTENSIONS'] = ['CSV']
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
configure_uploads(app,files)

def allowed_extension(filename):
    if not '.' in filename:
        return False
    ext = filename.rsplit('.',1)[1]
    if ext.upper() in app.config['ALLOWED_EXTENSIONS']:
        return True 
    else:
        return False

# Rota Índice
@app.route('/')
def index():
    return render_template('index.html')

# Rota para Processamento dos Dados
@app.route('/dataupload', methods=['GET', 'POST'])
def dataupload():
    if request.method == 'POST' and 'csv_data' in request.files:
        file = request.files['csv_data']

        # Verificar se o arquivo tem um nome
        if file.filename == "":
            print('File must have a filename')
            return "O arquivo enviado não tem um nome. Por favor, envie um arquivo válido.", 400

        # Verificar se o arquivo tem uma extensão permitida
        if not allowed_extension(file.filename):
            print('Extension not allowed')
            return "A extensão do arquivo não é permitida. Por favor, envie um arquivo CSV.", 400

        # Verificar o tamanho do arquivo manualmente (em bytes)
        max_size = 5 * 1024 * 1024  # Limite de 5 MB
        file.seek(0, os.SEEK_END)  # Ir para o final do arquivo para obter o tamanho
        file_size = file.tell()  # Tamanho em bytes
        file.seek(0)  # Voltar ao início do arquivo para não corromper a leitura

        if file_size > max_size:
            print(f"O arquivo é muito grande: {file_size} bytes")
            return f"O arquivo enviado é muito grande ({file_size / (1024 * 1024):.2f} MB). O limite é de 5 MB.", 400

        # Salvar o arquivo se todas as validações passarem
        filename = secure_filename(file.filename)
        file.save(os.path.join('static/dados', filename))
        filepath = os.path.join('static/dados', filename)

        # Processar o arquivo normalmente
        try:
            max_rows = 5000
            df = pd.read_csv(filepath, nrows=max_rows)
            total_rows = sum(1 for _ in open(filepath)) - 1  # Total de linhas no CSV
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            return "Erro ao carregar o arquivo. Por favor, verifique o formato do arquivo.", 400

        # Retornar os dados processados
        df_size = df.size
        df_shape = df.shape
        df_dtypes = df.dtypes
        info = io.StringIO()
        df_info = str(df.info(buf=info, verbose=True, null_counts=True))
        df_info = info.getvalue()
        df_columns = list(df.columns)
        df_describe = df.describe()

        return render_template(
            'details.html',
            filename=filename,
            df_size=df_size,
            df_shape=df_shape,
            df_dtypes=df_dtypes,
            df_info=df_info,
            df_columns=df_columns,
            df=df,
            df_describe=df_describe,
            total_rows=total_rows,
            max_rows=max_rows,
        )
    else:
        return render_template('index.html')

@app.route('/grafico')
def grafico():
    try:
        graph = pygal.Line()
        graph.title = 'Gráfico Linguagens de Programação'
        graph.x_labels = ['2011','2012','2013','2014','2015','2016']
        graph.add('Python',[15,31,89,200,356,900])
        graph.add('PHP',[100,200,300,140,200,22])
        graph.add('Java',[14,31,33,45,85,88])
        graph.add('C++',[12,44,66,33,100,35])
        graph.add('LISP',[33,32,55,12,133,40])
        graph.add('Outras',[5,13,55,13,50,55])
        graph_data = graph.render_data_uri()
        return render_template('grafico.html',graph_data=graph_data)

    except Exception:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)