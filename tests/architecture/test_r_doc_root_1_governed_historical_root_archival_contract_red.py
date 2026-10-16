from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "docs/history/root-archive-post-g22"

MOVE_MANIFEST = {
    (
        'ROBY_XI_2_2026_09_22_MASTER_PLAN_1_13_RECONCILIATION.md'
    ): (
        '380ad6df9fb3909511ade3d2b2064477905d0feb2ae9f69826b047f781243b5c'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C1_S1_PARTICIPATION_FEEDBACK_PROJECTION_CONTRAC'
        'T_RED.md'
    ): (
        '11a057676814fce5d84cdd935b7ccdba2dfc386a195e9934de9d21788be0342e'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C1_S1_PARTICIPATION_FEEDBACK_PROJECTION_GREEN_S'
        'URGICAL.md'
    ): (
        'b8d111a5b7fd1cca6624103242b6d743ffb5eca45524255c59dded7ed0e1b6f6'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S1_BOUNDED_GOVERNED_PLACE_BUSINESS_SOU'
        'RCE_QUERY_COMPOSITION_CONTRACT_RED.md'
    ): (
        '5cc9caabb23c9993ca8dbb9aa0b76bf0b5c52c93d449f867b5912c7a59bd31a0'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S1_BOUNDED_GOVERNED_PLACE_BUSINESS_SOU'
        'RCE_QUERY_COMPOSITION_GREEN_SURGICAL.md'
    ): (
        '8bcd5fd83080af3837f59e9ebd2cc095a56d9e7dacbc73759faf778ba896ebbf'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2A_PROVIDER_CONFIGURATION_ENABLEMENT_'
        'RECONCILIATION.md'
    ): (
        'd92a96c10955d5436659790d9cdc5ff516662374552440b051d8cfd94f48f901'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2A_PROVIDER_SOURCE_CREDENTIAL_GATED_E'
        'NABLEMENT_CONTRACT_RED.md'
    ): (
        '245239033ac82e4ef36361ad7416cd3df4cf564cae6b73faf6a7b9a427d936f3'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2A_RC1_GREEN_SURGICAL.md'
    ): (
        '276d901c21224bb4e8dde11737b295796042b34d0e8f4672cc0eff8769ad420c'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2A_RC1_NON_DEFAULT_SOURCE_EXTENSION_C'
        'ONTRACT_RED.md'
    ): (
        '10234a7dce65e60fe30dc2a86ee8f83456e89be5b289450b600f978c08bd9213'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2A_RC1_NON_DEFAULT_SOURCE_EXTENSION_S'
        'EAM_RECONCILIATION.md'
    ): (
        'd47704aeb3d440098fc1ac2573b66725401edd3a6aa65a2ff6c41877ddc04d9e'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2B_A_AUTHORIZED_EXECUTION_M400_INGRES'
        'S_CONTRACT_RED.md'
    ): (
        '4834cc1d00757b409a82ae95c1324f9fe649e73140bf9ce2ae10bd923aba7980'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2B_A_AUTHORIZED_EXECUTION_M400_INGRES'
        'S_GREEN_SURGICAL.md'
    ): (
        'de482ae36a19859acbcb3bbce29c44ff70609566572c0121240a0796431fd5ac'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2B_B_M400_M401_COGNITIVE_ADMISSION_HA'
        'NDOFF_CONTRACT_RED.md'
    ): (
        'c941d968ecd5b372954cfb387811ae6f94bbfebc793a58ceeb0cfbf36cc83e06'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2B_B_M400_M401_COGNITIVE_ADMISSION_HA'
        'NDOFF_GREEN_SURGICAL.md'
    ): (
        '0f35b2ca9c3c6a66d00c04626e5fe87af8803c6ef5ed05341f60438dad69b051'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2C_A_OFFICIAL_RUNTIME_FOURSQUARE_PROV'
        'IDER_AVAILABILITY_COMPOSITION_CONTRACT_RED.md'
    ): (
        '85f8ddd289c40448a6693317b27553a8dbd3acf5b8a4cba4553745a47e28036f'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2C_A_OFFICIAL_RUNTIME_FOURSQUARE_PROV'
        'IDER_AVAILABILITY_COMPOSITION_GREEN_SURGICAL.md'
    ): (
        '1f199e75458d64a5be79f7a021c92f7c5de0e04fb571a2d660fc3e0a39ae213f'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2C_B_EXPLICIT_TURN_CONVERSATIONAL_HAN'
        'DOFF_CONTRACT_RED.md'
    ): (
        '482b6440f968164218e60e4f66af4db26d21607480039347cd3ab537a32ca520'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2C_B_GREEN_SURGICAL.md'
    ): (
        '5a9db206f73198cf4d8b45b88c151ccffac251c68bd70a5f50ce58f9dabe0f66'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2C_B_RED_OWNER_PRECERTIFICATION_CORRE'
        'CTION.md'
    ): (
        '44d3c742675e855880dcaef0fd0f540f15c8907f98112d6a1ecd49f4696389cc'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_LOCAL_S2_PRODUCTIVE_REACHABILITY_INVENTORY.m'
        'd'
    ): (
        'a00458cee8026724fc7f26d1490cee96b3ccbb32bf0769e3f97c26d57c64f94e'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_S1_EXTERNAL_EVIDENCE_REASONING_COMPOSITION_C'
        'ONTRACT_RED.md'
    ): (
        'd0896466c21b1d533cc18cbaa5d3f18b0bfcff54a71bdaf0ac1173d9822391c5'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_S1_EXTERNAL_EVIDENCE_REASONING_COMPOSITION_G'
        'REEN_SURGICAL.md'
    ): (
        '7578398a3b7a58ef570799411abd3c64093ace1abc47edea925400d17607c878'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_SCI_S1_BOUNDED_SCIENTIFIC_EVIDENCE_SOURCE_DI'
        'SCRIMINATION_CONTRACT_RED.md'
    ): (
        'a1c33ac6c290be726fe57226b7d5edaed853fe5fb864c28a9f1eb4b26c0dad72'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_C2_SCI_S1_BOUNDED_SCIENTIFIC_EVIDENCE_SOURCE_DI'
        'SCRIMINATION_GREEN_SURGICAL.md'
    ): (
        'b46d178d7b62252aac472049a08dbfee0a288f7f08cd8aa57518c64a657026e1'
    ),
    (
        'ROBY_XI_2_POINT_7_P7_R1_GOVERNED_FAMILY_CONVERSATIONAL_PARTICIPATION'
        '_CONTRACT_RED.md'
    ): (
        '52dacf90ec9e034abd73caf223a787267da290ee59f2ad013e5bafe8eb769fcd'
    ),
    (
        'ROBY_XI_2_POINT_7_POST_P7_C2_LOCAL_S1_CLOSURE_MASTER_PLAN_RECONCILIA'
        'TION.md'
    ): (
        'b948d7a5be88c2684e9100c9fa6c9044467382cd6d01fcac6a3082daf831f9f5'
    ),
}

