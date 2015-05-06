# dcp

The database copy tool. Copy data between databases intelligently, using the
schema's structure.

## Methodology

Given a table T1, its parents are defined as those tables on which T1
has a foreign key dependency. Its children are defined as those tables
on which T1 is the target of a foreign key dependency.

To extract data, we start by enumerating the rows of T1. For each row
R, we then step through each of the parents of T1 and extract rows
from them that satisfy the dependencies of R. For any parents of those
parents we repeat this process recursively.

An analogous process is used for children - given the row R from T1,
we iterate through each child table and extract any rows that depend
on R, and repeat this recursively for children of the children.

Rows are emitted in dependency-order, such that if they were inserted
in the same order they'd satisfy all foreign key constraints.

Memoization is done on the query level to reduce duplicates in the
returned data, though it is still theoretically possible for
duplicates to occur. In particular, if a row is the target of two
separate foreign key dependencies, where each key is dependent on a
different column of the target table, then the row may be enumerated
twice. However, FK target columns should be primary keys, so this
isn't an excessively restrictive requirement.

## Caveats

### Backend-specific Notes

#### sqlite

Foreign key constraints declared without a column specification in the
source database aren't properly introspected, which causes issues
during schema reflection. To work around this, for now make sure to
avoid this pattern:

    CREATE TABLE distributors (
      id bigint PRIMARY KEY,
      ...
    );

    CREATE TABLE movies (
      ...
      distributor bigint REFERENCES distributors
    );

And instead declare foreign keys like so:

    CREATE TABLE distributors (
      id bigint PRIMARY KEY,
      ...
    );

    CREATE TABLE movies (
      ...
      distributor bigint REFERENCES distributors (id)
    );
