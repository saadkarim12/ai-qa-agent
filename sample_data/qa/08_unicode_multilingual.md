# Portail Client — Exigences / 客户门户需求

## US-501 Connexion Client
As a Client Enregistré, I want to se connecter avec mon adresse e-mail so that je peux accéder à mon compte.

Acceptance Criteria:
- Given un compte actif, when the client submits des identifiants valides, then le tableau de bord is displayed.
- When the client submits un mot de passe incorrect, then une erreur générique is displayed.

## US-502 通知設定
As a Registered User, I want to configure 通知設定 so that I receive relevant alerts.

Acceptance Criteria:
- Given a verified account, when the user disables 電子メール通知, then no further email notifications are sent.
- When the user enables SMS 通知, then a confirmation message «Réglages enregistrés» is displayed.

## US-503 Émoji & symbols
As a Customer, I want to use symbols £ € ¥ ☑ → in my display name so that it renders correctly.

Acceptance Criteria:
- Given a display name containing £ € ¥ ☑ →, when the profile is saved, then the name renders unchanged on the profile page.
