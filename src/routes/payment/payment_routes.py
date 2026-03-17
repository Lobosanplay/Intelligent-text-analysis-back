import os

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

load_dotenv()
router = APIRouter(prefix="/payment", tags=["Stripe"])

YOUR_DOMAIN = os.getenv("YOUR_DOMAIN", "http://localhost:5173/")
STRIPE_KEY = os.getenv("STRIPE_KEY")
stripe.api_key = STRIPE_KEY


@router.post("/create-checkout-session")
async def create_checkout_session(request: Request, userId: str, email: str):
    try:
        form = await request.form()
        lookup_key = form.get("lookup_key")

        prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": prices.data[0].id,
                    "quantity": 1,
                },
            ],
            metadata={"UserId": userId, "UserEmail": email},
            mode="subscription",
            success_url=f"{YOUR_DOMAIN}?success=true&session_id={{CHECKOUT_SESSION_ID}}",
        )
        return RedirectResponse(checkout_session.url, status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-portal-session")
async def customer_portal(request: Request):
    # For demonstration purposes, we're using the Checkout session to retrieve the customer_account ID.
    # Typically this is stored alongside the authenticated user in your database.
    form = await request.form()
    checkout_session_id = form.get("session_id")

    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

    # This is the URL to which the customer will be redirected after they're
    # done managing their billing with the portal.
    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=YOUR_DOMAIN,
    )
    return RedirectResponse(portalSession.url, status_code=303)
