from app.current_affairs_router import CurrentAffairsRouter


def test_gui_05_conversation_reference_is_not_current_affairs():
    question = (
        "\u00bfCu\u00e1l es la \u00faltima referencia vigente "
        "que establecimos para nuestra prueba? "
        "Respond\u00e9 \u00fanicamente con esa referencia."
    )

    assert CurrentAffairsRouter._RECENCY.search(question)
    assert CurrentAffairsRouter._DYNAMIC.search(question) is None

    assert CurrentAffairsRouter()._should_search(question) is False


def test_gui_05_recent_nasa_news_remains_current_affairs():
    question = "\u00daltimas noticias de la NASA"

    assert CurrentAffairsRouter()._should_search(question) is True


def test_gui_05_recent_esa_news_remains_current_affairs():
    question = "\u00daltimas noticias de la ESA"

    assert CurrentAffairsRouter()._should_search(question) is True
