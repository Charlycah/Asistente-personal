"""S3 surgical patch: normalize only residual explicit library-title searches."""

from pathlib import Path

TARGET = Path('app/governed_local_library_runtime_wiring.py')
OLD = '''        if compound_document_query is not None:
            return compound_document_query.group(1).strip()
        return query
'''
NEW = '''        if compound_document_query is not None:
            return compound_document_query.group(1).strip()
        # Only the residual explicit-search path needs title cleanup.
        query = re.sub(
            r"^(?:el\\s+)?(?:libro|documento)\\s+",
            "",
            query,
            count=1,
            flags=re.IGNORECASE,
        )
        return query.strip().rstrip(".?! ").strip()
'''


def main() -> None:
    if not TARGET.is_file():
        raise SystemExit(f'S3 STOP: missing canonical file: {TARGET}')
    source = TARGET.read_text(encoding='utf-8-sig')
    if source.count(OLD) != 1:
        if NEW in source:
            raise SystemExit('S3 STOP: patch already applied')
        raise SystemExit('S3 STOP: expected canonical anchor not found exactly once')
    revised = source.replace(OLD, NEW, 1)
    compile(revised, str(TARGET), 'exec')
    TARGET.write_text(revised, encoding='utf-8')
    print(f'S3 GREEN applied: {TARGET}')


if __name__ == '__main__':
    main()
