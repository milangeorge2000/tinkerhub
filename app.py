from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
import numpy as np
import os
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from torch.utils.data import DataLoader
from PIL import Image
from flask_ngrok import run_with_ngrok
import webbrowser


# Define a flask app
app = Flask(__name__)

# run_with_ngrok(app)


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index .html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        f.save("img.jpg")
    
        
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
        resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion
        
        def face_match(img_path, data_path): # img_path= location of photo, data_path= location of data.pt 
            # getting embedding matrix of the given img
            img = Image.open(img_path)
            face, prob = mtcnn(img, return_prob=True) # returns cropped face and probability
            emb = resnet(face.unsqueeze(0)).detach() # detech is to make required gradient false
            
            saved_data = torch.load('data2.pt') # loading data.pt file
            embedding_list = saved_data[0] # getting embedding data
            name_list = saved_data[1] # getting list of names
            dist_list = [] # list of matched distances, minimum distance is used to identify the person
            
            for idx, emb_db in enumerate(embedding_list):
                dist = torch.dist(emb, emb_db).item()
                dist_list.append(dist)
                
            idx_min = dist_list.index(min(dist_list))
            return (name_list[idx_min], min(dist_list))


        result = face_match("img.jpg", 'data2.pt')
        if(result[0] == "mammootty" and result[1] < 0.8):
            return render_template('mammootty.html')
        elif(result[0] == "mammootty" and result[1] > 0.8):
            return render_template('unknown.html')
        if(result[0] == "mohanlal" and result[1] < 0.8):
            return render_template('mohanlal.html')
        elif(result[0] == "mohanlal" and result[1] > 0.8):
            return render_template('unknown.html')
        elif(result[0] == "unknown"):
            return render_template('unknown.html')
        

if __name__ == '__main__':
    app.run(debug=False)
