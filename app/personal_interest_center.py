from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from types import MappingProxyType
from typing import Iterable, Mapping


class InterestDomain(StrEnum):
    CULTURE = "culture"
    SCIENCE = "science"
    TECHNOLOGY = "technology"
    AUDIOVISUAL = "audiovisual"
    HEALTH_AND_WELLBEING = "health_and_wellbeing"
    SPORTS = "sports"
    FOOD = "food"


class InterestPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class InterestTopic(StrEnum):
    CULTURE_CABA = "culture_caba"
    ARGENTINE_CUISINE = "argentine_cuisine"
    SPORTS = "sports"
    MUSIC = "music"
    THEATRE = "theatre"
    MUSEUMS = "museums"
    FREE_ACTIVITIES = "free_activities"
    SCIENCE = "science"
    ASTRONOMY = "astronomy"
    SPACE_EXPLORATION = "space_exploration"
    NASA_MISSIONS = "nasa_missions"
    INTERNATIONAL_SPACE_STATION = "international_space_station"
    JAMES_WEBB_SPACE_TELESCOPE = "james_webb_space_telescope"
    TECHNOLOGY = "technology"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    PROGRAMMING = "programming"
    PROGRAMMING_LANGUAGES = "programming_languages"
    SOFTWARE_ENGINEERING = "software_engineering"
    CINEMA = "cinema"
    SERIES = "series"
    RELEASES = "releases"
    SCIENCE_FICTION = "science_fiction"
    HARD_SCIENCE_FICTION = "hard_science_fiction"
    DOCUMENTARIES = "documentaries"
    HEALTHY_EATING = "healthy_eating"
    EVIDENCE_BASED_NUTRITION = "evidence_based_nutrition"
    HEALTHY_RECIPES = "healthy_recipes"
    MEDITERRANEAN_CUISINE = "mediterranean_cuisine"
    BOCA_JUNIORS = "boca_juniors"
    RIVER_PLATE = "river_plate"


@dataclass(frozen=True)
class InterestPreference:
    topic: InterestTopic
    domain: InterestDomain
    priority: InterestPriority = InterestPriority.MEDIUM
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized_tags = tuple(tag.strip() for tag in self.tags if tag.strip())
        if len(set(normalized_tags)) != len(normalized_tags):
            raise ValueError("interest preference tags must be unique")
        object.__setattr__(self, "tags", normalized_tags)


@dataclass(frozen=True)
class PersonalInterestProfile:
    person: str
    topics: frozenset[InterestTopic]
    notes: tuple[str, ...] = ()
    preferences: tuple[InterestPreference, ...] = ()

    def __post_init__(self) -> None:
        preference_topics = tuple(item.topic for item in self.preferences)
        if len(set(preference_topics)) != len(preference_topics):
            raise ValueError("interest preference topics must be unique")
        if not set(preference_topics).issubset(self.topics):
            raise ValueError("interest preferences must reference profile topics")

    def is_interested_in(self, topic: InterestTopic) -> bool:
        return topic in self.topics

    def preference_for(self, topic: InterestTopic) -> InterestPreference | None:
        return next(
            (item for item in self.preferences if item.topic is topic),
            None,
        )

    def priority_for(self, topic: InterestTopic) -> InterestPriority:
        preference = self.preference_for(topic)
        if preference is None:
            return InterestPriority.MEDIUM
        return preference.priority

    def topics_for_domain(self, domain: InterestDomain) -> frozenset[InterestTopic]:
        return frozenset(
            item.topic for item in self.preferences if item.domain is domain
        )


@dataclass(frozen=True)
class PersonalInterestCenterSnapshot:
    schema_version: str
    authority: str
    profiles: tuple[PersonalInterestProfile, ...]

    def profile_for(self, person: str) -> PersonalInterestProfile:
        normalized = _normalize_person(person)
        return next(
            profile
            for profile in self.profiles
            if _normalize_person(profile.person) == normalized
        )


