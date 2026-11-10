import hmac
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

TIPOS = [
    "Whisky", "Vodka", "Gin", "Cerveja", "Vinho", "Espumante", "Tequila", "Rum",
    "Cachaça", "Licor", "Outra alcoólica",
    "Água", "Refrigerante", "Suco", "Água de coco", "Energético", "Outra sem álcool",
]
ACCESS_CODE = os.environ.get("ACCESS_CODE", "")


def database_url():
    url = os.environ.get("DATABASE_URL", "sqlite:///bebidas.db")
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg2://" + url[len(prefix):]
    return url


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI=database_url(),
    # Neon suspende conexões ociosas: testa a conexão antes de usar e recicla as antigas.
    SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True, "pool_recycle": 280},
)
db = SQLAlchemy(app)


class Bebida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    who = db.Column(db.String(40), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    det = db.Column(db.String(60), nullable=False, default="")
    qtd = db.Column(db.Integer, nullable=False)
    ml = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {"id": self.id, "who": self.who, "tipo": self.tipo, "det": self.det,
                "qtd": self.qtd, "ml": self.ml, "litros": self.qtd * self.ml / 1000}


@app.before_request
def verificar_codigo():
    if ACCESS_CODE and request.path.startswith("/api/"):
        enviado = request.headers.get("X-Code", "").encode()
        if not hmac.compare_digest(enviado, ACCESS_CODE.encode()):
            return jsonify(erro="Código de acesso inválido."), 401


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/bebidas")
def listar():
    return jsonify([i.to_dict() for i in Bebida.query.order_by(Bebida.id).all()])


@app.post("/api/bebidas")
def criar():
    d = request.get_json(silent=True) or {}
    try:
        qtd, ml = int(d.get("qtd")), int(d.get("ml"))
    except (TypeError, ValueError):
        return jsonify(erro="Quantidade e tamanho inválidos."), 400
    who = str(d.get("who", "")).strip()[:40]
    tipo = d.get("tipo")
    if not who or tipo not in TIPOS or not 1 <= qtd <= 500 or not 1 <= ml <= 20000:
        return jsonify(erro="Dados inválidos."), 400
    item = Bebida(who=who, tipo=tipo, det=str(d.get("det", "")).strip()[:60], qtd=qtd, ml=ml)
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.delete("/api/bebidas/<int:item_id>")
def remover(item_id):
    item = db.session.get(Bebida, item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return "", 204


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
