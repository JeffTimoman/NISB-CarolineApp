from webdata import create_app
from webdata.config import Config
app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT, host='0.0.0.0')