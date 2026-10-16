from app.response_presenter import (
    PresentationMode,
    ResponsePresentation,
    ResponsePresenter,
)


def test_conversation_mode_hides_links_and_internal_metadata():
    presenter = ResponsePresenter()
    response = ResponsePresentation(
        body=(
            "Encontré una noticia relevante.\n"
            "Enlace: https://example.com/story\n"
            "request_id: internal-123\n"
            "https://example.com/raw"
        ),
        source="Medio Ejemplo",
        link="https://example.com/story",
    )

    assert presenter.present(response) == "Encontré una noticia relevante."


def test_source_only_returns_only_the_source():
    response = ResponsePresentation(
        body="Resumen",
        source="Medio Ejemplo",
        link="https://example.com/story",
    )

    assert ResponsePresenter().present(
        response,
        mode=PresentationMode.SOURCE_ONLY,
    ) == "Medio Ejemplo"


def test_link_only_returns_only_the_link():
    response = ResponsePresentation(
        body="Resumen",
        source="Medio Ejemplo",
        link="https://example.com/story",
    )

    assert ResponsePresenter().present(
        response,
        mode=PresentationMode.LINK_ONLY,
    ) == "https://example.com/story"


def test_presentation_is_deterministic_and_does_not_mutate_input():
    response = ResponsePresentation(
        body="Resumen limpio",
        source="Medio Ejemplo",
        link="https://example.com/story",
    )
    presenter = ResponsePresenter()

    first = presenter.present(response)
    second = presenter.present(response)

    assert first == second == "Resumen limpio"
    assert response.link == "https://example.com/story"
