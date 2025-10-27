from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Board
from .forms import BoardCreateForm, BoardUpdateForm


def board_list(request):
    """List all boards"""
    if request.user.is_authenticated:
        boards = Board.objects.filter(user=request.user) | Board.objects.filter(is_private=False)
        boards = boards.distinct()
    else:
        boards = Board.objects.filter(is_private=False)
    
    return render(request, 'boards/list.html', {'boards': boards})


@login_required
def board_create(request):
    """Create a new board"""
    if request.method == 'POST':
        form = BoardCreateForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.user = request.user
            board.save()
            messages.success(request, 'Board created successfully!')
            return redirect('boards:detail', pk=board.pk)
    else:
        form = BoardCreateForm()
    
    return render(request, 'boards/create.html', {'form': form})


def board_detail(request, pk):
    """Board detail view (placeholder)"""
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'boards/detail.html', {'board': board})


@login_required
def board_edit(request, pk):
    """Edit board"""
    board = get_object_or_404(Board, pk=pk)
    
    # Check if user owns the board
    if board.user != request.user:
        messages.error(request, 'You can only edit your own boards!')
        return redirect('boards:detail', pk=pk)
    
    if request.method == 'POST':
        form = BoardUpdateForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, 'Board updated successfully!')
            return redirect('boards:detail', pk=pk)
    else:
        form = BoardUpdateForm(instance=board)
    
    return render(request, 'boards/edit.html', {'form': form, 'board': board})


@login_required
def board_delete(request, pk):
    """Delete board"""
    board = get_object_or_404(Board, pk=pk)
    
    # Check if user owns the board
    if board.user != request.user:
        messages.error(request, 'You can only delete your own boards!')
        return redirect('boards:detail', pk=pk)
    
    if request.method == 'POST':
        board.delete()
        messages.success(request, 'Board deleted successfully!')
        return redirect('core:home')
    
    return render(request, 'boards/delete_confirm.html', {'board': board})
