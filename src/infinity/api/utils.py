# coding: utf-8


def get_model_resource(api, model):
    return getattr(api.client, model.Meta.plural)