CARLOS_PREFERENCES: tuple[InterestPreference, ...] = (
    InterestPreference(
        topic=InterestTopic.HARD_SCIENCE_FICTION,
        domain=InterestDomain.AUDIOVISUAL,
        priority=InterestPriority.VERY_HIGH,
        tags=("scientifically_plausible", "space", "technology"),
    ),
    InterestPreference(
        topic=InterestTopic.SCIENCE_FICTION,
        domain=InterestDomain.AUDIOVISUAL,
        priority=InterestPriority.HIGH,
        tags=("first_contact", "artificial_intelligence", "space_exploration"),
    ),
    InterestPreference(
        topic=InterestTopic.RELEASES,
        domain=InterestDomain.AUDIOVISUAL,
        priority=InterestPriority.HIGH,
        tags=("confirmed_dates", "argentina", "streaming"),
    ),
    InterestPreference(
        topic=InterestTopic.HEALTHY_EATING,
        domain=InterestDomain.HEALTH_AND_WELLBEING,
        priority=InterestPriority.HIGH,
        tags=("balanced_meals", "evidence_based"),
    ),
    InterestPreference(
        topic=InterestTopic.EVIDENCE_BASED_NUTRITION,
        domain=InterestDomain.HEALTH_AND_WELLBEING,
        priority=InterestPriority.HIGH,
        tags=("official_guidelines", "scientific_consensus"),
    ),
)


CRISTINA_PREFERENCES: tuple[InterestPreference, ...] = (
    InterestPreference(
        topic=InterestTopic.HEALTHY_EATING,
        domain=InterestDomain.HEALTH_AND_WELLBEING,
        priority=InterestPriority.HIGH,
        tags=("balanced_meals", "seasonal_food"),
    ),
    InterestPreference(
        topic=InterestTopic.HEALTHY_RECIPES,
        domain=InterestDomain.HEALTH_AND_WELLBEING,
        priority=InterestPriority.HIGH,
        tags=("practical", "home_cooking"),
    ),
    InterestPreference(
        topic=InterestTopic.MEDITERRANEAN_CUISINE,
        domain=InterestDomain.FOOD,
        priority=InterestPriority.HIGH,
        tags=("vegetables", "legumes", "olive_oil"),
    ),
)


DEFAULT_PERSONAL_INTERESTS: tuple[PersonalInterestProfile, ...] = (
    PersonalInterestProfile(
        person="Carlos",
        topics=frozenset(
            {
                InterestTopic.CULTURE_CABA,
                InterestTopic.ARGENTINE_CUISINE,
                InterestTopic.SPORTS,
                InterestTopic.MUSIC,
                InterestTopic.THEATRE,
                InterestTopic.MUSEUMS,
                InterestTopic.FREE_ACTIVITIES,
                InterestTopic.SCIENCE,
                InterestTopic.ASTRONOMY,
                InterestTopic.SPACE_EXPLORATION,
                InterestTopic.NASA_MISSIONS,
                InterestTopic.INTERNATIONAL_SPACE_STATION,
                InterestTopic.JAMES_WEBB_SPACE_TELESCOPE,
                InterestTopic.TECHNOLOGY,
                InterestTopic.ARTIFICIAL_INTELLIGENCE,
                InterestTopic.PROGRAMMING,
                InterestTopic.PROGRAMMING_LANGUAGES,
                InterestTopic.SOFTWARE_ENGINEERING,
                InterestTopic.CINEMA,
                InterestTopic.SERIES,
                InterestTopic.RELEASES,
                InterestTopic.SCIENCE_FICTION,
                InterestTopic.HARD_SCIENCE_FICTION,
                InterestTopic.DOCUMENTARIES,
                InterestTopic.HEALTHY_EATING,
                InterestTopic.EVIDENCE_BASED_NUTRITION,
                InterestTopic.HEALTHY_RECIPES,
                InterestTopic.MEDITERRANEAN_CUISINE,
                InterestTopic.BOCA_JUNIORS,
            }
        ),
        preferences=CARLOS_PREFERENCES,
    ),
    PersonalInterestProfile(
        person="Cristina",
        topics=frozenset(
            {
                InterestTopic.CULTURE_CABA,
                InterestTopic.ARGENTINE_CUISINE,
                InterestTopic.MUSIC,
                InterestTopic.THEATRE,
                InterestTopic.MUSEUMS,
                InterestTopic.FREE_ACTIVITIES,
                InterestTopic.SPACE_EXPLORATION,
                InterestTopic.NASA_MISSIONS,
                InterestTopic.INTERNATIONAL_SPACE_STATION,
                InterestTopic.JAMES_WEBB_SPACE_TELESCOPE,
                InterestTopic.CINEMA,
                InterestTopic.SERIES,
                InterestTopic.DOCUMENTARIES,
                InterestTopic.HEALTHY_EATING,
                InterestTopic.EVIDENCE_BASED_NUTRITION,
                InterestTopic.HEALTHY_RECIPES,
                InterestTopic.MEDITERRANEAN_CUISINE,
                InterestTopic.RIVER_PLATE,
            }
        ),
        preferences=CRISTINA_PREFERENCES,
    ),
)


