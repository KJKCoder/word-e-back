class CustomHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Modify request headers here
        request.META['CUSTOM_HEADER'] = 'access-token'
        response = self.get_response(request)
        return response