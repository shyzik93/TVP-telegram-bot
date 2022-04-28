from urllib.parse import quote

from django.conf import settings
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
import requests


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


def build_message_body(result_data, numeration_from=1):
    links = []
    github_url = result_data['path']
    results = result_data['results']
    for index, result in enumerate(results, numeration_from):
        title = result['title']
        quoted_title = quote(title)
        links.append(f'{index}. [{title}]({github_url}db/{quoted_title}.md)')

    links = '\n'.join(links)
    count = result_data['count']
    return f'Найдено результатов: {count}\n\n{links}'


def build_paginator_params(count_objects, limit, offset, results_message_id):
    page_count = count_objects // limit + (1 if count_objects % limit > 0 else 0)
    page_num = offset // limit + 1
    btn_count_pages = {
        'text': f'{page_num}/{page_count}',
        'callback_data': 'none',
    }

    btn_prev = {
        'text': '<< prev' if page_num > 1 else ' ',
        'callback_data': f'{offset - limit} {results_message_id}' if page_num > 1 else 'none',
    }

    btn_next = {
        'text': 'next >>' if page_num < page_count else ' ',
        'callback_data': f'{offset + limit} {results_message_id}' if page_num < page_count else 'none',
    }

    return {
        'inline_keyboard': [[btn_prev, btn_count_pages, btn_next]]
    }


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def telegram_hook(request, token):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}'

    message = request.data.get('message')
    if message:
        chat_from = message.get('chat')
        message_text = message.get('text')
        message_id = message.get('message_id')

        if message_text:# and message_text.startswith('.s '):
            #_, query = message_text.split(None, 1)
            query = message_text

            api_knowledge = ApiKnowledge()
            result_data = api_knowledge.note_search(query)

            limit = 10
            offset = 0
            reply_markup = build_paginator_params(result_data['count'], limit, offset, message_id)
            params = {
                'chat_id': chat_from['id'],
                'text': build_message_body(result_data),
                'reply_to_message_id': message_id,
                'disable_web_page_preview': True,
                'parse_mode': 'Markdown',
                'reply_markup': reply_markup,
            }
            requests.post(f'{url}/sendMessage', json=params)

    callback_query = request.data.get('callback_query')
    if callback_query:
        results_message = callback_query['message']
        results_message_id = results_message['message_id']
        if callback_query['data'] == 'none':
            return Response(status=status.HTTP_200_OK, data={})

        offset, query_message_id = callback_query['data'].split()
        offset = int(offset)

        query = results_message['reply_to_message']['text']
        api_knowledge = ApiKnowledge()
        result_data = api_knowledge.note_search(query, offset=int(offset))

        limit = 10
        reply_markup = build_paginator_params(result_data['count'], limit, offset, results_message_id)
        params = {
            'chat_id': results_message.get('chat').get('id'),
            'message_id': results_message.get('message_id'),
            'text': build_message_body(result_data, offset+1),
            'disable_web_page_preview': True,
            'parse_mode': 'Markdown',
            'reply_markup': reply_markup,
        }
        requests.post(f'{url}/editMessageText', json=params)

    return Response(status=status.HTTP_200_OK, data={})
