#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
# Copyright 2023-2024 Arm Ltd.

import sys
import argparse
import urllib

import dtschema


def path_list_to_str(path):
    return '/' + '/'.join(path)


def prop_generator(schema, path=[]):
    if not isinstance(schema, dict):
        return
    for prop_key in ['properties', 'patternProperties']:
        if prop_key in schema:
            for p, sch in schema[prop_key].items():
                yield path + [prop_key, p], sch
                yield from prop_generator(sch, path=path + [prop_key, p])


def _ref_to_id(schema_id, ref):
    ref = urllib.parse.urljoin(schema_id, ref)
    if '#/' not in ref:
        ref += '#'
    return ref


def _prop_in_schema(prop, schema, schemas):
    for p, sch in prop_generator(schema):
        if p[1] == prop:
            return True

    if 'allOf' in schema:
        for e in schema['allOf']:
            if '$ref' in e:
                ref_id = _ref_to_id(schema['$id'], e['$ref'])
                if ref_id in schemas:
                    if _prop_in_schema(prop, schemas[ref_id], schemas):
                        return True

    if '$ref' in schema:
        ref_id = _ref_to_id(schema['$id'], schema['$ref'])
        if ref_id in schemas and _prop_in_schema(prop, schemas[ref_id], schemas):
            return True

    return False


def check_removed_property(schema_id, base, schemas):
    for p, sch in prop_generator(base):
        if not _prop_in_schema(p[1], schemas[schema_id], schemas):
            print(f'{schema_id}{path_list_to_str(p)}: existing property removed', file=sys.stderr)


def check_deprecated_property(schema_id, base, schemas):
    for p, sch in prop_generator(base):
        if isinstance(sch, dict) and 'deprecated' in sch:
            continue
        schema = schema_get_from_path(schemas[schema_id], p)
        if schema and isinstance(schema, dict) and 'deprecated' in schema:
            print(f'{schema_id}{path_list_to_str(p)}: existing property deprecated', file=sys.stderr)


def schema_get_from_path(sch, path):
    for p in path:
        try:
            sch = sch[p]
        except:
            return None
    return sch


def check_new_items(schema_id, base, new):
    for p, sch in prop_generator(new):
        if not isinstance(sch, dict) or 'minItems' not in sch:
            continue

        new_min = sch['minItems']
        base_min = schema_get_from_path(base, p + ['minItems'])

        if base_min and new_min > base_min:
            print(f'{schema_id}{path_list_to_str(p)}: required entries increased from {base_min} to {new_min}', file=sys.stderr)


def _get_required(schema):
    required = []
    for k in {'allOf', 'oneOf', 'anyOf'} & schema.keys():
        for sch in schema[k]:
            if 'required' not in sch:
                continue
            required += sch['required']

    if 'required' in schema:
        required += schema['required']

    return set(required)


def _check_required(schema_id, base, new, path=[]):
    if not isinstance(base, dict) or not isinstance(new, dict):
        return

    base_req = _get_required(base)
    new_req = _get_required(new)

    if not new_req:
        return

    diff = new_req - base_req
    if diff:
        print(f'{schema_id}{path_list_to_str(path)}: new required properties added: {", ".join(diff)}', file=sys.stderr)
        return


def check_required(schema_id, base, new):
    _check_required(schema_id, base, new)

    for p, sch in prop_generator(new):
        _check_required(schema_id, schema_get_from_path(base, p), sch, path=p)


def main():
    ap = argparse.ArgumentParser(description="Compare 2 sets of schemas for possible ABI differences")
    ap.add_argument("baseline", type=str,
                    help="Baseline schema directory or preprocessed schema file")
    ap.add_argument("new", type=str,
                    help="New schema directory or preprocessed schema file")
    ap.add_argument('-V', '--version', help="Print version number",
                    action="version", version=dtschema.__version__)
    args = ap.parse_args()

    base_schemas = dtschema.DTValidator([args.baseline]).schemas
    schemas = dtschema.DTValidator([args.new]).schemas

    if not schemas or not base_schemas:
        return -1

    for schema_id, sch in schemas.items():
        if schema_id not in base_schemas or 'generated' in schema_id:
            continue

        check_required(schema_id, base_schemas[schema_id], sch)
        check_removed_property(schema_id, base_schemas[schema_id], schemas)
        check_deprecated_property(schema_id, base_schemas[schema_id], schemas)
        check_new_items(schema_id, base_schemas[schema_id], sch)
