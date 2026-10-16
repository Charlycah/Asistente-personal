from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from infrastructure.weather.weather_adapter import WeatherAdapter


@dataclass(frozen=True)
class WeatherConversationPolicy:
    default_forecast_days: int = 5


class WeatherUnavailableConversationInterceptionPort:
    """Reserve weather intent so the general model never invents live conditions."""

    def __init__(self, reason: str = "missing_credentials") -> None:
        self.reason = reason

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if not WeatherConversationInterceptionPort.is_weather_request(normalized):
            return None
        if self.reason == "missing_credentials":
            message = (
                "No puedo consultar el clima real porque falta la clave de "
                "OpenWeather. "
                "Revisá .roby/credentials.json y completá OPENWEATHER_API_KEY."
            )
        else:
            message = (
                "No puedo consultar el clima real en este momento. "
                "No voy a estimarlo ni inventar datos meteorológicos."
            )
        return GovernedOperationalInterception(
            response_text=message,
            rationale=f"weather_unavailable_{self.reason}",
        )


class WeatherConversationInterceptionPort:
    """Connect natural household weather requests to the official adapter."""

    _SHORT_WEATHER_REQUEST = re.compile(
        r"^\s*[¿¡]?\s*(?:clima|tiempo|temperatura|lluvia|llueve|viento|"
        r"humedad|fr[ií]o|calor)(?:\s+(?:hoy|ahora|mañana|manana))?"
        r"(?:\s+en\s+[\wÀ-ÿ .'-]+)?\s*[?!.¡¿]*\s*$",
        re.IGNORECASE,
    )
    _CONDITIONAL_WEATHER_PROPOSITION = re.compile(
        r"^\s*(?:si|cuando|aunque)\b[^,;:.!?]*"
        r"\b(?:llueve|llueva|hay\s+viento|hace\s+(?:fr[ií]o|calor))\b"
        r"[^,;:.!?]*[,;:]\s*.+$",
        re.IGNORECASE,
    )
    _EXPLICIT_WEATHER_REQUEST_PATTERNS = (
        re.compile(
            r"\b(?:decime|dec[ií]s|dime|contame|dame|mostrame)\b.*"
            r"\b(?:clima|tiempo|temperatura|lluvia|viento|humedad|"
            r"pron[oó]stico)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:c[oó]mo\s+(?:est[aá]|viene)\s+(?:el\s+)?"
            r"(?:clima|tiempo|pron[oó]stico)|qu[eé]\s+tiempo\s+hace)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:qu[eé]|cu[aá]nta?|cu[aá]nto)\s+"
            r"(?:temperatura|humedad|viento|lluvia)\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:hay\s+viento|va\s+a\s+llover|llueve|"
            r"hace\s+(?:fr[ií]o|calor))\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:necesito|llevo|hace\s+falta)\s+"
            r"(?:un\s+|el\s+|la\s+)?(?:paraguas|abrigo)\b",
            re.IGNORECASE,
        ),
    )
    _FORECAST_TERMS = (
        "pronóstico",
        "pronostico",
        "extendido",
        "mañana",
        "manana",
        "próximos días",
        "proximos dias",
        "esta semana",
        "fin de semana",
    )
    _AMBIENT_WEATHER_PATTERNS = (
        re.compile(r"\b(?:el\s+)?d[ií]a\s+(?:est[aá]\s+)?(?:muy\s+)?feo\b"),
        re.compile(r"\bqu[eé]\s+(?:d[ií]a\s+)?feo\b"),
        re.compile(r"\b(?:el\s+)?d[ií]a\s+(?:est[aá]\s+)?gris\b"),
        re.compile(r"\b(?:el\s+)?d[ií]a\s+(?:est[aá]\s+)?nublado\b"),
        re.compile(
            r"^\s*(?:bien(?:\s+roby)?\s+pero\s+)?con\s+"
            r"(?:un\s+poco\s+de\s+)?(?:lluvia|fr[ií]o|calor)"
            r"(?:\s+y\s+(?:lluvia|fr[ií]o|calor))?\s*[.!?]*\s*$"
        ),
        re.compile(r"^\s*est[aá]\s+lloviendo(?:\s+y\s+hace\s+fr[ií]o)?\s*[.!?]*\s*$"),
    )
    _LOCATION_PATTERNS = (
        re.compile(r"\ben\s+([\wÀ-ÿ .'-]+?)(?:[?.!,]|$)", re.IGNORECASE),
        re.compile(r"\bpara\s+([\wÀ-ÿ .'-]+?)(?:[?.!,]|$)", re.IGNORECASE),
    )

    def __init__(
        self,
        adapter: WeatherAdapter,
        policy: WeatherConversationPolicy | None = None,
    ) -> None:
        self.adapter = adapter
        self.policy = policy or WeatherConversationPolicy()

    @classmethod
    def is_weather_request(cls, text: str) -> bool:
        normalized = " ".join(text.strip().casefold().split())
        if not normalized:
            return False
        if cls._CONDITIONAL_WEATHER_PROPOSITION.fullmatch(normalized):
            return False
        if any(pattern.search(normalized) for pattern in cls._AMBIENT_WEATHER_PATTERNS):
            return True
        if cls._SHORT_WEATHER_REQUEST.fullmatch(normalized):
            return True

        has_forecast_word = "pronóstico" in normalized or "pronostico" in normalized
        if has_forecast_word:
            forecast_weather_context = (
                "extendido",
                "mañana",
                "manana",
                "próximos días",
                "proximos dias",
                "esta semana",
                "fin de semana",
                "lluvia",
                "temperatura",
                "clima",
                "tiempo",
            )
            if any(term in normalized for term in forecast_weather_context):
                return True
        elif "extendido" in normalized and any(
            term in normalized for term in ("clima", "tiempo")
        ):
            return True

        return any(
            pattern.search(normalized)
            for pattern in cls._EXPLICIT_WEATHER_REQUEST_PATTERNS
        )

    def intercept(self, request: GovernedConversationPipelineRequest, *, now):
        del now
        normalized = request.text.strip().casefold()
        if not self.is_weather_request(normalized):
            return None

        location = self._extract_location(request.text)
        try:
            if any(term in normalized for term in self._FORECAST_TERMS):
                payload = self.adapter.forecast(
                    {
                        "location": location,
                        "days": self.policy.default_forecast_days,
                    }
                )
                response = self._render_forecast(payload)
                rationale = "weather_forecast_conversation_completed"
            else:
                payload = self.adapter.current_conditions({"location": location})
                response = self._render_current(payload)
                rationale = "weather_current_conversation_completed"
        except Exception:
            return GovernedOperationalInterception(
                response_text=(
                    "No pude consultar el servicio meteorológico en este momento. "
                    "La capacidad está integrada, pero el proveedor no respondió."
                ),
                rationale="weather_provider_temporarily_unavailable",
            )

        return GovernedOperationalInterception(
            response_text=response,
            rationale=rationale,
        )

    def _extract_location(self, text: str) -> str:
        for pattern in self._LOCATION_PATTERNS:
            match = pattern.search(text.strip())
            if match is not None:
                location = match.group(1).strip(" .,!?")
                if location:
                    return location
        return self.adapter.policy.default_location

    @staticmethod
    def _render_current(payload) -> str:
        weather = payload["weather"]
        advice = tuple(payload.get("advice", ()))
        temperature = round(weather["temperature_celsius"])
        feels_like = round(weather["feels_like_celsius"])
        description = WeatherConversationInterceptionPort._natural_description(
            weather["description"]
        )
        humidity = weather["humidity_percent"]
        wind = weather["wind_kph"]

        if description.startswith("con "):
            condition = description[4:]
            opening = (
                f"Ahora en {weather['location']} hay {condition}, "
                f"con {temperature} °C"
            )
        else:
            opening = (
                f"Ahora en {weather['location']} está {description}, "
                f"con {temperature} °C"
            )
        opening += f" y una sensación térmica de {feels_like} °C."

        details = f"La humedad está en {humidity}% y el viento va a {wind:.1f} km/h"
        pressure = weather.get("pressure_hpa", 0)
        if pressure:
            details += f", con una presión de {pressure} hPa"
        details += "."

        lines = [opening, details]
        rain_probability = weather.get("rain_probability_percent", 0)
        if rain_probability:
            lines.append(f"La probabilidad de lluvia es del {rain_probability}%.")
        recommendation = WeatherConversationInterceptionPort._weather_recommendation(
            temperature=temperature,
            feels_like=feels_like,
            humidity=humidity,
            wind=wind,
            rain_probability=rain_probability,
            description=description,
            advice=advice,
        )
        if recommendation:
            lines.append(recommendation)
        return " ".join(lines)

    @staticmethod
    def _weather_recommendation(
        *,
        temperature: int,
        feels_like: int,
        humidity: int,
        wind: float,
        rain_probability: int,
        description: str,
        advice: tuple[str, ...],
    ) -> str:
        lowered_description = description.casefold()
        rain_expected = (
            rain_probability >= 35
            or "lluv" in lowered_description
            or "torment" in lowered_description
        )
        cold = feels_like <= 12
        very_cold = feels_like <= 7
        hot = feels_like >= 30 or temperature >= 32
        windy = wind >= 30

        recommendations: list[str] = []
        if very_cold:
            recommendations.append("Llevate un buen abrigo y cuidate del frío")
        elif cold:
            recommendations.append("Te conviene salir con abrigo")
        elif hot:
            recommendations.append("Tomá agua y tratá de evitar el sol fuerte")

        if rain_expected:
            recommendations.append("llevá paraguas porque puede llover")
        if windy:
            recommendations.append("abrigate bien porque está bastante ventoso")
        if humidity >= 90 and not rain_expected:
            recommendations.append("la humedad está muy alta")

        if not recommendations and advice:
            return WeatherConversationInterceptionPort._natural_advice(advice[0])
        if not recommendations:
            return "Está bastante agradable para salir."
        if len(recommendations) == 1:
            return recommendations[0].rstrip(".") + "."
        return (
            recommendations[0].rstrip(".")
            + "; además, "
            + recommendations[1].rstrip(".")
            + "."
        )

    @staticmethod
    def _natural_description(description: str) -> str:
        cleaned = str(description).strip().casefold()
        replacements = {
            "nubes": "nublado",
            "con nubes": "nublado",
            "cielo claro": "despejado",
            "clear sky": "despejado",
            "muy nuboso": "muy nublado",
            "algo de nubes": "algo nublado",
            "nubes dispersas": "parcialmente nublado",
            "nubes rotas": "muy nublado",
            "lluvia ligera": "con lluvia ligera",
            "lluvia moderada": "con lluvia",
            "lluvia intensa": "con lluvia intensa",
            "llovizna": "con llovizna",
            "llovizna ligera": "con llovizna",
            "bruma": "con neblina",
            "niebla": "con niebla",
            "tormenta": "con tormentas",
            "tormenta eléctrica": "con tormentas",
        }
        return replacements.get(cleaned, str(description).strip())

    @staticmethod
    def _forecast_description(description: str) -> str:
        natural = WeatherConversationInterceptionPort._natural_description(description)
        adjectival_conditions = (
            "nublado",
            "muy nublado",
            "algo nublado",
            "parcialmente nublado",
            "despejado",
            "cubierto",
        )
        if natural.startswith(adjectival_conditions):
            return f"y {natural}"
        if natural.startswith("con "):
            return natural
        return f"con {natural}"

    @staticmethod
    def _natural_advice(advice: str) -> str:
        cleaned = str(advice).strip().rstrip(".")
        lowered = cleaned.casefold()
        if "abrigo" in lowered or "campera" in lowered:
            return "Te recomiendo salir con abrigo."
        if "paraguas" in lowered or "lluvia" in lowered:
            return "Yo llevaría un paraguas por las dudas."
        if lowered.startswith("conviene "):
            return f"Te recomiendo que {cleaned[8:]}."
        return f"Te recomiendo {cleaned}."

    @staticmethod
    def _friendly_date(value: str) -> str:
        weekdays = (
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        )
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            return value
        return weekdays[parsed.weekday()].capitalize()

    @staticmethod
    def _render_forecast(payload) -> str:
        forecast = payload["forecast"]
        lines = [f"Pronóstico extendido para {forecast['location']}:"]
        for day in forecast["days"]:
            label = WeatherConversationInterceptionPort._friendly_date(day["date"])
            description = WeatherConversationInterceptionPort._forecast_description(
                day["description"]
            )
            detail = (
                f"- {label}: entre {day['min_celsius']:.0f} y "
                f"{day['max_celsius']:.0f} °C, {description}. "
                f"Probabilidad de lluvia: {day['rain_probability_percent']}%."
            )
            if day.get("wind_kph", 0):
                detail += f" Viento: {day['wind_kph']:.1f} km/h."
            if day.get("pressure_hpa", 0):
                detail += f" Presión: {day['pressure_hpa']} hPa."
            lines.append(detail)
        return "\n".join(lines)
