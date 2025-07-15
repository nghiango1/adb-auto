from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request

from adb_auto.api.v1.screen import screen_api
from adb_auto.config.setting import DEBUG, VERBOSE
from adb_auto.jobs.screen_reload_job import ScreenReloadJob
from adb_auto.utils.logger import debug
from adb_auto.views.home import home_view
import logging

logging.basicConfig(level=logging.ERROR)
if VERBOSE:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


template = {
    "swagger": "2.0",
    "info": {
        "title": "Adb Auto API",
        "description": "API for automation Android using adb",
        "version": "0.0.1",
    },
}

app = Flask(__name__)
app.config["SWAGGER"] = {"title": "Adb Auto API", "uiversion": 3}
swagger = Swagger(app, template=template)

app.register_blueprint(screen_api)
app.register_blueprint(home_view)


# Health check the server
@app.route("/api/hello")
@swag_from("docs/hello.yml")
def hello():
    name = request.args.get("name", type=str)
    result = {"result": f"hello {name}"}
    return jsonify(result)


# Spawn as many thread as you wanted here :)
def start_background_jobs():
    logger.info("[INFO] Start all background jobs")
    print("[INFO] Start all background jobs")
    ScreenReloadJob.start()


# Then try to exit each of them
def exit_background_jobs():
    debug("[INFO] Try to exit background jobs")
    ScreenReloadJob.stop()


def main():
    start_background_jobs()
    app.run(debug=DEBUG)
    exit_background_jobs()


if __name__ == "__main__":
    main()
