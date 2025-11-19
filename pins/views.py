from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Pin, Comment
from .forms import PinCreateForm, PinUpdateForm


def pin_list(request):
    """List all pins"""
    pins = Pin.objects.all()
    
    # Filter premium-only pins for non-premium users
    if not request.user.is_authenticated or not request.user.is_premium:
        pins = pins.filter(is_premium_only=False)
    
    return render(request, 'pins/list.html', {'pins': pins})


@login_required
def pin_create(request):
    """Create a new pin"""
    if request.method == 'POST':
        form = PinCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            pin = form.save(commit=False)
            pin.user = request.user
            pin.save()
            messages.success(request, 'Pin created successfully!')
            return redirect('pins:detail', pk=pin.pk)
    else:
        form = PinCreateForm(user=request.user)
    
    return render(request, 'pins/create.html', {'form': form})


def pin_detail(request, pk):
    """Pin detail view with related pins and comments"""
    pin = get_object_or_404(Pin, pk=pk)
    
    # Check if user can view premium content
    if pin.is_premium_only:
        if not request.user.is_authenticated or not request.user.is_premium:
            messages.warning(request, 'This is a premium-only pin. Upgrade to view!')
            return redirect('payments:premium')
    
    # Get comments (only top-level comments, replies are fetched separately)
    comments = pin.comments.filter(parent__isnull=True).select_related('user').prefetch_related('replies', 'likes')
    
    # Get related pins based on tags or same board
    related_pins = Pin.objects.exclude(pk=pk)
    
    # Filter premium-only pins for non-premium users
    if not request.user.is_authenticated or not request.user.is_premium:
        related_pins = related_pins.filter(is_premium_only=False)
    
    # Try to find pins with similar tags
    if pin.tags:
        pin_tags = pin.get_tags_list()
        related_by_tags = []
        for p in related_pins:
            p_tags = p.get_tags_list()
            if any(tag in p_tags for tag in pin_tags):
                related_by_tags.append(p)
        if related_by_tags:
            related_pins = related_by_tags[:12]
        else:
            related_pins = related_pins[:12]
    elif pin.board:
        # Get pins from same board
        related_pins = pin.board.pins.exclude(pk=pk)[:12]
    else:
        # Get random recent pins
        related_pins = related_pins[:12]
    
    return render(request, 'pins/detail.html', {
        'pin': pin,
        'comments': comments,
        'related_pins': related_pins
    })


@login_required
def pin_edit(request, pk):
    """Edit pin"""
    pin = get_object_or_404(Pin, pk=pk)
    
    # Check if user owns the pin
    if pin.user != request.user:
        messages.error(request, 'You can only edit your own pins!')
        return redirect('pins:detail', pk=pk)
    
    if request.method == 'POST':
        form = PinUpdateForm(request.POST, instance=pin, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pin updated successfully!')
            return redirect('pins:detail', pk=pk)
    else:
        form = PinUpdateForm(instance=pin, user=request.user)
    
    return render(request, 'pins/edit.html', {'form': form, 'pin': pin})


@login_required
def pin_delete(request, pk):
    """Delete pin"""
    pin = get_object_or_404(Pin, pk=pk)
    
    # Check if user owns the pin
    if pin.user != request.user:
        messages.error(request, 'You can only delete your own pins!')
        return redirect('pins:detail', pk=pk)
    
    if request.method == 'POST':
        pin.delete()
        messages.success(request, 'Pin deleted successfully!')
        return redirect('core:home')
    
    return render(request, 'pins/delete_confirm.html', {'pin': pin})


@login_required
def pin_like(request, pk):
    """Like/unlike a pin"""
    from notifications.models import Notification
    from notifications.utils import send_notification_to_user
    
    pin = get_object_or_404(Pin, pk=pk)
    
    if request.user in pin.likes.all():
        pin.likes.remove(request.user)
        liked = False
        # Delete notification if exists
        Notification.objects.filter(
            recipient=pin.user,
            sender=request.user,
            notification_type='like',
            link=f'/pins/{pin.pk}/'
        ).delete()
    else:
        pin.likes.add(request.user)
        liked = True
        # Create notification for pin owner (if not liking own pin)
        if request.user != pin.user:
            notification = Notification.objects.create(
                recipient=pin.user,
                sender=request.user,
                notification_type='like',
                message=f'{request.user.username} liked your pin "{pin.title}"',
                link=f'/pins/{pin.pk}/'
            )
            # Send real-time notification via WebSocket
            send_notification_to_user(pin.user, notification)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': pin.like_count
        })
    
    return redirect('pins:detail', pk=pk)


