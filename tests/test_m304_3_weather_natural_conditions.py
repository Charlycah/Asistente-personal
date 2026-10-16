from app.weather_conversation_runtime import WeatherConversationInterceptionPort


def _payload(description: str, *, feels_like: float = 8) -> dict:
    return {
        "weather": {
            "location": "Buenos Aires",
            "temperature_celsius": 10,
            "feels_like_celsius": feels_like,
            "description": description,
            "humidity_percent": 88,
            "wind_kph": 4.8,
            "pressure_hpa": 1011,
            "rain_probability_percent": 0,
        },
        "advice": (),
    }


def test_bad_day_comment_is_treated_as_weather_request():
    text = "estoy bien Roby, pero el día está muy feo"
    assert WeatherConversationInterceptionPort.is_weather_request(text)


def test_clouds_are_rendered_as_nublado_with_feels_like():
    rendered = WeatherConversationInterceptionPort._render_current(_payload("nubes"))
    assert rendered.startswith("Ahora en Buenos Aires está nublado")
    assert "sensación térmica de 8 °C" in rendered


def test_equal_feels_like_is_always_reported():
    rendered = WeatherConversationInterceptionPort._render_current(
        _payload("nubes", feels_like=10)
    )
    assert "sensación térmica de 10 °C" in rendered


def test_rain_and_drizzle_use_natural_phrasing():
    rain = WeatherConversationInterceptionPort._render_current(
        _payload("lluvia ligera")
    )
    drizzle = WeatherConversationInterceptionPort._render_current(_payload("llovizna"))
    assert "hay lluvia ligera" in rain
    assert "hay llovizna" in drizzle
