from rest_framework.views import APIView
from rest_framework.response import Response

from common.responses import error_response
from common.exceptions import AppError, ValidationError
from common.pagination import paginate_queryset

from .selectors import list_bookings
from .serializers import BookingListItemSerializer


class BookingListView(APIView):
    def get(self, request):
        try:
            resource_id = request.query_params.get("resource")
            date_from = request.query_params.get("date_from")
            date_to = request.query_params.get("date_to")
            status = request.query_params.get("status")

            page = int(request.query_params.get("page", "1"))
            page_size = int(request.query_params.get("page_size", "10"))

            qs = list_bookings(
                resource_id=resource_id,
                date_from=date_from,
                date_to=date_to,
                status=status,
            )
            paged = paginate_queryset(qs, page=page, page_size=page_size)

        except ValueError:
            return error_response(ValidationError("page and page_size must be integers"))
        except AppError as e:
            return error_response(e)

        ser = BookingListItemSerializer(paged["results"], many=True)
        return Response(
            {
                "count": paged["count"],
                "page": paged["page"],
                "page_size": paged["page_size"],
                "total_pages": paged["total_pages"],
                "results": ser.data,
            },
            status=200,
        )
