from diator.requests import Request


class SampleMiddleware:
    async def __call__(self, request: Request, handle):
        print("Before handling...")
        response = await handle(request)
        print("After handling...")
        return response
