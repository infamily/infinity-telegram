# coding: utf-8
from slumber.exceptions import HttpClientError

from inftybot.models import from_native


class APIResponsePaginator(object):
    """
    Paginates results list from the API
    Every fetch() call will retrieve portion of a data regarding get_current_page()
    """
    model = None
    api = None

    def __init__(self, **kwargs):
        super(APIResponsePaginator, self).__init__()
        self.iterable = []
        self.next_page_url = None
        self.prev_page_url = None

    @property
    def has_next_page(self):
        return bool(self.next_page_url)

    @property
    def has_prev_page(self):
        return bool(self.prev_page_url)

    @property
    def current_page(self):
        raise NotImplementedError

    @current_page.setter
    def current_page(self, value):
        raise NotImplementedError

    def get_next_page(self):
        return self.next_page_url.split('page')[-1] if self.next_page_url else None

    def get_prev_page(self):
        return self.prev_page_url.split('page')[-1] if self.prev_page_url else None

    def get_extra_params(self):
        return {}

    def fetch(self):
        params = {'page': self.current_page}
        params.update(self.get_extra_params())

        resource = getattr(self.api.client, self.model.Meta.plural)

        try:
            response = resource.get(**params)
        except HttpClientError:
            return []

        if isinstance(response, dict):
            object_list = response['results']

            if response['next']:
                self.next_page_url = response['next']
            else:
                self.next_page_url = None

            if response['previous']:
                self.prev_page_url = response['previous']
            else:
                self.prev_page_url = None
        else:
            object_list = response[0:10]  # todo remove slicing

        return [from_native(self.model, data) for data in object_list]
