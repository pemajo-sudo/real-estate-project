from django.contrib import messages
from listings.models import SellLead

class SellApprovalNotificationMiddleware:
    """
    Middleware to check for newly approved SellLeads for the logged-in user
    and display a success message upon any page refresh, then mark the
    notification as sent.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Check for approved SellLeads that haven't been notified yet
            pending_approved = SellLead.objects.filter(
                user=request.user,
                status=SellLead.STATUS_APPROVED,
                approval_notification_sent=False,
            )
            
            if pending_approved.exists():
                messages.success(
                    request,
                    "Good news! Your Sell Request has been approved. You can now Add Property from your dashboard."
                )
                pending_approved.update(approval_notification_sent=True)

            # Check for rejected SellLeads that haven't been notified yet
            pending_rejected = SellLead.objects.filter(
                user=request.user,
                status=SellLead.STATUS_REJECTED,
                rejection_notification_sent=False,
            )
            
            if pending_rejected.exists():
                messages.error(
                    request,
                    "We're sorry, your recent Sell Request has been declined. Please contact support for more details."
                )
                pending_rejected.update(rejection_notification_sent=True)
                
        response = self.get_response(request)
        return response
