# coding: utf-8
from inftybot import config


def prepare_comment(comment):
    comment = comment.strip()
    if comment.startswith('.:'):
        # language provided, bypass
        return comment
    return ".:{langcode}\n{comment}".format(langcode=config.DEFAULT_LANGUAGE, comment=comment)
