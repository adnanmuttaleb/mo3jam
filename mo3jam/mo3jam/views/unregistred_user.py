import uuid

from flask import request, current_app
from flask_restplus import Resource, Namespace

from mo3jam.models import UnRegisteredUser
from mo3jam.schemas import UnRegisteredUserSchema
from mo3jam.utils import get_pagination_urls, roles_accepted, roles_required, get_json_schema

user_ns = Namespace('unregistered-users', description='Unregistered Users API',)
user_fields = user_ns.schema_model(
    'UnRegistered User',
    get_json_schema(UnRegisteredUserSchema)
)


@user_ns.route('/')
class UserList(Resource):
    schema = UnRegisteredUserSchema()

    def get(self):
        response = {}
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', current_app.config['RESULTS_PER_PAGE'])) 
        queryset = UnRegisteredUser.objects[(page-1)*page_size:page*page_size]
        response['users'] = self.schema.dump(queryset, many=True)
        response.update(get_pagination_urls(queryset, page, page_size))
        return response
    
    @user_ns.expect(user_fields)
    def post(self):
        data = self.schema.load(request.get_json())     
        user = UnRegisteredUser(
            id=uuid.uuid4(),
            **data
        )
        user.save()
        return self.schema.dump(user)


@user_ns.route('/<string:user_id>')
@user_ns.doc(params={
    "user_id": 'ID of user to be updated.'
})
class UserDetails(Resource):
    schema = UnRegisteredUserSchema()

    def get(self, user_id):
        return self.schema.dump(UnRegisteredUser.objects.get_or_404(id=user_id))
    
    @user_ns.expect(user_fields)
    def put(self, user_id):       
        data = self.schema.load(request.get_json())
        user = UnRegisteredUser.objects.get_or_404(id=user_id)
        user.update(
            **data
        )
        user.reload()
        return self.schema.dump(user)

    
    def delete(self, user_id):
        user = UnRegisteredUser.objects.get_or_404(id=user_id)
        user.delete()
        return '', 204
    

