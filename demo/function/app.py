import os
from typing import TypedDict, Optional
from pyiceberg.catalog import load_catalog
from pyiceberg.expressions import EqualTo

database_name = os.getenv("ICEBERG_DATABASE_NAME")
table_name = os.getenv("ICEBERG_TABLE_NAME")

catalog = load_catalog("glue")
table = catalog.load_table(f"{database_name}.{table_name}")


def handler(event: "Query", context) -> "list[dict]":
    scan = table.scan()

    if "name" in event and event["name"]:
        scan = scan.filter(EqualTo("name", event["name"]))
    if "recid" in event and event["recid"]:
        scan = scan.filter(EqualTo("votes.recid", event["recid"]))
    if "suburb" in event and event["suburb"]:
        scan = scan.filter(EqualTo("votes.suburb", event["suburb"]))
    if "postcode" in event and event["postcode"]:
        scan = scan.filter(EqualTo("votes.postcode", event["postcode"]))

    limit = event["limit"] if "limit" in event else 10

    result = scan.to_arrow().slice_length(limit)

    return result.to_pylist()


class Query(TypedDict):
    name: "Optional[str]"
    recid: "Optional[str]"
    suburb: "Optional[str]"
    postcode: "Optional[str]"
    limit: "Optional[int]"
