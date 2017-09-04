from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from schema import Schema
from flask import Response, request, abort, send_from_directory
from PIL import Image
from io import StringIO

import config as cfg
import data


def create_app(**kwargs):
    app = Flask(__name__)
    app.debug = True
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view('graphql', schema=Schema, **kwargs)
    )
    return app

app = create_app(graphiql=True)


@app.route('/image/<filename>')
def image(filename):
    return send_from_directory(cfg.MEDIA_PATH, filename)


if __name__ == '__main__':
    CORS(app, resources={r'/graphql': {'origins': '*'}})
    app.run(host='0.0.0.0')
