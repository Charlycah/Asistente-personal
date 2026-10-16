from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "docs/history/root-archive-post-g22"
CURRENT_TRUTH = ROOT / "ROBY_XI_2_CURRENT_TRUTH.md"

MOVE_MANIFEST = {
    (
        'ROBY_XI_2_E1_B_S1_A_EXACT_GOVERNED_PROPOSAL_HUMAN_REVI'
        'EW_DISPOSITION_CONTRACT_RED.md'
    ):
        (
                '16b86320c1dad8d654afb285d7c0ddea404dada5dc5ffa9c2bc191'
                'e2d96b39db'
            ),
    (
        'ROBY_XI_2_E1_B_S1_B_EXACT_PRESENTED_PROPOSAL_REFERENCE'
        '_HUMAN_REVIEW_TRANSPORT_CONTRACT_RED.md'
    ):
        (
                'bf2dcf64473697f319c9308de7ac083a16dbc31fa349fd22c1b298'
                '5c39f2468e'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S4_Z_CURRENT_REGISTRY_RESOLUTION_PAT'
        'H_AVAILABILITY_CONTRACT_RED.md'
    ):
        (
                '5ec5bbea851c769869b71de10d737e39577d7fa41a8966837b86c6'
                'e0199c58ef'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_A_CANONICAL_RUNTIME_READINESS_PRO'
        'JECTION_CONTRACT_RED.md'
    ):
        (
                '8ce8431120d9c91c7ef16bbf15262240fe3cba0b163757a5802520'
                '8f218c730f'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B1_A_EXPLICIT_EPISTEMIC_SUITABILI'
        'TY_FOUNDATION_CONTRACT_RED.md'
    ):
        (
                '691929fe92c15ee057c8fecbbb84b89f503270830e6538a92f5ee9'
                'c3fc549d6f'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B1_B_GOVERNED_SELECTION_ELIGIBILI'
        'TY_CONTRACT_RED.md'
    ):
        (
                'cde3b79a5129c711256e1cda1e75914b6469b0a2593c16519d66dd'
                '081901d067'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_A1_EXPLICIT_PATH_DISCRIMINATIO'
        'N_REQUIREMENT_FOUNDATION_CONTRACT_RED.md'
    ):
        (
                '62b82217a7b70f4a4521c228ade221fff978ef4989c2b82cfd35fc'
                '914425bce4'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_A2_A_EXPLICIT_DISCRIMINATING_E'
        'VIDENCE_MATERIALIZATION_REQUIREMENT_BINDING_CONTRACT_R'
        'ED.md'
    ):
        (
                '33e71311fd89c1167373260d27574fce20aa38704aa4a0f9dca6bc'
                '10cbebfe59'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_A2_B_REQUIREMENT_SATISFACTION_'
        'FOUNDATION_CONTRACT_RED.md'
    ):
        (
                '2c8e1368dec0d8b94a0de56b877f1497f94b05c01f80e3cd045ba4'
                'dc5900921c'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_A3_A_EXPLICIT_COMPARATIVE_DISC'
        'RIMINATION_EFFECT_ORIGIN_AUTHORIZATION_CONTRACT_RED.md'
    ):
        (
                '0568a4c5cc5b089ea8330ad048683862483a0588f37acd9c4a11b2'
                '689e182eed'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_B1_EXPLICIT_EPISTEMIC_PATH_PRE'
        'FERENCE_ORIGIN_AUTHORIZATION_CONTRACT_RED.md'
    ):
        (
                'e1b89b41a3978dea1e1c5e78e81c7deebfa46ef720126db08f3143'
                '14cfed2dcd'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C1_GOVERNED_APPLICABLE_EPISTEM'
        'IC_PATH_PREFERENCE_SET_COMPOSITION_CONTRACT_RED.md'
    ):
        (
                '972b74667c4cb8a625f291b5c359ef2ab8e4aa1e8dd06ff8409300'
                '068464f36e'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C2_A_EXPLICIT_SELECTION_DETERM'
        'INACY_BASIS_ORIGIN_AUTHORIZATION_CONTRACT_RED.md'
    ):
        (
                'f229d448bdae2565d1903ab3c77121391dedda0bc03017e426ed47'
                '87b15cf6f1'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C2_B_GOVERNED_EPISTEMIC_PATH_S'
        'ELECTION_CONTRACT_RED.md'
    ):
        (
                'a50ea382d7dd61630a03cd51d58ad15475f7c62437206624d5b45d'
                '92b769ea8b'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C3_A1_GOVERNED_AUTHORIZATION_I'
        'NPUT_CORRESPONDENCE_CONTRACT_RED.md'
    ):
        (
                'c54ed4b519e00f589f705b47cf169f0708da37b5f44c24857dc173'
                '78635b875b'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C3_A2_GOVERNED_AUTHORIZATION_I'
        'NVOCATION_RESULT_BINDING_CONTRACT_RED.md'
    ):
        (
                '5b43c1750603e0d80d5a19438209c7bc8a3ab0bffd337261bd74d4'
                '79d7ea5e8a'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C3_A3_GOVERNED_AUTHORIZATION_P'
        'RODUCTIVE_CONSUMPTION_CORRESPONDENCE_CONTRACT_RED.md'
    ):
        (
                '20b680d5873336dbaea18eb247e6d830a4f20871c36c9f6006ddbf'
                'a0cf621b6f'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C3_B1_GOVERNED_AUTHORIZED_EPIS'
        'TEMIC_ACQUISITION_ROUTE_DETERMINATION_CONTRACT_RED.md'
    ):
        (
                '0c5b79be15eb93ff203f0ebb94fe9b59fb1740a6bac9e793635ce0'
                '4ee4207e52'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_B2_C3_CLOSE_GOVERNED_AUTHORIZATIO'
        'N_AND_ACQUISITION_REACHABILITY_CLOSURE_RECONCILIATION.'
        'md'
    ):
        (
                'b251a9230bec28e238980e7b9d58924028454fe1662c95dba52bd1'
                'c347722391'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_C1_GOVERNED_SELF_EPISTEMIC_NEED_T'
        'O_ASK_DETERMINATION_CONTRACT_RED.md'
    ):
        (
                '84fa941fff79333530ed921ffdd5a4354078cb4409e49f429c1c07'
                'd64b8456d0'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_C2_GOVERNED_SELF_EPISTEMIC_NEED_C'
        'URIOSITY_EVIDENCE_PROJECTION_CONTRACT_RED.md'
    ):
        (
                'd425393759faa8727bede1827bd1e7323e4919e08ade400006e5d6'
                '3481328949'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_C3_GOVERNED_SELF_EPISTEMIC_TOPIC_'
        'EVIDENCE_REACHABILITY_DETERMINATION_CONTRACT_RED.md'
    ):
        (
                '3b1c914db9c7477cd89e6b81a4b719e5db8ce984204f4686b51732'
                'c186e86be7'
            ),
    (
        'ROBY_XI_2_R_CI_SI_S5_CLOSE_GOVERNED_SELF_EPISTEMIC_REL'
        'EVANCE_HORIZON_CLOSURE_RECONCILIATION.md'
    ):
        (
                '77e830026c1bf7dc0cfd4e3b8fa13db7f7c1a883beb2ada62f4633'
                '5490035ac4'
            ),
    (
        'ROBY_XI_2_R_DOC_ROOT_1_GOVERNED_HISTORICAL_ROOT_ARCHIV'
        'AL_CONTRACT_RED.md'
    ):
        (
                '22e9fda174b224f904222fc56aa877f2484595da4b8c72bce9037b'
                '5330a96ea8'
            ),
}

