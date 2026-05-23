import os


def test_data_folder_exists():
    assert os.path.exists("data")


def test_policy_documents_exist():
    files = os.listdir("data")
    policy_files = [f for f in files if f.endswith(".md") or f.endswith(".txt") or f.endswith(".pdf")]
    assert len(policy_files) >= 5