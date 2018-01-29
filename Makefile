.PHONY: all
all: # empty default


.PHONY: deploy deploy-checkvar
deploy-checkvar:
ifndef DEPLOYDIR
    $(error DEPLOYDIR is undefined)
endif

deploy:
	@echo "[INFO] deploying to $(DEPLOYDIR)"
	mkdir -p "$(DEPLOYDIR)"
	go build -o $(DEPLOYDIR)/backend github.com/hadiko-i6/zischr/backend
	cp -r frontend $(DEPLOYDIR)/frontend
	install -m755 scanner.py $(DEPLOYDIR)/scanner.py
	@echo "[INFO] deployed to $(DEPLOYDIR)"
	rm -rf build

.PHONY: codegen
codegen: codegen-grpc
	make -C frontend codegen
	@echo "[INFO] Remember to commit generated code to the repository!"

.PHONY: codegen-grpc
codegen-grpc: rpc/main.proto
	@echo "[INFO] if code generation fails, try 'pip install grpcio-tools'"
	protoc -I rpc/ rpc/main.proto --go_out=plugins=grpc:backend/rpc/
	protoc -I rpc/ rpc/main.proto --go_out=plugins=grpc:backend/rpc/
	python -m grpc_tools.protoc -Irpc/ --python_out=frontend/ --grpc_python_out=frontend/ rpc/main.proto
