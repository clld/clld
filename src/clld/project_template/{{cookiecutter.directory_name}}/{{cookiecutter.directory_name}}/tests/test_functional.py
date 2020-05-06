def test_home(app):
    app.get_html('/', status=200)
