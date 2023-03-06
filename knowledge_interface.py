import requests

import settings


class ApiKnowledge:
    def __init__(self):
        self.url = f'{settings.URL_KNOWLEDGE}/api/v1/note/'

    def note_search(self, query, search_by='all', operator='or', limit=10, offset=0, fields='title', source=None):
        params = {
            'search-by': search_by,
            'operator': operator,
            'limit': limit,
            'offset': offset,
            'fields': fields,
        }
        if source:
            params['source'] = source

        response = requests.get(f'{self.url}/search/{query}/', params=params)
        return response.json()