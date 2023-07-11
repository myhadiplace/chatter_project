from .forms import TwitteForm, CreateUserForm, LoginUserForm, EditProfileForm, NewAvatarForm
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.http import Http404, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.shortcuts import render
from urllib.parse import urlparse
from django.conf import settings
from django.urls import reverse
from django.views import View
import os

# pymongo
from pymongo.errors import ConnectionFailure, OperationFailure
from pymongo import MongoClient, errors, TEXT
from bson.objectid import ObjectId
from bson.dbref import DBRef

cluster = "mongodb://hadi:54P9834jJ81946@localhost:27017/?authMechanism=DEFAULT&authSource=chatter"
client = MongoClient(cluster)
db = client.chatter

db.users.create_index([("name", TEXT), ("user_name", TEXT)],
                      default_language="english")
db.twittes.create_index([("text", TEXT)], default_language="english")


def handle_uploaded_file(f):
    path = os.path.join(settings.MEDIA_ROOT, 'avatar', str(f))
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def delete_file(path):
    # delete image from filesystem
    if os.path.isfile(path):
        os.remove(path)


def insert_document(collection, document):
    ''' insert post to twittes collection in mongodb '''
    try:
        db.twittes.insert_one(document)
        return True
    except errors.DuplicateKeyError as e:
        print("Document already exists: %s" % e)
        return False
    except errors.ConnectionFailure as e:
        print("Could not connect to server: %s" % e)
        return False
    except Exception as e:
        print("An unexpected error occurred: %s" % e)
        return False


def is_already_followed(username, username_for_follow_person):
    for_follow = db.users.find_one({"user_name": username_for_follow_person})
    return db.users.count_documents(
        {
            "user_name": username,
            "followings": {"$in": [DBRef("users", ObjectId(for_follow["_id"]))]},
        }
    )


def is_unique_username(user_input):
    if db.users.find_one({"user_name": user_input}) is None:
        return True
    return False


def update_post_num_field(username, amount):
    db.users.update_one({"user_name": username}, {"$inc": {"postNum": amount}})


def update_replys_num_field(postid):
    db.twittes.update_one({"_id": ObjectId(postid)},
                          {"$inc": {"replysNum": 1}})


def update_followings_number(username, quantity):
    db.users.update_one({"user_name": username}, {
                        "$inc": {"followingsNum": quantity}})


def update_followers_number(username, quantity):
    db.users.update_one({"user_name": username}, {
                        "$inc": {"followersNum": quantity}})


def find_user(username):
    return db.users.find_one({"user_name": username})


def find_user_twittes(user_doc):
    '''return all user twitte. argument must be user document'''
    return db.twittes.find({"user": DBRef("users", ObjectId(user_doc["_id"])), "type": "twitte"})


def increase_reply_num(twitte_id):
    db.twittes.update_one({"_id": ObjectId(twitte_id)},
                          {"$inc": {"replysNum": -1}})


def find_single_twitte(twitte_id):
    return db.twittes.find_one({"_id": ObjectId(twitte_id)})


def delete_twitte(twitte_id):
    db.twittes.delete_one({"_id": ObjectId(twitte_id)})


# class UpdateDatabase():
#     def __init__(self,collection_name):
#         self.collection_name = collection_name

#     def update_int_field(self,doc_id,filed_name,quantity):
#         db[self.collection_name].update_one({"_id":ObjectId(doc_id)},{"$inc":{filed_name:quantity}})

#     def delete(self,doc_id):
#         db[self.collection_name].delete_one({"_id": ObjectId(doc_id)})

#     def find_one_by_id(self,doc_id):
#         return db[self.collection_name].find_one({"_id": ObjectId(doc_id)})

#     def find_one_by_field(self,field_name,filed_value):
#         return db[self.collection_name].find_one({field_name: filed_value})


# twittes_db = UpdateDatabase("twittes")
# user_db = UpdateDatabase("users")


CONTENT_NUMBER = 3

