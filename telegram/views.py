import os

from django.conf import settings
from django.utils.encoding import uri_to_iri
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
import requests

from note.load_from_github import prepare_to_search, get_root_url, search
from note.credentials import args_uploader
from note.models import Note


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def telegram_hook(request, token):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}'

    message = request.data.get('message')
    if message:
        user_from = message.get('from')
        chat_from = message.get('chat')
        reply_to_message = message.get('reply_to_message')
        message_text = message.get('text')

        if message_text:# and message_text.startswith('.s '):
            #_, query = message_text.split(None, 1)
            query = message_text

            operator = 'or'
            limit = 10
            offset = 0
            fields = 'title'
            search_by = 'all'
            file_name = query if search_by in ('title', 'all') else None
            file_content = query if search_by in ('content', 'all') else None
            fields = ('title', 'content') if fields == 'all' else (fields,)
            uploader = settings.DEFAULT_UPLOADER
            result_data = search(
                uploader,
                args_uploader[uploader],
                operator=operator,
                limit=limit,
                offset=offset,
                fields=fields,
                file_name=file_name,
                file_content=file_content,
            )

            links = []
            github_url = result_data['path']
            for index, result in enumerate(result_data['results'], 1):
                title = result['title']
                links.append(f'{index}. [{title}]({github_url}{title}.md)')

            btn_prev = {
                'text': '< prev',
                'callback_data': '{offset-limit}',
            }
            btn_next = {
                'text': 'next >',
                'callback_data': '{offset+limit}',
            }

            #page_count = result_data['count'] // limit + (1 if result_data['count'] % limit > 0 else 0)
            #page_num = offset // limit
            #btn_count_pages = {
            #    'text': '{page_num}/{page_count}',
            #    'callback_data': 'none',
            #}

            reply_markup = {
                'inline_keyboard': [[btn_prev, btn_next], [btn_prev, btn_next]]
            }

            params = {
                'chat_id': chat_from['id'],
                'text': '\n'.join(links),
                'reply_to_message_id': message['message_id'],
                'disable_web_page_preview': True,
                'parse_mode': 'Markdown',
                #'reply_markup': reply_markup,
            }
            res = requests.get(f'{url}/sendMessage', params=params)
            res = res.json()

    return Response(status=status.HTTP_200_OK, data={})
