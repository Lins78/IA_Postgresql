from src.apps.main import IAPostgreSQL
from web_app import get_database_inspection_data

if __name__ == '__main__':
    ia_system = IAPostgreSQL()
    try:
        inspection = get_database_inspection_data()
        print('INSPECTION_OK')
        print(inspection)
    except Exception as e:
        import traceback
        print('ERROR', type(e).__name__, str(e))
        traceback.print_exc()