BYTE_PROTECTED_ROOT = {
    (
        'README.md'
    ): (
        '403d7edc48794629253f045ea0c682ef48d73a2a82fcaf91db8e4e75b87259dc'
    ),
    (
        'VISION.md'
    ): (
        '46e274fadca4e3c7f7919c6b52ce3216db3d56ac9fdc4d681ba20cff177d49ec'
    ),
    (
        'architecture_rules.md'
    ): (
        'bb1520a81c32bc2e7c692ef2b1eff8badaf9ced30ff4e239aed75150c33c189b'
    ),
    (
        'ROBY_XI_2_FUTURE_CAPABILITIES_AND_EVOLUTION_GUIDE.md'
    ): (
        '9706ee24bec3a4d507b4ed3fe90a23684f784a407bd63537e1969530ffde1c42'
    ),
    (
        'CHANGELOG.md'
    ): (
        'ab7749bab78d8ea39a816a15de349300efdd471edddb9182f3c4b78c32fcb1c0'
    ),
    (
        'CHANGELOG_ARCHITECTURE.md'
    ): (
        'd85bd47961700d6cdc578eb8874b457b3fbeff1f8fe8269aa338aa4f9a1e4fd8'
    ),
    (
        'external_capabilities.md'
    ): (
        'a7d41aad25be74157315bdfbe83cf0883071755edf70af0afc57c6939a4df908'
    ),
    (
        'integration_decision.md'
    ): (
        'ec7eae242062b033a6d91b588d4d851bb05bdc9754da8b0ef637ea39d3e1fa7b'
    ),
}

EVOLVABLE_ROOT_AUTHORITIES = frozenset(
    {
        "ROBY_XI_2_CURRENT_TRUTH.md",
        "ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md",
        "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md",
    }
)

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_red_r_doc_root_1_archives_exact_historical_manifest() -> None:
    for name, expected_sha256 in MOVE_MANIFEST.items():
        source = ROOT / name
        destination = ARCHIVE / name
        assert not source.exists(), f"RED R-DOC-ROOT-1: still in root: {name}"
        assert destination.is_file(), f"RED R-DOC-ROOT-1: archive missing: {name}"
        assert _sha256(destination) == expected_sha256, name


def test_red_r_doc_root_1_preserves_root_authorities_byte_identical() -> None:
    for name, expected_sha256 in BYTE_PROTECTED_ROOT.items():
        path = ROOT / name
        assert path.is_file(), f"RED R-DOC-ROOT-1: protected root missing: {name}"
        assert _sha256(path) == expected_sha256, name


def test_red_r_doc_root_1_manifest_has_exact_bounded_scope() -> None:
    assert len(MOVE_MANIFEST) == 26
    assert len(BYTE_PROTECTED_ROOT) == 8
    assert len(EVOLVABLE_ROOT_AUTHORITIES) == 3
    assert set(MOVE_MANIFEST).isdisjoint(BYTE_PROTECTED_ROOT)
    assert set(MOVE_MANIFEST).isdisjoint(EVOLVABLE_ROOT_AUTHORITIES)
    assert BYTE_PROTECTED_ROOT.keys().isdisjoint(EVOLVABLE_ROOT_AUTHORITIES)


def test_r_doc_root_1_evolvable_master_authorities_stay_at_root() -> None:
    for name in EVOLVABLE_ROOT_AUTHORITIES:
        path = ROOT / name
        assert path.is_file(), (
            f"R-DOC-ROOT-1-R1: evolvable root authority missing: {name}"
        )
        assert name not in BYTE_PROTECTED_ROOT, (
            "R-DOC-ROOT-1-R1: evolvable root authorities must not be frozen "
            "to one historical byte version"
        )
