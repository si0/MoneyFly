import os
import config
from datetime import date
from sqlalchemy import create_engine, text
from flask import Flask, g, request, flash, url_for, redirect, render_template


# Config
app = Flask(__name__)
DEBUG = config.flask_config["DEBUG"]
SECRET_KEY = config.flask_config["SECRET_KEY"]
app.config.from_object(__name__)
engine = create_engine(config.database_url)


# キャッシュバスター
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# データベースリクエスト前に接続
@app.before_request
def before_request():
    g.db = engine.connect()


# データベースリクエスト後に切断
@app.after_request
def after_request(response):
    g.db.close()
    return response


############################################
# トップページ / 過去の料金の表示
############################################
@app.route("/")
def show_money():
    moneys = [[]]

    rows = g.db.execute("SELECT \
                         cate.category, money.money, money.note, money.art_date \
                         FROM mf_money money, mf_category cate \
                         WHERE money.category = cate.id \
                         ORDER BY money.id DESC LIMIT 5")

    # 使用額を取得
    for row in rows.fetchall():
        # 備考がNoneの場合は空白で返す
        if row["note"] is None:
            note = ""
        else:
            note = row["note"]

        # 日付のフォーマットを変更する
        art_date = row["art_date"].strftime("%Y-%m-%d")

        moneys[0].append({"category": row["category"],
                          "money": row["money"],
                          "note": note,
                          "art_date": art_date})

    # 合計使用額を取得
    month = date.today().month
    sql = text("SELECT sum(money) FROM mf_money WHERE date_part('month', art_date) = :tmonth")
    row = g.db.execute(sql, tmonth = int(month))

    moneys.append({"summoney": row.fetchone()[0]})

    return render_template("show_money.html", moneys=moneys, month=month)


############################################
# 料金追加ページ / 料金の追加
############################################
@app.route("/add_money", methods=["POST", "GET"])
def add_money():
    # 直接のアクセスの場合はadd_money.htmlを開く
    if request.method == "GET":
        insert = [[], []]

        # カテゴリーレコードの取得
        rows = g.db.execute("SELECT id, category FROM mf_category")
        for row in rows.fetchall():
            insert[0].append({"id": row["id"],
                         "category": row["category"]})
        # 今日の日付を取得
        value = date.today()
        insert[1].append(value.strftime("%Y-%m-%d"))

        return render_template("add_money.html", insert=insert)

    if not request.form["category"] or not request.form["money"]:
        flash("投稿内容が誤っています")
        return redirect(url_for("add_money"))

    # 備考が記入されていない場合はNoneとする
    if request.form["note"] == "":
        note_value = None
    else:
        note_value = request.form["note"]

    # データ挿入SQLの実行
    sql = text("INSERT INTO mf_money \
                (category, money, note, art_date) VALUES \
                (:category, :money, :note, :art_date)")
    g.db.execute(sql,
                 category = request.form["category"],
                 money = request.form["money"],
                 note = note_value,
                 art_date = request.form["art_date"])
    flash("投稿が完了しました")

    return redirect(url_for("show_money"))


############################################
# 設定ページ / システムの設定
############################################
@app.route("/sys_config", methods=["POST", "GET"])
def sys_config():
    return redirect(url_for("show_money"))

if __name__ == "__main__":
    app.run()