class RenderPost(View):
    def get(self, request):
        content_number = request.session.get("all_contents")

        logged_user_username = request.session.get("username")
        logged_user = db.users.find_one({"user_name": logged_user_username})
        if logged_user_username:
            post_context = []
            followings_dbref = logged_user["followings"]
            for dbref in followings_dbref:
                try:
                    # find Nth twitte of user and create a template content
                    post = db.twittes.find({"user": dbref}).skip(
                        int(content_number/3)).limit(1)
                    template_content = render_to_string(
                        "chatter/include/post.html", {"post": post[0], 'logged_user': logged_user})

                except IndexError:
                    template_content = []
                    print('No document found')

                post_context.append(template_content)
            request.session["all_contents"] += 3
            return JsonResponse(post_context, safe=False)

        else:
            content_number = request.session.get('all_contents')
            # sort twittes by date and return 3 document and igronre document that already has returned
            posts = db.twittes.find({"type": "twitte"}).sort(
                "publishedAt", -1).skip(content_number).limit(3)
            request.session['all_contents'] += 3
            post_context = []
            for post in posts:

                template_content = render_to_string(
                    "chatter/include/post.html", {"post": post})
                post_context.append(template_content)

            return JsonResponse(post_context, safe=False)


class Home(View):
    def get(self, request):
        # set how many content in homepage must show up in first place
        request.session["all_contents"] = CONTENT_NUMBER

        logged_user_username = request.session.get("username")
        logged_user = find_user(logged_user_username)
        if logged_user_username:
            posts = []
            followings_dbref = logged_user["followings"]

            for dbref in followings_dbref:
                post = db.twittes.find({"user": dbref})[0]
                posts.append(post)

        else:
            posts = db.twittes.find({"type": "twitte"})[0:3]

        return render(
            request, "chatter/home.html", {"posts": posts,
                                           "logged_user": logged_user}
        )


def profile_page_index(request, username):
    logged_in_user = find_user(request.session.get("username"))
    try:
        user = find_user(username)
        if user == None:
            raise Http404
        user_twittes = find_user_twittes(user)

    except OperationFailure as error:
        raise error

    if logged_in_user:
        # check if logged user followed user or not
        followed = is_already_followed(logged_in_user["user_name"], username)
    else:
        followed = None

    return render(
        request,
        "chatter/single-page.html",
        {
            "user": user,
            "posts": user_twittes,
            "logged_user": logged_in_user,
            "followed": followed,
        },
    )


def post_twitte(request, username):
    # get essential data for sending to template
    session_username = request.session.get("username")
    logged_in_user = find_user(session_username)
    user = find_user(username)
    user_twittes = find_user_twittes(user)

    if request.method == "POST":
        form = TwitteForm(request.POST)
        if form.is_valid():
            update_post_num_field(username, 1)
            text = form.cleaned_data["text"]
            publishedAt = form.cleaned_data["publishedAt"]
            user_id = request.session.get("user_id")
            db.twittes.insert_one({'text': "somedummy text"})
            document = {
                "publishedAt": publishedAt,
                "text": text,
                "user": DBRef("users", ObjectId(user_id)),
                "user_info": {
                    "name": user["name"],
                    "user_name": user["user_name"],
                    "profile_img": user["profile_img"],
                },
                'type': 'twitte',
                        "replys": [],
                        "replysNum": 0,
                        "likeNum": 0,
                        "likedBy": [],
            }
            # inser twitte to the Database
            insert_document("twittes", document)

            redirect_path = reverse(
                "posttwitte", args=[request.session.get("username")])
            return HttpResponseRedirect(redirect_path)

    else:
        form = TwitteForm()
        # Checking whether the user has permission to access the tweet sending page or not
        if request.session.get("user_id") == str(user["_id"]):
            pass
        else:
            return HttpResponseForbidden("You are not authorized to access this page.")

    return render(request, 'chatter/post_twitte_page.html', {
        "form": form,
        "user": user,
        "posts": user_twittes,
        "logged_user": logged_in_user,
    },)


