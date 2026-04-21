# ==========================================
#  Call_Me_Maybe Project Makefile
# ==========================================

# プロジェクト名とメインスクリプト
NAME        = call_me_maybe
MAIN_SCRIPT = call_me_maybe.py

MAIN_DERECTRY = src

# ==========================================
#  Rules
# ==========================================

.PHONY: all install run debug clean lint lint-strict build re

all: install

# ------------------------------------------
#  Environment Setup
# ------------------------------------------
install: ## 仮想環境を作成し、依存関係をインストールする
	@echo "Creating virtual environment..."
	@echo "Installing dependencies..."
	uv sync
	@echo "Setup complete! Run 'make run' to start."

# ------------------------------------------
#  Execution
# ------------------------------------------
run: ## メインプログラムを実行
	@echo "Running $(NAME)..."
	uv run python $(MAIN_DERECTRY)/$(MAIN_SCRIPT)

debug: ## pdbデバッガを使って実行
	@echo "Debugging $(NAME)..."
	uv run python -pdb $(MAIN_DERECTRY)/$(MAIN_SCRIPT)

# ------------------------------------------
#  Quality Control
# ------------------------------------------
lint: ## Flake8とMypyによる静的解析を実行
	@echo "Running Linter (Standard)..."
	uv run flake8 .
	uv run mypy .

lint-strict: ## より厳しいMypyチェックを実行
	@echo "Running Linter (Strict)..."
	uv run flake8 .
	uv run mypy --strict .

# ------------------------------------------
#  Cleanup
# ------------------------------------------
clean: ## 一時ファイルやキャッシュを削除
	@echo "Cleaning up..."
	@rm -rf __pycache__
	@rm -rf **/__pycache__
	@rm -rf .mypy_cache
	@rm -rf .pytest_cache
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@rm -rf .ruff_cache
	@rm -rf data/output
	@echo "Clean complete."

fclean: clean ## cleanに加えて仮想環境も削除
	@echo "Full Cleaning up..."
	@rm -rf .venv
	@rm -rf ~/.cache/huggingface/hub/
	@echo "Full Clean complete."

re: fclean all
