from flask import Flask,flash,render_template,request,redirect, url_for
import os, sys, subprocess
import time
import sqlite3
import hashlib
from werkzeug import secure_filename
sys.path.append(os.getcwd()+'/scripts')
from features import features
from Bio import SeqIO
from libsvm import libsvm_surface, libsvm_secretory     


#----------------------SURFACE PROTEINS PEDICTION-----------------------

def run_surface(filename):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    parameter_file=open(filename+"_parameters.txt", 'w')
    seqID_list=[]
    result_file=open(filename+"_result.txt", 'w')
    result_file.write("Sequence_ID\tPrediction\n")

    records=SeqIO.parse(filename, "fasta")
    for record in records:
        i=0
        hash_sequence=hashlib.md5(str(record.seq)).hexdigest()
        c.execute("SELECT * FROM surface WHERE sequence='"+hash_sequence+"'")
        data=c.fetchone()
        if data is None:
            parameter_file.write(features(record.id, str(record.seq))+"\n")
            seqID_list.append(record.id)
                 
        else:
            c.execute("UPDATE surface SET access=access+1, time=CURRENT_TIMESTAMP WHERE sequence='"+hash_sequence+"'")
            conn.commit()
            c.execute("SELECT prediction FROM surface WHERE sequence='"+hash_sequence+"'")
            data1=c.fetchone()
            result_file.write(str(record.id)+"\t"+data1[0]+"\n")

    
    parameter_file.close()
    paraFile=filename+"_parameters.txt"
    libsvm_surface(paraFile)

    predicted = open(paraFile+".predict", "r")

    fasta_rec=SeqIO.index(filename, "fasta")
    print predicted
    i=0

    for pred in predicted:
        print pred
        if int(pred)==1:
            pred='Surface Protein'
        if int(pred)==0:
            pred='Non-Surface Protein'
            
        result_file.write(seqID_list[i]+"\t"+pred+"\n")
        c.execute("INSERT INTO surface VALUES ('"+hashlib.md5(str(fasta_rec[seqID_list[i]].seq)).hexdigest()+"', '"+pred+"', 0, CURRENT_TIMESTAMP)")
        i=i+1
    conn.commit()
    predicted.close()
    result_file.close()
    if surface_email!="":
        command = "echo 'Your SchistoProt Prediction Result is attached for job ID: '"+filename+"'\n\n\nKind regards,\n\nLutz Krause & Shihab Hasan\nBioinformatics Lab, QIMR Berghofer Medical Research Institute'"+" | EMAIL='Shihab Hasan <shihab.hasan@qimrberghofer.edu.au>' mutt -a "+filename+"'_result.txt' -s 'SchistoProt Prediction Result' -- "+surface_email
        subprocess.call(command, shell=(sys.platform!="Linux"))

#----------------------SECRETORY PEPTIDES PEDICTION-----------------------

def run_secretory(filename):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    parameter_file=open(filename+"_parameters.txt", 'w')
    seqID_list=[]
    result_file=open(filename+"_result.txt", 'w')
    result_file.write("Sequence_ID\tPrediction\n")

    records=SeqIO.parse(filename, "fasta")
    for record in records:
        i=0
        hash_sequence=hashlib.md5(str(record.seq)).hexdigest()
        c.execute("SELECT * FROM secretory WHERE sequence='"+hash_sequence+"'")
        data=c.fetchone()
        if data is None:
            parameter_file.write(features(record.id, str(record.seq))+"\n")
            seqID_list.append(record.id)
                 
        else:
            c.execute("UPDATE secretory SET access=access+1, time=CURRENT_TIMESTAMP WHERE sequence='"+hash_sequence+"'")
            conn.commit()
            c.execute("SELECT prediction FROM secretory WHERE sequence='"+hash_sequence+"'")
            data1=c.fetchone()
            result_file.write(str(record.id)+"\t"+data1[0]+"\n")

    
    parameter_file.close()
    paraFile=filename+"_parameters.txt"
    libsvm_secretory(paraFile)

    predicted = open(paraFile+".predict", "r")

    fasta_rec=SeqIO.index(filename, "fasta")
    print predicted
    i=0

    for pred in predicted:
        print pred
        if int(pred)==1:
            pred='Secretory Protein'
        if int(pred)==0:
            pred='Non-Secretory Protein'
            
        result_file.write(seqID_list[i]+"\t"+pred+"\n")
        c.execute("INSERT INTO secretory VALUES ('"+hashlib.md5(str(fasta_rec[seqID_list[i]].seq)).hexdigest()+"', '"+pred+"', 0, CURRENT_TIMESTAMP)")
        i=i+1
    conn.commit()
    predicted.close()
    result_file.close()
    if secretory_email!="":
        command = "echo 'Your SchistoProt Prediction Result is attached for job ID: '"+filename+"'\n\n\nKind regards,\n\nLutz Krause & Shihab Hasan\nBioinformatics Lab, QIMR Berghofer Medical Research Institute'"+" | EMAIL='Shihab Hasan <shihab.hasan@qimrberghofer.edu.au>' mutt -a "+filename+"'_result.txt' -s 'SchistoProt Prediction Result' -- "+secretory_email
        subprocess.call(command, shell=(sys.platform!="Linux"))



