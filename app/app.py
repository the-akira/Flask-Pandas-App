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
@app.route('/dataupload',methods=['GET','POST'])
def dataupload():
	if request.method == 'POST' and 'csv_data' in request.files:
		file = request.files['csv_data']
		if file.filename == "":
			print('file must have a filename')
			return redirect(request.url)
		if not allowed_extension(file.filename):
			print('Extension not allowed')
			return redirect(request.url)	
		else:		
			filename = secure_filename(file.filename)

			file.save(os.path.join('static/dados',filename))
			fullfile = os.path.join('static/dados',filename)

			df = pd.read_csv(os.path.join('static/dados',filename))
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
				df_describe=df_describe
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
