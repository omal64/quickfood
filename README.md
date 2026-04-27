# QuickFood V3 🍽️

Plateforme de livraison de repas pour le marché sénégalais.

## 🚀 Lancement rapide (Windows PowerShell)

```powershell
cd QUICKFOODS_V3
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## 🔐 Compte admin par défaut
- Email : `admin@quickfood.sn`
- Mot de passe : `admin123`

## 💳 Configuration PayTech (paiement)
1. Créer un compte sur [paytech.sn](https://paytech.sn)
2. Récupérer votre `API_KEY` et `API_SECRET` depuis le tableau de bord
3. Copier `.env.example` → `.env` et remplir les clés :
```
PAYTECH_API_KEY=votre_api_key
PAYTECH_API_SECRET=votre_api_secret
PAYTECH_ENV=test
PAYTECH_IPN_URL=https://votredomaine.com/payment/ipn
PAYTECH_SUCCESS_URL=https://votredomaine.com/payment/success
PAYTECH_CANCEL_URL=https://votredomaine.com/payment/cancel
```

## 🗺️ Frais de livraison par distance
| Distance | Frais |
|----------|-------|
| 0 – 2 km | 1000 FCFA |
| 2 – 5 km | 2 000 FCFA |
| 5 – 10 km | 3 000 FCFA |
| 10 – 20 km | 4 000 FCFA |
| > 20 km | 7 000 FCFA |

## 📁 Structure
```
├── app.py                  # Point d'entrée
├── config.py               # Configuration
├── extensions.py           # SQLAlchemy, LoginManager...
├── models/                 # User, Order, Restaurant, Product...
├── routes/                 # admin, auth, cart, client, partner, payment
├── services/               # CartService, OrderService, PayTechService
├── utils/                  # helpers, delivery (Haversine)
└── templates/              # Templates Jinja2
```

## ✅ Nouveautés V3
- 🗺️ **Distance sur chaque carte restaurant** (Haversine, tri automatique)
- 💳 **Paiement PayTech** (Wave, Orange Money, Visa/Mastercard)
- 🛵 **Dashboard livraisons admin** avec stats temps réel
- 📍 **Frais de livraison dynamiques** selon distance GPS
- 🔧 **Bug cart_count corrigé** (context processor global)
