from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import login_required
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your Password Has Been Updated.')
            return redirect('home-page')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'passwords/change_password.html', {'form': form})