class PersonalInterestCenter:
    """Canonical household-interest registry subordinate to the official gateway.

    M343.6 enriches the same profiles with domains, priorities and descriptive
    tags. It performs no web searches, recommendations, autonomous notifications,
    medical decisions or credential access.
    """

    SCHEMA_VERSION = "m343.2"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    def __init__(
        self,
        profiles: Iterable[PersonalInterestProfile] = DEFAULT_PERSONAL_INTERESTS,
    ) -> None:
        profile_items = tuple(profiles)
        indexed = {
            _normalize_person(profile.person): profile for profile in profile_items
        }
        if not indexed:
            raise ValueError("personal interest center needs at least one profile")
        if len(indexed) != len(profile_items):
            raise ValueError("personal interest profile names must be unique")
        self._profiles: dict[str, PersonalInterestProfile] = indexed

    @property
    def snapshot(self) -> PersonalInterestCenterSnapshot:
        return PersonalInterestCenterSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            profiles=tuple(self._profiles.values()),
        )

    @property
    def profiles(self) -> Mapping[str, PersonalInterestProfile]:
        return MappingProxyType(self._profiles)

    def profile_for(self, person: str) -> PersonalInterestProfile:
        try:
            return self._profiles[_normalize_person(person)]
        except KeyError as exc:
            raise KeyError(f"unknown household member: {person}") from exc

    def interested_people(self, topic: InterestTopic) -> tuple[str, ...]:
        return tuple(
            profile.person
            for profile in self._profiles.values()
            if profile.is_interested_in(topic)
        )

    def set_topics(
        self,
        person: str,
        topics: Iterable[InterestTopic],
    ) -> PersonalInterestProfile:
        key = _normalize_person(person)
        current = self.profile_for(person)
        topic_set = frozenset(topics)
        retained_preferences = tuple(
            item for item in current.preferences if item.topic in topic_set
        )
        updated = replace(
            current,
            topics=topic_set,
            preferences=retained_preferences,
        )
        self._profiles[key] = updated
        return updated

    def set_preferences(
        self,
        person: str,
        preferences: Iterable[InterestPreference],
    ) -> PersonalInterestProfile:
        key = _normalize_person(person)
        current = self.profile_for(person)
        preference_items = tuple(preferences)
        updated = replace(current, preferences=preference_items)
        self._profiles[key] = updated
        return updated


def _normalize_person(person: str) -> str:
    normalized = person.strip().casefold()
    if not normalized:
        raise ValueError("person name cannot be empty")
    return normalized
