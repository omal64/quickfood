from flask import Blueprint, redirect, request
from services.paytech_service import PayTechService

payment_bp = Blueprint("payment", __name__)


# 👉 Lancer paiement
@payment_bp.route("/pay/<int:order_id>")
def pay(order_id):

    amount = request.args.get("amount", 5000)
    email = request.args.get("email", "client@quickfood.sn")

    response = PayTechService.create_payment(order_id, amount, email)

    if "redirect_url" in response:
        return redirect(response["redirect_url"])

    return {"error": "Payment failed", "details": response}


# 👉 IPN (confirmation automatique)
@payment_bp.route("/payment/ipn", methods=["POST"])
def ipn():
    data = request.json

    print("IPN RECEIVED:", data)

    if data.get("status") == "success":
        order_id = data.get("command_name")

        # TODO: ici tu valides la commande dans DB
        # update_order_paid(order_id)

        return "OK", 200

    return "FAILED", 400


# 👉 Success page
@payment_bp.route("/payment/success")
def success():
    return "Paiement réussi ✔ Commande confirmée"


# 👉 Cancel page
@payment_bp.route("/payment/cancel")
def cancel():
    return "Paiement annulé ❌"