STATIC_ROOT = {
    'README.md':
        (
                '403d7edc48794629253f045ea0c682ef48d73a2a82fcaf91db8e4e'
                '75b87259dc'
            ),
    'VISION.md':
        (
                '46e274fadca4e3c7f7919c6b52ce3216db3d56ac9fdc4d681ba20c'
                'ff177d49ec'
            ),
    'architecture_rules.md':
        (
                'bb1520a81c32bc2e7c692ef2b1eff8badaf9ced30ff4e239aed751'
                '50c33c189b'
            ),
    'ROBY_XI_2_FUTURE_CAPABILITIES_AND_EVOLUTION_GUIDE.md':
        (
                '9706ee24bec3a4d507b4ed3fe90a23684f784a407bd63537e19695'
                '30ffde1c42'
            ),
    'CHANGELOG.md':
        (
                'ab7749bab78d8ea39a816a15de349300efdd471edddb9182f3c4b7'
                '8c32fcb1c0'
            ),
    'CHANGELOG_ARCHITECTURE.md':
        (
                'd85bd47961700d6cdc578eb8874b457b3fbeff1f8fe8269aa338aa'
                '4f9a1e4fd8'
            ),
    'external_capabilities.md':
        (
                'a7d41aad25be74157315bdfbe83cf0883071755edf70af0afc57c6'
                '939a4df908'
            ),
    'integration_decision.md':
        (
                'ec7eae242062b033a6d91b588d4d851bb05bdc9754da8b0ef637ea'
                '39d3e1fa7b'
            ),
}

