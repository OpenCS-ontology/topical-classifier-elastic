cp /home/container_test/test_concepts/* /home/concepts_json
mkdir /home/output/csis
mkdir /home/output/scpe
cp /home/container_test/test_ttl/* /home/output/csis
python3 /home/pipeline.py
