import os
from flask import Flask

app = Flask(name)

@app.route(’/’)
def home():
return ‘GREGVERSE Backend is LIVE!’

@app.route(’/health’)
def health():
return ‘OK’

if name == ‘main’:
port = int(os.environ.get(‘PORT’, 8080))
app.run(host=‘0.0.0.0’, port=port)
