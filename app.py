from flask import Flask, request, redirect, session, url_for, render_template
from onelogin.saml2.auth import OneLogin_Saml2_Auth
import json
import os

app = Flask(__name__)
app.secret_key = "mysamlapp-secret"


def prepare_flask_request(request):
    return {
        'https': 'off',
        'http_host': request.host,
        'server_port': request.environ.get('SERVER_PORT'),
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }


def init_saml_auth(req):
    return OneLogin_Saml2_Auth(
        req,
        custom_base_path=os.path.join(os.getcwd(), 'saml')
    )


@app.route("/")
def index():
    return render_template('index.html')
    # if "user" in session:
    #     return f"""
    #     <h2>Welcome to MySAMLapp</h2>
    #     <p>Logged in as: {session['user']}</p>
    #     <a href="/logout">Logout</a>
    #     """
    # else:
    #     return """
    #     <h2>Welcome to MySAMLapp</h2>
    #     <a href="/login">Login via SAML</a>
    #     """


@app.route("/login")
def login():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)
    return redirect(auth.login())


@app.route("/acs", methods=['POST'])
def acs():
    req = prepare_flask_request(request)
    auth = init_saml_auth(req)

    auth.process_response()
    errors = auth.get_errors()

    if errors:
        return "Errors: " + ", ".join(errors)

    session["user"] = auth.get_nameid()
    session["attributes"] = auth.get_attributes()

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("index"))

    return render_template(
        "results.html",
        nameid=session.get("user"),
        attributes=json.dumps(session.get("attributes"), indent=4)
    )


@app.route("/logout")
def logout():
    session.clear()

    return redirect(
        "https://dev-aaf.au.auth0.com/v2/logout"
        "?returnTo=http://localhost:5000/"
        "&client_id=V6qu7woaCvbywuGVuIS5JXHQRFVBX0nz"
    )


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)