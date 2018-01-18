from flask import Flask, request, send_from_directory

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')

@app.route('/download/<path:path>')
def send_js(path):
    return send_from_directory('download', path)

if __name__ == "__main__":
	app.run(
		debug=True,
		port=8000,
		host='0.0.0.0'
	)
