from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import UserRegister,Post,Likes,Comments,Messages,Follow,Notification
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.timesince import timesince


def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        re_enter_password = request.POST['re_enter_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        gender = request.POST['gender']
        date_of_birth = request.POST['date_of_birth']
        profile_picture = request.FILES.get('profile_picture')
        bio = request.POST['bio']
        location = request.POST['location']
        website = request.POST['website']

        if password != re_enter_password:
            messages.error(request, 'Passwords do not match')
            return redirect('user_register')

        if UserRegister.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('user_register')

        if UserRegister.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('user_register')
        if UserRegister.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already exists')
            return redirect('user_register')

        user_profile=UserRegister.objects.create(
            username=username,
            email=email,
            phone_number=phone_number,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            date_of_birth=date_of_birth,
            profile_picture=profile_picture,
            bio=bio,
            location=location,
            website=website,
        )
        user_profile.save()
        messages.success(request, 'User created successfully')
        return redirect('user_login')

    return render(request, 'users/user_register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user_profile = UserRegister.objects.get(email=email)
            if check_password(password,user_profile.password):
                request.session['user_id'] = user_profile.user_id
                request.session['user_name'] = user_profile.username
                messages.success(request, f'Welcome  {user_profile.username}')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid password or email')
                return redirect('user_login')
        except UserRegister.DoesNotExist:
            messages.error(request, 'Username does not exist')
            return redirect('user_login')
    return render(request, 'users/user_login.html')

def user_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')


    user_profile = get_object_or_404(UserRegister, user_id=user_id)

    posts = Post.objects.all().order_by('-created_at')

    # add "has_liked" flag for each post
    for post in posts:
        post.has_liked = Likes.objects.filter(post=post, user=user_profile).exists()
        post.comment_list = Comments.objects.filter(post=post).order_by('-created_at')
    return render(request, 'users/user_dashboard.html', {
        "user_profile": user_profile,
        "posts": posts
    })


def create_post(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user_login')
        user = get_object_or_404(UserRegister, user_id=user_id)

        content = request.POST.get('content')
        media = request.FILES.get('media')

        Post.objects.create(user=user, content=content, media=media)
        messages.success(request, 'Post created successfully')
        return redirect('user_dashboard')

    return render(request, 'users/create_post.html')

def like_post(request,post_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(UserRegister, user_id=user_id)

    like, created =Likes.objects.get_or_create(post=post, user=user)
    if not created:
        like.delete()
    else:
        if post.user != user:
            Notification.objects.create(
                user=post.user,  # owner of the post
                actor=user,  # the liker
                type="like",
                reference_id=post.id,
                status=False
            )
    return redirect('user_dashboard')

def add_comment(request,post_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')  # user not logged in

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        text = request.POST.get("comment_text")
        if text:
            user = get_object_or_404(UserRegister, user_id=user_id)
            Comments.objects.create(
                post=post,
                user=user,  # ✅ link to your UserRegister
                comment_text=text
            )
            if post.user != user:
                Notification.objects.create(
                    user=post.user,  # post owner
                    actor=user,  # commenter
                    type="comment",
                    reference_id=post.id,
                    status=False
                )
    return redirect("user_dashboard")

def user_logout(request):
    request.session.clear()
    return redirect('user_login')

def inbox(request):
    # Get current user from session
    current_user_id = request.session.get('user_id')
    if not current_user_id:
        return redirect('user_login')  # use your login view

    current_user = get_object_or_404(UserRegister, user_id=current_user_id)

    # Handle sending a new message
    if request.method == "POST":
        receiver_id = request.POST.get("receiver")
        message_text = request.POST.get("message_text", "").strip()

        if not receiver_id:
            messages.error(request, "Please select a receiver.")
            return redirect("inbox")

        receiver = get_object_or_404(UserRegister, user_id=receiver_id)

        if message_text:
            Messages.objects.create(
                sender=current_user,
                receiver=receiver,
                message_text=message_text
            )
            messages.success(request, "Message sent successfully!")
        else:
            messages.error(request, "Message cannot be empty.")

        return redirect("inbox")

    # GET request → show inbox page
    inbox_messages = Messages.objects.filter(receiver=current_user).order_by("-created_at")
    sent_messages = Messages.objects.filter(sender=current_user).order_by("-created_at")
    users = UserRegister.objects.exclude(user_id=current_user.user_id)

    return render(request, "users/inbox.html", {
        "inbox_messages": inbox_messages,
        "sent_messages": sent_messages,
        "users": users
    })


def sent_messages(request):
    current_user_id = request.session.get('user_id')
    if not current_user_id:
        return redirect('user_login')

    current_user = get_object_or_404(UserRegister, user_id=current_user_id)
    sent = Messages.objects.filter(sender=current_user).order_by("-created_at")

    return render(request, "users/sent_messages.html", {"messages": sent})


def send_message(request, user_id):
    sender_id = request.session.get('user_id')
    if not sender_id:
        return redirect('user_login')

    sender = get_object_or_404(UserRegister, user_id=sender_id)
    receiver = get_object_or_404(UserRegister, user_id=user_id)

    if request.method == "POST":
        msg = request.POST.get('message_text')
        if msg.strip():
            Messages.objects.create(sender=sender, receiver=receiver, message_text=msg)
        return redirect("inbox")
    Notification.objects.create(
        user=receiver,  # who receives the message
        actor=sender,  # who sent it
        type="message",
        reference_id=receiver.user_id,
        status=False
    )

    return render(request, 'users/send_message.html', {"receiver": receiver})

def conversation(request, user_id):
    current_user_id = request.session.get('user_id')
    if not current_user_id:
        return redirect('user_login')

    current_user = get_object_or_404(UserRegister, user_id=current_user_id)
    other_user = get_object_or_404(UserRegister, user_id=user_id)

    if request.method == "POST":
        msg = request.POST.get('message_text')
        if msg.strip():
            Messages.objects.create(sender=current_user, receiver=other_user, message_text=msg)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('conversation', user_id=other_user.user_id)

    # AJAX GET request for live updates
    if request.GET.get('ajax') == '1':
        chat = Messages.objects.filter(
            Q(sender=current_user, receiver=other_user) |
            Q(sender=other_user, receiver=current_user)
        ).order_by('created_at')
        chat_data = [
            {'sender_id': m.sender.user_id, 'text': m.message_text, 'time': m.created_at.strftime("%H:%M")}
            for m in chat
        ]
        return JsonResponse({'chat': chat_data})

    chat = Messages.objects.filter(
        Q(sender=current_user, receiver=other_user) |
        Q(sender=other_user, receiver=current_user)
    ).order_by('created_at')

    return render(request, 'users/conversation.html', {
        "chat": chat,
        "other_user": other_user,
        "current_user": current_user
    })



def search_users(request):
    query = request.GET.get('q', '')  # Get the search query from URL parameter
    results = []

    if query:
        results = UserRegister.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    return render(request, "users/search_results.html", {
        "results": results,
        "query": query
    })


def view_profile(request, user_id):
    profile_user = get_object_or_404(UserRegister, user_id=user_id)

    logged_in_user_id = request.session.get('user_id')
    logged_in_user = None
    if logged_in_user_id:
        logged_in_user = get_object_or_404(UserRegister, user_id=logged_in_user_id)

    # Check if logged-in user is following this profile
    is_following = False
    if logged_in_user:
        is_following = Follow.objects.filter(follower=logged_in_user, following=profile_user).exists()

    # Get posts of this user
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')

    context = {
        "user_profile": profile_user,
        "posts": posts,                     # pass posts explicitly
        "is_following": is_following,
        "logged_in_user_id": logged_in_user,
    }
    return render(request, "users/profile.html", context)


def toggle_follow(request, user_id):
    user_profile = get_object_or_404(UserRegister, user_id=user_id)

    logged_in_user_id = request.session.get('user_id')
    if not logged_in_user_id:
        return redirect('user_login')

    logged_in_user = get_object_or_404(UserRegister, user_id=logged_in_user_id)

    follow_obj, created = Follow.objects.get_or_create(
        follower=logged_in_user,
        following=user_profile
    )
    if not created:
        # Already following → unfollow
        follow_obj.delete()
    else:
        if user_profile != logged_in_user:
            Notification.objects.create(
                user=user_profile,  # the one being followed
                actor=logged_in_user,  # the one who followed
                type="follow",
                status=False
            )

    return redirect("view_profile", user_id=user_id)


def following_list(request, user_id):
    user_profile = get_object_or_404(UserRegister, user_id=user_id)

    # All users this user is following
    following = UserRegister.objects.filter(follower_relations__follower=user_profile)

    return render(request, "users/following.html", {
        "user_profile": user_profile,
        "following": following,
    })


def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user_profile = get_object_or_404(UserRegister, user_id=user_id)

    if request.method == "POST":
        user_profile.username = request.POST.get('username')
        user_profile.email = request.POST.get('email')
        user_profile.bio = request.POST.get('bio',user_profile.bio)

        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']

        user_profile.save()
        return redirect('view_profile', user_id=user_profile.user_id)
    return render(request, 'users/edit_profile.html', {
        "user_profile": user_profile,
    })


def followers_list(request, user_id):
    user_profile = get_object_or_404(UserRegister, pk=user_id)

    # All users who follow this user
    followers = UserRegister.objects.filter(following_relations__following=user_profile)

    return render(request, "users/followers.html", {
        "user_profile": user_profile,
        "followers": followers,
    })

def notifications(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(UserRegister, user_id=user_id)
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    # Mark as read
    notifications.update(status=True)

    # Prepare for display
    for n in notifications:
        n.time_ago = timesince(n.created_at) + " ago"

    return render(request, "users/notifications.html", {"notifications": notifications})