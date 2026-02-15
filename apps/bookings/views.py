from rest_framework.views import APIView
from rest_framework.response import Response

from common.responses import error_response
from common.exceptions import AppError, ValidationError
from common.pagination import paginate_queryset

from .selectors import list_bookings
from .services import create_booking
from .serializers import BookingListItemSerializer, BookingCreateSerializer
from .services import cancel_booking


class BookingCollectionView(APIView):
    """
    GET  /bookings      -> list + filters + pagination
    POST /bookings      -> create booking (overlap-protected)
    """

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

    def post(self, request):
        ser = BookingCreateSerializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"error": {"code": "VALIDATION_ERROR", "message": "Invalid input", "details": ser.errors}},
                status=400,
            )

        try:
            booking = create_booking(user=request.user, **ser.validated_data)
        except AppError as e:
            return error_response(e)

        out = BookingListItemSerializer(booking)
        return Response(out.data, status=201)


class BookingCancelView(APIView):
    """
    PATCH /bookings/{id}/cancel
    """
    def patch(self, request, booking_id: str):
        try:
            booking = cancel_booking(user=request.user, booking_id=booking_id)
        except AppError as e:
            return error_response(e)

        return Response(
            {
                "id": str(booking.id),
                "status": booking.status,
                "cancelled_at": booking.cancelled_at.isoformat().replace("+00:00", "Z") if booking.cancelled_at else None,
            },
            status=200,
        )
