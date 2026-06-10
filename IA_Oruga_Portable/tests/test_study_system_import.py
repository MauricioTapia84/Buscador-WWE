import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
# prefer ia-oruga/backend/study_system or ia-oruga/backend/src/study_system
study_system_path = ROOT / 'backend' / 'study_system'
if study_system_path.exists():
    sys.path.insert(0, str(ROOT / 'backend'))
else:
    # fallback to ia-oruga/backend/src if present
    sys.path.insert(0, str(ROOT / 'backend' / 'src'))

def test_import_study_system():
    try:
        import study_system
    except Exception as e:
        raise AssertionError(f"Importing study_system failed: {e}")
