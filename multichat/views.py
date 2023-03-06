from django.conf import settings
from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import status
import requests


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
            reply_markup = build_paginator_params(result_data['count'], limit, offset)
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
        if callback_query['data'] == 'none':
            return Response(status=status.HTTP_200_OK, data={})

        results_message = callback_query['message']
        offset = int(callback_query['data'])

        query = results_message['reply_to_message']['text']
        api_knowledge = ApiKnowledge()
        result_data = api_knowledge.note_search(query, offset=int(offset))

        limit = 10
        reply_markup = build_paginator_params(result_data['count'], limit, offset)
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


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def discord_hook(request, token):
    return Response(status=status.HTTP_200_OK, data={})


class IndexView(APIView):
    def get(self, request):
        context = {
        }
        return render(request, 'multichat/index.html', context)

    def post(self, request):
        ...

