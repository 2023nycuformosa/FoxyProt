from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from joblib import load
from Bio import SeqIO
import numpy as np
import re
import io

app = Flask(__name__, template_folder='templates', static_folder='static')

cors = CORS(app, resources={r"/classify-fasta": {"origins": "*"}})

data = np.load("./model/uniprotSeq.npz")
svm_model = load('./model/svm.joblib')
scaler = load('./model/scaler.joblib')

def extractEntryId(entry_name):
    match = re.match(r".*\|([A-Z0-9]+)\|.*", entry_name)
    if match:
        return match.group(1)
    else:
        return "N/A"

def embedEntry(entry):
    return data[entry]


@app.route('/')
def index():
    
    return render_template("index.html")

@app.route('/classify-fasta', methods=['POST'])
def classify():
    try:
        received_data = request.get_data()
        #print("Received Data:", received_data)
        
        if 'fastaFile' in request.files:
            fasta_file = request.files['fastaFile']
    
            if fasta_file:
                fasta_contents = fasta_file.read().decode("utf-8")
                entries = [str(record.id) for record in SeqIO.parse(io.StringIO(fasta_contents), 'fasta')]
                entry_names = [extractEntryId(entry) for entry in entries]

                results = []

                for entry in entry_names:
                    embedded_entry = embedEntry(entry)
                    X_reshaped = embedded_entry.reshape(1, -1)
                    X_scaled = scaler.transform(X_reshaped)
                    svm_pred = svm_model.predict_proba(X_scaled)

                    if 0 <= svm_pred[0][1] < 0.3:
                        pred = "Very Unlikely"
                    elif 0.3 <= svm_pred[0][1] < 0.5:
                        pred = "Unlikely"
                    elif 0.5 <= svm_pred[0][1] < 0.7:
                        pred = "Likely"
                    elif 0.7 <= svm_pred[0][1] <= 1:
                        pred = "Very Likely"

                    results.append(f"Prediction for {entry:10}: {svm_pred[0][1]:.2%} {pred:15} \n")

                return "\n".join(results)
        else:
            return "No file provided."

    except Exception as e:
        return str(e)


    
if __name__ == '__main__':
    app.run(port=8080)
