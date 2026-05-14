from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "O Bot está online e funcionando!"

def run():
    # O Render injeta a porta automaticamente na variável de ambiente PORT
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()