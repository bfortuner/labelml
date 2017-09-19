import os
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


@app.route('/img/<project>/<filename>')
def image(project, filename):
    img_dir = cfg.MEDIA_PATH
    return send_from_directory(img_dir, filename)


if __name__ == '__main__':
    CORS(app, resources={r'/graphql': {'origins': '*'}})
    app.run(host='0.0.0.0')
