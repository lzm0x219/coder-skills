#!/usr/bin/env python3
"""Validate traceability relations, without claiming source truth or behavior."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def section(content, title):
    pattern = rf'^## {re.escape(title)}\n(.*?)(?=^## |\Z)'
    match = re.search(pattern, content, re.M | re.S)
    if not match:
        raise ValueError(f'Missing section: {title}')
    return match.group(1)


def rows(content):
    result = []
    for line in content.splitlines():
        if line.startswith('| '):
            result.append([cell.strip() for cell in line.strip().strip('|').split('|')])
    return result


def anchors(content):
    # All linked rule headings use ordinary text and optional Latin identifiers.
    result = set()
    for title in re.findall(r'^#+ (.+)$', content, re.M):
        slug = re.sub(r'[^\w\-\s]', '', title.lower()).replace(' ', '-')
        result.add(slug)
    return result


def main():
    basis = ROOT / 'references/basis.md'
    text = basis.read_text()
    source_rows = [row for row in rows(section(text, '来源登记')) if re.fullmatch(r'[FWI]\d+', row[0])]
    source_ids = {row[0] for row in source_rows}
    abstract_ids = {row[0] for row in source_rows if 'Abstract' in row[2]}
    if len(source_rows) != len(source_ids) or not source_ids:
        raise ValueError('Duplicate or empty source registry')
    for row in source_rows:
        if len(row) != 4 or not re.search(r'\]\(https://[^)]+\)', row[1]):
            raise ValueError(f'Incomplete source record: {row[0]}')

    cases = {row[0] for row in rows((ROOT / 'tests/rubric.md').read_text()) if re.fullmatch(r'[a-z][a-z-]*', row[0])}
    control_rows = [row for row in rows(section(text, '执行映射')) if re.fullmatch(r'RF\d+', row[0])]
    if not control_rows or len({row[0] for row in control_rows}) != len(control_rows):
        raise ValueError('Duplicate or empty controls')
    allowed_levels = {'原文支持', '方法推导', '项目机制', '标准背景'}
    allowed_evidence = {'受控运行', '受控运行与结构走查', '分阶段运行', '受控运行与状态走查', '分阶段运行与受控运行', '分阶段运行与状态走查', '带提示运行与分阶段运行', '静态来源核验'}
    used_sources, used_cases = set(), set()
    for row in control_rows:
        if len(row) != 7:
            raise ValueError(f'Wrong column count: {row[0]}')
        identifier, rule, source, level, gate, case, evidence = row
        if level not in allowed_levels or evidence not in allowed_evidence:
            raise ValueError(f'Unknown evidence/derivation class: {identifier}')
        links = re.findall(r'\[[^]]+\]\(([^)]+)\)', rule)
        if not links:
            raise ValueError(f'No authoritative rule link: {identifier}')
        for target in links:
            name, _, heading = target.partition('#')
            file = basis.parent / name
            if not file.is_file() or (heading and heading not in anchors(file.read_text())):
                raise ValueError(f'Invalid rule pointer: {identifier}: {target}')
        sources = set(re.findall(r'\b[FWI]\d+\b', source))
        if not sources and level != '项目机制':
            raise ValueError(f'Missing source: {identifier}')
        if not sources <= source_ids:
            raise ValueError(f'Unknown source: {identifier}: {sources - source_ids}')
        if level == '原文支持' and sources & abstract_ids:
            raise ValueError(f'Abstract-only source cannot support direct normative mapping: {identifier}')
        if not re.fullmatch(r'S[0-5](?:/S[0-5])*', gate):
            raise ValueError(f'Unknown state gate: {identifier}: {gate}')
        selected_cases = set(case.split(', '))
        if not selected_cases <= cases:
            raise ValueError(f'Unknown case: {identifier}: {selected_cases - cases}')
        used_sources.update(sources)
        used_cases.update(selected_cases)
    if source_ids - used_sources:
        raise ValueError(f'Unused source records: {source_ids - used_sources}')
    print(f'PASS traceability: {len(source_ids)} sources, {len(control_rows)} controls, {len(used_cases)} referenced cases')
    print('LIMIT: relation integrity only; source semantics, runtime coverage and ISO conformance require separate evidence')


if __name__ == '__main__':
    main()
