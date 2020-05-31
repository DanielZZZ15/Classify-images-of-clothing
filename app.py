import os 
import tensorflow as tf
import numpy as np
from tensorflow import keras
import datetime
from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename
from flask import Flask,render_template,request,flash
import cv2


from cassandra.cluster import Cluster #引入Cluster模块
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()#指定连接keyspace，相当于sql中use dbname
keyspacename = "data"
try:
    session.execute("create keyspace %s with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};" % keyspacename)
except:
    pass
session.set_keyspace('data')
session.execute('use data')
s = session
try:
    s.execute("CREATE TABLE data(uploadfilename text PRIMARY KEY,uploadtime text,prediction text)")
except:
    pass

app = Flask(__name__)
app.secret_key="znx_"

fashion_mnist = keras.datasets.fashion_mnist

def create_model():
    model = tf.keras.models.Sequential([
    keras.layers.Flatten(input_shape=(28, 28)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(10)])

    model.compile(optimizer='adam',loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),metrics=['accuracy'])

    return model

model = create_model()
model.load_weights('./checkpoints/model')

#读取模型结束
@app.route('/',methods=['GET','POST'])
def index():
    return render_template("login.html")

basedir = os.path.abspath(os.path.dirname(__file__))

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG'])  
def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
  
@app.route('/mnist', methods=['post'])
def mnist():
    req_time=datetime.datetime.now()
    if request.method=='POST':
        file=request.files['file']
        if file and allowed_file(file.filename):
            upload_filename=secure_filename((file).filename)
            save_filename=str(req_time).rsplit('.',1)[1]+'.'+upload_filename 
            save_filepath=os.path.join(app.root_path,save_filename)
            file.save(save_filepath)
            
            probability_model = tf.keras.Sequential([model,tf.keras.layers.Softmax()])
            img=cv2.imread(save_filepath,0)   
            size=(28,28)
            img_resize = cv2.resize(img, size) 
            img_resize = (np.expand_dims(img_resize,0))
            predictions_single = probability_model.predict(img_resize)
            np.argmax(predictions_single[0])
            
            
            params = [save_filename,req_time.strftime('%Y-%m-%d %H:%M:%S.%f'),str(np.argmax(predictions_single[0]))]
            s.execute("INSERT INTO data (uploadfilename,uploadtime,prediction)VALUES (%s, %s,%s)", params)
            

            return("%s%s%s%s%s%s%s%s%s"%("Upload File Name:",save_filename,"\n","Upload Time:",req_time,"\n","Prediction:",np.argmax(predictions_single[0]),"\n"))
          
if __name__ == '__main__':
    app.run()
    
