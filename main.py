from wsgiref.simple_server import make_server

import falcon
from request_handler import GenericResource
from swagger_parser import SwaggerParser

app = falcon.App()


def init_swag_forger():
    parse_result = SwaggerParser("swagger.json")
    for path, resp_meta_info in parse_result.paths.items():
        app.add_route(path, GenericResource(parse_result, resp_meta_info))


if __name__ == '__main__':
    init_swag_forger()
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')
        # Serve until process is killed
        httpd.serve_forever()
