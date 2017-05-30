import config
from sqlalchemy import create_engine, text
from flask import Flask, g, request, flash, url_for, redirect, render_template


# Config
app = Flask(__name__)
DEBUG = config.flask_config["DEBUG"]
SECRET_KEY = config.flask_config["SECRET_KEY"]
app.config.from_object(__name__)
engine = create_engine(config.database_url)


# データベースリクエスト前に接続
@app.before_request
def before_request():
    g.db = engine.connect()


# データベースリクエスト後に切断
@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route("/")
def show_money():
    moneys = [[]]
    rows = g.db.execute("SELECT id, title, money, note, datetime FROM moneyfly ORDER BY id DESC LIMIT 5")

    # 使用額を取得
    for row in rows.fetchall():
        # 備考がNoneの場合は空白で返す
        if row["note"] is None:
            note = ""
        else:
            note = row["note"]

        moneys[0].append({"id": row["id"],
                          "title": row["title"],
                          "money": row["money"],
                          "note": note,
                          "date": row["datetime"]})

    # 合計使用額を取得
    row = g.db.execute("SELECT sum(money) FROM moneyfly")
    moneys.append({"summoney": row.fetchone()[0]})

    return render_template("show_money.html", moneys=moneys)


@app.route("/add_money", methods=["POST"])
def add_money():
    if not request.form["title"] or not request.form["money"]:
        flash("投稿内容が誤っています")
        return redirect(url_for("show_money"))

    # 備考が記入されていない場合はNoneとする
    if request.form["note"] == "":
        note_value = None
    else:
        note_value = request.form["note"]

    # データ挿入SQLの実行
    sql = text("INSERT INTO moneyfly \
                (title, money, note) VALUES \
                (:title, :money, :note)")
    g.db.execute(sql,
                 title = request.form["title"],
                 money = request.form["money"],
                 note = note_value)
    flash("投稿が完了しました")

    return redirect(url_for("show_money"))

if __name__ == "__main__":
    app.run()
