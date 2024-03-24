from server.extensions import app, db

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8088, debug=True, use_reloader=False)