class DeleteTwitte(View):
    def post(self, request, post_id):
        # decrease postNum field in user document
        update_post_num_field(request.session.get('username'), -1)
        post_doc = find_single_twitte(post_id)
        if post_doc['type'] == 'reply':
            # if my document type was reply, we decrease total number of reply(replyNum) of parent document
            reply_to_id = post_doc["replyTo"][-1].id
            increase_reply_num(reply_to_id)

        delete_twitte(post_id)

        # Get URL of the page that initiated the request
        referer_url = request.META.get('HTTP_REFERER')
        referer_path = urlparse(referer_url).path  # turn full url to path
        return HttpResponseRedirect(referer_path)


@csrf_exempt
def like_twitte(request, postid, username):
    session_username = request.session.get("username")
    target_twitte = db.twittes.find_one({"_id": ObjectId(postid)})

    logged_in_user = find_user(session_username)
    logged_user_id = request.session.get("user_id")
    logged_user_dbref = DBRef("users", ObjectId(logged_user_id))

    # chack if already like the twitte
    user_liked_post = DBRef("twittes", ObjectId(
        postid)) in logged_in_user["likedPosts"]
    if user_liked_post:
        # remove user liked

        db.twittes.update_one(target_twitte, {"$inc": {"likeNum": -1}})
        # remove user DBRef from likedBy field
        db.twittes.update_one(
            {"_id": ObjectId(postid)},
            {"$pull": {"likedBy": DBRef("users", ObjectId(logged_user_id))}},
        )
        # remove from logged-user liked posts
        db.users.update_one(
            {"_id": ObjectId(logged_user_id)},
            {"$pull": {"likedPosts": DBRef("twittes", ObjectId(postid))}},
        )

        return JsonResponse({"already_liked": 1})
    else:
        # add to total number of likes
        db.twittes.update_one(target_twitte, {"$inc": {"likeNum": 1}})
        # add user DBRef to likedBy field
        db.twittes.update_one(
            {"_id": ObjectId(postid)},
            {"$push": {"likedBy": DBRef("users", ObjectId(logged_user_id))}},
        )
        # add to logged user liked posts
        db.users.update_one(
            {"_id": ObjectId(logged_user_id)},
            {"$push": {"likedPosts": DBRef("twittes", ObjectId(postid))}},
        )

    return JsonResponse({"messages": "successfull", "already_liked": 0})


def edit_profile(request):
    session_username = request.session.get("username")
    user_document = find_user(session_username)
    if request.method == "POST":
        profile_form = EditProfileForm(request.POST)
        if profile_form.is_valid():
            new_username = profile_form.cleaned_data["user_name"]

            if is_unique_username(new_username) or new_username == session_username:
                new_name = profile_form.cleaned_data["name"]
                user_submitted_data = {
                    "name": new_name,
                    "user_name": new_username,
                    "email_address": profile_form.cleaned_data["email_address"],
                    "bio": profile_form.cleaned_data["bio"],
                }
                db.users.update_one(
                    {"user_name": session_username}, {"$set": user_submitted_data})

                # update user_info field in all user twittes
                if new_username != session_username or new_name != user_document['name']:
                    db.twittes.update_many({"user": DBRef('users', ObjectId(user_document['_id']))}, {"$set": {"user_info": {
                                           'name': new_name, 'user_name': new_username, "profile_img": user_document['profile_img']}}})

                # change username in session to new username
                request.session["username"] = profile_form.cleaned_data["user_name"]
            else:
                profile_form.add_error(
                    field="user_name", error="this username already taken")
                return render(request, "chatter/edit_profile.html", {"profile_form": profile_form})

        else:
            profile_form = EditProfileForm()
            return render(request, "chatter/edit_profile.html", {"profile_form": profile_form})
        redirect_path = reverse("edit_profile")
        return HttpResponseRedirect(redirect_path)

    else:
        initial_data = {
            "name": user_document["name"],
            "user_name": user_document["user_name"],
            "email_address": user_document["email_address"],
            "bio": user_document["bio"],
        }
        profile_form = EditProfileForm(initial=initial_data)
        avatar_form = NewAvatarForm()

        return render(request, "chatter/edit_profile.html", {"profile_form": profile_form, "avatar_form": avatar_form, 'logged_user': user_document})


