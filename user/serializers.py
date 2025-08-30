from rest_framework.serializers import ModelSerializer

from user.models import User


class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserSerializers(ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"

    def get_field_names(self, declared_fields, info):
        expanded_fields = super().get_field_names(declared_fields, info)
        return expanded_fields + self.Meta.extra_fields


class UserPublicSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["first_name", "country", "avatar"]
        read_only_fields = fields


class UserDetailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "phone",
            "country",
            "avatar",
            "chat_id",
            ]
