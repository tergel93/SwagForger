import random

import falcon


# TODO support OpenAPI 2.0 & 3.0
# TODO check required request param types and values
# TODO Customize response content
# TODO Fetch config file from remote address

def _random_resp(resps):
    code = random.choice(list(resps.keys()))
    return code, resps[code]


def _parse_model_ref(model_ref_str):
    return model_ref_str.split('/')[2]


def _parse_resp_type(api_spec, resp_def):
    if 'items' in resp_def:  # if contains 'items', we assert that it must an array type
        model_ref = resp_def['items']['$ref']
        return [_parse_model_ref(model_ref)]
    elif 'type' in resp_def:
        resp_type = resp_def['type']
        if resp_type == 'string':
            return 'string'
        else:
            resp_type = resp_def['additionalProperties']['type']
            if resp_type == 'string':
                return 'string'
            elif resp_type == 'integer':
                return 1
            else:
                return []
    else:
        model_ref = resp_def.get('$ref')
        model_name = _parse_model_ref(model_ref)
        return api_spec.definitions_example[model_name]


def _parse_resp(api_spec, response_mappings):
    responses = {}
    for http_code, resp in response_mappings.items():
        if http_code != '200':
            responses['200' if http_code == 'default' else http_code] = resp['description']
        else:
            responses['200'] = (str(_parse_resp_type(api_spec, resp['schema'])))
    return lambda: _random_resp(responses)


class GenericResource:

    def __init__(self, api_spec, resp_meta_info):
        self.handlers = {}
        for http_method in resp_meta_info.keys():
            self.handlers[http_method.lower()] = _parse_resp(api_spec, resp_meta_info[http_method]['responses'])

    def on_get(self, req, resp, **kwargs):
        self.handle_request(req, resp)

    def on_post(self, req, resp, **kwargs):
        self.handle_request(req, resp)

    def on_put(self, req, resp, **kwargs):
        self.handle_request(req, resp)

    def on_patch(self, req, resp, **kwargs):
        self.handle_request(req, resp)

    def on_delete(self, req, resp, **kwargs):
        self.handle_request(req, resp)

    def on_head(self, req, resp, **kwargs):
        self.handle_request(req, resp)

    def handle_request(self, req, resp):
        print("{}:{}", req.method, req.url)

        method = req.method.lower()
        if method in self.handlers:
            (code, msg) = self.handlers[method]()
            resp.status = code
            resp.text = msg
        else:
            resp.status = falcon.HTTP_501
            resp.text = 'Not Implemented'
