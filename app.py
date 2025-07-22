#!/usr/bin/env python3
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(name)
CORS(app)

@app.route(’/’)
def home():
return jsonify({
‘status’: ‘GREGVERSE Backend is LIVE!’,
‘message’: ‘Welcome to the ultimate Greg Isenberg archive!’,
‘version’: ‘1.0.0’
})

@app.route(’/health’)
def health():
return jsonify({
‘status’: ‘healthy’,
‘service’: ‘gregverse-backend’,
‘timestamp’: ‘2025-07-22’
})

@app.route(’/api/test’)
def test():
return jsonify({
‘message’: ‘GREGVERSE API is working!’,
‘status’: ‘success’
})

if name == ‘main’:
port = int(os.environ.get(‘PORT’, 8080))
app.run(host=‘0.0.0.0’, port=port, debug=False)

