# Configuration PayTech — Guide complet

---

## 1. Créer un compte
→ https://paytech.sn → S'inscrire

## 2. Récupérer les clés API
→ Tableau de bord → Paramètres → Clés API

Vous aurez 2 clés :
- **API_KEY**
- **API_SECRET**

---

## 3. Configurer le projet

Copier `.env.example` → `.env` à la racine du projet et remplir :

```env
PAYTECH_API_KEY=votre_api_key_ici
PAYTECH_API_SECRET=votre_api_secret_ici
PAYTECH_ENV=test

# URLs callback (remplacer par votre domaine HTTPS en production)
PAYTECH_IPN_URL=https://votredomaine.sn/payment/ipn
PAYTECH_SUCCESS_URL=https://votredomaine.sn/payment/success
PAYTECH_CANCEL_URL=https://votredomaine.sn/payment/cancel
```

> ⚠️ En développement local, PayTech ne peut pas contacter `127.0.0.1`.
> Utilisez ngrok pour exposer votre serveur local :
> ```bash
> ngrok http 5000
> # Puis copiez l'URL https://xxxx.ngrok.io dans PAYTECH_IPN_URL
> ```

---

## 4. Installer les dépendances

```bash
pip install -r requirements.txt
flask db upgrade   # applique les migrations (inclut les colonnes split payment)
```

---

## 5. Flux de paiement avec Split automatique

```
Client clique "Payer en ligne"
        ↓
POST https://paytech.sn/api/payment/request-payment
        ↓
Redirection vers la page de paiement PayTech
        ↓
Client paie (Wave / Orange Money / Carte bancaire)
        ↓
PayTech envoie IPN → /payment/ipn  (type_event=sale_complete)
        ↓
Commande marquée "En préparation" + payment_status="success"
        ↓
╔══════════════════════════════════════════════════╗
║           SPLIT PAYMENT AUTOMATIQUE              ║
║                                                  ║
║  SplitService.execute(order) calcule :           ║
║                                                  ║
║  commission = subtotal × commission_rate / 100   ║
║  restaurant_amount = subtotal − commission       ║
║  delivery_fee → 100 % QuickFood                  ║
║                                                  ║
║  → Enregistré en base (split_status = "done")    ║
╚══════════════════════════════════════════════════╝
        ↓
Redirection → /payment/success
```

---

## 6. Répartition des fonds (Split Payment)

| Flux | Destinataire | Calcul |
|------|-------------|--------|
| Commission | QuickFood | subtotal × taux_commission |
| Frais de livraison | QuickFood | 100 % |
| Net restaurant | Restaurant | subtotal − commission |

Le taux de commission est défini par restaurant dans `Restaurant.commission_rate`
(modifiable dans l'interface admin → Restaurants).

### Exemple avec commission 10 % :

| Élément | Montant |
|---------|---------|
| Sous-total articles | 10 000 FCFA |
| Frais de livraison  |  1 000 FCFA |
| **Total client**    | **11 000 FCFA** |
| Commission QuickFood (10 %) | 1 000 FCFA |
| Livraison QuickFood | 1 000 FCFA |
| **Total QuickFood** | **2 000 FCFA** |
| **Net restaurant**  | **9 000 FCFA** |

---

## 7. Suivi des splits — Interface Admin

| URL | Description |
|-----|-------------|
| `/admin/splits` | Monitoring de tous les splits (statut, montants, filtres) |
| `/admin/commissions` | Vue agrégée par restaurant avec colonnes livraison et split |
| `/admin/splits/export` | Export CSV complet de tous les splits |
| `/admin/splits/recalc/<id>` | Recalcul forcé si l'IPN a échoué |

**Statuts split :**
- `pending` — commande payée mais split pas encore calculé
- `done`    — split calculé et enregistré ✓
- `error`   — erreur lors du calcul (voir logs)

Si des splits restent en `pending`, utiliser le bouton Recalculer dans
`/admin/splits` pour les relancer sans ré-encaisser le client.

---

## 8. Vue partenaire (Restaurant)

Les partenaires accèdent à leur tableau de bord de revenus via :

```
/partner/revenus
```

Ils y voient, pour chaque restaurant :
- Total encaissé par les clients
- Commission déduite par QuickFood
- Frais de livraison (QuickFood)
- Leur montant net à recevoir

---

## 9. Virement réel vers le restaurant

Le split est comptable : QuickFood encaisse l'intégralité, puis reverse
la part du restaurant. Deux approches :

### Option A — Virement manuel (recommandé au démarrage)
1. Aller sur `/admin/splits` ou `/admin/commissions`
2. Cliquer "Exporter CSV"
3. Effectuer les virements Wave Business / Orange Money Business en lot
4. Fréquence suggérée : hebdomadaire ou mensuelle

### Option B — Virement automatique via PayTech Transfer API
Ajouter `wave_phone` / `om_phone` sur le modèle `Restaurant`, puis
après `SplitService.execute()`, appeler l'API PayTech Transfer :

```python
# Dans services/split_service.py → execute()
# Décommenter et adapter selon la doc PayTech Transfer :
#
# import requests
# requests.post("https://paytech.sn/api/transfer/send", data={
#     "amount": split["restaurant_amount"],
#     "phone":  order.restaurant.wave_phone,
#     "env":    current_app.config["PAYTECH_ENV"],
# }, headers={"API_KEY": ..., "API_SECRET": ...})
```

---

## 10. Tester en mode test

En mode `PAYTECH_ENV=test`, PayTech fournit des numéros Wave / Orange Money
fictifs pour simuler des paiements sans argent réel.

Le split est déclenché normalement — vérifier les résultats dans `/admin/splits`
immédiatement après chaque paiement test.

---

## 11. Passer en production

1. Changer `PAYTECH_ENV=prod` dans `.env`
2. Remplacer toutes les URLs `PAYTECH_*_URL` par votre domaine HTTPS
3. S'assurer que `/payment/ipn` est accessible publiquement
4. Vérifier dans `/admin/splits` que les splits passent en `done` après les premiers vrais paiements

---

## Sans clés PayTech

L'application fonctionne normalement — le bouton "Payer en ligne" redirige
vers paiement à la livraison avec un message explicatif.
Le split ne se déclenche que sur les paiements confirmés par PayTech.
