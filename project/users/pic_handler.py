from PIL import Image
import os
from flask import current_app
import secrets

def pic_saver(file,username):
    filename = secrets.token_hex(4)+username+'.'+file.filename.split('.')[-1]
    saving_path = os.path.join(current_app.root_path,'static/profile_pics',filename)
    pic = Image.open(file)
    pic.thumbnail((125,125))
    pic.save(saving_path)
    return filename
    
