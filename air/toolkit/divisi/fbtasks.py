from celery.tasks import tasks
import facebook

@task
def dlInfo(graphapi,fbid):
    try:
        info = graphapi.get_object(fbid)
        return (fbid, 'info', info)
    except (facebook.GraphAPIError), exc:
        dlInfo.retry(exc=exc)

@task
def dlFriends(graphapi,fbid):
    try:
        friends = graphapi.get_connections(fbid,"friends")['data']
        return (fbid, 'friends', friends)
    except (facebook.GraphAPIError), exc:
        dlFriends.retry(exc=exc)

@task
def dlLikes(graphapi,fbid):
    try:
        likes = graphapi.get_connections(fbid,"likes")['data']
        return (fbid, 'likes', likes)
    except (facebook.GraphAPIError), exc:
        dlLikes.retry(exc=exc)
