# Subscriptions and Paypal

The new subscriptions system should automate most of the job of accepting payments, upgrading accounts, awaiting cancellations and downgrading cancelled accounts.

## How it works

The fuksubs app is in charge of all this, with help from the Django-paypal app.

It has a single model (and therefore database table and admin screen), with 4 fields:

- User (foreign key to user object)
- Status. The subscription status, can be Active, Expired or Unknown (a bit of a hedge!)
- Expiry. Date field, when the subscription expires
- Paypalref. The reference to the paypal subscription transaction.

### Subscribing

When a user hits the subscribe button, they go off to Paypal for a standard transaction sequence. At the end of that sequence, assuming the user hasn't cancelled along the way, Paypal sends a post request to a special URL on our site, with details of the transaction.

The post request is processed and subject to a bit of error checking, the user's account is upgraded. The full details of the transaction are logged in the Paypal IPN table of the database.

### Cancellations

When a user cancels their subscription through their Paypal account, Paypal sends another post request to our site with details of the cancellation.