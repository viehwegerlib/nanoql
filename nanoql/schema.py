'''
Use case: Given a list of accession ids, get both taxonomic info and sequence info from it. Sequence can be raw reads, assembly (curation level 1) or annotation (curation level 2).

https://stackoverflow.com/questions/39381436/graphql-django-resolve-queries-using-raw-postgresql-query

https://github.com/graphql-python/graphene/issues/462
https://github.com/graphql-python/graphene/issues/431
'''


from graphene import Schema, ObjectType
from graphene import Int, String, ID, Field, List

from nanoql.fields import Lineage, InputLineage
from nanoql.fields import Taxon, InputTaxon
from nanoql.fields import Sequence, InputSequence
from nanoql.resolver import resolve_taxon


class Query(ObjectType):
    taxon = List(  # do we need a list?
        Taxon,
        # all the following are arguments, i.e. in the query: taxon(<arguments>){...}
        description='Description of the entire class',
        key=ID(
            description='(Synonymous/ approximate) name or NCBI ID of taxon.',
            default_value=42),
        n_children=Int(
            description='The number of children to return.',
            default_value=int(1e6)),  # basically "all"
        resolver=resolve_taxon)


schema = Schema(query=Query, auto_camelcase=False)


'''
{
  taxon(key: "Pseudomonas aeruginosa", n_children: 4) {
    taxid
    stats
    name
    lineage {
      family
      order
      cls
      phylum
    }
    children {
      name
      taxid
    }
  }
}


{
  taxon(key: 287) {
    stats
  }
}


# nice error messages
{
  taxon(key: 278) {
    stats
  }
}
'''

