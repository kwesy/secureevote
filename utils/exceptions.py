from rest_framework.views import exception_handler
from utils.response import standard_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        message = response.data.get('detail', 'An error occurred')
        return standard_response(
            data=None,
            message=message,
            status=False,
            status_code=response.status_code
        )

    # Handle non-DRF exceptions
    return standard_response(
        data=None,
        message="Internal server error",
        status=False,
        status_code=500
    )
