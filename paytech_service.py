import os
import requests

class PayTechService:

    URL = "https://paytech.sn/api/payment/request-payment"

    @staticmethod
    def create_payment(order_id, amount, customer_email):
        payload = {
            "item_name": f"Commande QuickFood #{order_id}",
            "item_price": amount,
            "currency": "XOF",
            "command_name": str(order_id),

            "env": os.getenv("PAYTECH_ENV", "test"),
            "ipn_url": os.getenv("PAYTECH_IPN_URL"),
            "success_url": os.getenv("PAYTECH_SUCCESS_URL"),
            "cancel_url": os.getenv("PAYTECH_CANCEL_URL"),
        }

        headers = {
            "API_KEY": os.getenv("PAYTECH_API_KEY"),
            "API_SECRET": os.getenv("PAYTECH_API_SECRET"),
        }

        response = requests.post(PayTechService.URL, json=payload, headers=headers)

        return response.json()