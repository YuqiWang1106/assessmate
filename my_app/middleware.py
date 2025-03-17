from django.shortcuts import redirect

# middleware restricts access, controlling role-based access
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/dashboard") and "user_id" not in request.session:
            return redirect("select_role")
        
        return self.get_response(request)