@login_required
def save_to_board(request, pin_pk, board_pk):
    """Save a pin to a board"""
    from boards.models import Board
    from notifications.models import Notification
    from notifications.utils import send_notification_to_user
    
    pin = get_object_or_404(Pin, pk=pin_pk)
    board = get_object_or_404(Board, pk=board_pk, user=request.user)
    
    # Check if pin already in this board
    if pin.board and pin.board.pk == board.pk:
        return JsonResponse({
            'success': False,
            'error': f'This pin is already in "{board.title}"'
        })
    
    # Update pin's board
    pin.board = board
    pin.save()
    
    # Create notification for pin owner (if not saving own pin)
    if request.user != pin.user:
        notification = Notification.objects.create(
            recipient=pin.user,
            sender=request.user,
            notification_type='save',
            message=f'{request.user.username} saved your pin "{pin.title}" to "{board.title}"',
            link=f'/pins/{pin.pk}/'
        )
        # Send real-time notification via WebSocket
        send_notification_to_user(pin.user, notification)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'Saved to {board.title}'
        })
    
    messages.success(request, f'Pin saved to {board.title}')
    return redirect('pins:detail', pk=pin_pk)


@login_required
def report_pin(request, pk):
    """Report a pin"""
    pin = get_object_or_404(Pin, pk=pk)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # In a real app, you would create a Report model and save the report
        # For now, just return success
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your report. We will review this pin.'
        })
    
    messages.success(request, 'Thank you for your report. We will review this pin.')
    return redirect('pins:detail', pk=pk)


@login_required
def add_comment(request, pk):
    """Add a comment to a pin"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
    pin = get_object_or_404(Pin, pk=pk)
    text = request.POST.get('text', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not text:
        return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
    
    if len(text) > 1000:
        return JsonResponse({'success': False, 'error': 'Comment is too long (max 1000 characters)'}, status=400)
    
    # Create the comment
    comment = Comment.objects.create(
        pin=pin,
        user=request.user,
        text=text,
        parent_id=parent_id if parent_id else None
    )
    
    # Create notification for pin owner (if not commenting on own pin)
    if pin.user != request.user:
        from notifications.models import Notification
        Notification.objects.create(
            recipient=pin.user,
            sender=request.user,
            notification_type='comment',
            message=f'{request.user.username} commented on your pin: "{text[:50]}..."',
            link=f'/pins/{pin.id}/'
        )
    
    # If replying to a comment, notify the parent comment author
    if parent_id:
        parent_comment = Comment.objects.filter(id=parent_id).first()
        if parent_comment and parent_comment.user != request.user:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=parent_comment.user,
                sender=request.user,
                notification_type='comment',
                message=f'{request.user.username} replied to your comment: "{text[:50]}..."',
                link=f'/pins/{pin.id}/'
            )
    
    # Return comment data
    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'text': comment.text,
            'user': {
                'username': comment.user.username,
                'profile_picture': comment.user.profile_picture.url if comment.user.profile_picture else None,
            },
            'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'like_count': 0,
            'reply_count': 0,
            'is_liked': False,
        }
    })


@login_required
def delete_comment(request, pk, comment_id):
    """Delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id, pin_id=pk)
    
    # Only the comment author can delete it
    if comment.user != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    comment.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Comment deleted successfully'
    })


@login_required
def like_comment(request, pk, comment_id):
    """Like or unlike a comment"""
    comment = get_object_or_404(Comment, id=comment_id, pin_id=pk)
    
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        is_liked = False
    else:
        comment.likes.add(request.user)
        is_liked = True
        
        # Create notification for comment author
        if comment.user != request.user:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=comment.user,
                sender=request.user,
                notification_type='like',
                pin=comment.pin,
                text=f'{request.user.username} liked your comment'
            )
    
    return JsonResponse({
        'success': True,
        'is_liked': is_liked,
        'like_count': comment.like_count
    })
