"""Infer airline identity from flight callsign prefixes."""

from __future__ import annotations

# ICAO three-letter airline prefixes (callsign = prefix + flight number).
_ICAO_AIRLINES: dict[str, str] = {
    "AIC": "Air India",
    "AXB": "Air India Express",
    "AKJ": "Akasa Air",
    "IGO": "IndiGo",
    "SEJ": "SpiceJet",
    "GOW": "Go First",
    "VTI": "Vistara",
    "KAC": "Korean Air",
    "UAE": "Emirates",
    "ETD": "Etihad Airways",
    "QTR": "Qatar Airways",
    "SIA": "Singapore Airlines",
    "THY": "Turkish Airlines",
    "BAW": "British Airways",
    "DLH": "Lufthansa",
    "AFR": "Air France",
    "UAL": "United Airlines",
    "AAL": "American Airlines",
    "DAL": "Delta Air Lines",
}


def infer_airline_from_callsign(callsign: str | None) -> str | None:
    """Return an airline name inferred from the ICAO callsign prefix."""
    if not callsign or not callsign.strip():
        return None
    prefix = callsign.strip().upper()[:3]
    if len(prefix) < 3 or not prefix.isalnum():
        return None
    return _ICAO_AIRLINES.get(prefix)