def update_avatar(request):
    user_id = request.session.get('user_id')
    user_document = db.users.find_one({"_id": ObjectId(user_id)})
    if request.method == "POST":
        form = NewAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["avatar"]
            # save image in directory
            handle_uploaded_file(image)
            # delete old avatar from server
            old_avatar_path = os.path.join(
                settings.MEDIA_ROOT, 'avatar', user_document['profile_img'])
            delete_file(old_avatar_path)
            # update user document
            db.users.update_one({"_id": ObjectId(user_id)}, {
                                "$set": {"profile_img": str(image)}})

            # update all user_info field in all user twittes
            user_info_doc = {
                "name": user_document['name'], 'user_name': user_document['user_name'], "profile_img": str(image)}
            db.twittes.update_many({"user": DBRef("users", ObjectId(user_id))}, {
                                   "$set": {"user_info": user_info_doc}})

        else:
            profile_form = EditProfileForm()
            return render(request, "chatter/edit_profile.html", {"profile_form": profile_form, "avatar_form": form, 'logged_user': user_document})

        redirect_path = reverse("edit_profile")
        return HttpResponseRedirect(redirect_path)


class ReplayTwitte(View):
    def get(self, request, username, postid):
        session_username = request.session.get("username")
        logged_user = find_user(session_username)
        already_logged = request.session.get("username")
        form = TwitteForm()
        user = find_user(username)
        post = find_single_twitte(postid)
        replys = []
        reply_to = []

        # loop through replys field(that contain an array of DBRefs class) and turn DBRef to actuall document and append it to replys list if document exist in twitte collection
        for rep in post["replys"]:
            document_dict = db.dereference(rep)
            if document_dict != None:
                replys.append(document_dict)

        # Add Tweets that have been replied to to reply_to list
        if post["type"] == "reply":
            for rep in post['replyTo']:
                reply_to.append(db.dereference(rep))

        return render(
            request,
            "chatter/reply_twitte_page.html",
            {
                "post": post,
                "user": user,
                "form": form,
                "replys": replys,
                "reply_to": reply_to,
                "logged_user": logged_user,
                "already_logged": already_logged
            },
        )

    def post(self, request, username, postid):
        form = TwitteForm(request.POST)
        session_username = request.session.get("username")
        replier_user = find_user(session_username)

        if form.is_valid():
            # get logged user database object
            logged_user_username = request.session.get("username")
            logged_user_obj = find_user(logged_user_username)

            # get logged user submitted form data
            text = form.cleaned_data["text"]
            publishedAt = form.cleaned_data["publishedAt"]

            # which twitte did that person reply to
            to_reply_post = find_single_twitte(postid)

            if to_reply_post["type"] == "reply":
                reply_chain = to_reply_post["replyTo"]
                new_reply = DBRef("twittes", ObjectId(postid))
                reply_chain.append(new_reply)
            else:
                reply_chain = [DBRef("twittes", ObjectId(postid))]

            # add logged user reply document to twitte collection with type of reply
            query = {
                "publishedAt": publishedAt,
                "text": text,
                "textLanguage": 'en',
                "user": DBRef("users", ObjectId(logged_user_obj["_id"])),
                "user_info": {
                    "name": logged_user_obj["name"],
                    "user_name": logged_user_obj["user_name"],
                    "profile_img": logged_user_obj["profile_img"],
                },
                "type": "reply",
                "replyTo": reply_chain,
                "replys": [],
                "replysNum": 0,
                "likedBy": [],
                "likeNum": 0,
                "replyDepth": len(reply_chain),

            }
            reply = db.twittes.insert_one(query)
            new_reply_doc_id = reply.inserted_id

            # add reply twitte DBRef to replyed post document
            db.twittes.update_one(
                {"_id": ObjectId(postid)},
                {"$push": {"replys": DBRef(
                    "twittes", ObjectId(new_reply_doc_id))}},
            )
            # increase number of reply nember by add 1 to replyNum field
            db.twittes.update_one({"_id": ObjectId(postid)}, {
                                  "$inc": {"replysNum": 1}})

            # increase total number of user twittes(db => postNum + 1)
            update_post_num_field(logged_user_username, 1)

            redirect_path = reverse("replytwitte", args=[username, postid])
            return HttpResponseRedirect(redirect_path)


