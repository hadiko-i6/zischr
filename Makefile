grpc: rpc/main.proto
	@echo "[INFO] if code generation fails, try 'pip install grpcio-tools'"
	protoc -I rpc/ rpc/main.proto --go_out=plugins=grpc:backend/rpc/
	protoc -I rpc/ rpc/main.proto --go_out=plugins=grpc:backend/rpc/
	python -m grpc_tools.protoc -Irpc/ --python_out=frontend/ --grpc_python_out=frontend/ rpc/main.proto
	@echo "[INFO] Remember to commit generated code to the repository!"
