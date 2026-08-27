# Platform Notes — Session and Caching Behaviour

Session handling has been a recurring source of support tickets across the last two releases. When a
customer leaves a tab open overnight and returns the following morning, the application sometimes keeps
them signed in well past the intended window, and in other cases signs them out in the middle of a
checkout with no warning and no way to recover the basket they had assembled.

Support has also reported that signing out on one device does not reliably end sessions elsewhere. This
matters most for the shared machines used in store branches, where a colleague picking up a terminal may
still be operating inside the previous colleague's session.

Separately, the caching layer occasionally serves stale pricing after a promotion ends. The window
appears to be small, but finance has raised it twice because the discount is honoured at checkout.