class IndexFollows(View):
    def get(self, request, username, kind):
        users = []
        if kind == "followers":
            all_followers = find_user(username)["followers"]
            for user in all_followers:
                users.append(db.dereference(user))
        else:
            all_followers = find_user(username)["followings"]
            for user in all_followers:
                users.append(db.dereference(user))

        return render(request, "chatter/follow_list.html", {"follow_user": users})


class FollowUserView(View):
    def post(self, request, username):
        logged_user = find_user(request.session.get("username"))
        third_person_user = find_user(username)
        # check if the user has followed the specefice person or not
        if is_already_followed(logged_user["user_name"], username):
            # remove from followings
            db.users.update_one(
                logged_user,
                {
                    "$pull": {
                        "followings": DBRef("users", ObjectId(third_person_user["_id"]))
                    }
                },
            )
            # decrease followings number
            update_followings_number(logged_user["user_name"], -1)
            # remove from followers of third-person
            db.users.update_one(
                third_person_user,
                {"$pull": {"followers": DBRef(
                    "users", ObjectId(logged_user["_id"]))}},
            )
            # decrease followers number of third-person
            update_followers_number(third_person_user["user_name"], -1)

        else:
            # add to followings
            db.users.update_one(
                logged_user,
                {
                    "$push": {
                        "followings": DBRef("users", ObjectId(third_person_user["_id"]))
                    }
                },
            )
            # increase folloing number of logged-user
            update_followings_number(logged_user["user_name"], 1)
            # add to followers of third-person user
            db.users.update_one(
                third_person_user,
                {"$push": {"followers": DBRef(
                    "users", ObjectId(logged_user["_id"]))}},
            )
            # add to followers number of third person
            update_followers_number(third_person_user["user_name"], 1)

        return HttpResponseRedirect(f"/{username}")


def search(request):
    if request.POST:
        search_query = request.POST["search-query"]

        return render(request, "chatter/search_result.html", {"query": search_query})
    else:
        q = request.GET.get("q")
        search_in = request.GET.get("in")
        if search_in == 'users':
            result = db.users.find({"$text": {"$search": q}}).limit(20)
        else:
            result = db.twittes.find({"$text": {"$search": q}}).limit(20)

        # return number of document that founded
        total_doc = result.explain()["executionStats"]['totalDocsExamined']
        if total_doc == 0:
            result = 'Not found'

        return render(request, "chatter/search_result.html", {"result": result, "search_in": search_in})


def sing_up_user(request):
    session_username = request.session.get("username")
    logged_user = find_user(session_username)
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            db.users.insert_one(form.cleaned_data)
            return HttpResponseRedirect(reverse("login"))

    else:
        form = CreateUserForm()

        already_logged = request.session.get("username")

        return render(request, "chatter/authentication/sing_up.html", {"form": form, "already_logged": already_logged, "logged_user": logged_user})


def login_user(request):
    session_username = request.session.get("username")
    logged_user = find_user(session_username)
    if request.method == "POST":
        print(request.POST)
        form = LoginUserForm(request.POST)
        if form.is_valid():
            username = request.POST["user_name"]
            password = request.POST["password"]
            user = db.users.find_one({"user_name": username})

            if user and user["password"] == password:
                request.session.clear()
                user_name = user["user_name"]
                user_id = str(user["_id"])
                request.session["user_id"] = user_id
                request.session["username"] = user_name

                redirect_path = reverse("posttwitte", args=[user_name])

                return HttpResponseRedirect(redirect_path)
            else:
                error = "user name or password are incorrecct"
                return render(
                    request,
                    "chatter/authentication/login.html",
                    {"form": form, "error": error},
                )

    else:
        logged_in = False
        if request.session.get("username"):
            logged_in = True
        form = LoginUserForm()
    return render(
        request,
        "chatter/authentication/login.html",
        {"form": form, "logged_user": logged_user, "logged": logged_in},
    )


def logout(request):
    request.session.clear()
    return HttpResponseRedirect(reverse("login"))
