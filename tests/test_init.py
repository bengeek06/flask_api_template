from flask import Flask
import app

def test_main_runs(monkeypatch):
    called = {}

    def fake_run(self, debug):
        called['run'] = True
        called['debug'] = debug

    monkeypatch.setattr("flask.Flask.run", fake_run)
    app.create_app('app.config.TestingConfig').run(debug=True)
    assert called.get('run') is True
    assert called.get('debug') is True

def test_create_app_returns_flask_app():
    application = app.create_app('app.config.TestingConfig')
    assert isinstance(application, Flask)

def test_handle_404(client):
    response = client.get('/v0/route/inexistante')
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["message"] == "Resource not found"

def test_error_handler_400(client):
    from werkzeug.exceptions import BadRequest

    @client.application.route("/bad")
    def bad():
        raise BadRequest()

    response = client.get("/bad")
    assert response.status_code == 400
    assert response.get_json() == {"message": "Bad request"}

def test_error_handler_500(client):
    # Désactive la propagation pour tester le handler 500
    client.application.config["PROPAGATE_EXCEPTIONS"] = False

    @client.application.route("/fail")
    def fail():
        raise Exception("fail!")
    response = client.get("/fail")
    assert response.status_code == 500
    assert response.get_json() == {"message": "Internal server error"}