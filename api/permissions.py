from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Custom permission: only allows the owner of the object.
    """
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user


class IsSeller(BasePermission):
    """
    Custom permission: only allows users with seller role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller()


class IsBuyerOrSeller(BasePermission):
    """
    Custom permission: allows buyers and sellers.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['buyer', 'seller', 'both']
