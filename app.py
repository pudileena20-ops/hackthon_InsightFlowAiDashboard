from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from services.db_service import fetch_table_data

import json

app = Flask(__name__)
app.secret_key = "supersecretkey"  


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.username = "Leenaa"
        self.password = "76800"

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "Leenaa" and password == "76800":
            user = User(id=1)
            login_user(user)
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    selected_region = request.args.get("region", "")
    selected_category = request.args.get("category", "")

    df = fetch_table_data()

    if not df.empty:
        df.columns = df.columns.str.lower().str.strip()

        
        region_options = sorted(df["region"].dropna().unique().tolist()) if "region" in df.columns else []
        category_options = sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else []

      
        if selected_region:
            df = df[df["region"] == selected_region]
        if selected_category:
            df = df[df["category"] == selected_category]
    else:
        region_options = []
        category_options = []


    total_rows = len(df)
    total_columns = len(df.columns)
    total_sales = round(float(df["sales"].sum()), 2) if "sales" in df.columns else 0
    total_profit = round(float(df["profit"].sum()), 2) if "profit" in df.columns else 0

    table_data = df.to_dict(orient="records") if not df.empty else []
    columns = df.columns.tolist() if not df.empty else []

 
    if not df.empty and "region" in df.columns:
        region_group = df.groupby("region")["sales"].sum()
        region_labels = json.dumps(list(region_group.index))
        region_values = json.dumps(list(region_group.values))
    else:
        region_labels = json.dumps([])
        region_values = json.dumps([])

    if not df.empty and "category" in df.columns:
        category_group = df.groupby("category")["profit"].sum()
        category_labels = json.dumps(list(category_group.index))
        category_values = json.dumps(list(category_group.values))
    else:
        category_labels = json.dumps([])
        category_values = json.dumps([])

   
    ai_summary = generate_summary(df) if not df.empty else "No matching data found."

    return render_template(
        "dashboard.html",
        total_rows=total_rows,
        total_columns=total_columns,
        total_sales=total_sales,
        total_profit=total_profit,
        columns=columns,
        table_data=table_data,
        region_labels=region_labels,
        region_values=region_values,
        category_labels=category_labels,
        category_values=category_values,
        ai_summary=ai_summary,
        region_options=region_options,
        category_options=category_options,
        selected_region=selected_region,
        selected_category=selected_category
    )

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)