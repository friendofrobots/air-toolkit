DJANGO_SETTINGS_MODULE = 'air.settings'
def test_profile():
    from django.contrib.auth.models import User
    from django.http import HttpRequest
    request = HttpRequest()
    request.user = User.objects.get(username='712547')
    from air_explorer.views import likes
    return likes(request)

if __name__=='__main__':
    from timeit import Timer
    t = Timer("test_profile()", "from __main__ import test_profile")
    print t.timeit(10)
