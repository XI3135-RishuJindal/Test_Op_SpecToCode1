# ============================================================
# Makefile — Account Management Service
# GnuCOBOL build system
# ============================================================

COBC        ?= cobc
COBC_FLAGS  ?= -x -free
BIN_DIR     ?= ./bin
SRC_DIR     := ./src
COPY_DIR    := $(SRC_DIR)/copybooks

# ── Source files ─────────────────────────────────────────────
DOMAIN_SRC   := $(SRC_DIR)/domain/ACCTDMN.cbl
PORT_SRC     := $(SRC_DIR)/ports/ACCTPORT.cbl
FILE_SRC     := $(SRC_DIR)/adapters/secondary/ACCTFILE.cbl
IMPORT_SRC   := $(SRC_DIR)/adapters/secondary/ACCTIMPT.cbl
API_SRC      := $(SRC_DIR)/adapters/primary/ACCTAPI.cbl
HEALTH_SRC   := $(SRC_DIR)/adapters/primary/ACCTHLTH.cbl

ALL_PROGRAMS := ACCTDMN ACCTPORT ACCTFILE ACCTIMPT ACCTAPI ACCTHLTH

.PHONY: all compile clean test run help

# ── Default target ───────────────────────────────────────────
all: compile

# ── Create bin directory ─────────────────────────────────────
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# ── Compile all programs ─────────────────────────────────────
compile: $(BIN_DIR)
	$(COBC) $(COBC_FLAGS) -I $(COPY_DIR) -o $(BIN_DIR)/ACCTDMN   $(DOMAIN_SRC)
	$(COBC) $(COBC_FLAGS) -I $(COPY_DIR) -o $(BIN_DIR)/ACCTPORT  $(PORT_SRC)
	$(COBC) $(COBC_FLAGS) -I $(COPY_DIR) -o $(BIN_DIR)/ACCTFILE  $(FILE_SRC)
	$(COBC) $(COBC_FLAGS) -I $(COPY_DIR) -o $(BIN_DIR)/ACCTIMPT  $(IMPORT_SRC)
	$(COBC) $(COBC_FLAGS) -I $(COPY_DIR) -o $(BIN_DIR)/ACCTAPI   $(API_SRC)
	$(COBC) $(COBC_FLAGS) -I $(COPY_DIR) -o $(BIN_DIR)/ACCTHLTH  $(HEALTH_SRC)
	@echo "✓ All programs compiled to $(BIN_DIR)/"

# ── Run health check ─────────────────────────────────────────
run: compile
	$(BIN_DIR)/ACCTHLTH

# ── Run test suite ───────────────────────────────────────────
test: compile
	python3 -m pytest tests/ -v --tb=short

# ── Clean build artifacts ────────────────────────────────────
clean:
	rm -rf $(BIN_DIR)
	find . -name "*.o" -delete
	find . -name "*.so" -delete
	@echo "✓ Build artifacts cleaned"

# ── Help ─────────────────────────────────────────────────────
help:
	@echo "Account Management Service — Makefile targets:"
	@echo "  make compile   Compile all COBOL programs"
	@echo "  make run       Compile and run health check"
	@echo "  make test      Compile and run test suite"
	@echo "  make clean     Remove compiled binaries"
