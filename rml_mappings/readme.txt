To run the mappings you need to download the rml mapper (https://github.com/RMLio/rmlmapper-java) and have the mapping file and csv file in the same directory.
The command to run the mapping is: 

java -jar rmlmapper-7.3.1-r374-all.jar -m updated_parsec_mapping.ttl -o output.rdf
-m represents the mapping file
-o represents the output file


The output can also be of the following type 
rdf (RDF/XML — default)
ttl (Turtle — what you want)
nq (N-Quads)
nt (N-Triples)


