from app.household_conversation_style import HouseholdConversationStyle
from app.local_provider_factory import build_local_provider_from_environment


def test_household_style_uses_argentine_voseo_without_diacritics():
    style = HouseholdConversationStyle()

    rendered = style.render("Podés decirme cómo está el pronóstico.")

    assert rendered == "Podes decirme como esta el pronostico."
    assert "voseo" in style.system_prompt
    assert "sin tildes" in style.system_prompt


def test_local_provider_uses_household_style_by_default(monkeypatch):
    monkeypatch.delenv("ROBY_LOCAL_PROVIDER_SYSTEM_PROMPT", raising=False)

    provider = build_local_provider_from_environment()

    assert "espanol argentino" in provider.settings.system_prompt
    assert "Usa voseo" in provider.settings.system_prompt


def test_household_style_preserves_protected_inline_content():
    style = HouseholdConversationStyle()

    text = (
        "Pod\u00e9s revisar `a\u00f1o_actual` en "
        "D:\\M\u00fasica\\Canci\u00f3n.mp3."
    )

    rendered = style.render(text)

    assert "Podes revisar" in rendered
    assert "`a\u00f1o_actual`" in rendered
    assert "D:\\M\u00fasica\\Canci\u00f3n.mp3" in rendered


def test_household_style_preserves_fenced_code_content():
    style = HouseholdConversationStyle()

    text = (
        "Pod\u00e9s revisar este c\u00f3digo:\n"
        "```python\n"
        "canci\u00f3n = 'M\u00fasica'\n"
        "a\u00f1o_actual = 2026\n"
        "```"
    )

    rendered = style.render(text)

    assert "Podes revisar este codigo:" in rendered
    assert (
        "```python\n"
        "canci\u00f3n = 'M\u00fasica'\n"
        "a\u00f1o_actual = 2026\n"
        "```"
    ) in rendered
