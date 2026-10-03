from flask import Flask, request, jsonify
from flask_cors import CORS
from analyzer import analyze_error
app = Flask(__name__)
CORS(app)
@app.get('/api/health')
def health(): return jsonify({'status':'ok','service':'TraceBack AI analyzer'})
@app.post('/api/analyze')
def analyze():
    body=request.get_json(silent=True) or {}
    error=(body.get('error') or '').strip()
    if not error: return jsonify({'error':'error is required'}),400
    if len(error)>20000: return jsonify({'error':'Please keep the error under 20,000 characters.'}),400
    return jsonify(analyze_error(body.get('language') or 'Python', error, body.get('context') or ''))
if __name__=='__main__': app.run(debug=True, port=5000)
