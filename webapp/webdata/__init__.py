from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from webdata.config import Config
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from webdata.main.routes import main 
    from webdata.summary_bandwith.routes import summary_bandwith
    from webdata.ip_allocation.routes import ip_allocation as ip_allocation_bp
    app.register_blueprint(main, url_prefix="/")
    
    # Services
    app.register_blueprint(summary_bandwith, url_prefix="/summary_bandwith")
    # IP allocation service
    app.register_blueprint(ip_allocation_bp, url_prefix="/ip_allocation")

    @app.context_processor
    def inject_request():
        from flask import request
        return dict(request=request)
    
    @app.context_processor
    def inject_confi_name():
        return dict(user_confi_name=app.config['USER'])
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    print(Config.TESSERACT_CMD_PATH)
    return app
