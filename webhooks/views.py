import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import Conversation, Message
from .serializer import ConversationSerializer, MessageSerializer
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from datetime import datetime

@csrf_exempt
@require_POST
def webhook_view(request):
    try:
        # Tenta carregar o JSON do corpo da requisição
        event = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'}, status=400)

    # Verifica se os campos básicos existem
    event_type = event.get("type")
    event_data = event.get("data")
    event_timestamp = event.get("timestamp")

    if not event_type or not event_data or not event_timestamp:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields: type, data, or timestamp.'}, status=400)

    # Converte timestamp
    try:
        event_datetime = datetime.fromisoformat(event_timestamp)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid timestamp format.'}, status=400)

    # Processamento dos eventos
    if event_type == "NEW_CONVERSATION":
        try:
            Conversation.objects.create(
                id=event_data["id"],
                state="OPEN",
                datetime=event_datetime
            )
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Conversation already exists.'}, status=422)
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {str(e)}'}, status=400)

    elif event_type == "NEW_MESSAGE":
        try:
            conversation = Conversation.objects.get(id=event_data["conversation_id"])
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Conversation not found.'}, status=404)
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {str(e)}'}, status=400)

        if conversation.state == "CLOSED":
            return JsonResponse({'status': 'error', 'message': 'Conversation closed. Not allowed to add new messages.'}, status=422)

        try:
            Message.objects.create(
                id=event_data["id"],
                datetime=event_datetime,
                conversation=conversation,
                direction=event_data["direction"],
                content=event_data["content"]
            )
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {str(e)}'}, status=400)

    elif event_type == "CLOSE_CONVERSATION":
        try:
            conversation = Conversation.objects.get(id=event_data["id"])
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Conversation not found.'}, status=404)
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {str(e)}'}, status=400)

        conversation.state = "CLOSED"
        conversation.datetime = event_datetime
        conversation.save()

    else:
        return JsonResponse({'status': 'error', 'message': 'Incorrect event type.'}, status=400)

    return JsonResponse({'status': 'success'})

class ConversationView(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().order_by('datetime')
    serializer_class = ConversationSerializer
    http_method_names = ['get']





class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conversations to be viewed or edited.
    """
    queryset = Conversation.objects.all().order_by('datetime')
    serializer_class = ConversationSerializer
    # permission_classes = [permissions.IsAuthenticated]
    
class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messagens to be viewed or edited.
    """
    queryset = Message.objects.all().order_by('datetime')
    serializer_class = MessageSerializer
    # permission_classes = [permissions.IsAuthenticated]