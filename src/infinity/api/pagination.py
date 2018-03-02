# coding: utf-8
from slumber.exceptions import HttpClientError

from infinity.api.utils import get_model_resource
from inftybot.core.models import from_native


class APIResponsePaginator(object):
    """
    Paginates results list from the API
    Every fetch() call will retrieve portion of a data regarding ```get_current_page()```

    API calls will use ```api``` high-level API wrapper (see ```inftybot.api.base.API``` class)
    API endpoint will be determined regarding ```model```'s Meta property: ```plural```

    Every item in paginated result (list) will be instantiated with ```model``` cls using ```from_native``` method
    (see ```inftybot.models.from_native()```)
    """
    model = None
    api = None

    def __init__(self, **kwargs):
        super(APIResponsePaginator, self).__init__()
        self.iterable = []
        self.next_page_url = None
        self.prev_page_url = None

    @property
    def has_prev_page(self):
        return bool(self.prev_page_url)

    @property
    def has_next_page(self):
        return bool(self.next_page_url)

    def get_current_page(self):
        raise NotImplementedError

    def get_extra_params(self):
        return {}

    def fetch(self):
        """Fetch portion of the data (current page) from the API"""
        params = {'page': self.get_current_page()}
        params.update(self.get_extra_params())

        resource = get_model_resource(self.api, self.model)

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
