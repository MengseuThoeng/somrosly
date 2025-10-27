from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from .models import Friendship, ChatRoom, Message
from users.models import User
from notifications.models import Notification
from notifications.utils import send_notification_to_user


@login_required
def friends_list(request):
    """List all friends and pending requests"""
    friends = Friendship.get_friends(request.user)
    
    # Pending requests received
    pending_requests = Friendship.objects.filter(
        to_user=request.user,
        status='pending'
    )
    
    # Pending requests sent
    sent_requests = Friendship.objects.filter(
        from_user=request.user,
        status='pending'
    )
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    
    # Get all users except current user and existing relationships
    friend_ids = Friendship.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    ).values_list('from_user_id', 'to_user_id')
    
    excluded_ids = set([request.user.id])
    for from_id, to_id in friend_ids:
        excluded_ids.add(from_id)
        excluded_ids.add(to_id)
    
    # Suggested friends with search
    suggested_friends = User.objects.exclude(id__in=excluded_ids)
    
    if search_query:
        suggested_friends = suggested_friends.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(full_name__icontains=search_query)
        )
    
    suggested_friends = suggested_friends[:20]  # Show more results
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'suggested_friends': suggested_friends,
        'search_query': search_query,
    }
    
    return render(request, 'chat/friends_list.html', context)


@login_required
def send_friend_request(request, username):
    """Send a friend request"""
    to_user = get_object_or_404(User, username=username)
    
    if to_user == request.user:
        messages.error(request, "You can't send a friend request to yourself!")
        return redirect('chat:friends_list')
    
    # Check if already friends or request exists
    existing = Friendship.objects.filter(
        Q(from_user=request.user, to_user=to_user) |
        Q(from_user=to_user, to_user=request.user)
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            messages.info(request, f"You are already friends with {to_user.username}")
        elif existing.status == 'pending':
            messages.info(request, "Friend request already sent")
        return redirect('chat:friends_list')
    
    # Create friend request
    friendship = Friendship.objects.create(
        from_user=request.user,
        to_user=to_user,
        status='pending'
    )
    
    # Create notification
    notification = Notification.objects.create(
        recipient=to_user,
        sender=request.user,
        notification_type='follow',
        message=f'{request.user.username} sent you a friend request',
        link=f'/chat/friends/'
    )
    send_notification_to_user(to_user, notification)
    
    messages.success(request, f"Friend request sent to {to_user.username}!")
    return redirect('chat:friends_list')


@login_required
def accept_friend_request(request, request_id):
    """Accept a friend request"""
    friendship = get_object_or_404(Friendship, id=request_id, to_user=request.user)
    
    friendship.status = 'accepted'
    friendship.save()
    
    # Create notification
    notification = Notification.objects.create(
        recipient=friendship.from_user,
        sender=request.user,
        notification_type='follow',
        message=f'{request.user.username} accepted your friend request',
        link=f'/chat/friends/'
    )
    send_notification_to_user(friendship.from_user, notification)
    
    messages.success(request, f"You are now friends with {friendship.from_user.username}!")
    return redirect('chat:friends_list')


@login_required
def reject_friend_request(request, request_id):
    """Reject a friend request"""
    friendship = get_object_or_404(Friendship, id=request_id, to_user=request.user)
    friendship.status = 'rejected'
    friendship.save()
    
    messages.info(request, "Friend request rejected")
    return redirect('chat:friends_list')


@login_required
def remove_friend(request, username):
    """Remove a friend"""
    friend = get_object_or_404(User, username=username)
    
    Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend) |
        Q(from_user=friend, to_user=request.user)
    ).delete()
    
    messages.success(request, f"Removed {friend.username} from friends")
    return redirect('chat:friends_list')


@login_required
def chat_list(request):
    """List all chat rooms"""
    from types import SimpleNamespace
    
    rooms = request.user.chat_rooms.annotate(
        last_message_time=Max('messages__created_at'),
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
    ).order_by('-last_message_time')
    
    # Add other_user to each room
    chat_rooms = []
    for room in rooms:
        participants = room.participants.exclude(id=request.user.id)
        if participants.exists():
            # Create a namespace object to hold room data
            room_data = SimpleNamespace(
                id=room.id,
                other_user=participants.first(),
                last_message=room.last_message,  # Using the property
                unread_count=room.unread_count,
                updated_at=room.updated_at,
            )
            chat_rooms.append(room_data)
    
    context = {
        'chat_rooms': chat_rooms,
    }
    
    return render(request, 'chat/chat_list.html', context)


@login_required
def chat_room(request, username):
    """Chat room with a specific user"""
    other_user = get_object_or_404(User, username=username)
    
    # Check if friends
    if not Friendship.are_friends(request.user, other_user):
        messages.error(request, "You can only chat with friends!")
        return redirect('chat:friends_list')
    
    # Get or create chat room
    room = ChatRoom.get_or_create_room(request.user, other_user)
    
    # Mark messages as read
    room.messages.filter(sender=other_user, is_read=False).update(is_read=True)
    
    # Get messages
    chat_messages = room.messages.all()[:50][::-1]  # Last 50 messages, reversed
    
    context = {
        'room': room,
        'other_user': other_user,
        'messages': chat_messages,
    }
    
    return render(request, 'chat/chat_room.html', context)


@login_required
def send_message(request, room_id):
    """Send a message via AJAX"""
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
        content = request.POST.get('content', '').strip()
        
        if content:
            message = Message.objects.create(
                room=room,
                sender=request.user,
                content=content
            )
            
            # Update room timestamp
            room.save()
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'created_at': message.created_at.strftime('%H:%M')
                }
            })
        
        return JsonResponse({'success': False, 'error': 'Empty message'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def get_friends_api(request):
    """API endpoint to get friends list for sharing"""
    friends = Friendship.get_friends(request.user)
    friends_data = []
    
    for friend in friends:
        friends_data.append({
            'username': friend.username,
            'full_name': friend.full_name if hasattr(friend, 'full_name') else '',
            'profile_image': friend.profile_picture.url if hasattr(friend, 'profile_picture') and friend.profile_picture else None
        })
    
    return JsonResponse({'friends': friends_data})


@login_required
def share_pin_api(request):
    """API endpoint to share a pin with a friend via message"""
    if request.method == 'POST':
        import json
        from pins.models import Pin
        
        data = json.loads(request.body)
        username = data.get('username')
        pin_id = data.get('pin_id')
        message_text = data.get('message')
        
        try:
            friend = User.objects.get(username=username)
            pin = Pin.objects.get(id=pin_id)
            
            # Check if friends
            if not Friendship.are_friends(request.user, friend):
                return JsonResponse({'success': False, 'error': 'Not friends'})
            
            # Get or create chat room
            room = ChatRoom.get_or_create_room(request.user, friend)
            
            # Send message
            Message.objects.create(
                room=room,
                sender=request.user,
                content=message_text
            )
            
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Pin.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pin not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def get_unread_count(request):
    """Get total unread message count"""
    # Get all rooms where user is participant
    user_rooms = ChatRoom.objects.filter(participants=request.user)
    
    # Count unread messages from others
    unread_count = Message.objects.filter(
        room__in=user_rooms,
        is_read=False
    ).exclude(sender=request.user).count()
    
    return JsonResponse({'unread_count': unread_count})
