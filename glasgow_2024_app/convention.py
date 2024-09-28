from datetime import datetime, timezone

from nomnom.convention import (
    ConventionConfiguration,
    ConventionTheme,
)

theme = ConventionTheme(
    stylesheets="css/glasgow-2024.css",
    font_urls=[],
)

convention = ConventionConfiguration(
    name="Glasgow 2024",
    subtitle="Convention Subtitle (in glasgow_2024_app/convention.py)",
    slug="glasgow-2024",
    site_url="https://glasgow2024.org",
    nomination_eligibility_cutoff=datetime(2024, 2, 1, 0, 0, 0, tzinfo=timezone.utc),
    authentication_backends=[],
    hugo_help_email="hugo-help@glasgow2024.org",
    hugo_admin_email="hugo-admin@glasgow2024.org",
    hugo_packet_backend="digitalocean",
    registration_email="registration@glasgow2024.org",
    logo="images/logo_withouttitle_transparent-300x293.png",
    logo_alt_text="Glasgow 2024 logo",
    urls_app_name="glasgow_2024_app",
    advisory_votes_enabled=True,
)
