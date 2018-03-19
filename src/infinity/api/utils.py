# coding: utf-8


def get_model_resource(api, model):
    meta = getattr(model, '_meta')
    plural = meta.verbose_name_plural.lower()
    return getattr(api.client, plural)
