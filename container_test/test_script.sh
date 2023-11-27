cp /home/container_test/test_concepts/* /home/concepts_json
mkdir -p /home/output/csis/volume_test
mkdir -p /home/output/scpe/volume_test
cp /home/container_test/test_ttl/* /home/output/csis/volume_test
python3 /home/pipeline.py
