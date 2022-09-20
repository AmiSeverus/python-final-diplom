from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.type == 'client'


class IsSeller(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.type == 'seller'