EVOLVABLE_UNCHANGED = {
    'ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md':
        (
                '973b41c614b401915d0429bb3206f742fbfc1057779fd8fc577861'
                '30b6eeb320'
            ),
}

EVOLVABLE_ROOT_PRESENCE = {
    (
        'ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GU'
        'IDE.md'
    ),
}

NORTH_STAR = (
    'ROBY_XI_2_CONVERSATIONAL_IDENTITY_SELF_INQUIRY_NORTH_STAR.md',
    '5d9636eac13ed0ff097cb2feb1667b8e31603bc8f51d19442966fce395704b3e',
)

REQUIRED_CURRENT_TRUTH_TERMS = (
    "13,110 PASS",
    "NEED_TO_ASK",
    "MultisourceKnowledgeGapEvidence",
    "relevance=UNKNOWN",
    "NO_COMPATIBLE_GOVERNED_TOPIC_EVIDENCE_ROUTE",
    "No C4",
    "STOP before Relevance",
)

REQUIRED_CURRENT_TRUTH_SECTIONS = (
    "CURRENT CERTIFIED BASELINE",
    "CANONICAL DOCUMENTARY AUTHORITIES",
    "CERTIFIED / FROZEN ARCHITECTURAL BOUNDARIES",
    "CURRENT OPEN RESIDUALS",
    "REMAINING MASTER PLAN HORIZONS",
    "NEXT AUTHORIZED STEP",
    "HISTORICAL PROVENANCE",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_s1_archives_exact_24_file_manifest_byte_identical() -> None:
    for name, expected_sha256 in MOVE_MANIFEST.items():
        source = ROOT / name
        destination = ARCHIVE / name
        assert not source.exists(), f"S1: historical record still in root: {name}"
        assert destination.is_file(), f"S1: archive missing: {name}"
        assert _sha256(destination) == expected_sha256, name


def test_s1_root_markdown_surface_is_exactly_12_files() -> None:
    actual = {path.name for path in ROOT.glob("*.md")}
    expected = (
        set(STATIC_ROOT)
        | set(EVOLVABLE_UNCHANGED)
        | EVOLVABLE_ROOT_PRESENCE
        | {
        "ROBY_XI_2_CURRENT_TRUTH.md",
            NORTH_STAR[0],
        }
    )
    assert actual == expected
    assert len(actual) == 12


def test_s1_preserves_static_root_authorities_byte_identical() -> None:
    for name, expected_sha256 in STATIC_ROOT.items():
        path = ROOT / name
        assert path.is_file(), name
        assert _sha256(path) == expected_sha256, name


def test_s1_preserves_unchanged_evolvable_masters() -> None:
    # S1 digest remains frozen in EVOLVABLE_UNCHANGED as historical evidence.
    # Later governed changes to the live master must not fail this root gate.
    for name in EVOLVABLE_UNCHANGED:
        path = ROOT / name
        assert path.is_file(), name


def test_s1_preserves_evolvable_cognitive_master_root_authority() -> None:
    for name in EVOLVABLE_ROOT_PRESENCE:
        path = ROOT / name
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8")
        assert "Cognitive Inventory Reconciliation" in text
        assert "Master Surgical Guide" in text


def test_s1_keeps_active_north_star_in_root_byte_identical() -> None:
    name, expected_sha256 = NORTH_STAR
    path = ROOT / name
    assert path.is_file()
    assert _sha256(path) == expected_sha256


def test_s1_current_truth_is_compact_operational_entrypoint() -> None:
    text = CURRENT_TRUTH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) <= 400
    for section in REQUIRED_CURRENT_TRUTH_SECTIONS:
        assert section in text, section
    for term in REQUIRED_CURRENT_TRUTH_TERMS:
        assert term in text, term


def test_s1_current_truth_does_not_embed_closed_contract_chronology() -> None:
    text = CURRENT_TRUTH.read_text(encoding="utf-8")
    for name in MOVE_MANIFEST:
        assert name not in text, name


def test_s1_scope_is_exact_and_non_destructive() -> None:
    assert len(MOVE_MANIFEST) == 24
    assert len(STATIC_ROOT) == 8
    assert len(EVOLVABLE_UNCHANGED) == 1
    assert len(EVOLVABLE_ROOT_PRESENCE) == 1
    assert NORTH_STAR[0] not in MOVE_MANIFEST
    assert "ROBY_XI_2_CURRENT_TRUTH.md" not in MOVE_MANIFEST
    assert set(MOVE_MANIFEST).isdisjoint(STATIC_ROOT)
    assert set(MOVE_MANIFEST).isdisjoint(EVOLVABLE_UNCHANGED)
    assert set(MOVE_MANIFEST).isdisjoint(EVOLVABLE_ROOT_PRESENCE)
