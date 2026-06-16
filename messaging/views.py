from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from messaging import services, selectors
from messaging.forms import MessageForm
import json

@login_required
@require_http_methods(["GET"])
def inbox_view(request):
    conversations = selectors.get_conversations_by_user(user=request.user)
    return render(request, 'messaging/inbox.html', {'conversations': conversations})

@login_required
@require_http_methods(["GET"])
def conversation_view(request, conversation_id):
    try:
        conversation = selectors.get_conversation_by_id(conversation_id=conversation_id)
        if request.user not in [conversation.buyer, conversation.seller]:
            messages.error(request, 'Bu konuşmayı görüntüleme yetkiniz yok.')
            return redirect('messaging:inbox')
            
        messages_list = selectors.get_messages_by_conversation(conversation=conversation)
        services.mark_messages_as_read(user=request.user, conversation_id=conversation_id)
        
        form = MessageForm()
        return render(request, 'messaging/conversation.html', {
            'conversation': conversation, 
            'messages': messages_list,
            'form': form
        })
    except Exception:
        messages.error(request, 'Konuşma bulunamadı.')
        return redirect('messaging:inbox')

@login_required
@require_http_methods(["POST"])
def start_conversation_view(request, listing_id):
    try:
        conversation = services.get_or_create_conversation(buyer=request.user, listing_id=listing_id)
        return redirect('messaging:conversation', conversation_id=conversation.id)
    except (PermissionError, ValueError) as e:
        messages.error(request, str(e))
        referer = request.META.get('HTTP_REFERER', '/')
        return redirect(referer)

@login_required
@require_http_methods(["POST"])
def send_message_view(request, conversation_id):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST.dict()

    form = MessageForm(data)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
        
    try:
        message = services.send_message(
            sender=request.user,
            conversation_id=conversation_id,
            body=form.cleaned_data['body']
        )
        return JsonResponse({
            'message_id': message.id,
            'body': message.body,
            'sender': message.sender.email,
            'created_at': message.created_at.isoformat(),
        })
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def delete_message_view(request, message_id):
    try:
        services.delete_message(user=request.user, message_id=message_id)
        return JsonResponse({'message': 'Mesaj silindi.'})
    except (PermissionError, ValueError) as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["POST"])
def close_conversation_view(request, conversation_id):
    try:
        services.close_conversation(user=request.user, conversation_id=conversation_id)
        messages.success(request, 'Konuşma başarıyla kapatıldı.')
    except PermissionError as e:
        messages.error(request, str(e))
    return redirect('messaging:inbox')
