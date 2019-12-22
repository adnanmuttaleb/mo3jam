import uuid

from mo3jam import create_app, db
from mo3jam.models import Role

roles = [
    {
        'name': 'superuser',
        'id': uuid.uuid4()
    },
    {
        'name': 'editor',
        'id': uuid.uuid4()
    },
    {
        'name': 'member',
        'id': uuid.uuid4()
    }
]

if __name__ == "__main__":
    app = create_app()
    with app.app_context() as ctx:
        for role_data in roles:
            role = Role(**role_data)
            role.save()