#----------------------WORKING WITH HTML-----------------------------------
app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'some_secret'

@app.route('/',methods=['GET','POST'])
def index():
   return render_template('index.html')

@app.route('/home',methods=['GET','POST'])
def home():
   return render_template('index.html')

@app.route('/help',methods=['GET','POST'])
def manual():
   return render_template('help.html')

@app.route('/contact',methods=['GET','POST'])
def contact():
    return render_template('contact.html')

@app.route('/thanks',methods=['POST'])
def thanks():
    name=request.form['name']
    email=request.form['email']
    message=request.form['message']
    command = "echo 'Name: '"+name+"'\nEmail: '"+email+"'\nMessage: '"+message+" | EMAIL='Shihab Hasan <shihab.hasan@qimrberghofer.edu.au>' mutt -s 'SchistoProt Prediction Query' -- pharm.shihab@gmail.com"
    subprocess.call(command, shell=(sys.platform!="Linux"))
    return render_template('thanks.html', name=name)



@app.route('/surface',methods=['POST'])
def surface():
    global surface_email
    surface_email=request.form['surface_email'].replace(" ","")
    if request.form['surface_sequences'].replace(" ","")!="":
        filename=hashlib.md5(time.asctime()).hexdigest()
        file_in=open(filename, 'w')
        file_in.write(request.form['surface_sequences'].replace(" >",">"))
        file_in.close()
    else:
        file = request.files['surface_file']
        filename = secure_filename(file.filename)+"_"+hashlib.md5(time.asctime()).hexdigest()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        records=SeqIO.parse(filename, "fasta")
    id=filename
    return redirect(url_for('surface_progress', id=id))

@app.route('/secretory',methods=['POST'])
def secretory():
    global secretory_email
    secretory_email=request.form['secretory_email'].replace(" ","")
    if request.form['secretory_sequences'].replace(" ","")!="":
        filename=hashlib.md5(time.asctime()).hexdigest()
        file_in=open(filename, 'w')
        file_in.write(request.form['secretory_sequences'].replace(" >",">"))
        file_in.close()
    else:
        file = request.files['secretory_file']
        filename = secure_filename(file.filename)+"_"+hashlib.md5(time.asctime()).hexdigest()
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        records=SeqIO.parse(filename, "fasta")
    id=filename
    return redirect(url_for('secretory_progress', id=id))

@app.route('/surface_progress/<id>')
def surface_progress(id):
    return render_template('surface_progress.html', id=id)
      
@app.route('/status/<id>')
def status(id):
    return 'success'

@app.route('/surface_results/<id>')
def surface_results(id):
    run_surface(id)
    f = open(id+"_result.txt",'r')
    lines = f.readlines()[1:]
    f.close()
    os.remove(id)
    os.remove(id+"_result.txt")
    os.remove(id+"_parameters.txt")
    os.remove(id+"_parameters.txt.scale")
    os.remove(id+"_parameters.txt.predict")
    os.remove(id+"_parameters.txt.libsvm")
    return render_template('surface_result.html', surface_result=lines)

#-----------------------------------------------
@app.route('/secretory_progress/<id>')
def secretory_progress(id):
    return render_template('secretory_progress.html', id=id)


@app.route('/secretory_results/<id>')
def secretory_results(id):
    run_secretory(id)
    f = open(id+"_result.txt",'r')
    lines = f.readlines()[1:]
    f.close()
    os.remove(id)
    os.remove(id+"_result.txt")
    os.remove(id+"_parameters.txt")
    os.remove(id+"_parameters.txt.scale")
    os.remove(id+"_parameters.txt.predict")
    os.remove(id+"_parameters.txt.libsvm")
    return render_template('secretory_result.html', secretory_result=lines)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
