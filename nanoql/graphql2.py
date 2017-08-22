'''
Use case: Given a list of accession ids, get both taxonomic info and sequence info from it. Sequence can be raw reads, assembly (curation level 1) or annotation (curation level 2).
'''

import json
import graphene
from graphene import InputObjectType, ObjectType, String, ID, Field, List
# from graphene.types.json import JSONString


class Sequence(ObjectType):
    '''Gets passed a dict (from e.g. InputSequence object).'''
    seqid = ID()
    seq = List(String)

    def resolve_seqid(self, args, context, info):
        return int(self.get('seqid')[-1]) + 1

    def resolve_seq(self, args, context, info):
        from nanoql.restapi import fetch_uid, fmt_fasta

        result = fetch_uid(uid=self.get('seqid'), context='ncbi')
        header, seq = next(fmt_fasta(result))
        return ['fasta', header + '\n' + seq + '\n']  # problem: this is a string


class Taxon(ObjectType):
    taxid = ID()
    name = String()
    sequence = Field(Sequence)

    def resolve_taxid(self, args, context, info):
        return self.get('taxid')

    def resolve_name(self, args, context, info):
        return self.get('name')

    def resolve_sequence(self, args, context, info):
        return self.get('sequence')


# https://github.com/graphql-python/graphene/issues/431
class InputSequence(InputObjectType):
    seqid = ID()
    seq = String()


class Query(ObjectType):
    taxon = List(  # why not Field? because returns list?
        Taxon,
        taxid=List(ID),
        name=String(),
        sequence=InputSequence()
    )

    def resolve_taxon(self, args, context, info):
        # to return multiple results, just return them
        return [dict(
            taxid=k, name='pseudomonas',
            sequence={"seqid": k, "seq": "ACTG"})
            # in the query this could be
            # taxon(sequence: {seqid: K3232, ...})
            # i.e. we could pass this directly via InputSequence object
            # note also how to pass a param from taxon down to sequence (k)
                for k in args['taxid']]

    # sequence2 = Field(
    #     Sequence2,
    #     seqid = ID(),
    #     seq = String()
    # )

    sequence = List(
        Sequence,
        seqid = List(ID),
        seq = String()  # this is the reason a string is returned from Sequence object
    )

    def resolve_sequence(self, args, context, info):
        return [dict(seqid=k) for k in args['seqid']]

schema = graphene.Schema(query=Query)


# Aim: For a list of IDs, get the taxon info as well as the sequencing info.
params = {'key': ["KC790375", "KC790376", "KC790377"]}
query = '''
query($key: [ID]) {
  taxon(taxid: $key, ) {
    taxid
    name
    sequence {
      seqid
      seq
    }
  }
}
'''

# e = schema.execute(query, variable_values=params)
# e.data, e.errors, e.invalid
# print(json.dumps(e.data, indent=2))


# query = '''
# query {
#   sequence(seq: "ACTG", seqid: "KC790375") {
#     seqid
#     seq
#     }
# }
# '''
#
# e = schema.execute(query)
# e.data, e.errors, e.invalid


'''
query{
  sequence(seqid: ["KC750375", "KC750376"]){
    seq
    seqid
  }
}

query {
  taxon(taxid: ["KC750375", "KC750377"]) {
    taxid
    name
    sequence {
      seqid
      seq
    }
  }
}
'''